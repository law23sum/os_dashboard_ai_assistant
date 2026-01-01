"""Project Management System (PMS) API router."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.security import AuthUser
from assistant_hub_gui.assistant_hub import pms_store, pms_scheduler, pms_invariants
from assistant_hub_gui.assistant_hub.db import db_list_project_events
from assistant_hub_gui.assistant_hub.pms_models import (
    PMS_DEFAULT_PRIORITY_TIERS,
    PMS_DOCUMENT_KINDS,
    PMS_DOCUMENT_VISIBILITY,
)

router = APIRouter()


@dataclass
class ScopeContext:
    mode: str
    scope_type: str
    scope_id: str
    user: AuthUser


def resolve_scope(
    scope: str = Query("personal"),
    workspace_id: Optional[str] = Query(None),
    user: AuthUser = Depends(get_current_user),
) -> ScopeContext:
    if scope not in {"personal", "enterprise"}:
        raise HTTPException(status_code=400, detail="Invalid scope")
    if scope == "enterprise":
        scope_type = "tenant"
        scope_id = workspace_id or user.environment or "default"
    else:
        scope_type = "user"
        scope_id = user.id
    return ScopeContext(mode=scope, scope_type=scope_type, scope_id=scope_id, user=user)


def _require_project(
    conn,
    project_id: str,
    scope: ScopeContext,
) -> Dict[str, Any]:
    project = pms_store.pms_get_project(conn, project_id, scope.scope_type, scope.scope_id)
    if project and project.get("is_sample") and not scope.user.is_admin:
        project = None
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _list_projects_for_scope(conn, scope: ScopeContext) -> List[Dict[str, Any]]:
    return pms_store.list_projects(
        conn,
        mode=scope.mode,
        scope_type=scope.scope_type,
        scope_id=scope.scope_id,
        include_samples=bool(scope.user.is_admin),
    )


def _ensure_default_project(conn, scope: ScopeContext) -> Dict[str, Any]:
    projects = _list_projects_for_scope(conn, scope)
    if projects:
        return projects[0]
    return pms_store.create_project(
        conn,
        name="Default Workspace",
        mode=scope.mode,
        scope_type=scope.scope_type,
        scope_id=scope.scope_id,
        status="active",
        config={"priority_tiers": list(PMS_DEFAULT_PRIORITY_TIERS)},
        created_by=scope.user.id,
    )


class ProjectCreate(BaseModel):
    name: str
    status: str = "active"
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
    status: str = "PLANNED"


class EpicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    status: Optional[str] = None


class TaskCreate(BaseModel):
    title: str
    epic_id: Optional[str] = None
    deliverable_spec: str = ""
    acceptance_criteria: str = ""
    priority: str = "P1"
    category: str = "General"
    task_type: str = "General"
    status: str = "TODO"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    epic_id: Optional[str] = None
    deliverable_spec: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[str] = None


class TodoCreate(BaseModel):
    text: str


class TodoInsert(BaseModel):
    text: str
    after_todo_id: Optional[str] = None
    position: Optional[int] = Field(None, alias="index")

    class Config:
        allow_population_by_field_name = True


class TodoReorder(BaseModel):
    todo_ids: List[str]


class NextTaskRequest(BaseModel):
    mutate: bool = True


class RunStart(BaseModel):
    project_id: str
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    todo_id: Optional[str] = None
    input_params: Dict[str, Any] = Field(default_factory=dict)
    status: str = "running"


class RunComplete(BaseModel):
    status: str = "succeeded"
    summary: Optional[str] = None


class ArtifactCreate(BaseModel):
    project_id: str
    run_id: Optional[str] = None
    kind: str = "file"
    filename: Optional[str] = None
    display_name: Optional[str] = None
    mime_type: Optional[str] = None
    content_base64: Optional[str] = None


class DocumentCreate(BaseModel):
    project_id: Optional[str] = None
    title: str
    kind: str = "notes"
    visibility: str = "private"
    epic_id: Optional[str] = None
    task_id: Optional[str] = None


class DocumentRevisionCreate(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentPublish(BaseModel):
    revision_hash: str


class MeetingCreate(BaseModel):
    project_id: Optional[str] = None
    title: str
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    language: str = "en"


class TranscriptRequest(BaseModel):
    segments: List[Dict[str, Any]] = Field(default_factory=list)


class MeetingAudioUpload(BaseModel):
    filename: str
    content_base64: str
    mime_type: Optional[str] = None
    recording_consent: bool = False


class SpeakerMappingUpdate(BaseModel):
    mapping: Dict[str, str]
    consent: bool = False


class ExpenseCreate(BaseModel):
    project_id: str
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    amount: float
    currency: str = "USD"
    category: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    occurred_at: Optional[str] = None


class TimeEntryCreate(BaseModel):
    project_id: str
    epic_id: Optional[str] = None
    task_id: Optional[str] = None
    actor_id: Optional[str] = None
    role: Optional[str] = None
    duration_minutes: int
    hourly_rate: float
    occurred_at: Optional[str] = None


@router.get("/projects")
async def list_projects(scope: ScopeContext = Depends(resolve_scope)) -> List[Dict[str, Any]]:
    with db_session() as conn:
        return _list_projects_for_scope(conn, scope)


@router.post("/projects")
async def create_project(
    payload: ProjectCreate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        project = pms_store.create_project(
            conn,
            name=payload.name,
            mode=scope.mode,
            scope_type=scope.scope_type,
            scope_id=scope.scope_id,
            status=payload.status,
            config=payload.config,
            budget_amount=payload.budget_amount,
            budget_currency=payload.budget_currency,
            template_pack=payload.template_pack,
            created_by=scope.user.id,
        )
        return project


@router.get("/projects/{project_id}")
async def get_project(project_id: str, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        return _require_project(conn, project_id, scope)


@router.put("/projects/{project_id}")
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        project = pms_store.update_project(
            conn,
            project_id=project_id,
            patch=payload.model_dump(exclude_unset=True),
            user_id=scope.user.id,
        )
        return project


@router.get("/projects/{project_id}/epics")
async def list_epics(project_id: str, scope: ScopeContext = Depends(resolve_scope)) -> List[Dict[str, Any]]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        return pms_store.list_epics(conn, project_id)


@router.post("/projects/{project_id}/epics")
async def create_epic(
    project_id: str,
    payload: EpicCreate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        epic = pms_store.create_epic(
            conn,
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            acceptance_criteria=payload.acceptance_criteria,
            status=payload.status,
            user_id=scope.user.id,
        )
        return epic


@router.put("/projects/{project_id}/epics/{epic_id}")
async def update_epic(
    project_id: str,
    epic_id: str,
    payload: EpicUpdate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        before = pms_store.pms_get_epic(conn, epic_id)
        if not before:
            raise HTTPException(status_code=404, detail="Epic not found")
        epic = pms_store.update_epic(
            conn,
            project_id=project_id,
            epic_id=epic_id,
            patch=payload.model_dump(exclude_unset=True),
            user_id=scope.user.id,
        )
        return epic


@router.post("/projects/{project_id}/epics/{epic_id}/archive")
async def archive_epic(
    project_id: str,
    epic_id: str,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        try:
            return pms_store.archive_epic(
                conn,
                project_id=project_id,
                epic_id=epic_id,
                user_id=scope.user.id,
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Epic not found")


@router.get("/projects/{project_id}/tasks")
async def list_tasks(
    project_id: str,
    scope: ScopeContext = Depends(resolve_scope),
    epic_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        return pms_store.list_tasks(
            conn,
            project_id=project_id,
            epic_id=epic_id,
            status=status,
            priority=priority,
            category=category,
            task_type=task_type,
        )


@router.post("/projects/{project_id}/tasks")
async def create_task(
    project_id: str,
    payload: TaskCreate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        task = pms_store.add_task(
            conn,
            project_id=project_id,
            epic_id=payload.epic_id,
            title=payload.title,
            deliverable_spec=payload.deliverable_spec,
            acceptance_criteria=payload.acceptance_criteria,
            priority=payload.priority,
            category=payload.category,
            task_type=payload.task_type,
            status=payload.status,
            user_id=scope.user.id,
        )
        return task


@router.get("/projects/{project_id}/tasks/{task_id}")
async def get_task(
    project_id: str,
    task_id: str,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        task = pms_store.pms_get_task(conn, task_id)
        if not task or task.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


@router.put("/projects/{project_id}/tasks/{task_id}")
async def update_task(
    project_id: str,
    task_id: str,
    payload: TaskUpdate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        before = pms_store.pms_get_task(conn, task_id)
        if not before or before.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return pms_store.update_task_metadata(
            conn,
            project_id=project_id,
            task_id=task_id,
            patch=payload.model_dump(exclude_unset=True),
            user_id=scope.user.id,
        )


@router.post("/projects/{project_id}/tasks/{task_id}/archive")
async def archive_task(
    project_id: str,
    task_id: str,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        try:
            task = pms_store.archive_task(
                conn,
                project_id=project_id,
                task_id=task_id,
                user_id=scope.user.id,
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


@router.get("/projects/{project_id}/tasks/{task_id}/todos")
async def list_todos(project_id: str, task_id: str, scope: ScopeContext = Depends(resolve_scope)) -> List[Dict[str, Any]]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        task = pms_store.pms_get_task(conn, task_id)
        if not task or task.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return pms_store.list_todos(conn, task_id)


@router.post("/projects/{project_id}/tasks/{task_id}/todos")
async def add_todo(
    project_id: str,
    task_id: str,
    payload: TodoCreate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        task = pms_store.pms_get_task(conn, task_id)
        if not task or task.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return pms_store.add_todo(conn, task_id=task_id, text=payload.text, user_id=scope.user.id)


@router.post("/projects/{project_id}/tasks/{task_id}/todos/insert")
async def insert_todo(
    project_id: str,
    task_id: str,
    payload: TodoInsert,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        task = pms_store.pms_get_task(conn, task_id)
        if not task or task.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        todo = pms_store.insert_todo(
            conn,
            task_id=task_id,
            text=payload.text,
            after_todo_id=payload.after_todo_id,
            position=payload.position,
            user_id=scope.user.id,
        )
        return todo


@router.post("/projects/{project_id}/tasks/{task_id}/todos/reorder")
async def reorder_todos(
    project_id: str,
    task_id: str,
    payload: TodoReorder,
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        task = pms_store.pms_get_task(conn, task_id)
        if not task or task.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        return pms_store.reorder_todos(conn, task_id=task_id, new_order=payload.todo_ids, user_id=scope.user.id)


@router.post("/projects/{project_id}/tasks/{task_id}/todos/{todo_id}/complete")
async def complete_todo(
    project_id: str,
    task_id: str,
    todo_id: str,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        task = pms_store.pms_get_task(conn, task_id)
        if not task or task.get("project_id") != project_id:
            raise HTTPException(status_code=404, detail="Task not found")
        todo = pms_store.get_todo(conn, todo_id)
        if todo.get("task_id") != task_id:
            raise HTTPException(status_code=404, detail="Todo not found")
        return pms_store.complete_todo(conn, todo_id=todo_id, user_id=scope.user.id)


@router.post("/projects/{project_id}/schedule/next")
async def next_task(
    project_id: str,
    payload: NextTaskRequest,
    scope: ScopeContext = Depends(resolve_scope),
) -> Optional[Dict[str, Any]]:
    with db_session() as conn:
        project = _require_project(conn, project_id, scope)
        config = project.get("config") or {}
        tiers = config.get("priority_tiers") or list(PMS_DEFAULT_PRIORITY_TIERS)
        tasks = pms_store.list_tasks(conn, project_id=project_id)
        next_task = pms_scheduler.next_task(tasks, tiers)
        if not next_task:
            return None
        if payload.mutate:
            pms_store.update_task_metadata(
                conn,
                project_id=project_id,
                task_id=next_task["task_id"],
                patch={"enqueue_time": pms_store._now()},
                user_id=scope.user.id,
            )
        return pms_store.get_task(conn, next_task["task_id"])


@router.get("/projects/{project_id}/schedule/peek")
async def peek_tasks(
    project_id: str,
    count: int = Query(5, ge=1, le=20),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        project = _require_project(conn, project_id, scope)
        config = project.get("config") or {}
        tiers = config.get("priority_tiers") or list(PMS_DEFAULT_PRIORITY_TIERS)
        tasks = pms_store.list_tasks(conn, project_id=project_id)
        return pms_scheduler.peek_next_tasks(tasks, count, tiers)


@router.get("/projects/{project_id}/schedule/index")
async def schedule_index(
    project_id: str,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        project = _require_project(conn, project_id, scope)
        config = project.get("config") or {}
        tiers = config.get("priority_tiers") or list(PMS_DEFAULT_PRIORITY_TIERS)
        tasks = pms_store.list_tasks(conn, project_id=project_id)
        index = pms_scheduler.build_scheduler_index_from_tasks(tasks, tiers)
        return {
            "project_id": project_id,
            "tiers": [
                {
                    "tier": tier.tier,
                    "lanes": [
                        {"lane_key": lane.lane_key, "task_ids": lane.task_ids}
                        for lane in tier.lanes
                    ],
                }
                for tier in index.tiers
            ],
        }


@router.post("/projects/{project_id}/schedule/validate")
async def validate_invariants(project_id: str, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        project = _require_project(conn, project_id, scope)
        epics = pms_store.list_epics(conn, project_id)
        tasks = pms_store.list_tasks(conn, project_id=project_id)
        todos = []
        for task in tasks:
            todos.extend(task.get("todos") or [])
        config = project.get("config") or {}
        tiers = config.get("priority_tiers") if config else None
        errors = pms_invariants.validate_pms_invariants(epics, tasks, todos, tiers)
        return {"valid": not errors, "errors": errors}


@router.post("/runs")
async def start_run(payload: RunStart, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, payload.project_id, scope)
        run = pms_store.start_run(
            conn,
            project_id=payload.project_id,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            todo_id=payload.todo_id,
            input_params=payload.input_params,
            status=payload.status,
            user_id=scope.user.id,
        )
        return run


@router.post("/runs/{run_id}/complete")
async def complete_run(run_id: str, payload: RunComplete, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        run = pms_store.get_run(conn, run_id)
        project_id = run.get("project_id") if run else None
        if not project_id:
            raise HTTPException(status_code=404, detail="Run not found")
        _require_project(conn, project_id, scope)
        run = pms_store.complete_run(
            conn,
            run_id=run_id,
            project_id=project_id,
            status=payload.status,
            summary=payload.summary,
            user_id=scope.user.id,
        )
        return run


@router.post("/runs/{run_id}/artifacts")
async def attach_artifact(run_id: str, payload: ArtifactCreate, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        run = pms_store.get_run(conn, run_id)
        if run and run.get("project_id") != payload.project_id:
            raise HTTPException(status_code=400, detail="Project mismatch for run")
        project_id = run.get("project_id") if run else payload.project_id
        _require_project(conn, project_id, scope)
        content = None
        if payload.content_base64:
            try:
                content = base64.b64decode(payload.content_base64, validate=True)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Invalid base64 content") from exc
        artifact = pms_store.attach_artifact(
            conn,
            project_id=project_id,
            run_id=run_id,
            kind=payload.kind,
            content=content,
            filename=payload.filename,
            display_name=payload.display_name,
            mime_type=payload.mime_type,
            user_id=scope.user.id,
        )
        return artifact


@router.get("/runs")
async def list_runs(
    project_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if task_id and not project_id:
            task = pms_store.pms_get_task(conn, task_id)
            if not task:
                return []
            project_id = task.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
            return pms_store.list_runs(conn, project_id=project_id, task_id=task_id, limit=limit)

        projects = _list_projects_for_scope(conn, scope)
        runs: List[Dict[str, Any]] = []
        for project in projects:
            runs.extend(pms_store.list_runs(conn, project_id=project["project_id"], task_id=task_id, limit=limit))
        return runs


@router.get("/artifacts")
async def list_artifacts(
    project_id: Optional[str] = Query(None),
    run_id: Optional[str] = Query(None),
    task_id: Optional[str] = Query(None),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if run_id and not project_id:
            run = pms_store.get_run(conn, run_id)
            if not run:
                return []
            project_id = run.get("project_id")
        if task_id and not project_id:
            task = pms_store.pms_get_task(conn, task_id)
            if not task:
                return []
            project_id = task.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
            return pms_store.list_artifacts(conn, project_id=project_id, run_id=run_id, task_id=task_id)

        projects = _list_projects_for_scope(conn, scope)
        artifacts: List[Dict[str, Any]] = []
        for project in projects:
            artifacts.extend(
                pms_store.list_artifacts(
                    conn,
                    project_id=project["project_id"],
                    run_id=run_id,
                    task_id=task_id,
                )
            )
        return artifacts


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(artifact_id: str, scope: ScopeContext = Depends(resolve_scope)):
    with db_session() as conn:
        artifact = pms_store.get_artifact(conn, artifact_id)
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        project_id = artifact.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        path = artifact.get("storage_path")
        if not path:
            raise HTTPException(status_code=404, detail="Artifact has no stored file")
        return FileResponse(path, filename=artifact.get("filename") or "artifact")


@router.post("/documents")
async def create_document(payload: DocumentCreate, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    if payload.kind not in PMS_DOCUMENT_KINDS:
        raise HTTPException(status_code=400, detail="Invalid document kind")
    if payload.visibility not in PMS_DOCUMENT_VISIBILITY:
        raise HTTPException(status_code=400, detail="Invalid visibility")
    with db_session() as conn:
        _require_project(conn, payload.project_id, scope)
        document = pms_store.create_document(
            conn,
            project_id=payload.project_id,
            title=payload.title,
            kind=payload.kind,
            visibility=payload.visibility,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            user_id=scope.user.id,
        )
        return document


@router.post("/documents/{document_id}/revisions")
async def add_revision(
    document_id: str,
    payload: DocumentRevisionCreate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        existing = pms_store.get_document(conn, document_id, view="latest")
        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")
        project_id = existing.get("document", {}).get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        revision = pms_store.add_document_revision(
            conn,
            document_id=document_id,
            content=payload.content,
            metadata=payload.metadata,
            user_id=scope.user.id,
        )
        return revision


@router.post("/documents/{document_id}/publish")
async def publish_revision(
    document_id: str,
    payload: DocumentPublish,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        existing = pms_store.get_document(conn, document_id, view="latest")
        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")
        project_id = existing.get("document", {}).get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        doc = pms_store.publish_document_revision(
            conn, document_id=document_id, revision_hash=payload.revision_hash
        )
        return doc


@router.get("/documents")
async def list_documents(
    project_id: Optional[str] = Query(None),
    kind: Optional[str] = Query(None),
    published_only: bool = Query(False),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if project_id:
            _require_project(conn, project_id, scope)
            return pms_store.list_documents(conn, project_id, kind=kind, published_only=published_only)
        projects = _list_projects_for_scope(conn, scope)
        docs: List[Dict[str, Any]] = []
        for project in projects:
            docs.extend(
                pms_store.list_documents(conn, project["project_id"], kind=kind, published_only=published_only)
            )
        return docs


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    view: str = Query("published"),
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        if view not in {"published", "latest", "history"}:
            raise HTTPException(status_code=400, detail="Invalid document view")
        doc = pms_store.get_document(conn, document_id, view=view)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        project_id = doc.get("document", {}).get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        if view == "history":
            return {"document": doc.get("document"), "history": doc.get("revisions", [])}
        revision_hash = doc.get("revision_hash")
        revision_meta = None
        if revision_hash:
            history = pms_store.get_document(conn, document_id, view="history")
            revisions = history.get("revisions", []) if history else []
            revision = next(
                (item for item in revisions if item.get("revision_hash") == revision_hash),
                None,
            )
            revision_meta = {
                "revision_hash": revision_hash,
                "document_id": document_id,
                "created_at": (revision or {}).get("created_at") or doc.get("document", {}).get("updated_at"),
                "content": doc.get("content"),
            }
        return {"document": doc.get("document"), "revision": revision_meta}


@router.post("/meetings")
async def create_meeting(payload: MeetingCreate, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, payload.project_id, scope)
        meeting = pms_store.create_meeting(
            conn,
            project_id=payload.project_id,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            title=payload.title,
            started_at=payload.started_at,
            ended_at=payload.ended_at,
            participants=payload.participants,
            language=payload.language,
            user_id=scope.user.id,
        )
        return meeting


@router.get("/meetings")
async def list_meetings(
    project_id: Optional[str] = Query(None),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if project_id:
            _require_project(conn, project_id, scope)
            return pms_store.list_meetings(conn, project_id)
        projects = _list_projects_for_scope(conn, scope)
        meetings: List[Dict[str, Any]] = []
        for project in projects:
            meetings.extend(pms_store.list_meetings(conn, project["project_id"]))
        return meetings


@router.get("/meetings/{meeting_id}")
async def get_meeting(meeting_id: str, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        meeting = pms_store.pms_get_meeting(conn, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        project_id = meeting.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        return meeting


@router.post("/meetings/{meeting_id}/audio")
async def attach_meeting_audio(
    meeting_id: str,
    payload: MeetingAudioUpload,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    if not payload.recording_consent:
        raise HTTPException(status_code=400, detail="Recording consent required")
    with db_session() as conn:
        meeting = pms_store.pms_get_meeting(conn, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        project_id = meeting.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        try:
            content = base64.b64decode(payload.content_base64, validate=True)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid base64 content") from exc
        return pms_store.attach_meeting_audio(
            conn,
            meeting_id=meeting_id,
            project_id=project_id,
            content=content,
            filename=payload.filename,
            mime_type=payload.mime_type,
            user_id=scope.user.id,
        )


@router.post("/meetings/{meeting_id}/transcribe")
async def transcribe_and_generate_journal(
    meeting_id: str,
    payload: TranscriptRequest,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        meeting = pms_store.pms_get_meeting(conn, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        project_id = meeting.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        pms_store.add_transcript_segments(conn, meeting_id=meeting_id, segments=payload.segments, user_id=scope.user.id)
        journal = pms_store.generate_meeting_journal(conn, meeting_id=meeting_id, user_id=scope.user.id)
        return {"meeting_id": meeting_id, "journal_blocks": journal}


@router.get("/meetings/{meeting_id}/segments")
async def list_transcript_segments(meeting_id: str, scope: ScopeContext = Depends(resolve_scope)) -> List[Dict[str, Any]]:
    with db_session() as conn:
        meeting = pms_store.pms_get_meeting(conn, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        project_id = meeting.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        return pms_store.list_transcript_segments(conn, meeting_id)


@router.get("/meetings/{meeting_id}/journal")
async def list_journal_blocks(
    meeting_id: str,
    section_type: Optional[str] = Query(None),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        meeting = pms_store.pms_get_meeting(conn, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        project_id = meeting.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        return pms_store.list_journal_blocks(conn, meeting_id, section_type)


@router.post("/meetings/{meeting_id}/speaker-mapping")
async def update_speaker_mapping(
    meeting_id: str,
    payload: SpeakerMappingUpdate,
    scope: ScopeContext = Depends(resolve_scope),
) -> Dict[str, Any]:
    with db_session() as conn:
        meeting = pms_store.pms_get_meeting(conn, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        project_id = meeting.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        mapping = None
        try:
            for label, name in payload.mapping.items():
                mapping = pms_store.upsert_speaker_mapping(
                    conn,
                    meeting_id=meeting_id,
                    speaker_label=label,
                    display_name=name,
                    consent=payload.consent,
                    user_id=scope.user.id,
                )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return mapping or {}


@router.get("/meetings/{meeting_id}/packet")
async def export_meeting_packet(meeting_id: str, scope: ScopeContext = Depends(resolve_scope)) -> JSONResponse:
    with db_session() as conn:
        meeting = pms_store.pms_get_meeting(conn, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        project_id = meeting.get("project_id")
        if project_id:
            _require_project(conn, project_id, scope)
        segments = pms_store.list_transcript_segments(conn, meeting_id)
        blocks = pms_store.list_journal_blocks(conn, meeting_id)
        payload = {"meeting": meeting, "segments": segments, "journal_blocks": blocks}
        return JSONResponse(content=payload)


@router.post("/expenses")
async def add_expense(payload: ExpenseCreate, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, payload.project_id, scope)
        expense = pms_store.add_expense(
            conn,
            project_id=payload.project_id,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            amount=payload.amount,
            currency=payload.currency,
            category=payload.category,
            vendor=payload.vendor,
            description=payload.description,
            occurred_at=payload.occurred_at or pms_store._now(),
            user_id=scope.user.id,
        )
        return expense


@router.get("/expenses")
async def list_expenses(
    project_id: Optional[str] = Query(None),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if project_id:
            _require_project(conn, project_id, scope)
            return pms_store.list_expenses(conn, project_id)
        projects = _list_projects_for_scope(conn, scope)
        results: List[Dict[str, Any]] = []
        for project in projects:
            results.extend(pms_store.list_expenses(conn, project["project_id"]))
        return results


@router.post("/time-entries")
async def add_time_entry(payload: TimeEntryCreate, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, payload.project_id, scope)
        entry = pms_store.add_time_entry(
            conn,
            project_id=payload.project_id,
            epic_id=payload.epic_id,
            task_id=payload.task_id,
            actor_id=payload.actor_id,
            role=payload.role,
            duration_minutes=payload.duration_minutes,
            hourly_rate=payload.hourly_rate,
            occurred_at=payload.occurred_at or pms_store._now(),
            user_id=scope.user.id,
        )
        return entry


@router.get("/time-entries")
async def list_time_entries(
    project_id: Optional[str] = Query(None),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if project_id:
            _require_project(conn, project_id, scope)
            return pms_store.list_time_entries(conn, project_id)
        projects = _list_projects_for_scope(conn, scope)
        results: List[Dict[str, Any]] = []
        for project in projects:
            results.extend(pms_store.list_time_entries(conn, project["project_id"]))
        return results


@router.get("/projects/{project_id}/rollup")
async def project_rollup(project_id: str, scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        rollup = pms_store.project_cost_rollup(conn, project_id, include_breakdown=False)
        return {
            "project_id": project_id,
            "expense_total": rollup.get("expense_total"),
            "labor_total": rollup.get("labor_total"),
            "combined_total": rollup.get("combined_total"),
            "total": rollup.get("combined_total"),
            "currency": rollup.get("currency"),
        }


@router.get("/audit")
async def list_audit_events(
    project_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    scope: ScopeContext = Depends(resolve_scope),
) -> List[Dict[str, Any]]:
    with db_session() as conn:
        if project_id:
            _require_project(conn, project_id, scope)
            events = db_list_project_events(conn, project_id=project_id, limit=limit)
        else:
            projects = _list_projects_for_scope(conn, scope)
            events = []
            for project in projects:
                events.extend(
                    db_list_project_events(conn, project_id=project["project_id"], limit=limit)
                )
            events.sort(key=lambda event: event.get("created_at") or "", reverse=True)
            events = events[:limit]
        return [
            {
                "event_id": str(event.get("id")),
                "project_id": event.get("project_id"),
                "actor_id": event.get("user_id", ""),
                "entity_type": event.get("payload", {}).get("entity_type"),
                "entity_id": event.get("payload", {}).get("entity_id"),
                "action": event.get("event_type"),
                "timestamp": event.get("created_at"),
                "before": event.get("payload", {}).get("data", {}).get("before"),
                "after": event.get("payload", {}).get("data", {}).get("after"),
                "correlation_id": None,
            }
            for event in events
        ]


@router.get("/search")
async def search(q: str = Query(""), scope: ScopeContext = Depends(resolve_scope)) -> Dict[str, Any]:
    if not q:
        return {"results": []}
    with db_session() as conn:
        results = pms_store.search_pms(
            conn,
            scope_type=scope.scope_type,
            scope_id=scope.scope_id,
            query=q,
            include_samples=bool(scope.user.is_admin),
        )
        return {"results": results}


@router.get("/projects/{project_id}/evidence-pack")
async def export_evidence_pack(project_id: str, scope: ScopeContext = Depends(resolve_scope)) -> JSONResponse:
    if scope.mode == "enterprise" and not scope.user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    with db_session() as conn:
        _require_project(conn, project_id, scope)
        events = db_list_project_events(conn, project_id=project_id, limit=200)
        docs = pms_store.list_documents(conn, project_id, published_only=True)
        runs = pms_store.list_runs(conn, project_id=project_id, task_id=None, limit=50)
        payload = {
            "project_id": project_id,
            "audit_events": events,
            "documents": docs,
            "runs": runs,
        }
        return JSONResponse(content=payload)
