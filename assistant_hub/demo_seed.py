"""Seed helper to ensure demo data exists for the shared FastAPI + React UI."""

from __future__ import annotations

from datetime import datetime
from sqlite3 import Connection
from typing import Iterable

from .db import db_insert_task, db_upsert_project, Project, Task


def _table_empty(conn: Connection, table: str) -> bool:
    cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    return count == 0


def _seed_projects(conn: Connection) -> None:
    projects = [
        ("AI Research Workspace", "Research backlog and experiments", "active", "HIGH"),
        ("Automation Platform", "Workflow + integration automation", "active", "HIGH"),
        ("Client Readiness", "Docs + security reviews", "in_progress", "MEDIUM"),
    ]
    for name, desc, status, priority in projects:
        db_upsert_project(
            conn,
            Project(
                name=name,
                description=desc,
                status=status,
                priority=priority,
            ),
        )


def _seed_tasks(conn: Connection) -> None:
    sample_tasks: Iterable[dict] = [
        {
            "title": "Wire up FastAPI backend to React",
            "project": "AI Research Workspace",
            "priority": "HIGH",
            "status": "IN_PROGRESS",
            "notes": "Ensure all Tkinter data endpoints are exposed via /api.",
            "owner": "AIC",
        },
        {
            "title": "Migrate Tkinter Tools tab to React",
            "project": "Automation Platform",
            "priority": "HIGH",
            "status": "IN_PROGRESS",
            "notes": "Shared command catalog + terminal with spec-sheet commands.",
            "owner": "Aria",
        },
        {
            "title": "Prep desktop/web release artifacts",
            "project": "Client Readiness",
            "priority": "MEDIUM",
            "status": "TODO",
            "notes": "Electron installers for macOS/Windows/Linux, plus static web build.",
            "owner": "Chris",
        },
        {
            "title": "Add AI Ops dashboard cards",
            "project": "AI Research Workspace",
            "priority": "MEDIUM",
            "status": "TODO",
            "notes": "Mirror Tkinter AI Ops widgets with glass UI theme.",
            "owner": "Sora",
        },
    ]
    for task in sample_tasks:
        db_insert_task(
            conn,
            Task(
                id=0,
                title=task["title"],
                project=task["project"],
                status=task["status"],
                priority=task["priority"],
                notes=task["notes"],
                owner=task["owner"],
                created_at=datetime.now().isoformat(timespec="seconds"),
            ),
        )


def ensure_demo_data(conn: Connection) -> None:
    """Populate the SQLite store with sample projects/tasks if it is empty."""

    if _table_empty(conn, "projects"):
        _seed_projects(conn)
    if _table_empty(conn, "tasks"):
        _seed_tasks(conn)
    conn.commit()
