"""Operational platform endpoints backing the React dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import random
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ai_os.app.ai_proxy import ask_ai
from ai_os.app.system_monitor import get_system_stats
from assistant_hub_gui.assistant_hub.db import (
    db_record_document_operation,
    db_update_document_operation_status,
)
from backend_api.db import db_session


router = APIRouter()


class SystemStatus(BaseModel):
    """CPU/memory/disk stats mirroring the Tk dashboard."""

    cpu_percent: float
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    spec_refs: List[str]
    updated_at: str


class PlaneStatus(BaseModel):
    data_plane: Dict[str, Any]
    control_plane: Dict[str, Any]
    governance_plane: Dict[str, Any]
    spec_refs: List[str]
    updated_at: str


class BillingRecord(BaseModel):
    id: int
    agent: str
    action_type: str
    input_context: Optional[str] = None
    output_summary: Optional[str] = None
    related_files: Optional[str] = None
    git_commit_hash: Optional[str] = None
    created_at: str


class BillingUsageResponse(BaseModel):
    estimated_cost: float
    currency: str
    records: List[BillingRecord]


class AskPayload(BaseModel):
    prompt: str
    persona: Optional[str] = None


class AskResponse(BaseModel):
    response: str
    persona: str
    spec_refs: Optional[List[str]] = None


@dataclass
class DaemonProfile:
    """Runtime metadata surfaced to the daemon control panel."""

    name: str
    description: str
    scopes: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    risk_level: str = "medium"
    success_rate: float = 0.9
    enabled: bool = True
    last_run: Optional[datetime] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["last_run"] = (
            self.last_run.isoformat() + "Z" if self.last_run else None
        )
        return payload


DAEMON_REGISTRY: Dict[str, DaemonProfile] = {
    "regulation_ingest": DaemonProfile(
        name="regulation_ingest",
        description="Summarizes new regulations and maps to policies.",
        scopes=["/Regulations", "Policy/Privacy"],
        triggers=["pdf.added.regulations"],
        risk_level="medium",
        success_rate=0.93,
        last_run=datetime.utcnow(),
    ),
    "workspace_sync": DaemonProfile(
        name="workspace_sync",
        description="Keeps Word/Notes deliverables aligned.",
        scopes=["/Docs", "/Notes"],
        triggers=["notes.updated", "word.updated"],
        risk_level="low",
        success_rate=0.88,
    ),
    "ops_guardian": DaemonProfile(
        name="ops_guardian",
        description="Scans audit signals for drift.",
        scopes=["/Audit", "/Observability"],
        triggers=["audit.recorded", "signals.spike"],
        risk_level="high",
        success_rate=0.91,
        enabled=False,
    ),
}


def _estimate_cost(record_count: int) -> float:
    return round(record_count * 0.02, 2)


def _record_daemon_operation(name: str) -> int:
    """Persist a short audit log entry for daemon execution."""

    title = f"Daemon run · {name.replace('_', ' ').title()}"
    external_id = str(uuid.uuid4())
    with db_session() as conn:
        operation_id = db_record_document_operation(
            conn,
            title=title,
            project_id="control-plane",
            integration_type="daemon",
            external_id=external_id,
            operation=f"{name}.run",
            status="running",
            persona="AIC",
            version_tag=None,
            diff_path=None,
            external_company=None,
            notes="Triggered via FastAPI daemon control panel",
        )
        db_update_document_operation_status(
            conn,
            operation_id,
            status="succeeded",
            notes="Daemon execution completed",
            mark_complete=True,
        )
        return operation_id


@router.get("/system", response_model=SystemStatus)
async def system_status() -> SystemStatus:
    """Expose psutil-backed stats for the Command Center widgets."""

    stats = get_system_stats().copy()
    stats["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return SystemStatus(**stats)


@router.get("/planes/status", response_model=PlaneStatus)
async def planes_status() -> PlaneStatus:
    """Summarize data/control/governance plane health."""

    with db_session() as conn:
        project_rows = conn.execute(
            "SELECT DISTINCT project FROM tasks WHERE project != ''"
        ).fetchall()
        collections = sorted({row[0] for row in project_rows}) or ["projects"]
        op_cursor = conn.execute("SELECT COUNT(*) FROM document_operations")
        documents_indexed = op_cursor.fetchone()[0]
        pending_reviews = conn.execute(
            "SELECT COUNT(*) FROM document_operations WHERE status != 'succeeded'"
        ).fetchone()[0]

    data_plane = {
        "collections": collections,
        "documents_indexed": documents_indexed,
        "last_snapshot": datetime.utcnow().isoformat() + "Z",
    }
    control_plane = {
        "middlewares": 3,
        "active_workflows": random.randint(1, 4),
        "last_heartbeat": datetime.utcnow().isoformat() + "Z",
    }
    governance_plane = {
        "policy": "AllowAllPolicy",
        "open_reviews": pending_reviews,
        "last_audit": datetime.utcnow().isoformat() + "Z",
    }
    return PlaneStatus(
        data_plane=data_plane,
        control_plane=control_plane,
        governance_plane=governance_plane,
        spec_refs=["1.7", "5.2", "6.6"],
        updated_at=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/daemons")
async def list_daemons() -> Dict[str, Any]:
    """Return the known daemon inventory."""

    return {"daemons": [daemon.to_payload() for daemon in DAEMON_REGISTRY.values()]}


def _get_daemon(name: str) -> DaemonProfile:
    daemon = DAEMON_REGISTRY.get(name)
    if not daemon:
        raise HTTPException(status_code=404, detail="Daemon not found")
    return daemon


@router.post("/daemons/{name}/enable")
async def enable_daemon(name: str) -> Dict[str, Any]:
    daemon = _get_daemon(name)
    daemon.enabled = True
    return {"daemon": daemon.to_payload(), "status": "running"}


@router.post("/daemons/{name}/disable")
async def disable_daemon(name: str) -> Dict[str, Any]:
    daemon = _get_daemon(name)
    daemon.enabled = False
    return {"daemon": daemon.to_payload(), "status": "stopped"}


@router.post("/daemons/{name}/run")
async def run_daemon(name: str) -> Dict[str, Any]:
    daemon = _get_daemon(name)
    if not daemon.enabled:
        raise HTTPException(status_code=400, detail="Daemon is disabled")
    daemon.last_run = datetime.utcnow()
    operation_id = _record_daemon_operation(name)
    return {
        "status": "queued",
        "daemon": daemon.name,
        "operation_id": operation_id,
    }


@router.post("/ai/ask", response_model=AskResponse)
async def ask_ai_route(payload: AskPayload) -> AskResponse:
    """Passthrough to the lightweight AI proxy used elsewhere."""

    result = ask_ai(payload.prompt)
    response = result.get("response", "AI service unavailable.")
    persona = payload.persona or "AIC"
    spec_refs = result.get("spec_refs")
    return AskResponse(response=response, persona=persona, spec_refs=spec_refs)


@router.get("/billing/usage", response_model=BillingUsageResponse)
async def billing_usage(
    limit: int = Query(20, ge=1, le=100)
) -> BillingUsageResponse:
    """Read recent agent runs and estimate compute cost."""

    with db_session() as conn:
        cursor = conn.execute(
            """
            SELECT id, agent, action_type, input_context, output_summary,
                   related_files, git_commit_hash, created_at
            FROM agent_runs
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = [dict(row) for row in cursor.fetchall()]

    return BillingUsageResponse(
        estimated_cost=_estimate_cost(len(rows)),
        currency="USD",
        records=rows,
    )
