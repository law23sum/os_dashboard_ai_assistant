"""AI-powered task creation from chat messages."""

import re
from typing import List, Optional
from datetime import datetime

from .db import Task, db_insert_task, PERSONAS, PRIORITY_OPTIONS, STATUS_OPTIONS


def extract_tasks_from_text(
    text: str, default_project: str = "General", default_owner: str = "Chris"
) -> List[Task]:
    """Extract task information from natural language text."""
    tasks = []

    # Pattern to match task-like phrases
    # Examples: "Create a task to...", "I need to...", "TODO: ...", "Task: ..."
    patterns = [
        r"(?:create|add|make)\s+(?:a\s+)?task\s+(?:to\s+)?(?:for\s+)?(.+?)(?:\.|$|due|priority)",
        r"todo:\s*(.+?)(?:\.|$|due|priority)",
        r"task:\s*(.+?)(?:\.|$|due|priority)",
        r"i\s+need\s+to\s+(.+?)(?:\.|$|due|priority)",
        r"remind\s+me\s+to\s+(.+?)(?:\.|$|due|priority)",
    ]

    # Extract potential tasks
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            task_text = match.group(1).strip()
            if len(task_text) > 3:  # Minimum task length
                task = _parse_task_text(task_text, default_project, default_owner)
                if task:
                    tasks.append(task)

    # If no patterns matched, check if the whole text looks like a task
    if not tasks and len(text.strip()) > 10 and len(text.strip()) < 200:
        task = _parse_task_text(text, default_project, default_owner)
        if task:
            tasks.append(task)

    return tasks


def _parse_task_text(
    text: str, default_project: str, default_owner: str
) -> Optional[Task]:
    """Parse task text to extract task details."""
    # Extract priority
    priority = "MEDIUM"
    for p in PRIORITY_OPTIONS:
        if p.lower() in text.lower():
            priority = p
            text = re.sub(r"\b" + p + r"\b", "", text, flags=re.IGNORECASE).strip()

    # Extract due date (simple patterns)
    due_date = None
    date_patterns = [
        r"due\s+(?:on\s+)?(\d{4}-\d{2}-\d{2})",
        r"due\s+(?:on\s+)?(\d{1,2}/\d{1,2}/\d{4})",
        r"by\s+(\d{4}-\d{2}-\d{2})",
        r"deadline\s+(\d{4}-\d{2}-\d{2})",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            # Try to parse and format
            try:
                if "/" in date_str:
                    # Convert MM/DD/YYYY to YYYY-MM-DD
                    parts = date_str.split("/")
                    if len(parts) == 3:
                        due_date = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                else:
                    due_date = date_str
                text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
            except Exception:
                pass

    # Extract project (look for "project: X" or "for project X")
    project = default_project
    project_match = re.search(r"(?:project|proj):\s*(\w+)", text, re.IGNORECASE)
    if project_match:
        project = project_match.group(1)
        text = re.sub(r"(?:project|proj):\s*\w+", "", text, flags=re.IGNORECASE).strip()

    # Extract owner
    owner = default_owner
    owner_match = re.search(r"(?:owner|assign|to):\s*(\w+)", text, re.IGNORECASE)
    if owner_match:
        potential_owner = owner_match.group(1)
        if potential_owner in PERSONAS:
            owner = potential_owner
            text = re.sub(
                r"(?:owner|assign|to):\s*\w+", "", text, flags=re.IGNORECASE
            ).strip()

    # Clean up the title
    title = text.strip()
    # Remove extra whitespace
    title = " ".join(title.split())

    if not title or len(title) < 3:
        return None

    # Create task
    return Task(
        id=0,
        title=title,
        project=project,
        status="TODO",
        priority=priority,
        due_date=due_date or "",
        notes="",
        owner=owner,
        created_at=datetime.now().isoformat(timespec="seconds"),
        depends_on=None,
        recurrence_pattern=None,
        recurrence_end=None,
        time_estimated=None,
        time_logged=None,
        template_id=None,
    )


def create_task_from_ai_message(
    conn,
    message_text: str,
    default_project: str = "General",
    default_owner: str = "Chris",
) -> List[Task]:
    """Create tasks from AI chat message."""
    tasks = extract_tasks_from_text(message_text, default_project, default_owner)

    created_tasks = []
    for task in tasks:
        task.id = db_insert_task(conn, task)
        created_tasks.append(task)

    return created_tasks
