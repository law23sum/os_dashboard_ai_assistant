"""Seed helper to ensure demo data exists for the shared FastAPI + React UI."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from sqlite3 import Connection
from typing import Dict, Iterable, List, Optional
import subprocess
import re

from .db import db_insert_task, db_upsert_project, get_meta, set_meta, Project, Task
from . import pms_store


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


def _parse_deliverables_pdf(pdf_path: Path) -> List[dict]:
    if not pdf_path.exists():
        return []
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []

    lines = [line.strip() for line in result.stdout.splitlines()]
    epics: List[dict] = []
    current: Optional[dict] = None
    section: Optional[str] = None
    for line in lines:
        if not line:
            continue
        if re.match(r"^\\d+\\.\\s+", line):
            if current:
                epics.append(current)
            title = re.sub(r"^\\d+\\.\\s+", "", line).strip()
            current = {"title": title, "reason": [], "tasks": [], "deliverables": []}
            section = None
            continue
        if line.lower().startswith("reason"):
            section = "reason"
            continue
        if line.lower().startswith("next tasks"):
            section = "tasks"
            continue
        if line.lower().startswith("deliverables"):
            section = "deliverables"
            continue
        if line.lower().startswith("publication"):
            section = None
            continue
        if not current:
            continue
        if section == "tasks" and re.match(r"^\\d+\\.", line):
            cleaned = re.sub(r"^\\d+\\.\\s*", "", line).strip()
            if cleaned:
                current["tasks"].append(cleaned)
            continue
        if section == "deliverables" and re.match(r"^[^A-Za-z0-9]+", line):
            cleaned = re.sub(r"^[^A-Za-z0-9]+", "", line).strip()
            if cleaned:
                current["deliverables"].append(cleaned)
            continue
        if section == "reason":
            current["reason"].append(line)

    if current:
        epics.append(current)

    unique: Dict[str, dict] = {}
    for epic in epics:
        title = epic.get("title") or ""
        if not title:
            continue
        if title not in unique:
            unique[title] = epic
    return list(unique.values())


def _seed_admin_pms_samples(conn: Connection, admin_user_id: str) -> None:
    marker = f"pms.seed.admin.{admin_user_id}"
    if get_meta(conn, marker) == "1":
        return

    deliverables_pdf = Path.home() / "Desktop" / "Project Deliverables (Reorder By Complexity Without Dependency).pdf"
    epics = _parse_deliverables_pdf(deliverables_pdf)

    if epics:
        project = pms_store.create_project(
            conn,
            name="Project Deliverables Roadmap",
            mode="personal",
            scope_type="user",
            scope_id=admin_user_id,
            status="active",
            config={"priority_tiers": ["P0", "P1", "P2", "P3"]},
            created_by=admin_user_id,
            is_sample=1,
        )
        first_task_id: Optional[str] = None
        for epic in epics:
            epic_row = pms_store.create_epic(
                conn,
                project_id=project["project_id"],
                title=epic["title"],
                description=" ".join(epic["reason"]).strip(),
                acceptance_criteria="\n".join(epic["deliverables"]).strip(),
                status="active",
                user_id=admin_user_id,
            )
            task = pms_store.add_task(
                conn,
                project_id=project["project_id"],
                epic_id=epic_row["epic_id"],
                title=epic["title"],
                deliverable_spec="\n".join(epic["deliverables"]).strip(),
                acceptance_criteria="".join(epic["reason"]).strip(),
                priority="P1",
                category="Deliverables",
                task_type="Planning",
                status="TODO",
                user_id=admin_user_id,
            )
            if not first_task_id:
                first_task_id = task["task_id"]
            for todo_text in epic["tasks"]:
                pms_store.add_todo(conn, task_id=task["task_id"], text=todo_text, user_id=admin_user_id)

        if first_task_id:
            now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            run = pms_store.start_run(
                conn,
                project_id=project["project_id"],
                epic_id=None,
                task_id=first_task_id,
                todo_id=None,
                input_params={"sample": True},
                status="running",
                user_id=admin_user_id,
            )
            pms_store.complete_run(
                conn,
                run_id=run["run_id"],
                project_id=project["project_id"],
                status="succeeded",
                summary="Seeded demo run for PMS.",
                user_id=admin_user_id,
            )
            pms_store.attach_artifact(
                conn,
                project_id=project["project_id"],
                run_id=run["run_id"],
                kind="json",
                content=json.dumps({"task_id": first_task_id, "status": "ok"}, indent=2).encode("utf-8"),
                filename="run_summary.json",
                display_name="Run Summary",
                mime_type="application/json",
                user_id=admin_user_id,
            )
            document = pms_store.create_document(
                conn,
                project_id=project["project_id"],
                title="PMS Deliverables Brief",
                kind="notes",
                visibility="team",
                epic_id=None,
                task_id=first_task_id,
                user_id=admin_user_id,
            )
            revision = pms_store.add_document_revision(
                conn,
                document_id=document["document_id"],
                content="PMS deliverables seed document.",
                author=admin_user_id,
                metadata={"seeded": True},
            )
            revision_hash = revision["revision_hash"] if isinstance(revision, dict) else revision
            pms_store.publish_document_revision(
                conn,
                document_id=document["document_id"],
                revision_hash=revision_hash,
                user_id=admin_user_id,
            )
            meeting = pms_store.create_meeting_session(
                conn,
                project_id=project["project_id"],
                title="PMS Kickoff",
                started_at=now,
                ended_at=None,
                participants=["Speaker 1", "Speaker 2"],
                language="en",
                epic_id=None,
                task_id=first_task_id,
                user_id=admin_user_id,
            )
            segments = [
                {
                    "ts_start": 0,
                    "ts_end": 42,
                    "speaker_label": "Speaker 1",
                    "text_original": "Next steps are to align deliverables and schedule.",
                    "confidence": 0.94,
                },
                {
                    "ts_start": 43,
                    "ts_end": 88,
                    "speaker_label": "Speaker 2",
                    "text_original": "We should document the technical design for the scheduler.",
                    "confidence": 0.91,
                },
            ]
            pms_store.add_transcript_segments(
                conn,
                meeting_id=meeting["meeting_id"],
                segments=segments,
                user_id=admin_user_id,
            )
            pms_store.generate_meeting_journal(
                conn, meeting_id=meeting["meeting_id"], user_id=admin_user_id
            )
            pms_store.add_expense(
                conn,
                project_id=project["project_id"],
                epic_id=None,
                task_id=first_task_id,
                amount=420.0,
                currency="USD",
                category="Tools",
                vendor="Cloud Lab",
                description="Seeded platform cost",
                occurred_at=now,
                user_id=admin_user_id,
            )
            pms_store.add_time_entry(
                conn,
                project_id=project["project_id"],
                epic_id=None,
                task_id=first_task_id,
                actor_id=admin_user_id,
                role="Lead",
                duration_minutes=180,
                hourly_rate=120.0,
                occurred_at=now,
                user_id=admin_user_id,
            )

    projects_dir = Path(__file__).resolve().parents[1] / "documents" / "projects"
    if projects_dir.exists():
        names = sorted({entry.name.strip() for entry in projects_dir.iterdir() if entry.is_dir() or entry.is_file()})
        if names:
            portfolio = pms_store.create_project(
                conn,
                name="Portfolio Projects Index",
                mode="personal",
                scope_type="user",
                scope_id=admin_user_id,
                status="active",
                config={"priority_tiers": ["P0", "P1", "P2", "P3"]},
                created_by=admin_user_id,
                is_sample=1,
            )
            for name in names:
                epic_row = pms_store.create_epic(
                    conn,
                    project_id=portfolio["project_id"],
                    title=name,
                    description="Imported from documents/projects",
                    acceptance_criteria="Define scope, deliverables, and schedule.",
                    status="active",
                    user_id=admin_user_id,
                )
                task = pms_store.add_task(
                    conn,
                    project_id=portfolio["project_id"],
                    epic_id=epic_row["epic_id"],
                    title=f"Scope {name}",
                    deliverable_spec="Define scope and deliverables.",
                    acceptance_criteria="Draft outline + acceptance criteria.",
                    priority="P2",
                    category="Portfolio",
                    task_type="Planning",
                    status="TODO",
                    user_id=admin_user_id,
                )
                pms_store.add_todo(
                    conn,
                    task_id=task["task_id"],
                    text="Draft scope statement and deliverable list.",
                    user_id=admin_user_id,
                )

    set_meta(conn, marker, "1")


def ensure_demo_data(conn: Connection, admin_user_id: Optional[str] = None) -> None:
    """Populate the SQLite store with sample projects/tasks if it is empty."""

    if _table_empty(conn, "projects"):
        _seed_projects(conn)
    if _table_empty(conn, "tasks"):
        _seed_tasks(conn)
    if admin_user_id:
        _seed_admin_pms_samples(conn, admin_user_id)
    conn.commit()
