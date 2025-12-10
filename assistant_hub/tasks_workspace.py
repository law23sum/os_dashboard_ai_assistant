"""Shared helpers for presenting tasks in Tk and React."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence

from assistant_hub.db import PERSONAS, PRIORITY_OPTIONS, STATUS_OPTIONS, Task


def _serialize(task: Task) -> Dict[str, object]:
    return {
        "id": task.id,
        "title": task.title,
        "project": task.project,
        "priority": task.priority,
        "status": task.status,
        "owner": task.owner,
        "due_date": task.due_date,
        "notes": task.notes,
    }


@dataclass
class TaskWorkspaceSnapshot:
    tasks: List[Dict[str, object]]
    status_counts: Dict[str, int]
    priority_counts: Dict[str, int]
    persona_counts: Dict[str, int]
    generated_at: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "tasks": self.tasks,
            "status_counts": self.status_counts,
            "priority_counts": self.priority_counts,
            "persona_counts": self.persona_counts,
            "generated_at": self.generated_at,
        }


def build_task_snapshot(
    tasks: Sequence[Task],
    *,
    include_done: bool = True,
    owner: Optional[str] = None,
) -> TaskWorkspaceSnapshot:
    """Create a normalized snapshot of task data for Tk + React."""
    filtered: Iterable[Task] = tasks
    if not include_done:
        filtered = [task for task in filtered if task.status != "DONE"]
    if owner:
        filtered = [task for task in filtered if task.owner == owner]

    filtered_list = list(filtered)
    status_counts: Dict[str, int] = {status: 0 for status in STATUS_OPTIONS}
    priority_counts: Dict[str, int] = {priority: 0 for priority in PRIORITY_OPTIONS}
    persona_counts: Dict[str, int] = {persona: 0 for persona in PERSONAS}

    for task in filtered_list:
        status_counts[task.status] = status_counts.get(task.status, 0) + 1
        priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1
        persona_counts[task.owner] = persona_counts.get(task.owner, 0) + 1

    serialized = [_serialize(task) for task in filtered_list]
    return TaskWorkspaceSnapshot(
        tasks=serialized,
        status_counts=status_counts,
        priority_counts=priority_counts,
        persona_counts=persona_counts,
        generated_at=datetime.now().isoformat(timespec="seconds"),
    )
