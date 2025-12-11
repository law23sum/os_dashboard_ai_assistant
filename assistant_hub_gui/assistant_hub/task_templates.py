"""Task template management."""

import sqlite3
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from .db import Task, db_insert_task


@dataclass
class TaskTemplate:
    """A template for creating tasks."""

    id: str
    name: str
    title: str
    project: str = "General"
    priority: str = "MEDIUM"
    notes: str = ""
    time_estimated: Optional[int] = None
    created_at: str = ""


def save_template(conn: sqlite3.Connection, template: TaskTemplate):
    """Save a task template to the database."""
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO task_templates (id, name, title, project, priority, notes, time_estimated, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            title = excluded.title,
            project = excluded.project,
            priority = excluded.priority,
            notes = excluded.notes,
            time_estimated = excluded.time_estimated
        """,
        (
            template.id,
            template.name,
            template.title,
            template.project,
            template.priority,
            template.notes,
            template.time_estimated,
            template.created_at,
        ),
    )
    conn.commit()


def load_templates(conn: sqlite3.Connection) -> List[TaskTemplate]:
    """Load all task templates."""
    c = conn.cursor()
    c.execute("SELECT * FROM task_templates ORDER BY name")
    rows = c.fetchall()

    templates = []
    for r in rows:
        templates.append(
            TaskTemplate(
                id=r["id"],
                name=r["name"],
                title=r["title"],
                project=r.get("project") or "General",
                priority=r.get("priority") or "MEDIUM",
                notes=r.get("notes") or "",
                time_estimated=r.get("time_estimated"),
                created_at=r.get("created_at") or "",
            )
        )

    return templates


def delete_template(conn: sqlite3.Connection, template_id: str):
    """Delete a task template."""
    c = conn.cursor()
    c.execute("DELETE FROM task_templates WHERE id = ?", (template_id,))
    conn.commit()


def create_task_from_template(
    conn: sqlite3.Connection,
    template: TaskTemplate,
    owner: str = "Chris",
    due_date: Optional[str] = None,
) -> Task:
    """Create a task from a template."""
    task = Task(
        id=0,
        title=template.title,
        project=template.project,
        status="TODO",
        priority=template.priority,
        due_date=due_date or "",
        notes=template.notes,
        owner=owner,
        created_at=datetime.now().isoformat(timespec="seconds"),
        depends_on=None,
        recurrence_pattern=None,
        recurrence_end=None,
        time_estimated=template.time_estimated,
        time_logged=None,
        template_id=template.id,
    )
    task.id = db_insert_task(conn, task)
    return task
