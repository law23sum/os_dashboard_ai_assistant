"""Project Management System (PMS) API router."""

from __future__ import annotations

import base64
import io
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub import pms_scheduler  # noqa: E402
from assistant_hub_gui.assistant_hub import pms_invariants  # noqa: E402
from assistant_hub_gui.assistant_hub import pms_store  # noqa: E402
from assistant_hub_gui.assistant_hub.config import get_attachment_path  # noqa: E402
from assistant_hub_gui.assistant_hub.db import db_list_project_events  # noqa: E402
from backend_api.db import db_session  # noqa: E402
from backend_api.deps import get_current_user  # noqa: E402
from backend_api.security import AuthUser  # noqa: E402

router = APIRouter()


def _resolve_scope(user: AuthUser, mode: str, scope_id: Optional[str]) -> Dict[str, str]:
    if mode == "enterprise":
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="Enterprise scope requires admin access")
        return {"mode": mode, "scope_type": "tenant", "scope_id": scope_id or "enterprise-default"}
    return {"mode": "personal", "scope_type": "user", "scope_id": user.id}


def _ensure_project_access(
    conn,
    project_id: str,
    user: AuthUser,
    scope_id: Optional[str] = None,
) -> Dict[str, Any]:
    project = pms_store.get_project(conn, project_id)
    if project["mode"] == "personal":
        if project["scope_id"] != user.id and not user.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized for this project")
    if project["mode"] == "enterprise" and not user.is_admin:
        raise HTTPException(status_code=403, detail="Enterprise access requires admin")
    if scope_id and project["scope_id"] != scope_id and project["mode"] == "enterprise":
        raise HTTPException(status_code=403, detail="Enterprise scope mismatch")
    return project


class ProjectCreate(BaseModel):
    name: str
    mode: str = "personal"
    status: str = "active"
    scope_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    budget_amount: Optional[float] = None
    budget_currency: Optional[str] = None
    template_pack: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    budget_amount: Optional[float] = None
    budget_currency: Optional[str] = None


class EpicCreate(BaseModel):
    title: str
    description: str = ""
    acceptance_criteria: str = ""
    status: str = "active"


class EpicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    status: Optional[str] = None


class TaskCreate(BaseModel):
    title: str
    deliverable_spec: str = ""
    acceptance_criteria: str = ""
    priority: str = "P1"
    category: str = "General"
    task_type: str = Field("General", alias="type")
    status: str = "TODO"
    epic_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    deliverable_spec: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[str] = None
    epic_id: Optional[str] = None


class TodoCreate(BaseModel):
    text: str
    after_todo_id: Optional[str] = None
    position: Optional[int] = None


class TodoReorder(BaseModel):
    todo_ids: List[str]


class RunStart(BaseModel):
    project_id: str
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    todo_id: Optional[str] = None
    input_params: Dict[str, Any] = Field(default_factory=dict)


class RunComplete(BaseModel):
    status: str
    summary: Optional[str] = None


class ArtifactAttach(BaseModel):
    kind: str
    filename: Optional[str] = None
    display_name: Optional[str] = None
    mime_type: Optional[str] = None
    content_base64: Optional[str] = None


class DocumentCreate(BaseModel):
    project_id: str
    title: str
    kind: str
    visibility: str
    epic_id: Optional[str] = None
    task_id: Optional[str] = None


class DocumentRevisionCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentPublish(BaseModel):
    revision_hash: str


class MeetingCreate(BaseModel):
    title: str
    started_at: str
    ended_at: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    epic_id: Optional[str] = None
    task_id: Optional[str] = None


class TranscriptIngest(BaseModel):
    segments: List[Dict[str, Any]]


class SpeakerMappingUpdate(BaseModel):
    speaker_label: str
    display_name: str
    consent: bool = False


class ExpenseCreate(BaseModel):
    amount: float
    currency: str
    category: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    occurred_at: str
    epic_id: Optional[str] = None
    task_id: Optional[str] = None


class TimeEntryCreate(BaseModel):
    duration_minutes: int
    hourly_rate: float
    occurred_at: str
    actor_id: Optional[str] = None
    role: Optional[str] = None
    epic_id: Optional[str] = None
    task_id: Optional[str] = None


@router.get("/template-packs")
async def list_template_packs() -> List[Dict[str, Any]]:
    return pms_store.list_template_packs()


@router.get("/projects")
async def list_projects(
    mode: str = "personal",
    scope_id: Optional[str] = None,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    scope = _resolve_scope(user, mode, scope_id) if mode != "all" else {}
    with db_session() as db:
        return pms_store.list_projects(
            db,
            mode=None if mode == "all" else scope.get("mode"),
            scope_type=None if mode == "all" else scope.get("scope_type"),
            scope_id=None if mode == "all" else scope.get("scope_id"),
        )


@router.post("/projects", status_code=201)
async def create_project(
    payload: ProjectCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    scope = _resolve_scope(user, payload.mode, payload.scope_id)
    with db_session() as db:
        return pms_store.create_project(
            db,
            name=payload.name,
            mode=scope["mode"],
            scope_type=scope["scope_type"],
            scope_id=scope["scope_id"],
            status=payload.status,
            config=payload.config,
            budget_amount=payload.budget_amount,
            budget_currency=payload.budget_currency,
            template_pack=payload.template_pack,
            created_by=user.id,
        )


@router.get("/projects/{project_id}")
async def get_project(project_id: str, user: AuthUser = Depends(get_current_user)) -> Dict[str, Any]:
    with db_session() as db:
        return _ensure_project_access(db, project_id, user)


@router.put("/projects/{project_id}")
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.update_project(
            db,
            project_id=project_id,
            patch=payload.model_dump(exclude_unset=True),
            user_id=user.id,
        )


@router.get("/projects/{project_id}/epics")
async def list_epics(project_id: str, user: AuthUser = Depends(get_current_user)) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.list_epics(db, project_id)


@router.post("/projects/{project_id}/epics", status_code=201)
async def create_epic(
    project_id: str,
    payload: EpicCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.create_epic(
            db,
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            acceptance_criteria=payload.acceptance_criteria,
            status=payload.status,
            user_id=user.id,
        )


@router.put("/projects/{project_id}/epics/{epic_id}")
async def update_epic(
    project_id: str,
    epic_id: str,
    payload: EpicUpdate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.update_epic(
            db,
            project_id=project_id,
            epic_id=epic_id,
            patch=payload.model_dump(exclude_unset=True),
            user_id=user.id,
        )


@router.get("/projects/{project_id}/tasks")
async def list_tasks(
    project_id: str,
    epic_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    task_type: Optional[str] = None,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.list_tasks(
            db,
            project_id=project_id,
            epic_id=epic_id,
            status=status,
            priority=priority,
            category=category,
            task_type=task_type,
        )


@router.post("/projects/{project_id}/tasks", status_code=201)
async def add_task(
    project_id: str,
    payload: TaskCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.add_task(
            db,
            project_id=project_id,
            epic_id=payload.epic_id,
            title=payload.title,
            deliverable_spec=payload.deliverable_spec,
            acceptance_criteria=payload.acceptance_criteria,
            priority=payload.priority,
            category=payload.category,
            task_type=payload.task_type,
            status=payload.status,
            user_id=user.id,
        )


@router.get("/projects/{project_id}/tasks/{task_id}")
async def get_task(
    project_id: str,
    task_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.get_task(db, task_id)


@router.put("/projects/{project_id}/tasks/{task_id}")
async def update_task(
    project_id: str,
    task_id: str,
    payload: TaskUpdate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.update_task_metadata(
            db,
            project_id=project_id,
            task_id=task_id,
            patch=payload.model_dump(exclude_unset=True),
            user_id=user.id,
        )


@router.delete("/projects/{project_id}/tasks/{task_id}")
async def archive_task(
    project_id: str,
    task_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.archive_task(db, project_id=project_id, task_id=task_id, user_id=user.id)


@router.get("/tasks/{task_id}/todos")
async def list_todos(task_id: str, user: AuthUser = Depends(get_current_user)) -> List[Dict[str, Any]]:
    with db_session() as db:
        task = pms_store.get_task(db, task_id)
        _ensure_project_access(db, task["project_id"], user)
        return pms_store.list_todos(db, task_id)


@router.post("/tasks/{task_id}/todos", status_code=201)
async def add_todo(
    task_id: str,
    payload: TodoCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        task = pms_store.get_task(db, task_id)
        _ensure_project_access(db, task["project_id"], user)
        if payload.after_todo_id or payload.position:
            return pms_store.insert_todo(
                db,
                task_id=task_id,
                text=payload.text,
                after_todo_id=payload.after_todo_id,
                position=payload.position,
                user_id=user.id,
            )
        return pms_store.add_todo(db, task_id=task_id, text=payload.text, user_id=user.id)


@router.post("/tasks/{task_id}/todos/reorder")
async def reorder_todos(
    task_id: str,
    payload: TodoReorder,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        task = pms_store.get_task(db, task_id)
        _ensure_project_access(db, task["project_id"], user)
        return pms_store.reorder_todos(db, task_id=task_id, new_order=payload.todo_ids, user_id=user.id)


@router.post("/todos/{todo_id}/complete")
async def complete_todo(
    todo_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        todo = pms_store.get_todo(db, todo_id)
        task = pms_store.get_task(db, todo["task_id"])
        _ensure_project_access(db, task["project_id"], user)
        return pms_store.complete_todo(db, todo_id=todo_id, user_id=user.id)


@router.get("/projects/{project_id}/scheduler/next")
async def next_task(
    project_id: str,
    dequeue: bool = False,
    user: AuthUser = Depends(get_current_user),
) -> Optional[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        tasks = pms_store.list_tasks(db, project_id=project_id)
        task = pms_scheduler.next_task(tasks)
        if task and dequeue:
            return pms_store.update_task_metadata(
                db,
                project_id=project_id,
                task_id=task["task_id"],
                patch={"enqueue_time": datetime.utcnow().isoformat(timespec="seconds") + "Z"},
                user_id=user.id,
            )
        return task


@router.get("/projects/{project_id}/scheduler/peek")
async def peek_next_tasks(
    project_id: str,
    count: int = Query(5, ge=1, le=50),
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        tasks = pms_store.list_tasks(db, project_id=project_id)
        return pms_scheduler.peek_next_tasks(tasks, count)


@router.get("/projects/{project_id}/scheduler/index")
async def scheduler_index(project_id: str, user: AuthUser = Depends(get_current_user)) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        tasks = pms_store.list_tasks(db, project_id=project_id)
        index = pms_scheduler.build_scheduler_index(tasks)
        tiers = []
        for tier in index["tiers"]:
            lanes = []
            for lane_key, task_ids in index["lanes"].get(tier, {}).items():
                category, task_type = lane_key.split("::", 1)
                lane_tasks = [index["tasks_by_id"][task_id] for task_id in task_ids]
                lanes.append(
                    {
                        "lane_key": lane_key,
                        "category": category,
                        "task_type": task_type,
                        "count": len(task_ids),
                        "tasks": lane_tasks,
                    }
                )
            tiers.append({"tier": tier, "lanes": lanes})
        return {"tiers": tiers}


@router.post("/projects/{project_id}/scheduler/validate")
async def validate_invariants(
    project_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        tasks = pms_store.list_tasks(db, project_id=project_id)
        epics = pms_store.list_epics(db, project_id)
        todos = []
        for task in tasks:
            todos.extend(pms_store.list_todos(db, task["task_id"]))
        errors = pms_invariants.validate_pms_invariants(tasks=tasks, epics=epics, todos=todos)
        return {"ok": not errors, "errors": errors}


@router.post("/runs", status_code=201)
async def start_run(payload: RunStart, user: AuthUser = Depends(get_current_user)) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, payload.project_id, user)
        return pms_store.start_run(
            db,
            project_id=payload.project_id,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            todo_id=payload.todo_id,
            input_params=payload.input_params,
            status="running",
            user_id=user.id,
        )


@router.post("/runs/{run_id}/complete")
async def complete_run(
    run_id: str,
    payload: RunComplete,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        run = pms_store.get_run(db, run_id)
        _ensure_project_access(db, run["project_id"], user)
        return pms_store.complete_run(
            db,
            run_id=run_id,
            project_id=run["project_id"],
            status=payload.status,
            summary=payload.summary,
            user_id=user.id,
        )


@router.post("/runs/{run_id}/artifacts", status_code=201)
async def attach_artifact(
    run_id: str,
    payload: ArtifactAttach,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        run = pms_store.get_run(db, run_id)
        _ensure_project_access(db, run["project_id"], user)
        content = base64.b64decode(payload.content_base64) if payload.content_base64 else None
        return pms_store.attach_artifact(
            db,
            project_id=run["project_id"],
            run_id=run_id,
            kind=payload.kind,
            content=content,
            filename=payload.filename,
            display_name=payload.display_name,
            mime_type=payload.mime_type,
            user_id=user.id,
        )


@router.post("/runs/{run_id}/artifacts/upload", status_code=201)
async def upload_artifact_file(
    run_id: str,
    kind: str = Query(...),
    file: UploadFile = File(...),
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        run = pms_store.get_run(db, run_id)
        _ensure_project_access(db, run["project_id"], user)
        content = await file.read()
        return pms_store.attach_artifact(
            db,
            project_id=run["project_id"],
            run_id=run_id,
            kind=kind,
            content=content,
            filename=file.filename,
            mime_type=file.content_type,
            user_id=user.id,
        )


@router.get("/runs")
async def list_runs(
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    limit: Optional[int] = Query(None, ge=1, le=100),
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        if project_id:
            _ensure_project_access(db, project_id, user)
        return pms_store.list_runs(db, project_id=project_id, task_id=task_id, limit=limit)


@router.get("/artifacts")
async def list_artifacts(
    project_id: Optional[str] = None,
    run_id: Optional[str] = None,
    task_id: Optional[str] = None,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        if project_id:
            _ensure_project_access(db, project_id, user)
        if run_id:
            run = pms_store.get_run(db, run_id)
            _ensure_project_access(db, run["project_id"], user)
        return pms_store.list_artifacts(db, project_id=project_id, run_id=run_id, task_id=task_id)


@router.get("/artifacts/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        artifact = pms_store.get_artifact(db, artifact_id)
        _ensure_project_access(db, artifact["project_id"], user)
        return artifact


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(
    artifact_id: str,
    user: AuthUser = Depends(get_current_user),
) -> FileResponse:
    with db_session() as db:
        artifact = pms_store.get_artifact(db, artifact_id)
        _ensure_project_access(db, artifact["project_id"], user)
    path = Path(artifact.get("storage_path") or "")
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact file not found")
    return FileResponse(path)


@router.post("/documents", status_code=201)
async def create_document(
    payload: DocumentCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, payload.project_id, user)
        return pms_store.create_document(
            db,
            project_id=payload.project_id,
            title=payload.title,
            kind=payload.kind,
            visibility=payload.visibility,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            user_id=user.id,
        )


@router.post("/documents/{document_id}/revisions", status_code=201)
async def add_document_revision(
    document_id: str,
    payload: DocumentRevisionCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        doc = pms_store.get_document(db, document_id, view="latest")
        _ensure_project_access(db, doc["project_id"], user)
        revision_hash = pms_store.add_document_revision(
            db,
            document_id=document_id,
            content=payload.content,
            author=user.id,
            metadata=payload.metadata,
        )
        return {"revision_hash": revision_hash}


@router.post("/documents/{document_id}/publish")
async def publish_document_revision(
    document_id: str,
    payload: DocumentPublish,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        doc = pms_store.get_document(db, document_id, view="latest")
        _ensure_project_access(db, doc["project_id"], user)
        return pms_store.publish_document_revision(
            db,
            document_id=document_id,
            revision_hash=payload.revision_hash,
            user_id=user.id,
        )


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    view: str = Query("published", pattern="^(published|latest|history)$"),
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        doc = pms_store.get_document(db, document_id, view=view)
        _ensure_project_access(db, doc["project_id"], user)
        return doc


@router.get("/projects/{project_id}/documents")
async def list_documents(
    project_id: str,
    kind: Optional[str] = None,
    published_only: bool = False,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.list_documents(db, project_id=project_id, kind=kind, published_only=published_only)


@router.post("/projects/{project_id}/meetings", status_code=201)
async def create_meeting(
    project_id: str,
    payload: MeetingCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.create_meeting_session(
            db,
            project_id=project_id,
            title=payload.title,
            started_at=payload.started_at,
            ended_at=payload.ended_at,
            participants=payload.participants,
            language=payload.language,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            user_id=user.id,
        )


@router.get("/projects/{project_id}/meetings")
async def list_meetings(
    project_id: str,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.list_meetings(db, project_id)


@router.post("/meetings/{meeting_id}/audio", status_code=201)
async def upload_meeting_audio(
    meeting_id: str,
    file: UploadFile = File(...),
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        meeting = pms_store.get_meeting(db, meeting_id)
        _ensure_project_access(db, meeting["project_id"], user)
        content = await file.read()
        return pms_store.attach_meeting_audio(
            db,
            meeting_id=meeting_id,
            project_id=meeting["project_id"],
            content=content,
            filename=file.filename or f"{meeting_id}.audio",
            user_id=user.id,
        )


@router.post("/meetings/{meeting_id}/transcript")
async def ingest_transcript(
    meeting_id: str,
    payload: TranscriptIngest,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        meeting = pms_store.get_meeting(db, meeting_id)
        _ensure_project_access(db, meeting["project_id"], user)
        return pms_store.add_transcript_segments(
            db,
            meeting_id=meeting_id,
            segments=payload.segments,
            user_id=user.id,
        )


@router.post("/meetings/{meeting_id}/journal")
async def generate_journal(
    meeting_id: str,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        meeting = pms_store.get_meeting(db, meeting_id)
        _ensure_project_access(db, meeting["project_id"], user)
        return pms_store.generate_meeting_journal(db, meeting_id=meeting_id, user_id=user.id)


@router.get("/meetings/{meeting_id}/transcript")
async def list_transcript(
    meeting_id: str,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        meeting = pms_store.get_meeting(db, meeting_id)
        _ensure_project_access(db, meeting["project_id"], user)
        return pms_store.list_transcript_segments(db, meeting_id)


@router.get("/meetings/{meeting_id}/journal")
async def list_journal(
    meeting_id: str,
    section_type: Optional[str] = None,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        meeting = pms_store.get_meeting(db, meeting_id)
        _ensure_project_access(db, meeting["project_id"], user)
        return pms_store.list_journal_blocks(db, meeting_id, section_type=section_type)


@router.put("/meetings/{meeting_id}/speaker-mapping")
async def update_speaker_mapping(
    meeting_id: str,
    payload: SpeakerMappingUpdate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Consent required to map speakers")
    with db_session() as db:
        meeting = pms_store.get_meeting(db, meeting_id)
        _ensure_project_access(db, meeting["project_id"], user)
        return pms_store.upsert_speaker_mapping(
            db,
            meeting_id=meeting_id,
            speaker_label=payload.speaker_label,
            display_name=payload.display_name,
            consent=payload.consent,
            user_id=user.id,
        )


@router.get("/meetings/{meeting_id}/export")
async def export_meeting_packet(
    meeting_id: str,
    user: AuthUser = Depends(get_current_user),
) -> FileResponse:
    with db_session() as db:
        meeting = pms_store.get_meeting(db, meeting_id)
        _ensure_project_access(db, meeting["project_id"], user)
        transcript = pms_store.list_transcript_segments(db, meeting_id)
        journal = pms_store.list_journal_blocks(db, meeting_id)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("meeting.json", json.dumps(meeting, indent=2))
        zf.writestr("transcript.json", json.dumps(transcript, indent=2))
        zf.writestr("journal.json", json.dumps(journal, indent=2))
    buffer.seek(0)
    export_path = get_attachment_path("pms", "meeting_exports", f"{meeting_id}.zip")
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_bytes(buffer.read())
    return FileResponse(export_path, filename=f"{meeting_id}-packet.zip")


@router.post("/projects/{project_id}/expenses", status_code=201)
async def add_expense(
    project_id: str,
    payload: ExpenseCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.add_expense(
            db,
            project_id=project_id,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            amount=payload.amount,
            currency=payload.currency,
            category=payload.category,
            vendor=payload.vendor,
            description=payload.description,
            occurred_at=payload.occurred_at,
            user_id=user.id,
        )


@router.get("/projects/{project_id}/expenses")
async def list_expenses(
    project_id: str,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.list_expenses(db, project_id)


@router.post("/projects/{project_id}/time-entries", status_code=201)
async def add_time_entry(
    project_id: str,
    payload: TimeEntryCreate,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.add_time_entry(
            db,
            project_id=project_id,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            actor_id=payload.actor_id,
            role=payload.role,
            duration_minutes=payload.duration_minutes,
            hourly_rate=payload.hourly_rate,
            occurred_at=payload.occurred_at,
            user_id=user.id,
        )


@router.get("/projects/{project_id}/time-entries")
async def list_time_entries(
    project_id: str,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.list_time_entries(db, project_id)


@router.get("/projects/{project_id}/cost-rollup")
async def cost_rollup(
    project_id: str,
    include_breakdown: bool = False,
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return pms_store.project_cost_rollup(db, project_id, include_breakdown=include_breakdown)


@router.get("/projects/{project_id}/audit-events")
async def list_audit_events(
    project_id: str,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        return db_list_project_events(db, project_id=project_id)


@router.get("/projects/{project_id}/evidence-pack")
async def export_project_evidence_pack(
    project_id: str,
    user: AuthUser = Depends(get_current_user),
) -> FileResponse:
    with db_session() as db:
        _ensure_project_access(db, project_id, user)
        events = db_list_project_events(db, project_id=project_id)
        docs = pms_store.list_documents(db, project_id=project_id)
        meetings = pms_store.list_meetings(db, project_id)
        runs = pms_store.list_runs(db, project_id=project_id)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("audit_events.json", json.dumps(events, indent=2))
        zf.writestr("documents.json", json.dumps(docs, indent=2))
        zf.writestr("meetings.json", json.dumps(meetings, indent=2))
        zf.writestr("runs.json", json.dumps(runs, indent=2))
    buffer.seek(0)
    export_path = get_attachment_path("pms", "evidence_packs", f"{project_id}.zip")
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_bytes(buffer.read())
    return FileResponse(export_path, filename=f"{project_id}-evidence-pack.zip")


@router.get("/search")
async def search(
    q: str = Query(..., min_length=2),
    mode: str = "personal",
    scope_id: Optional[str] = None,
    user: AuthUser = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    scope = _resolve_scope(user, mode, scope_id) if mode != "all" else {}
    with db_session() as db:
        return pms_store.search_pms(
            db,
            scope_type=None if mode == "all" else scope.get("scope_type"),
            scope_id=None if mode == "all" else scope.get("scope_id"),
            query=q,
        )
