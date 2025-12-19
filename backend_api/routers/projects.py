"""Projects API router."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import hashlib
import random
import sys
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import (  # pylint: disable=wrong-import-position
    db_delete_project,
    db_get_note_links,
    db_list_project_events,
    db_record_project_event,
    db_upsert_project,
    load_state,
    Project as DBProject,
)
from assistant_hub_gui.assistant_hub.config import DATA_DIR  # pylint: disable=wrong-import-position
from assistant_hub_gui.assistant_hub.project_insights import (  # pylint: disable=wrong-import-position
    analyze_project_risks,
    predict_project_completion,
)
from backend_api.db import db_session  # pylint: disable=wrong-import-position

router = APIRouter()

REPO_ROOT = parent_dir
DOCS_DIR = REPO_ROOT / "docs"
LEGACY_UI_DIR = REPO_ROOT / "ui"
DOCUMENTATION_DIR = REPO_ROOT / "documentation"
DOCUMENTS_BASE_DIR = Path(DATA_DIR) / "documents"

INTEGRATION_LABELS = {
    "onenote": "OneNote Notebook",
    "local_onenote": "OneNote Mirror",
    "local_word": "Word Doc",
    "local_excel": "Excel Workbook",
    "local_pdf": "PDF Archive",
    "filesystem": "Filesystem Asset",
}


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    status: str = "active"
    priority: str = "MEDIUM"
    order_num: int = 0


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    order_num: Optional[int] = None


class ProjectResponse(BaseModel):
    name: str
    description: str
    status: str
    priority: str
    order_num: int

    class Config:
        from_attributes = True


class ProjectLinkResponse(BaseModel):
    id: int
    project_id: str
    integration_type: str
    title: str
    description: str
    external_id: str
    created_at: str
    last_synced: Optional[str]
    label: str
    href: Optional[str]
    available: bool


class ProjectLedgerEvent(BaseModel):
    id: str
    project_id: str
    event_type: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    payload: Dict[str, Any]
    created_at: str
    hash_prev: Optional[str]
    hash_curr: Optional[str]


class ProjectRiskInsight(BaseModel):
    risk_score: int
    severity: str
    risks: List[Dict[str, Any]]
    recommendations: str
    total_tasks: Optional[int] = 0
    completed_tasks: Optional[int] = 0
    completion_rate: Optional[float] = 0.0


class ProjectForecastInsight(BaseModel):
    predicted_date: Optional[str]
    confidence: str = "unknown"
    reasoning: str = ""
    estimated_days: Optional[int] = None
    avg_completion_days: Optional[float] = None
    pending_task_count: Optional[int] = 0


class ProjectInsightResponse(BaseModel):
    project: str
    generated_at: str
    risk: ProjectRiskInsight
    forecast: ProjectForecastInsight


class ProjectIntelligenceResponse(BaseModel):
    project_id: str
    health_score: float
    risk_level: str
    completion_ratio: float
    total_tasks: int
    open_tasks: int
    critical_tasks: int
    ledger_ok: bool
    last_event_at: Optional[str]
    last_event_type: Optional[str]
    summary: str


class PersonaHealthSnapshot(BaseModel):
    persona: str
    role: str
    status: str
    utilization: int
    context: str


class TRFHeuristic(BaseModel):
    label: str
    status: str
    detail: str
    spec_ref: str


class TRFTrace(BaseModel):
    trace_id: str
    project_id: str
    operator: str
    persona: str
    premise: str
    conclusion: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)
    compliance_gate: str
    created_at: str


class ProjectTRFResponse(BaseModel):
    project_id: str
    spec_refs: List[str]
    entropy: float
    resonance: float
    continuity: float
    heuristics: List[TRFHeuristic]
    personas: List[PersonaHealthSnapshot]
    traces: List[TRFTrace]


def _friendly_label(integration: str) -> str:
    """Return a human-friendly label for integration types."""
    if integration in INTEGRATION_LABELS:
        return INTEGRATION_LABELS[integration]
    if integration.startswith("local_"):
        return f"{integration.replace('local_', '').title()} Document"
    return integration.replace("_", " ").title()


def _detect_href_and_presence(external_id: str) -> Tuple[Optional[str], bool]:
    """Return a web-friendly href (if accessible) and whether the asset exists."""
    if not external_id:
        return None, False

    identifier = external_id.strip()
    if identifier.startswith(("http://", "https://")):
        return identifier, True

    candidates = []
    normalized = identifier.lstrip("./")
    candidates.append(REPO_ROOT / normalized)
    candidates.append(DOCS_DIR / normalized)
    candidates.append(LEGACY_UI_DIR / normalized)
    candidates.append(DOCUMENTATION_DIR / normalized)
    candidates.append(DOCUMENTS_BASE_DIR / normalized)

    for candidate in candidates:
        if candidate.exists():
            try:
                rel_path = candidate.relative_to(REPO_ROOT)
            except ValueError:
                rel_path = None

            if rel_path and (
                rel_path.parts[0] in ("docs", "ui")
                or rel_path.as_posix().startswith("docs/")
                or rel_path.as_posix().startswith("ui/")
            ):
                return f"/{rel_path.as_posix()}", True
            return None, True

    return None, False


def _project_exists(conn, project_name: str) -> bool:
    cursor = conn.execute("SELECT 1 FROM projects WHERE name = ?", (project_name,))
    return cursor.fetchone() is not None


def _serialize_links(links) -> List[ProjectLinkResponse]:
    payload: List[ProjectLinkResponse] = []
    for link in links:
        href, available = _detect_href_and_presence(link.external_id or "")
        payload.append(
            ProjectLinkResponse(
                id=link.id,
                project_id=link.project_id,
                integration_type=link.integration_type,
                title=link.title or _friendly_label(link.integration_type),
                description=link.description or "",
                external_id=link.external_id,
                created_at=link.created_at,
                last_synced=link.last_synced,
                label=_friendly_label(link.integration_type),
                href=href,
                available=available,
            )
        )
    return payload


def _group_tasks_by_project(conn) -> Dict[str, List[Dict[str, Any]]]:
    cursor = conn.execute("SELECT project, status, priority FROM tasks")
    tasks_by_project: Dict[str, List[Dict[str, Any]]] = {}
    for row in cursor.fetchall():
        project_name = row["project"] or "General"
        tasks_by_project.setdefault(project_name, []).append(
            {
                "status": row["status"] or "UNKNOWN",
                "priority": row["priority"] or "MEDIUM",
            }
        )
    return tasks_by_project


TRF_OPERATORS = ["ASSERT", "WEAVE", "RESONATE", "COLLAPSE", "ESCALATE"]
TRF_PERSONAS = ["AIC", "Aria", "Sora", "Echo"]


def _hash_pick(seed: str, options: List[str]) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return options[int(digest, 16) % len(options)]


def _collect_project_tasks(conn, project_id: str) -> List[Dict[str, Any]]:
    cursor = conn.execute(
        "SELECT id, title, status, priority, owner, due_date FROM tasks WHERE project = ?",
        (project_id,),
    )
    tasks = []
    for row in cursor.fetchall():
        tasks.append(
            {
                "id": row["id"],
                "title": row["title"],
                "status": row["status"] or "UNKNOWN",
                "priority": row["priority"] or "MEDIUM",
                "owner": row["owner"] or "AIC",
                "due_date": row["due_date"],
            }
        )
    return tasks


def _compute_trf_scores(tasks: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> Tuple[float, float, float]:
    if not tasks:
        return 0.2, 0.6, 0.4

    total = len(tasks)
    open_tasks = len([t for t in tasks if (t["status"] or "").lower() != "done"])
    critical = len([t for t in tasks if (t["priority"] or "").upper() == "CRITICAL"])
    blocked = len([t for t in tasks if (t["status"] or "").lower() in ("blocked", "waiting")])

    entropy = min(1.0, (open_tasks + critical) / max(1, total * 1.2))
    resonance = max(0.15, 1.0 - (critical / max(1, total)))
    continuity = max(0.1, 1.0 - (blocked / max(1, total)) + min(0.25, len(events) / 40))
    return round(entropy, 3), round(resonance, 3), round(continuity, 3)


def _build_persona_health(tasks: List[Dict[str, Any]]) -> List[PersonaHealthSnapshot]:
    if not tasks:
        return [
            PersonaHealthSnapshot(
                persona="AIC",
                role="Meta-Governor",
                status="steady",
                utilization=32,
                context="Awaiting TRF inputs",
            )
        ]

    owners = Counter([t["owner"] or "Chris" for t in tasks])
    critical_by_owner = Counter(
        [t["owner"] or "Chris" for t in tasks if (t["priority"] or "").upper() == "CRITICAL"]
    )
    persona_rows: List[PersonaHealthSnapshot] = []
    for owner, count in owners.items():
        critical = critical_by_owner.get(owner, 0)
        utilization = min(100, int((count / max(1, len(tasks))) * 120))
        status = "steady"
        if critical >= 2:
            status = "watch"
        if critical >= 4:
            status = "constrained"
        persona_rows.append(
            PersonaHealthSnapshot(
                persona=owner,
                role="Persona" if owner in TRF_PERSONAS else "Contributor",
                status=status,
                utilization=utilization,
                context=f"{count} open · {critical} critical",
            )
        )
    return sorted(persona_rows, key=lambda row: row.utilization, reverse=True)


def _build_trf_heuristics(project: str, tasks: List[Dict[str, Any]], entropy: float) -> List[TRFHeuristic]:
    total = len(tasks)
    due_dates = len([t for t in tasks if t.get("due_date")])
    heuristics = [
        TRFHeuristic(
            label="Tensor Risk Field",
            status="watch" if entropy > 0.55 else "steady",
            detail=f"{project} entropy at {int(entropy * 100)}% · monitoring §4.6 invariants",
            spec_ref="§4.6",
        ),
        TRFHeuristic(
            label="Persona Coverage",
            status="steady" if total <= 12 else "calibrate",
            detail=f"{total} active intents routed across personas",
            spec_ref="§4.5",
        ),
        TRFHeuristic(
            label="Continuity Hooks",
            status="warning" if due_dates >= 3 else "steady",
            detail=f"{due_dates} scheduled milestones require TRF trace sign-off",
            spec_ref="§4.7",
        ),
    ]
    return heuristics


def _build_trf_traces(
    project: str,
    tasks: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    limit: int,
) -> List[TRFTrace]:
    traces: List[TRFTrace] = []
    source_items = events or tasks
    if not source_items:
        return traces

    for item in source_items[:limit]:
        if "event_type" in item:
            seed = f"{project}-{item['id']}"
            detail = item["payload"] or {}
            premise = detail.get("description") or item["event_type"].replace("_", " ").title()
            conclusion = detail.get("status") or f"{item['event_type']} recorded"
            created_at = item["created_at"]
            evidence = f"Ledger hash {item.get('hash_curr', 'n/a')}"
        else:
            seed = f"{project}-{item['id']}"
            premise = item.get("title") or "Task intent"
            conclusion = f"Route {item.get('priority', 'MEDIUM').title()} workload"
            created_at = datetime.utcnow().isoformat() + "Z"
            evidence = "Task telemetry"

        operator = _hash_pick(seed, TRF_OPERATORS)
        persona = _hash_pick(seed[::-1], TRF_PERSONAS)
        confidence = (int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % 35) / 100 + 0.6

        traces.append(
            TRFTrace(
                trace_id=str(uuid.uuid4()),
                project_id=project,
                operator=operator,
                persona=persona,
                premise=premise,
                conclusion=conclusion,
                evidence=evidence,
                confidence=round(min(confidence, 0.98), 2),
                compliance_gate="AIC Review" if operator in ("ESCALATE", "COLLAPSE") else "Daemon Runtime",
                created_at=created_at,
            )
        )
    return traces


def _calculate_event_hash(
    event_id: str,
    project_id: str,
    event_type: str,
    created_at: str,
    entity_type: Optional[str],
    entity_id: Optional[str],
    hash_prev: Optional[str],
) -> str:
    source = f"{event_id}{project_id}{event_type}{created_at}"
    if entity_type:
        source += entity_type
    if entity_id:
        source += entity_id
    if hash_prev:
        source += hash_prev
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _verify_ledger(events: List[Dict[str, Any]]) -> bool:
    if not events:
        return True
    ordered = sorted(events, key=lambda evt: evt["created_at"])
    prev_hash: Optional[str] = None
    for event in ordered:
        expected_prev = prev_hash
        if expected_prev and event.get("hash_prev") != expected_prev:
            return False
        recalculated = _calculate_event_hash(
            event["id"],
            event["project_id"],
            event["event_type"],
            event["created_at"],
            event.get("entity_type"),
            event.get("entity_id"),
            event.get("hash_prev"),
        )
        if event.get("hash_curr") != recalculated:
            return False
        prev_hash = event.get("hash_curr")
    return True


def _determine_risk_level(
    completion_ratio: float, open_tasks: int, critical_tasks: int, ledger_ok: bool, stale_hours: float
) -> str:
    if not ledger_ok or critical_tasks >= 3:
        return "critical"
    if critical_tasks >= 1 or open_tasks > 12 or completion_ratio < 0.4:
        return "high"
    if open_tasks > 0 or stale_hours > 48 or completion_ratio < 0.7:
        return "guarded"
    return "steady"


def _compute_health_score(
    completion_ratio: float, open_tasks: int, critical_tasks: int, ledger_ok: bool, stale_hours: float
) -> float:
    score = 50 + completion_ratio * 40
    score -= min(open_tasks, 25) * 1.2
    score -= critical_tasks * 7
    if stale_hours > 24:
        score -= min((stale_hours - 24) * 0.5, 15)
    if not ledger_ok:
        score -= 25
    return max(5.0, min(95.0, round(score, 2)))


def _format_summary(risk_level: str, open_tasks: int, critical_tasks: int, ledger_ok: bool) -> str:
    fragments = []
    if risk_level == "critical":
        fragments.append("Immediate attention required")
    elif risk_level == "high":
        fragments.append("High risk posture")
    elif risk_level == "guarded":
        fragments.append("Guarded state")
    else:
        fragments.append("Steady state")

    if critical_tasks:
        fragments.append(f"{critical_tasks} critical tasks open")
    if open_tasks and critical_tasks == 0:
        fragments.append(f"{open_tasks} tasks remaining")
    if not ledger_ok:
        fragments.append("ledger integrity alert")
    return " · ".join(fragments)


def _compute_project_intelligence(
    conn, project_id: str, tasks_map: Dict[str, List[Dict[str, Any]]]
) -> ProjectIntelligenceResponse:
    tasks = tasks_map.get(project_id, [])
    total_tasks = len(tasks)
    open_tasks = sum(1 for task in tasks if (task["status"] or "").upper() not in ("DONE", "CANCELLED"))
    critical_tasks = sum(
        1
        for task in tasks
        if (task["priority"] or "").upper() == "CRITICAL"
        and (task["status"] or "").upper() not in ("DONE", "CANCELLED")
    )
    completion_ratio = (total_tasks - open_tasks) / total_tasks if total_tasks else 1.0

    events = db_list_project_events(conn, project_id=project_id, limit=250)
    ledger_ok = _verify_ledger(events)
    last_event = events[0] if events else None

    last_event_at = last_event["created_at"] if last_event else None
    last_event_type = last_event["event_type"] if last_event else None

    stale_hours = 0.0
    if last_event_at:
        try:
            timestamp = datetime.fromisoformat(last_event_at)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        except ValueError:
            timestamp = None
        if timestamp:
            stale_hours = max(0.0, (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600)

    risk_level = _determine_risk_level(completion_ratio, open_tasks, critical_tasks, ledger_ok, stale_hours)
    health_score = _compute_health_score(completion_ratio, open_tasks, critical_tasks, ledger_ok, stale_hours)
    summary = _format_summary(risk_level, open_tasks, critical_tasks, ledger_ok)

    return ProjectIntelligenceResponse(
        project_id=project_id,
        health_score=health_score,
        risk_level=risk_level,
        completion_ratio=round(completion_ratio, 3),
        total_tasks=total_tasks,
        open_tasks=open_tasks,
        critical_tasks=critical_tasks,
        ledger_ok=ledger_ok,
        last_event_at=last_event_at,
        last_event_type=last_event_type,
        summary=summary,
    )


def _serialize_events(events: List[Dict[str, Any]]) -> List[ProjectLedgerEvent]:
    """Convert DB rows into API responses."""
    serialized: List[ProjectLedgerEvent] = []
    for event in events:
        serialized.append(
            ProjectLedgerEvent(
                id=str(event["id"]),
                project_id=str(event["project_id"]),
                event_type=event["event_type"],
                entity_type=event.get("entity_type"),
                entity_id=event.get("entity_id"),
                payload=event.get("payload") or {},
                created_at=event["created_at"],
                hash_prev=event.get("hash_prev"),
                hash_curr=event.get("hash_curr"),
            )
        )
    return serialized


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(status: Optional[str] = None):
    """List all projects with optional status filtering."""
    query = "SELECT * FROM projects WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY order_num, name"

    with db_session() as db:
        cursor = db.execute(query, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

    projects = []
    for row in rows:
        project_dict = dict(zip(columns, row))
        projects.append(ProjectResponse(**project_dict))

    return projects


@router.get("/links", response_model=List[ProjectLinkResponse])
async def list_links(project: Optional[str] = None, integration: Optional[str] = None):
    """Return document/OneNote links for all projects or a specific project."""
    with db_session() as db:
        if project and not _project_exists(db, project):
            raise HTTPException(status_code=404, detail="Project not found")
        links = db_get_note_links(
            db, project_id=project, integration_type=integration
        )

    return _serialize_links(links)


@router.get("/ledger", response_model=List[ProjectLedgerEvent])
async def list_project_ledger(project: Optional[str] = None, limit: int = 50):
    """Return recent ledger events for one or all projects."""
    safe_limit = max(1, min(limit, 500))
    with db_session() as db:
        if project and not _project_exists(db, project):
            raise HTTPException(status_code=404, detail="Project not found")
        events = db_list_project_events(db, project_id=project, limit=safe_limit)
    return _serialize_events(events)


@router.get("/count")
async def get_project_count():
    """Get total count of projects for quick health check."""
    with db_session() as db:
        cursor = db.execute("SELECT COUNT(*) as count FROM projects")
        row = cursor.fetchone()
        return {"count": row["count"] if row else 0}


@router.get("/intelligence", response_model=List[ProjectIntelligenceResponse])
async def list_project_intelligence():
    """Return calculated project intelligence/health metrics."""
    with db_session() as db:
        cursor = db.execute("SELECT name FROM projects ORDER BY order_num, name")
        project_rows = cursor.fetchall()
        tasks_map = _group_tasks_by_project(db)
        return [
            _compute_project_intelligence(db, project_row["name"], tasks_map) for project_row in project_rows
        ]


@router.get("/{project_name}", response_model=ProjectResponse)
async def get_project(project_name: str):
    """Get a single project by name."""
    with db_session() as db:
        cursor = db.execute("SELECT * FROM projects WHERE name = ?", (project_name,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")

        columns = [description[0] for description in cursor.description]
        project_dict = dict(zip(columns, row))
    return ProjectResponse(**project_dict)


@router.get("/{project_name}/links", response_model=List[ProjectLinkResponse])
async def get_project_links(project_name: str, integration: Optional[str] = None):
    """Return document/OneNote links for a specific project."""
    return await list_links(project=project_name, integration=integration)


@router.get("/{project_name}/ledger", response_model=List[ProjectLedgerEvent])
async def get_project_ledger(project_name: str, limit: int = 50):
    """Return ledger events for a specific project."""
    return await list_project_ledger(project=project_name, limit=limit)


@router.get("/{project_name}/insights", response_model=ProjectInsightResponse)
async def get_project_insights(project_name: str):
    """Return AI-powered risk + forecast insights for a project."""
    with db_session() as db:
        if not _project_exists(db, project_name):
            raise HTTPException(status_code=404, detail="Project not found")
        state = load_state(db)

    risk_snapshot = analyze_project_risks(state, project_name)
    forecast_snapshot = predict_project_completion(state, project_name)

    return ProjectInsightResponse(
        project=project_name,
        generated_at=datetime.now(timezone.utc).isoformat(),
        risk=ProjectRiskInsight(**risk_snapshot),
        forecast=ProjectForecastInsight(**forecast_snapshot),
    )


@router.get("/{project_name}/intelligence", response_model=ProjectIntelligenceResponse)
async def get_project_intelligence(project_name: str):
    """Return intelligence metrics for a single project."""
    with db_session() as db:
        if not _project_exists(db, project_name):
            raise HTTPException(status_code=404, detail="Project not found")
        tasks_map = _group_tasks_by_project(db)
        return _compute_project_intelligence(db, project_name, tasks_map)


@router.get("/{project_name}/trf", response_model=ProjectTRFResponse)
async def get_project_trf(project_name: str, limit: int = 10):
    """Return TRF reasoning traces + heuristics for a project."""
    safe_limit = max(3, min(limit, 25))
    with db_session() as conn:
        if not _project_exists(conn, project_name):
            raise HTTPException(status_code=404, detail="Project not found")
        tasks = _collect_project_tasks(conn, project_name)
        events_raw = db_list_project_events(conn, project_id=project_name, limit=safe_limit)

    entropy, resonance, continuity = _compute_trf_scores(tasks, events_raw)
    heuristics = _build_trf_heuristics(project_name, tasks, entropy)
    personas = _build_persona_health(tasks)
    traces = _build_trf_traces(project_name, tasks, events_raw, safe_limit)

    return ProjectTRFResponse(
        project_id=project_name,
        spec_refs=["§4.5", "§4.6", "§4.7", "§4.8"],
        entropy=entropy,
        resonance=resonance,
        continuity=continuity,
        heuristics=heuristics,
        personas=personas,
        traces=traces,
    )


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    with db_session() as db:
        db_project = DBProject(
            name=project.name,
            description=project.description,
            status=project.status,
            priority=project.priority,
            order_num=project.order_num,
        )
        db_upsert_project(db, db_project)

        cursor = db.execute("SELECT * FROM projects WHERE name = ?", (project.name,))
        row = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        project_dict = dict(zip(columns, row))
        db_record_project_event(
            db,
            project_id=project_dict["name"],
            event_type="project_created",
            entity_type="project",
            entity_id=project_dict["name"],
            payload={
                "status": project_dict.get("status"),
                "priority": project_dict.get("priority"),
                "description": project_dict.get("description"),
            },
        )
    return ProjectResponse(**project_dict)


@router.put("/{project_name}", response_model=ProjectResponse)
async def update_project(project_name: str, project_update: ProjectUpdate):
    """Update an existing project."""
    with db_session() as db:
        cursor = db.execute("SELECT * FROM projects WHERE name = ?", (project_name,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing values from the row
        columns = [desc[0] for desc in cursor.description]
        existing = dict(zip(columns, row))

        update_dict = project_update.model_dump(exclude_unset=True)
        
        # Create a DBProject with merged values
        db_project = DBProject(
            name=update_dict.get("name", project_name),
            description=update_dict.get("description", existing.get("description", "")),
            status=update_dict.get("status", existing.get("status", "active")),
            priority=update_dict.get("priority", existing.get("priority", "MEDIUM")),
            order_num=update_dict.get("order_num", existing.get("order_num", 0)),
        )

        db_upsert_project(db, db_project)

        cursor = db.execute(
            "SELECT * FROM projects WHERE name = ?",
            (update_dict.get("name", project_name),),
        )
        row = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        project_dict = dict(zip(columns, row))
        db_record_project_event(
            db,
            project_id=project_dict["name"],
            event_type="project_updated",
            entity_type="project",
            entity_id=project_dict["name"],
            payload={
                "status": project_dict.get("status"),
                "priority": project_dict.get("priority"),
                "description": project_dict.get("description"),
            },
        )
    return ProjectResponse(**project_dict)


@router.delete("/{project_name}", status_code=204)
async def delete_project(project_name: str):
    """Delete a project."""
    with db_session() as db:
        cursor = db.execute("SELECT * FROM projects WHERE name = ?", (project_name,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        columns = [description[0] for description in cursor.description]
        project_dict = dict(zip(columns, row))

        db_delete_project(db, project_name)
        db_record_project_event(
            db,
            project_id=project_name,
            event_type="project_deleted",
            entity_type="project",
            entity_id=project_name,
            payload={
                "status": project_dict.get("status"),
                "priority": project_dict.get("priority"),
                "description": project_dict.get("description"),
            },
        )
    return None


# ============================================================================
# IMPORT/EXPORT ENDPOINTS - Prevent data loss (Spec §6.7 Archive & Backup)
# ============================================================================

class ProjectExportData(BaseModel):
    """Complete project data for export/import."""
    name: str
    description: str = ""
    status: str = "active"
    priority: str = "MEDIUM"
    order_num: int = 0
    tasks: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []
    ledger_events: List[Dict[str, Any]] = []


class ExportResponse(BaseModel):
    """Full export bundle with metadata."""
    version: str = "1.0"
    exported_at: str
    environment: str = "local"
    projects: List[ProjectExportData]
    total_projects: int
    total_tasks: int
    total_links: int
    total_ledger_events: int


class ImportRequest(BaseModel):
    """Import request with projects data."""
    projects: List[Dict[str, Any]]
    overwrite_existing: bool = False
    import_tasks: bool = True
    import_links: bool = True


class ImportResult(BaseModel):
    """Import operation result."""
    success: bool
    projects_imported: int
    projects_skipped: int
    projects_updated: int
    tasks_imported: int
    links_imported: int
    errors: List[str]


@router.get("/export/all", response_model=ExportResponse)
async def export_all_projects():
    """Export all projects with their tasks, links, and ledger events."""
    with db_session() as db:
        # Get all projects
        cursor = db.execute("SELECT * FROM projects ORDER BY order_num, name")
        project_rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        projects_data: List[ProjectExportData] = []
        total_tasks = 0
        total_links = 0
        total_ledger = 0
        
        for row in project_rows:
            project_dict = dict(zip(columns, row))
            project_name = project_dict["name"]
            
            # Get tasks for this project
            task_cursor = db.execute(
                "SELECT * FROM tasks WHERE project = ?", (project_name,)
            )
            task_rows = task_cursor.fetchall()
            task_columns = [desc[0] for desc in task_cursor.description]
            tasks = [dict(zip(task_columns, t)) for t in task_rows]
            total_tasks += len(tasks)
            
            # Get links for this project
            links = db_get_note_links(db, project_id=project_name)
            link_dicts = [
                {
                    "integration_type": link.integration_type,
                    "external_id": link.external_id,
                    "title": link.title,
                    "description": link.description,
                    "created_at": link.created_at,
                    "last_synced": link.last_synced,
                }
                for link in links
            ]
            total_links += len(link_dicts)
            
            # Get ledger events for this project
            events = db_list_project_events(db, project_id=project_name, limit=1000)
            total_ledger += len(events)
            
            projects_data.append(
                ProjectExportData(
                    name=project_dict["name"],
                    description=project_dict.get("description", ""),
                    status=project_dict.get("status", "active"),
                    priority=project_dict.get("priority", "MEDIUM"),
                    order_num=project_dict.get("order_num", 0),
                    tasks=tasks,
                    links=link_dicts,
                    ledger_events=events,
                )
            )
        
        return ExportResponse(
            version="1.0",
            exported_at=datetime.now(timezone.utc).isoformat(),
            environment="local",
            projects=projects_data,
            total_projects=len(projects_data),
            total_tasks=total_tasks,
            total_links=total_links,
            total_ledger_events=total_ledger,
        )


@router.post("/import/bulk", response_model=ImportResult)
async def import_projects_bulk(request: ImportRequest):
    """Import multiple projects with their associated data."""
    errors: List[str] = []
    projects_imported = 0
    projects_skipped = 0
    projects_updated = 0
    tasks_imported = 0
    links_imported = 0
    
    with db_session() as db:
        for project_data in request.projects:
            try:
                project_name = project_data.get("name", "").strip()
                if not project_name:
                    errors.append("Skipped project with empty name")
                    continue
                
                # Check if project exists
                existing = _project_exists(db, project_name)
                
                if existing and not request.overwrite_existing:
                    projects_skipped += 1
                    continue
                
                # Upsert project
                db_project = DBProject(
                    name=project_name,
                    description=project_data.get("description", ""),
                    status=project_data.get("status", "active"),
                    priority=project_data.get("priority", "MEDIUM"),
                    order_num=project_data.get("order_num", 0),
                )
                db_upsert_project(db, db_project)
                
                if existing:
                    projects_updated += 1
                else:
                    projects_imported += 1
                
                # Import tasks if requested
                if request.import_tasks and "tasks" in project_data:
                    for task_data in project_data.get("tasks", []):
                        try:
                            # Insert task (always create new to avoid ID conflicts)
                            db.execute(
                                """
                                INSERT INTO tasks (title, project, status, priority, due_date, 
                                    notes, owner, created_at, depends_on, recurrence_pattern,
                                    recurrence_end, time_estimated, time_logged, template_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    task_data.get("title", "Imported Task"),
                                    project_name,
                                    task_data.get("status", "TODO"),
                                    task_data.get("priority", "MEDIUM"),
                                    task_data.get("due_date"),
                                    task_data.get("notes", ""),
                                    task_data.get("owner", "Chris"),
                                    task_data.get("created_at", datetime.now().isoformat()),
                                    task_data.get("depends_on"),
                                    task_data.get("recurrence_pattern"),
                                    task_data.get("recurrence_end"),
                                    task_data.get("time_estimated"),
                                    task_data.get("time_logged"),
                                    task_data.get("template_id"),
                                ),
                            )
                            tasks_imported += 1
                        except Exception as task_err:
                            errors.append(f"Task import error in {project_name}: {str(task_err)}")
                
                # Import links if requested
                if request.import_links and "links" in project_data:
                    for link_data in project_data.get("links", []):
                        try:
                            db.execute(
                                """
                                INSERT INTO note_links (project_id, integration_type, external_id, 
                                    title, description, created_at, last_synced)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    project_name,
                                    link_data.get("integration_type", "local_document"),
                                    link_data.get("external_id", ""),
                                    link_data.get("title", ""),
                                    link_data.get("description", ""),
                                    link_data.get("created_at", datetime.now().isoformat()),
                                    link_data.get("last_synced"),
                                ),
                            )
                            links_imported += 1
                        except Exception as link_err:
                            errors.append(f"Link import error in {project_name}: {str(link_err)}")
                
                # Record import event in ledger
                db_record_project_event(
                    db,
                    project_id=project_name,
                    event_type="project_imported",
                    entity_type="project",
                    entity_id=project_name,
                    payload={
                        "source": "bulk_import",
                        "tasks_imported": len(project_data.get("tasks", [])),
                        "links_imported": len(project_data.get("links", [])),
                    },
                )
                
            except Exception as project_err:
                errors.append(f"Project {project_data.get('name', 'unknown')} import error: {str(project_err)}")
        
        db.commit()
    
    return ImportResult(
        success=len(errors) == 0,
        projects_imported=projects_imported,
        projects_skipped=projects_skipped,
        projects_updated=projects_updated,
        tasks_imported=tasks_imported,
        links_imported=links_imported,
        errors=errors,
    )
