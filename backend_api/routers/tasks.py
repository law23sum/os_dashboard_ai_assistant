"""Tasks API router."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from datetime import datetime
from assistant_hub_gui.assistant_hub.db import (
    db_delete_task,
    Task,
    STATUS_OPTIONS,
    PRIORITY_OPTIONS,
    db_record_project_event,
)
from backend_api.db import db_session


def db_insert_task(
    conn,
    title: str,
    project: str = "General",
    status: str = "TODO",
    priority: str = "MEDIUM",
    due_date: str = "",
    notes: str = "",
    owner: str = "Chris",
    depends_on: Optional[int] = None,
    recurrence_pattern: Optional[str] = None,
    recurrence_end: Optional[str] = None,
    time_estimated: Optional[int] = None,
    time_logged: Optional[int] = None,
    template_id: Optional[str] = None,
) -> int:
    """Insert a new task and return its ID."""
    c = conn.cursor()
    created_at = datetime.now().isoformat(timespec="seconds")
    c.execute(
        """
        INSERT INTO tasks
        (title, project, status, priority, due_date, notes, owner, created_at,
         depends_on, recurrence_pattern, recurrence_end, time_estimated, time_logged, template_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, project, status, priority, due_date, notes, owner, created_at,
         depends_on, recurrence_pattern, recurrence_end, time_estimated, time_logged, template_id),
    )
    conn.commit()
    return c.lastrowid


def db_update_task(
    conn,
    task_id: int,
    title: Optional[str] = None,
    project: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    notes: Optional[str] = None,
    owner: Optional[str] = None,
    depends_on: Optional[int] = None,
    recurrence_pattern: Optional[str] = None,
    recurrence_end: Optional[str] = None,
    time_estimated: Optional[int] = None,
    time_logged: Optional[int] = None,
    template_id: Optional[str] = None,
) -> None:
    """Update an existing task with only the provided fields."""
    c = conn.cursor()
    
    # Build dynamic UPDATE query based on provided fields
    updates = []
    params = []
    
    field_mapping = {
        'title': title,
        'project': project,
        'status': status,
        'priority': priority,
        'due_date': due_date,
        'notes': notes,
        'owner': owner,
        'depends_on': depends_on,
        'recurrence_pattern': recurrence_pattern,
        'recurrence_end': recurrence_end,
        'time_estimated': time_estimated,
        'time_logged': time_logged,
        'template_id': template_id,
    }
    
    for field, value in field_mapping.items():
        if value is not None:
            updates.append(f"{field} = ?")
            params.append(value)
    
    if not updates:
        return
    
    params.append(task_id)
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    c.execute(query, params)
    conn.commit()

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
):
    """List all tasks with optional filtering."""
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if project:
        query += " AND project = ?"
        params.append(project)
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY created_at DESC"

    with db_session() as db:
        cursor = db.execute(query, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

    tasks = []
    for row in rows:
        task_dict = dict(zip(columns, row))
        tasks.append(TaskResponse(**task_dict))

    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int):
    """Get a single task by ID."""
    with db_session() as db:
        cursor = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")

        columns = [description[0] for description in cursor.description]
        task_dict = dict(zip(columns, row))
    return TaskResponse(**task_dict)

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate):
    """Create a new task."""
    if task.status not in STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {STATUS_OPTIONS}")
    if task.priority not in PRIORITY_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Must be one of {PRIORITY_OPTIONS}")
    
    with db_session() as db:
        task_id = db_insert_task(
            db,
            title=task.title,
            project=task.project,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date or "",
            notes=task.notes,
            owner=task.owner,
            depends_on=task.depends_on,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_end=task.recurrence_end,
            time_estimated=task.time_estimated,
            time_logged=task.time_logged,
            template_id=task.template_id,
        )

        cursor = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
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
        )
    return TaskResponse(**task_dict)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task."""
    update_dict = task_update.model_dump(exclude_unset=True)
    if update_dict.get("status") and update_dict["status"] not in STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {STATUS_OPTIONS}")
    if update_dict.get("priority") and update_dict["priority"] not in PRIORITY_OPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid priority. Must be one of {PRIORITY_OPTIONS}")

    with db_session() as db:
        cursor = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")

        db_update_task(
            db,
            task_id=task_id,
            **update_dict
        )

        cursor = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
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
        )
    return TaskResponse(**task_dict)

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int):
    """Delete a task."""
    with db_session() as db:
        cursor = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        columns = [description[0] for description in cursor.description]
        task_dict = dict(zip(columns, row))

        db_delete_task(db, task_id)
        db_record_project_event(
            db,
            project_id=task_dict.get("project") or "General",
            event_type="task_deleted",
            entity_type="task",
            entity_id=str(task_id),
            payload=_task_event_payload(task_dict),
        )
    return None
