"""Export and import functionality for tasks and projects."""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import sqlite3

from .db import Task, Project, load_state, db_insert_task, db_upsert_project, init_db


def export_tasks_to_csv(
    conn: sqlite3.Connection, file_path: str, project_filter: str = None
):
    """Export tasks to CSV file."""
    state = load_state(conn)
    tasks = state.tasks

    if project_filter:
        tasks = [t for t in tasks if t.project == project_filter]

    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(
            [
                "ID",
                "Title",
                "Project",
                "Owner",
                "Status",
                "Priority",
                "Due Date",
                "Time Estimated (min)",
                "Time Logged (min)",
                "Depends On",
                "Recurrence Pattern",
                "Recurrence End",
                "Notes",
                "Created At",
            ]
        )

        # Data rows
        for task in tasks:
            writer.writerow(
                [
                    task.id,
                    task.title,
                    task.project,
                    task.owner,
                    task.status,
                    task.priority,
                    task.due_date or "",
                    task.time_estimated or "",
                    task.time_logged or "",
                    task.depends_on or "",
                    task.recurrence_pattern or "",
                    task.recurrence_end or "",
                    task.notes or "",
                    task.created_at,
                ]
            )


def export_tasks_to_json(
    conn: sqlite3.Connection, file_path: str, project_filter: str = None
):
    """Export tasks to JSON file."""
    state = load_state(conn)
    tasks = state.tasks

    if project_filter:
        tasks = [t for t in tasks if t.project == project_filter]

    tasks_data = []
    for task in tasks:
        tasks_data.append(
            {
                "id": task.id,
                "title": task.title,
                "project": task.project,
                "owner": task.owner,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date or None,
                "time_estimated": task.time_estimated,
                "time_logged": task.time_logged,
                "depends_on": task.depends_on,
                "recurrence_pattern": task.recurrence_pattern,
                "recurrence_end": task.recurrence_end,
                "notes": task.notes or "",
                "created_at": task.created_at,
            }
        )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            {"export_date": datetime.now().isoformat(), "tasks": tasks_data},
            f,
            indent=2,
            ensure_ascii=False,
        )


def export_projects_to_json(conn: sqlite3.Connection, file_path: str):
    """Export projects to JSON file."""
    state = load_state(conn)

    projects_data = []
    for project in state.projects:
        projects_data.append(
            {
                "name": project.name,
                "description": project.description or "",
                "status": project.status,
                "priority": project.priority,
            }
        )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            {"export_date": datetime.now().isoformat(), "projects": projects_data},
            f,
            indent=2,
            ensure_ascii=False,
        )


def import_tasks_from_csv(
    conn: sqlite3.Connection, file_path: str, project_override: str = None
) -> int:
    """Import tasks from CSV file. Returns number of tasks imported."""
    imported = 0

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                task = Task(
                    id=0,
                    title=row.get("Title", "").strip(),
                    project=project_override or row.get("Project", "General").strip(),
                    owner=row.get("Owner", "Chris").strip(),
                    status=row.get("Status", "TODO").strip().upper(),
                    priority=row.get("Priority", "MEDIUM").strip().upper(),
                    due_date=row.get("Due Date", "").strip() or None,
                    notes=row.get("Notes", "").strip(),
                    created_at=row.get(
                        "Created At", datetime.now().isoformat(timespec="seconds")
                    ),
                    time_estimated=int(row["Time Estimated (min)"])
                    if row.get("Time Estimated (min)")
                    else None,
                    time_logged=int(row["Time Logged (min)"])
                    if row.get("Time Logged (min)")
                    else None,
                    depends_on=int(row["Depends On"])
                    if row.get("Depends On")
                    else None,
                    recurrence_pattern=row.get("Recurrence Pattern", "").strip()
                    or None,
                    recurrence_end=row.get("Recurrence End", "").strip() or None,
                    template_id=None,
                )

                if task.title:
                    db_insert_task(conn, task)
                    imported += 1
            except Exception as e:
                continue

    return imported


def import_tasks_from_json(
    conn: sqlite3.Connection, file_path: str, project_override: str = None
) -> int:
    """Import tasks from JSON file. Returns number of tasks imported."""
    imported = 0

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        tasks_data = data.get("tasks", [])

        for task_data in tasks_data:
            try:
                task = Task(
                    id=0,
                    title=task_data.get("title", "").strip(),
                    project=project_override
                    or task_data.get("project", "General").strip(),
                    owner=task_data.get("owner", "Chris").strip(),
                    status=task_data.get("status", "TODO").strip().upper(),
                    priority=task_data.get("priority", "MEDIUM").strip().upper(),
                    due_date=task_data.get("due_date") or None,
                    notes=task_data.get("notes", "").strip(),
                    created_at=task_data.get(
                        "created_at", datetime.now().isoformat(timespec="seconds")
                    ),
                    time_estimated=task_data.get("time_estimated"),
                    time_logged=task_data.get("time_logged"),
                    depends_on=task_data.get("depends_on"),
                    recurrence_pattern=task_data.get("recurrence_pattern"),
                    recurrence_end=task_data.get("recurrence_end"),
                    template_id=None,
                )

                if task.title:
                    db_insert_task(conn, task)
                    imported += 1
            except Exception as e:
                continue

    return imported


def export_full_backup(conn: sqlite3.Connection, file_path: str):
    """Export full database backup as JSON."""
    state = load_state(conn)

    backup_data = {
        "export_date": datetime.now().isoformat(),
        "version": "1.0",
        "tasks": [],
        "projects": [],
    }

    for task in state.tasks:
        backup_data["tasks"].append(
            {
                "id": task.id,
                "title": task.title,
                "project": task.project,
                "owner": task.owner,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date or None,
                "time_estimated": task.time_estimated,
                "time_logged": task.time_logged,
                "depends_on": task.depends_on,
                "recurrence_pattern": task.recurrence_pattern,
                "recurrence_end": task.recurrence_end,
                "notes": task.notes or "",
                "created_at": task.created_at,
            }
        )

    for project in state.projects:
        backup_data["projects"].append(
            {
                "name": project.name,
                "description": project.description or "",
                "status": project.status,
                "priority": project.priority,
            }
        )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
