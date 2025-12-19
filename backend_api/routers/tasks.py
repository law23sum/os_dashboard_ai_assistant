"""Tasks API router."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import (
    db_insert_task,
    db_update_task,
    db_delete_task,
    Task,
    STATUS_OPTIONS,
    PRIORITY_OPTIONS,
    db_record_project_event,
)
from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.security import AuthUser

router = APIRouter()


def _task_event_payload(task_dict: dict) -> dict:
    """Return a trimmed payload for ledger events."""
    return {
        "title": task_dict.get("title"),
        "status": task_dict.get("status"),
        "priority": task_dict.get("priority"),
        "owner": task_dict.get("owner"),
        "due_date": task_dict.get("due_date"),
    }

class TaskCreate(BaseModel):
    title: str
    project: str = "General"
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: Optional[str] = None
    notes: str = ""
    owner: str = "Chris"
    depends_on: Optional[int] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end: Optional[str] = None
    time_estimated: Optional[int] = None
    time_logged: Optional[int] = None
    template_id: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    project: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None
    owner: Optional[str] = None
    depends_on: Optional[int] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end: Optional[str] = None
    time_estimated: Optional[int] = None
    time_logged: Optional[int] = None
    template_id: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    project: str
    status: str
    priority: str
    due_date: Optional[str]
    notes: str
    owner: str
    created_at: str
    depends_on: Optional[int]
    recurrence_pattern: Optional[str]
    recurrence_end: Optional[str]
    time_estimated: Optional[int]
    time_logged: Optional[int]
    template_id: Optional[str]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    project: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    owner: Optional[str] = None,
    user: AuthUser = Depends(get_current_user),
):
    """List all tasks with optional filtering."""
    try:
        query = "SELECT * FROM tasks WHERE 1=1 AND user_id = ?"
        params = [user.id]

        # Non-admins can only see their own tasks (Django-like per-user isolation).
        is_admin = getattr(user, 'is_admin', False)
        effective_owner = owner if is_admin else user.id
        if effective_owner:
            query += " AND owner = ?"
            params.append(effective_owner)

        if project:
            query += " AND project = ?"
            params.append(project)
        if status:
            # Validate status to prevent invalid queries
            if status not in STATUS_OPTIONS:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {STATUS_OPTIONS}")
            query += " AND status = ?"
            params.append(status)
        if priority:
            # Validate priority to prevent invalid queries
            if priority not in PRIORITY_OPTIONS:
                raise HTTPException(status_code=400, detail=f"Invalid priority. Must be one of {PRIORITY_OPTIONS}")
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_at DESC"

        with db_session() as db:
            cursor = db.execute(query, params)
            rows = cursor.fetchall()
            # Handle case where query returns no rows (cursor.description might not exist)
            if cursor.description:
                columns = [description[0] for description in cursor.description]
            else:
                columns = []

        tasks = []
        for row in rows:
            task_dict = dict(zip(columns, row))
            tasks.append(TaskResponse(**task_dict))

        return tasks
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, user: AuthUser = Depends(get_current_user)):
    """Get a single task by ID."""
    try:
        with db_session() as db:
            cursor = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user.id))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Task not found")

            columns = [description[0] for description in cursor.description]
            task_dict = dict(zip(columns, row))
        return TaskResponse(**task_dict)
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error fetching task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch task: {str(e)}")

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, user: AuthUser = Depends(get_current_user)):
    """Create a new task."""
    if task.status not in STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {STATUS_OPTIONS}")
    if task.priority not in PRIORITY_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Must be one of {PRIORITY_OPTIONS}")
    
    is_admin = getattr(user, 'is_admin', False)
    effective_owner = task.owner if (is_admin and task.owner) else user.id

    with db_session() as db:
        db_task = Task(
            id=0,  # Will be assigned by database
            title=task.title,
            project=task.project,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date or "",
            notes=task.notes,
            owner=effective_owner,
            depends_on=task.depends_on,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_end=task.recurrence_end,
            time_estimated=task.time_estimated,
            time_logged=task.time_logged,
            template_id=task.template_id,
            user_id=user.id,
        )
        task_id = db_insert_task(db, db_task)

        cursor = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user.id))
        row = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        task_dict = dict(zip(columns, row))
        db_record_project_event(
            db,
            project_id=task_dict.get("project") or "General",
            event_type="task_created",
            entity_type="task",
            entity_id=str(task_id),
            payload=_task_event_payload(task_dict),
            user_id=user.id,
        )
    return TaskResponse(**task_dict)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, user: AuthUser = Depends(get_current_user)):
    """Update an existing task."""
    update_dict = task_update.model_dump(exclude_unset=True)
    is_admin = getattr(user, 'is_admin', False)
    if not is_admin:
        # Prevent non-admins from reassigning tasks.
        update_dict.pop("owner", None)
    if update_dict.get("status") and update_dict["status"] not in STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {STATUS_OPTIONS}")
    if update_dict.get("priority") and update_dict["priority"] not in PRIORITY_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Must be one of {PRIORITY_OPTIONS}")

    with db_session() as db:
        cursor = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user.id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Create Task object with merged values
        db_task = Task(
            id=task_id,
            title=update_dict.get("title", existing.get("title", "")),
            project=update_dict.get("project", existing.get("project", "General")),
            status=update_dict.get("status", existing.get("status", "TODO")),
            priority=update_dict.get("priority", existing.get("priority", "MEDIUM")),
            due_date=update_dict.get("due_date", existing.get("due_date", "")),
            notes=update_dict.get("notes", existing.get("notes", "")),
            owner=update_dict.get("owner", existing.get("owner", user.id)),
            created_at=existing.get("created_at", ""),
            depends_on=update_dict.get("depends_on", existing.get("depends_on")),
            recurrence_pattern=update_dict.get("recurrence_pattern", existing.get("recurrence_pattern")),
            recurrence_end=update_dict.get("recurrence_end", existing.get("recurrence_end")),
            time_estimated=update_dict.get("time_estimated", existing.get("time_estimated")),
            time_logged=update_dict.get("time_logged", existing.get("time_logged")),
            template_id=update_dict.get("template_id", existing.get("template_id")),
            user_id=user.id,
        )
        
        db_update_task(db, db_task)

        cursor = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user.id))
        row = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        task_dict = dict(zip(columns, row))
        db_record_project_event(
            db,
            project_id=task_dict.get("project") or "General",
            event_type="task_updated",
            entity_type="task",
            entity_id=str(task_id),
            payload=_task_event_payload(task_dict),
            user_id=user.id,
        )
    return TaskResponse(**task_dict)

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, user: AuthUser = Depends(get_current_user)):
    """Delete a task."""
    is_admin = getattr(user, 'is_admin', False)
    with db_session() as db:
        cursor = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, user.id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        columns = [description[0] for description in cursor.description]
        task_dict = dict(zip(columns, row))
        if not is_admin and (task_dict.get("user_id") or "") != user.id:
            raise HTTPException(status_code=404, detail="Task not found")

        db_delete_task(db, task_id)
        db_record_project_event(
            db,
            project_id=task_dict.get("project") or "General",
            event_type="task_deleted",
            entity_type="task",
            entity_id=str(task_id),
            payload=_task_event_payload(task_dict),
            user_id=user.id,
        )
    return None
