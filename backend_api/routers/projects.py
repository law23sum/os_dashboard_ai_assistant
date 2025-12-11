"""Projects API router."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import hashlib
import sys
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    hash_curr: str


class ProjectRiskInsight(BaseModel):
    risk_score: int
    severity: str
    risks: List[Dict[str, Any]]
    recommendations: str
    total_tasks: int
    completed_tasks: int
    completion_rate: float


class ProjectForecastInsight(BaseModel):
    predicted_date: Optional[str]
    confidence: str
    reasoning: str
    estimated_days: Optional[int]
    avg_completion_days: Optional[float] = None
    pending_task_count: int


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
            {"status": row["status"], "priority": row["priority"]}
        )
    return tasks_by_project


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
                id=event["id"],
                project_id=event["project_id"],
                event_type=event["event_type"],
                entity_type=event.get("entity_type"),
                entity_id=event.get("entity_id"),
                payload=event.get("payload") or {},
                created_at=event["created_at"],
                hash_prev=event.get("hash_prev"),
                hash_curr=event["hash_curr"],
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


@router.get("/{project_name}/intelligence", response_model=ProjectIntelligenceResponse)
async def get_project_intelligence(project_name: str):
    """Return intelligence metrics for a single project."""
    with db_session() as db:
        if not _project_exists(db, project_name):
            raise HTTPException(status_code=404, detail="Project not found")
        tasks_map = _group_tasks_by_project(db)
        return _compute_project_intelligence(db, project_name, tasks_map)


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    with db_session() as db:
        db_upsert_project(
            db,
            name=project.name,
            description=project.description,
            status=project.status,
            priority=project.priority,
            order_num=project.order_num,
        )

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

        update_dict = project_update.model_dump(exclude_unset=True)
        update_dict["name"] = project_name if "name" not in update_dict else update_dict["name"]

        db_upsert_project(db, **update_dict)

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
