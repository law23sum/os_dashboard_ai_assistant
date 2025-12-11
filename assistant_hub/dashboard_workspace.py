"""Shared dashboard snapshot logic for Tk, FastAPI, and React clients."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Sequence

from .db import AssistantState, PERSONAS, PRIORITY_OPTIONS, STATUS_OPTIONS, Task

_PRIORITY_WEIGHT = {priority: idx for idx, priority in enumerate(PRIORITY_OPTIONS)}


def _priority_score(task: Task) -> int:
    """Lower score = higher priority."""
    base = _PRIORITY_WEIGHT.get(task.priority, len(_PRIORITY_WEIGHT))
    due_penalty = 0
    if task.due_date:
        try:
            due_penalty = max(0, int(datetime.strptime(task.due_date, "%Y-%m-%d").timestamp()))
        except Exception:
            due_penalty = 0
    return base * 1000000000 + due_penalty


def _serialize_task(task: Task) -> Dict[str, str]:
    return {
        "id": task.id,
        "title": task.title,
        "project": task.project,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "owner": task.owner,
        "notes": task.notes,
    }


@dataclass
class DashboardSnapshot:
    totals: Dict[str, int]
    today_tasks: List[Task]
    upcoming_tasks: List[Task]
    top_priority_tasks: List[Task]
    status_counts: Dict[str, int]
    persona_load: Dict[str, int]
    generated_at: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "totals": self.totals,
            "today_tasks": [_serialize_task(t) for t in self.today_tasks],
            "upcoming_tasks": [_serialize_task(t) for t in self.upcoming_tasks],
            "top_priority_tasks": [_serialize_task(t) for t in self.top_priority_tasks],
            "status_counts": self.status_counts,
            "persona_load": self.persona_load,
            "generated_at": self.generated_at,
        }


def build_dashboard_snapshot(state: AssistantState, limit: int = 5) -> DashboardSnapshot:
    """Compute dashboard metrics from assistant state."""
    tasks: Sequence[Task] = state.tasks or []
    today = datetime.now().strftime("%Y-%m-%d")
    today_tasks = [t for t in tasks if t.due_date == today and t.status != "DONE"]
    upcoming = sorted(
        (t for t in tasks if t.due_date and t.due_date > today and t.status != "DONE"),
        key=lambda t: t.due_date,
    )[:limit]

    incomplete = [t for t in tasks if t.status != "DONE"]
    top_priority = sorted(incomplete, key=_priority_score)[:limit]

    status_counts: Dict[str, int] = {status: 0 for status in STATUS_OPTIONS}
    for task in tasks:
        status_counts[task.status] = status_counts.get(task.status, 0) + 1

    persona_load: Dict[str, int] = {persona: 0 for persona in PERSONAS}
    for task in incomplete:
        persona_load[task.owner] = persona_load.get(task.owner, 0) + 1

    totals = {
        "tasks": len(tasks),
        "active_tasks": len(incomplete),
        "projects": len(getattr(state, "projects", [])),
        "due_today": len(today_tasks),
    }

    return DashboardSnapshot(
        totals=totals,
        today_tasks=today_tasks,
        upcoming_tasks=upcoming,
        top_priority_tasks=top_priority,
        status_counts=status_counts,
        persona_load=persona_load,
        generated_at=datetime.now().isoformat(timespec="seconds"),
    )
