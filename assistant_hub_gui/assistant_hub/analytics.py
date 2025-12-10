"""Analytics and reporting for tasks and projects."""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

from .db import AssistantState, Task, Project


def get_task_completion_stats(state: AssistantState) -> Dict:
    """Get task completion statistics."""
    total = len(state.tasks)
    done = len([t for t in state.tasks if t.status == "DONE"])
    in_progress = len([t for t in state.tasks if t.status == "IN_PROGRESS"])
    todo = len([t for t in state.tasks if t.status == "TODO"])
    blocked = len([t for t in state.tasks if t.status == "BLOCKED"])

    completion_rate = (done / total * 100) if total > 0 else 0

    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "todo": todo,
        "blocked": blocked,
        "completion_rate": round(completion_rate, 1),
    }


def get_project_stats(state: AssistantState) -> Dict[str, Dict]:
    """Get statistics per project."""
    project_stats = {}

    for project in state.projects:
        project_tasks = [t for t in state.tasks if t.project == project.name]
        total = len(project_tasks)
        done = len([t for t in project_tasks if t.status == "DONE"])

        project_stats[project.name] = {
            "total": total,
            "done": done,
            "in_progress": len([t for t in project_tasks if t.status == "IN_PROGRESS"]),
            "todo": len([t for t in project_tasks if t.status == "TODO"]),
            "completion_rate": round((done / total * 100) if total > 0 else 0, 1),
            "priority": project.priority,
        }

    return project_stats


def get_time_tracking_stats(state: AssistantState) -> Dict:
    """Get time tracking statistics."""
    total_estimated = sum(t.time_estimated or 0 for t in state.tasks)
    total_logged = sum(t.time_logged or 0 for t in state.tasks)

    tasks_with_time = [t for t in state.tasks if t.time_estimated or t.time_logged]

    return {
        "total_estimated_minutes": total_estimated,
        "total_logged_minutes": total_logged,
        "tasks_with_time": len(tasks_with_time),
        "estimated_hours": round(total_estimated / 60, 1),
        "logged_hours": round(total_logged / 60, 1),
    }


def get_recent_activity(state: AssistantState, days: int = 7) -> List[Dict]:
    """Get recent task activity."""
    cutoff = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff.isoformat(timespec="seconds")

    recent_tasks = []
    for task in state.tasks:
        try:
            created = datetime.fromisoformat(task.created_at)
            if created >= cutoff:
                recent_tasks.append(
                    {
                        "id": task.id,
                        "title": task.title,
                        "project": task.project,
                        "status": task.status,
                        "created_at": task.created_at,
                    }
                )
        except Exception:
            continue

    return sorted(recent_tasks, key=lambda x: x["created_at"], reverse=True)


def get_productivity_metrics(state: AssistantState) -> Dict:
    """Get productivity metrics."""
    stats = get_task_completion_stats(state)
    time_stats = get_time_tracking_stats(state)

    # Calculate average time per task
    done_tasks = [t for t in state.tasks if t.status == "DONE" and t.time_logged]
    avg_time = (
        sum(t.time_logged for t in done_tasks) / len(done_tasks) if done_tasks else 0
    )

    return {
        "completion_rate": stats["completion_rate"],
        "tasks_completed": stats["done"],
        "tasks_in_progress": stats["in_progress"],
        "total_time_logged_hours": time_stats["logged_hours"],
        "average_time_per_task_minutes": round(avg_time, 1),
    }


def generate_report(state: AssistantState) -> str:
    """Generate a text report of all statistics."""
    task_stats = get_task_completion_stats(state)
    project_stats = get_project_stats(state)
    time_stats = get_time_tracking_stats(state)
    productivity = get_productivity_metrics(state)

    report = []
    report.append("=" * 60)
    report.append("ASSISTANT HUB ANALYTICS REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    report.append("TASK STATISTICS")
    report.append("-" * 60)
    report.append(f"Total Tasks: {task_stats['total']}")
    report.append(f"  Done: {task_stats['done']}")
    report.append(f"  In Progress: {task_stats['in_progress']}")
    report.append(f"  TODO: {task_stats['todo']}")
    report.append(f"  Blocked: {task_stats['blocked']}")
    report.append(f"Completion Rate: {task_stats['completion_rate']}%")
    report.append("")

    report.append("PROJECT STATISTICS")
    report.append("-" * 60)
    for project_name, stats in sorted(
        project_stats.items(), key=lambda x: x[1]["total"], reverse=True
    ):
        report.append(f"{project_name}:")
        report.append(
            f"  Total: {stats['total']}, Done: {stats['done']}, Completion: {stats['completion_rate']}%"
        )
    report.append("")

    report.append("TIME TRACKING")
    report.append("-" * 60)
    report.append(f"Estimated: {time_stats['estimated_hours']} hours")
    report.append(f"Logged: {time_stats['logged_hours']} hours")
    report.append(f"Tasks with time data: {time_stats['tasks_with_time']}")
    report.append("")

    report.append("PRODUCTIVITY METRICS")
    report.append("-" * 60)
    report.append(f"Completion Rate: {productivity['completion_rate']}%")
    report.append(f"Tasks Completed: {productivity['tasks_completed']}")
    report.append(f"Total Time Logged: {productivity['total_time_logged_hours']} hours")
    report.append(
        f"Average Time per Task: {productivity['average_time_per_task_minutes']} minutes"
    )

    return "\n".join(report)
