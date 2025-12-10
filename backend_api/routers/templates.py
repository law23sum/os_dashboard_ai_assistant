"""Templates API router shared by desktop + web clients."""
from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from assistant_hub.task_templates import (
    TaskTemplate,
    create_task_from_template,
    delete_template as delete_task_template,
    load_templates as load_task_templates,
    save_template as save_task_template,
)
from assistant_hub.templates_workspace import TemplatesWorkspace
from backend_api.db import db_session

router = APIRouter()


def _serialize_task_template(template: TaskTemplate) -> Dict[str, Any]:
    return {
        "id": template.id,
        "name": template.name,
        "title": template.title,
        "project": template.project,
        "priority": template.priority,
        "notes": template.notes,
        "time_estimated": template.time_estimated,
        "created_at": template.created_at,
    }


class TaskTemplatePayload(BaseModel):
    name: str
    title: str
    project: str = "General"
    priority: str = "MEDIUM"
    notes: str = ""
    time_estimated: Optional[int] = None


class TaskTemplateUpdatePayload(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    project: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    time_estimated: Optional[int] = None


class CreateTaskFromTemplatePayload(BaseModel):
    template_id: str
    owner: str = "Chris"
    due_date: Optional[str] = None


@router.get("/")
async def list_task_templates() -> Dict[str, List[Dict[str, Any]]]:
    """Return all task templates stored in SQLite."""
    with db_session() as conn:
        templates = load_task_templates(conn)
    return {"templates": [_serialize_task_template(template) for template in templates]}


@router.post("/")
async def create_task_template(payload: TaskTemplatePayload) -> Dict[str, Dict[str, Any]]:
    """Create a new task template."""
    template = TaskTemplate(
        id=str(uuid.uuid4()),
        name=payload.name.strip(),
        title=payload.title.strip(),
        project=payload.project or "General",
        priority=payload.priority or "MEDIUM",
        notes=payload.notes or "",
        time_estimated=payload.time_estimated,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )
    with db_session() as conn:
        save_task_template(conn, template)
    return {"template": _serialize_task_template(template)}


@router.put("/{template_id}")
async def update_task_template(
    template_id: str, payload: TaskTemplateUpdatePayload
) -> Dict[str, Dict[str, Any]]:
    """Update an existing task template."""
    updates = payload.model_dump(exclude_unset=True)
    with db_session() as conn:
        templates = {template.id: template for template in load_task_templates(conn)}
        if template_id not in templates:
            raise HTTPException(status_code=404, detail="Template not found")

        template = templates[template_id]
        for key, value in updates.items():
            if value is not None:
                setattr(template, key, value)
        template.created_at = template.created_at or datetime.now().isoformat(timespec="seconds")
        save_task_template(conn, template)
    return {"template": _serialize_task_template(template)}


@router.delete("/{template_id}")
async def delete_task_template(template_id: str) -> Dict[str, str]:
    """Delete a task template by ID."""
    with db_session() as conn:
        templates = {template.id: template for template in load_task_templates(conn)}
        if template_id not in templates:
            raise HTTPException(status_code=404, detail="Template not found")
        delete_task_template(conn, template_id)
    return {"status": "deleted"}


@router.post("/create-task")
async def create_task_from_template_endpoint(
    payload: CreateTaskFromTemplatePayload,
) -> Dict[str, Any]:
    """Instantiate a real task from a template."""
    with db_session() as conn:
        templates = {template.id: template for template in load_task_templates(conn)}
        template = templates.get(payload.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        task = create_task_from_template(
            conn, template, owner=payload.owner, due_date=payload.due_date
        )
    return {"task": task.__dict__}


@router.get("/documents")
async def document_template_catalog() -> Dict[str, Any]:
    """Expose the governed document template catalog + placeholder matrix."""
    workspace = TemplatesWorkspace()
    return workspace.snapshot()
