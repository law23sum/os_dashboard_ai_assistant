"""Utilities to build analytics snapshots for API + shared UI."""
from __future__ import annotations

from typing import Dict, List

from .analytics import (
    generate_report,
    get_productivity_metrics,
    get_project_stats,
    get_recent_activity,
    get_task_completion_stats,
    get_time_tracking_stats,
)
from .suggestions import (
    get_deadline_reminders,
    get_project_health,
    get_smart_prioritization_suggestions,
    get_workload_balance,
)
from .db import AssistantState


def build_analytics_summary(state: AssistantState) -> Dict[str, object]:
    tasks = get_task_completion_stats(state)
    projects = get_project_stats(state)
    time_stats = get_time_tracking_stats(state)
    productivity = get_productivity_metrics(state)
    recent_activity = get_recent_activity(state)
    reminders = [
        {
            "task_id": reminder["task"].id,
            "title": reminder["task"].title,
            "project": reminder["task"].project,
            "due_date": reminder["task"].due_date,
            "priority": reminder["task"].priority,
            "days_until": reminder["days_until"],
            "urgency": reminder["urgency"],
        }
        for reminder in get_deadline_reminders(state, days_ahead=7)
    ]
    workload = get_workload_balance(state)
    project_health = get_project_health(state)
    suggestions = get_smart_prioritization_suggestions(state)

    return {
        "tasks": tasks,
        "projects": projects,
        "time_tracking": time_stats,
        "productivity": productivity,
        "recent_activity": recent_activity,
        "deadline_reminders": reminders,
        "workload": workload,
        "project_health": project_health,
        "suggestions": suggestions,
    }


def build_analytics_report(state: AssistantState) -> str:
    """Generate the text report shared between Tk and React."""
    return generate_report(state)
