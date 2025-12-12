"""Office integration endpoints bridging the realtime router and React UI."""
from __future__ import annotations

import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from assistant_core.integrations.office_realtime import (
    AIOfficeWebSocketRouter,
    ApplicationType,
    MessageType,
)
from assistant_core.intelligence.office_ai_service import OfficeAIProcessingService

router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = (REPO_ROOT / "tmp" / "office_workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

_service = OfficeAIProcessingService(workspace_dir=str(WORKSPACE))
_router = AIOfficeWebSocketRouter(ai_service_client=_service.process_message)
_router_lock = threading.Lock()
_recent_jobs: Deque[Dict[str, Any]] = deque(maxlen=25)

_DEMO_DOCUMENTS: Dict[str, Dict[str, str]] = {
    "doc-2024-q4": {
        "title": "Q4 Performance Review",
        "summary": "Live PowerPoint + Excel mashup that streams ops metrics into the dashboard.",
    },
    "doc-ops-brief": {
        "title": "Operations Briefing",
        "summary": "OneNote workspace where the AI dashboard annotates findings in real time.",
    },
}

_DEMO_CLIENTS = [
    {
        "client_id": "client-powerpoint",
        "application": ApplicationType.POWERPOINT,
        "user_id": "designer-ops",
        "document_id": "doc-2024-q4",
        "capabilities": ["generate_content", "design_review"],
    },
    {
        "client_id": "client-excel",
        "application": ApplicationType.EXCEL,
        "user_id": "finance-analyst",
        "document_id": "doc-2024-q4",
        "capabilities": ["stream_metrics", "scenario_plans"],
    },
    {
        "client_id": "client-onenote",
        "application": ApplicationType.ONENOTE,
        "user_id": "research-curator",
        "document_id": "doc-ops-brief",
        "capabilities": ["knowledge_capture", "insights"],
    },
    {
        "client_id": "client-dashboard",
        "application": ApplicationType.WEB_DASHBOARD,
        "user_id": "ai-ops",
        "document_id": "doc-2024-q4",
        "capabilities": ["monitor_sessions", "trigger_ai"],
    },
]
_DEFAULT_CLIENT_ID = "client-dashboard"

_DOC_LINKS = [
    {
        "label": "AI Office Agent Architecture",
        "href": "/docs/AI_OFFICE_AGENT_REALTIME.md",
        "description": "Explains the realtime event bus mirrored here.",
    },
    {
        "label": "Automation Orchestration",
        "href": "/docs/AUTOMATION_ORCHESTRATION_INTEGRATION.md",
        "description": "How document events feed downstream daemons.",
    },
    {
        "label": "OneNote / Office Integration",
        "href": "/docs/ONEDRIVE_INTEGRATION.md",
        "description": "The deployment playbook used for Microsoft 365 tenants.",
    },
]

_MANIFEST_PREVIEW = """<OfficeApp xmlns=\"http://schemas.microsoft.com/office/appforoffice/1.1\"
         xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
         xsi:type=\"TaskPaneApp\">
  <Id>osd-ai-office-dashboard</Id>
  <DisplayName>OS Dashboard — AI Copilot</DisplayName>
  <Description>Streams live AI assistance into PowerPoint, Excel, and Word.</Description>
  <Hosts>
    <Host Name=\"Document\" />
    <Host Name=\"Presentation\" />
    <Host Name=\"Workbook\" />
  </Hosts>
  <DefaultSettings>
    <SourceLocation DefaultValue=\"https://localhost:8800/office\" />
  </DefaultSettings>
</OfficeApp>""".strip()


class OfficeRealtimeClient(BaseModel):
    client_id: str
    application: str
    user_id: Optional[str] = None
    document_id: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    session_id: str
    last_seen: str


class OfficeRealtimeDocument(BaseModel):
    document_id: str
    title: str
    summary: Optional[str] = None
    participant_count: int
    participants: List[OfficeRealtimeClient]


class OfficeRealtimeJob(BaseModel):
    job_id: str
    client_id: str
    message_type: str
    status: str
    success: bool
    queued_at: str
    completed_at: Optional[str] = None
    duration_ms: float
    result_summary: Optional[str] = None


class OfficeRealtimeSummary(BaseModel):
    documents: List[OfficeRealtimeDocument]
    clients: List[OfficeRealtimeClient]
    recent_jobs: List[OfficeRealtimeJob]
    ai_metrics: Dict[str, Any]
    docs_links: List[Dict[str, str]]
    manifest_preview: str
    governance: Dict[str, str]
    last_updated: str


class OfficeAITrigger(BaseModel):
    operation: str = Field(
        ...,
        description="AI request to perform (analyze, generate, suggest).",
        pattern="^(analyze|generate|suggest)$",
    )
    client_id: Optional[str] = None
    target: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    wait_seconds: float = Field(
        default=5.0,
        ge=0.5,
        le=20.0,
        description="How long to wait for the AI job result before returning.",
    )


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _to_iso_timestamp(value: Any) -> str:
    try:
        # Handle float/int epoch timestamps.
        return datetime.utcfromtimestamp(float(value)).isoformat() + "Z"
    except Exception:
        try:
            text = str(value)
            if text:
                return text
        except Exception:
            pass
    return _now_iso()


def _ensure_demo_clients() -> None:
    with _router_lock:
        existing = {client.client_id for client in _router.list_clients()}
        for entry in _DEMO_CLIENTS:
            if entry["client_id"] in existing:
                continue
            _router.register_client(
                entry["client_id"],
                entry["application"],
                user_id=entry.get("user_id"),
                document_id=entry.get("document_id"),
                capabilities=entry.get("capabilities"),
            )


def _serialize_client(session) -> OfficeRealtimeClient:
    return OfficeRealtimeClient(
        client_id=session.client_id,
        application=session.application.value,
        user_id=session.user_id,
        document_id=session.document_id,
        capabilities=session.capabilities,
        session_id=session.session_id,
        last_seen=datetime.utcfromtimestamp(session.last_seen).isoformat() + "Z",
    )


def _summarize_result(result: Optional[Dict[str, Any]]) -> Optional[str]:
    if not result:
        return None
    payload = result.get("result") if isinstance(result, dict) else None
    payload = payload or result
    if not isinstance(payload, dict):
        return str(payload)[:140]

    parts: List[str] = []
    status = payload.get("status") or result.get("status")
    if status:
        parts.append(str(status))
    if "analysis" in payload:
        summary = payload["analysis"].get("summary")
        if summary:
            parts.append(summary[:120])
    if "suggestions" in payload:
        parts.append(f"{len(payload['suggestions'])} suggestions")
    if "output" in payload and isinstance(payload["output"], dict):
        keys = [key for key in payload["output"].keys() if key != "status"]
        if keys:
            parts.append(f"outputs: {', '.join(keys)}")
    return " · ".join(parts) if parts else None


def _message_type_from_operation(operation: str) -> MessageType:
    mapping = {
        "analyze": MessageType.AI_ANALYZE_REQUEST,
        "generate": MessageType.AI_GENERATE_REQUEST,
        "suggest": MessageType.AI_SUGGEST_REQUEST,
    }
    try:
        return mapping[operation]
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Unsupported operation '{operation}'.") from exc


@router.get("/realtime/summary", response_model=OfficeRealtimeSummary)
async def get_office_realtime_summary() -> OfficeRealtimeSummary:
    """Return a snapshot of the realtime Office mesh the dashboard is simulating."""
    _ensure_demo_clients()
    clients = _router.list_clients()
    client_lookup = {client.client_id: client for client in clients}
    document_index = _router.list_active_documents()

    documents: List[OfficeRealtimeDocument] = []
    for doc_id, participant_ids in document_index.items():
        participants = [
            _serialize_client(client_lookup[cid])
            for cid in participant_ids
            if cid in client_lookup
        ]
        doc_meta = _DEMO_DOCUMENTS.get(doc_id, {})
        documents.append(
            OfficeRealtimeDocument(
                document_id=doc_id,
                title=doc_meta.get("title") or doc_id.replace("-", " ").title(),
                summary=doc_meta.get("summary"),
                participant_count=len(participants),
                participants=participants,
            )
        )

    if not documents and clients:
        fallback_doc = OfficeRealtimeDocument(
            document_id="adhoc",
            title="Live Collaboration",
            summary="All connected clients are idle but ready to receive updates.",
            participant_count=len(clients),
            participants=[_serialize_client(client) for client in clients],
        )
        documents.append(fallback_doc)

    ai_metrics = {
        "pending_jobs": len(getattr(_router, "_pending_jobs", {})),
        "queue_depth": getattr(getattr(_router, "_ai_queue", None), "qsize", lambda: 0)(),
        "local_service": _router._ai_service_client is not None,  # type: ignore[attr-defined]
        "ai_service_url": _router.ai_service_url,
    }

    governance = {
        "banner": "Every AI edit is tracked • every document change is ledgered • Office clients stay tethered to the AI OS.",
        "behaviors": "Notifies stale decks · drafts slides · scores formatting · streams metrics from Excel into PowerPoint.",
    }

    return OfficeRealtimeSummary(
        documents=documents,
        clients=[_serialize_client(client) for client in clients],
        recent_jobs=[OfficeRealtimeJob(**item) for item in list(_recent_jobs)],
        ai_metrics=ai_metrics,
        docs_links=list(_DOC_LINKS),
        manifest_preview=_MANIFEST_PREVIEW,
        governance=governance,
        last_updated=_now_iso(),
    )


# FastAPI treats `/realtime/summary` and `/realtime/overview` differently,
# but the dashboard historically called the latter. Keep both paths so the
# frontend can request either without hitting 404s.
@router.get("/realtime/overview", response_model=OfficeRealtimeSummary)
async def get_office_realtime_overview() -> OfficeRealtimeSummary:
    """Backwards-compatible alias for the summary endpoint."""

    return await get_office_realtime_summary()


@router.post("/realtime/ai")
async def trigger_office_ai(payload: OfficeAITrigger) -> Dict[str, Any]:
    """Queue an AI request through the realtime router and wait for the result."""
    _ensure_demo_clients()
    client_id = payload.client_id or _DEFAULT_CLIENT_ID
    message_type = _message_type_from_operation(payload.operation)

    try:
        ack = _router.handle_ai_request(
            client_id,
            message_type,
            payload=payload.payload,
            target=payload.target,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    start = time.perf_counter()
    result = _router.get_ai_job_result(ack["job_id"], timeout=payload.wait_seconds)
    duration_ms = (time.perf_counter() - start) * 1000.0
    completed_at = _now_iso()
    success = bool(result and result.get("success", True))
    status = "success" if success else "error"
    summary = _summarize_result(result)
    job_record = {
        "job_id": ack["job_id"],
        "client_id": client_id,
        "message_type": ack["message"]["type"],
        "status": status,
        "success": success,
        "queued_at": _to_iso_timestamp(ack["message"]["timestamp"]),
        "completed_at": completed_at,
        "duration_ms": duration_ms,
        "result_summary": summary,
    }
    _recent_jobs.appendleft(job_record)

    return {
        "job": ack,
        "result": result,
        "metrics": {
            "duration_ms": duration_ms,
            "completed_at": completed_at,
        },
    }
