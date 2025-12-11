"""Smart suggestions for task prioritization and workload management."""

from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

from .db import AssistantState, Task, Project, STATUS_OPTIONS, PRIORITY_OPTIONS


def get_deadline_reminders(state: AssistantState, days_ahead: int = 7) -> List[Dict]:
    """Get tasks with upcoming deadlines."""
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)

    reminders = []
    for task in state.tasks:
        if task.status == "DONE" or not task.due_date:
            continue

        try:
            due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            if today <= due_date <= cutoff:
                days_until = (due_date - today).days
                reminders.append(
                    {
                        "task": task,
                        "days_until": days_until,
                        "urgency": "high"
                        if days_until <= 2
                        else "medium"
                        if days_until <= 5
                        else "low",
                    }
                )
        except Exception:
            continue

    return sorted(reminders, key=lambda x: (x["days_until"], x["task"].priority))


def get_workload_balance(state: AssistantState) -> Dict[str, Dict]:
    """Analyze workload distribution across personas."""
    workload = {}

    for persona in ["Chris", "AIC", "Aria", "Sora"]:
        tasks = [t for t in state.tasks if t.owner == persona and t.status != "DONE"]
        total_estimated = sum(t.time_estimated or 0 for t in tasks)
        total_logged = sum(t.time_logged or 0 for t in tasks)
        high_priority = len(
            [t for t in tasks if t.priority == "HIGH" or t.priority == "CRITICAL"]
        )

        workload[persona] = {
            "task_count": len(tasks),
            "estimated_hours": round(total_estimated / 60, 1),
            "logged_hours": round(total_logged / 60, 1),
            "high_priority_count": high_priority,
            "overloaded": len(tasks) > 20
            or total_estimated > 40 * 60,  # > 20 tasks or > 40 hours
        }

    return workload


def get_project_health(state: AssistantState) -> Dict[str, Dict]:
    """Get health indicators for each project."""
    project_health = {}

    for project in state.projects:
        project_tasks = [t for t in state.tasks if t.project == project.name]
        total = len(project_tasks)
        done = len([t for t in project_tasks if t.status == "DONE"])
        blocked = len([t for t in project_tasks if t.status == "BLOCKED"])
        overdue = 0

        today = datetime.now().date()
        for task in project_tasks:
            if task.due_date and task.status != "DONE":
                try:
                    due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    if due_date < today:
                        overdue += 1
                except Exception:
                    pass

        completion_rate = (done / total * 100) if total > 0 else 0

        # Health score (0-100)
        health_score = completion_rate
        if blocked > 0:
            health_score -= (blocked / total * 30) if total > 0 else 0
        if overdue > 0:
            health_score -= (overdue / total * 20) if total > 0 else 0

        health_status = (
            "healthy"
            if health_score >= 70
            else "warning"
            if health_score >= 40
            else "critical"
        )

        project_health[project.name] = {
            "total_tasks": total,
            "completed": done,
            "blocked": blocked,
            "overdue": overdue,
            "completion_rate": round(completion_rate, 1),
            "health_score": round(max(0, health_score), 1),
            "health_status": health_status,
        }

    return project_health


def get_smart_prioritization_suggestions(state: AssistantState) -> List[Dict]:
    """Get AI-style suggestions for task prioritization."""
    suggestions = []

    # Check for tasks with dependencies that are done
    done_ids = {t.id for t in state.tasks if t.status == "DONE"}
    for task in state.tasks:
        if task.status != "DONE" and task.depends_on:
            if task.depends_on in done_ids:
                suggestions.append(
                    {
                        "type": "dependency_ready",
                        "task_id": task.id,
                        "message": f"Task #{task.id} dependencies are complete - ready to start",
                        "priority": "high",
                    }
                )

    # Check for high-priority tasks with no progress
    for task in state.tasks:
        if task.status == "TODO" and task.priority in ["HIGH", "CRITICAL"]:
            # Check if it's been around for a while
            try:
                created = datetime.fromisoformat(task.created_at)
                days_old = (datetime.now() - created).days
                if days_old > 3:
                    suggestions.append(
                        {
                            "type": "stale_high_priority",
                            "task_id": task.id,
                            "message": f"High priority task #{task.id} has been TODO for {days_old} days",
                            "priority": "high",
                        }
                    )
            except Exception:
                pass

    # Check for tasks approaching deadlines
    reminders = get_deadline_reminders(state, days_ahead=3)
    for reminder in reminders[:5]:  # Top 5
        suggestions.append(
            {
                "type": "deadline_approaching",
                "task_id": reminder["task"].id,
                "message": f"Task #{reminder['task'].id} due in {reminder['days_until']} days",
                "priority": reminder["urgency"],
            }
        )

    return suggestions
