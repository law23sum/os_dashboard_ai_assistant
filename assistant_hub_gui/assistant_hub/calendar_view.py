"""Calendar view for tasks with due dates."""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from calendar import monthrange, monthcalendar

from .db import AssistantState, Task


def get_calendar_month(year: int, month: int, state: AssistantState) -> Dict:
    """Get calendar month view with tasks displayed on due dates.

    Args:
        year: Year (e.g., 2024)
        month: Month (1-12)
        state: AssistantState with tasks

    Returns:
        Dict with:
        - year, month
        - weeks: List of weeks, each week is a list of days
        - tasks_by_date: Dict mapping date strings to lists of tasks
    """
    # Get all tasks with due dates
    tasks_with_dates = [t for t in state.tasks if t.due_date and t.status != "DONE"]

    # Parse and filter tasks for this month
    tasks_by_date = {}
    for task in tasks_with_dates:
        try:
            due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            if due_date.year == year and due_date.month == month:
                date_str = due_date.isoformat()
                if date_str not in tasks_by_date:
                    tasks_by_date[date_str] = []
                tasks_by_date[date_str].append(task)
        except Exception:
            pass

    # Generate calendar weeks
    calendar = monthcalendar(year, month)
    weeks = []
    for week in calendar:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)
            else:
                day_date = date(year, month, day)
                date_str = day_date.isoformat()
                day_tasks = tasks_by_date.get(date_str, [])

                # Check if overdue
                today = date.today()
                is_overdue = day_date < today

                week_days.append(
                    {
                        "day": day,
                        "date": date_str,
                        "tasks": day_tasks,
                        "task_count": len(day_tasks),
                        "is_overdue": is_overdue,
                        "is_today": day_date == today,
                    }
                )
        weeks.append(week_days)

    return {
        "year": year,
        "month": month,
        "month_name": datetime(year, month, 1).strftime("%B"),
        "weeks": weeks,
        "tasks_by_date": tasks_by_date,
        "total_tasks": len(tasks_with_dates),
    }


def get_week_view(state: AssistantState, start_date: Optional[date] = None) -> Dict:
    """Get weekly task overview.

    Args:
        state: AssistantState with tasks
        start_date: Start date of week (defaults to today)

    Returns:
        Dict with:
        - start_date, end_date
        - days: List of days with tasks
    """
    if start_date is None:
        start_date = date.today()

    # Get Monday of the week
    days_since_monday = start_date.weekday()
    monday = start_date - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)

    # Get tasks with due dates in this week
    tasks_with_dates = [t for t in state.tasks if t.due_date and t.status != "DONE"]

    days = []
    for i in range(7):
        day_date = monday + timedelta(days=i)
        date_str = day_date.isoformat()

        day_tasks = []
        for task in tasks_with_dates:
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if due_date == day_date:
                    day_tasks.append(task)
            except Exception:
                pass

        is_overdue = day_date < date.today()
        is_today = day_date == date.today()

        days.append(
            {
                "date": date_str,
                "day_name": day_date.strftime("%A"),
                "day_number": day_date.day,
                "tasks": day_tasks,
                "task_count": len(day_tasks),
                "is_overdue": is_overdue,
                "is_today": is_today,
            }
        )

    return {
        "start_date": monday.isoformat(),
        "end_date": sunday.isoformat(),
        "days": days,
    }


def get_upcoming_tasks(state: AssistantState, days: int = 14) -> List[Dict]:
    """Get tasks due in the next N days.

    Args:
        state: AssistantState with tasks
        days: Number of days ahead to look

    Returns:
        List of dicts with task info and days_until
    """
    today = date.today()
    end_date = today + timedelta(days=days)

    tasks_with_dates = [t for t in state.tasks if t.due_date and t.status != "DONE"]

    upcoming = []
    for task in tasks_with_dates:
        try:
            due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            if today <= due_date <= end_date:
                days_until = (due_date - today).days
                is_overdue = due_date < today

                upcoming.append(
                    {
                        "task": task,
                        "due_date": task.due_date,
                        "days_until": days_until,
                        "is_overdue": is_overdue,
                        "urgency": "overdue"
                        if is_overdue
                        else (
                            "urgent"
                            if days_until <= 1
                            else ("soon" if days_until <= 3 else "upcoming")
                        ),
                    }
                )
        except Exception:
            pass

    # Sort by due date
    upcoming.sort(key=lambda x: x["due_date"])

    return upcoming


def get_overdue_tasks(state: AssistantState) -> List[Task]:
    """Get all overdue tasks."""
    today = date.today()
    overdue = []

    for task in state.tasks:
        if task.status != "DONE" and task.due_date:
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if due_date < today:
                    overdue.append(task)
            except Exception:
                pass

    # Sort by how overdue (most overdue first)
    overdue.sort(
        key=lambda t: (
            datetime.strptime(t.due_date, "%Y-%m-%d").date() if t.due_date else date.max
        )
    )

    return overdue
