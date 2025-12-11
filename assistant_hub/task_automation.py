"""Task automation utilities: recurring tasks, dependencies, etc."""

from datetime import datetime, timedelta
from typing import List, Optional
import sqlite3

from .db import Task, db_insert_task, load_state, STATUS_OPTIONS


def process_recurring_tasks(conn: sqlite3.Connection) -> int:
    """Process recurring tasks and create next occurrences."""
    state = load_state(conn)
    created = 0
    today = datetime.now().date()

    for task in state.tasks:
        if task.status != "DONE" or not task.recurrence_pattern:
            continue

        # Check if recurrence has ended
        if task.recurrence_end:
            end_date = datetime.strptime(task.recurrence_end, "%Y-%m-%d").date()
            if today > end_date:
                continue

        # Calculate next occurrence date
        next_date = _calculate_next_occurrence(
            task.due_date or task.created_at, task.recurrence_pattern, today
        )

        if next_date and next_date <= today:
            # Create next occurrence
            new_task = Task(
                id=0,
                title=task.title,
                project=task.project,
                status="TODO",
                priority=task.priority,
                due_date=next_date.strftime("%Y-%m-%d"),
                notes=task.notes,
                owner=task.owner,
                created_at=datetime.now().isoformat(timespec="seconds"),
                depends_on=task.depends_on,
                recurrence_pattern=task.recurrence_pattern,
                recurrence_end=task.recurrence_end,
                time_estimated=task.time_estimated,
                time_logged=None,
                template_id=task.template_id,
            )
            db_insert_task(conn, new_task)
            created += 1

    return created


def _calculate_next_occurrence(
    last_date_str: str, pattern: str, today: datetime.date
) -> Optional[datetime.date]:
    """Calculate next occurrence date based on pattern."""
    try:
        if last_date_str:
            last_date = datetime.strptime(last_date_str[:10], "%Y-%m-%d").date()
        else:
            last_date = today

        if pattern == "daily":
            next_date = last_date + timedelta(days=1)
        elif pattern == "weekly":
            next_date = last_date + timedelta(weeks=1)
        elif pattern == "monthly":
            # Add approximately one month
            if last_date.month == 12:
                next_date = last_date.replace(year=last_date.year + 1, month=1)
            else:
                next_date = last_date.replace(month=last_date.month + 1)
        elif pattern == "yearly":
            next_date = last_date.replace(year=last_date.year + 1)
        else:
            return None

        return next_date if next_date >= today else None
    except Exception:
        return None


def check_task_dependencies(state) -> List[Task]:
    """Check which tasks are blocked by dependencies."""
    blocked = []
    done_ids = {t.id for t in state.tasks if t.status == "DONE"}

    for task in state.tasks:
        if task.status == "DONE" or not task.depends_on:
            continue

        if task.depends_on not in done_ids:
            blocked.append(task)

    return blocked


def can_start_task(task: Task, state) -> bool:
    """Check if a task can be started (dependencies met)."""
    if not task.depends_on:
        return True

    done_ids = {t.id for t in state.tasks if t.status == "DONE"}
    return task.depends_on in done_ids


def get_task_dependency_chain(task: Task, state) -> List[Task]:
    """Get the full dependency chain for a task."""
    chain = []
    visited = set()
    current = task

    while current and current.depends_on and current.depends_on not in visited:
        visited.add(current.id)
        chain.append(current)

        # Find dependency
        dep = next((t for t in state.tasks if t.id == current.depends_on), None)
        if not dep:
            break
        current = dep

    if current:
        chain.append(current)

    return list(reversed(chain))
