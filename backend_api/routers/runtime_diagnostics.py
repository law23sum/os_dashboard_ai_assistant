"""Runtime diagnostics endpoint for capturing client-side failures."""
from __future__ import annotations

import json
import os
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, Field
from assistant_hub.ui.terminal.harness import latest_workspace_report
from backend_api.db import db_session
from backend_api.routers.logs import record_event

router = APIRouter()

_LOG_ENV_VAR = "OSDASH_RUNTIME_LOG"
_DEFAULT_LOG_PATH = Path("logs") / "runtime_diagnostics.log"


class RuntimeDiagnostic(BaseModel):
    source: str = Field(..., description="Component or page that triggered the report")
    message: str = Field(..., description="Human-readable summary")
    stack: Optional[str] = Field(None, description="Captured stack trace when available")
    severity: str = Field("error", description="error|warning|info")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional diagnostic information (browser metadata, etc.)",
    )


class RuntimeEvent(BaseModel):
    id: str
    type: str
    source: str
    message: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    stack: Optional[str] = None


class RuntimeDiagnosticsSummary(BaseModel):
    total: int
    errors: int
    warnings: int
    infos: int
    last_seen: Optional[str] = None
    log_path: str


class RuntimeDiagnosticsResponse(BaseModel):
    events: List[RuntimeEvent]
    summary: RuntimeDiagnosticsSummary


class HarnessProjectSummary(BaseModel):
    name: str
    status: str
    failed: int
    passed: int
    skipped: int
    commands: List[str] = Field(default_factory=list)


class HarnessReport(BaseModel):
    generated_at: Optional[str] = None
    status: str = "unknown"
    root: str
    total_projects: int
    total_checks: int
    failed_checks: int
    passed_checks: int
    skipped_checks: int
    run_id: Optional[str] = None
    report_path: Optional[str] = None
    projects: List[HarnessProjectSummary] = Field(default_factory=list)


def _resolve_log_path() -> Path:
    override = os.environ.get(_LOG_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    return _DEFAULT_LOG_PATH


def _append_event(payload: Dict[str, Any]) -> None:
    log_path = _resolve_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)
        handle.write("\n")


def _load_events(limit: int) -> List[RuntimeEvent]:
    log_path = _resolve_log_path()
    if not log_path.exists():
        return []

    records: deque[Dict[str, Any]] = deque(maxlen=limit)
    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                raw = json.loads(line.strip())
                records.append(raw)
            except json.JSONDecodeError:
                continue

    events: List[RuntimeEvent] = []
    for idx, record in enumerate(reversed(records)):
        ts = record.get("timestamp")
        timestamp = ts if isinstance(ts, str) else datetime.now(timezone.utc).isoformat()
        severity = record.get("severity") or record.get("type") or "info"
        events.append(
            RuntimeEvent(
                id=str(record.get("id", idx)),
                type=severity,
                source=record.get("source", "unknown"),
                message=record.get("message", "No message provided"),
                timestamp=timestamp,
                metadata=record.get("context") or record.get("metadata") or {},
                stack=record.get("stack"),
            )
        )
    return events


def _summarize(events: List[RuntimeEvent]) -> RuntimeDiagnosticsSummary:
    errors = len([e for e in events if e.type == "error"])
    warnings = len([e for e in events if e.type == "warning"])
    infos = len([e for e in events if e.type not in ("error", "warning")])
    last_seen = events[0].timestamp if events else None
    return RuntimeDiagnosticsSummary(
        total=len(events),
        errors=errors,
        warnings=warnings,
        infos=infos,
        last_seen=last_seen,
        log_path=str(_resolve_log_path()),
    )


def _summarize_harness_project(entry: Dict[str, Any]) -> HarnessProjectSummary:
    profile = entry.get("profile") or {}
    counts = entry.get("counts") or {}
    commands: List[str] = []
    for category, command_sets in (profile.get("commands") or {}).items():
        for command in command_sets:
            if isinstance(command, list):
                commands.append(" ".join(str(part) for part in command))
            elif isinstance(command, str):
                commands.append(command)
    return HarnessProjectSummary(
        name=str(profile.get("name") or profile.get("root") or "unknown"),
        status=str(entry.get("status") or "unknown"),
        failed=int(counts.get("failed") or 0),
        passed=int(counts.get("passed") or 0),
        skipped=int(counts.get("skipped") or 0),
        commands=commands,
    )


def _load_harness_report() -> HarnessReport:
    raw = latest_workspace_report()
    if not raw:
        return HarnessReport(
            status="missing",
            root=str(Path(".").resolve()),
            total_projects=0,
            total_checks=0,
            failed_checks=0,
            passed_checks=0,
            skipped_checks=0,
            projects=[],
        )

    summary = raw.get("summary") or {}
    projects_payload = raw.get("projects") or []
    projects = [_summarize_harness_project(entry) for entry in projects_payload]

    def _sum(attr: str) -> int:
        return sum(getattr(project, attr) for project in projects)

    return HarnessReport(
        generated_at=str(summary.get("generated_at")),
        status=str(summary.get("status") or "unknown"),
        root=str(summary.get("root") or Path(".").resolve()),
        total_projects=int(summary.get("projects") or len(projects)),
        total_checks=int(summary.get("checks") or (_sum("failed") + _sum("passed") + _sum("skipped"))),
        failed_checks=int(summary.get("failed") or _sum("failed")),
        passed_checks=int(summary.get("passed") or _sum("passed")),
        skipped_checks=int(summary.get("skipped") or _sum("skipped")),
        run_id=summary.get("run_id"),
        report_path=raw.get("report_path") or summary.get("report_path"),
        projects=projects,
    )


@router.post(
    "/runtime/diagnostics",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Record a runtime diagnostic event",
)
async def record_runtime_diagnostic(event: RuntimeDiagnostic) -> Dict[str, str]:
    payload = event.model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    _append_event(payload)
    # Also mirror into the unified DB event log for endless streaming.
    try:
        with db_session() as db:
            record_event(
                db=db,
                source=str(event.source or "runtime"),
                level=str(event.severity or "info"),
                message=str(event.message or ""),
                user_id=None,
                metadata=event.context or {},
            )
    except Exception:
        pass
    return {"status": "accepted"}


@router.get(
    "/runtime/diagnostics/ping",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def runtime_ping() -> Response:
    """Simple liveness endpoint for smoke tests."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/runtime/diagnostics",
    response_model=RuntimeDiagnosticsResponse,
    summary="Read recent runtime diagnostic events",
)
async def list_runtime_diagnostics(
    limit: int = Query(100, ge=1, le=500),
) -> RuntimeDiagnosticsResponse:
    """
    Return a bounded set of runtime diagnostic events plus a rolled-up summary.

    The handler reads from the NDJSON log used by the POST endpoint so the React
    observability page can render errors without requiring filesystem access.
    """

    events = _load_events(limit)
    summary = _summarize(events)
    return RuntimeDiagnosticsResponse(events=events, summary=summary)


@router.get(
    "/runtime/harness-report",
    response_model=HarnessReport,
    summary="Read the latest workspace harness report",
)
async def read_harness_report() -> HarnessReport:
    """Expose the most recent osdash harness run for the Observability UI."""

    return _load_harness_report()
