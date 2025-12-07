"""Calendar view utilities for tasks and deadlines."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

from .db import AssistantState, Task


def get_calendar_month(year: int, month: int, state: AssistantState) -> Dict:
    """Get calendar data for a specific month."""
    # Get all tasks with due dates
    tasks_by_date = defaultdict(list)
    
    for task in state.tasks:
        if task.due_date and task.status != "DONE":
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d")
                if due_date.year == year and due_date.month == month:
                    tasks_by_date[due_date.day].append({
                        "id": task.id,
                        "title": task.title,
                        "priority": task.priority,
                        "status": task.status,
                        "project": task.project,
                        "overdue": due_date.date() < datetime.now().date()
                    })
            except Exception:
                continue
    
    # Build calendar structure
    first_day = datetime(year, month, 1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Get first day of week (0 = Monday, 6 = Sunday)
    start_weekday = first_day.weekday()
    
    calendar = {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B"),
        "days": []
    }
    
    # Add empty cells for days before month starts
    for _ in range(start_weekday):
        calendar["days"].append(None)
    
    # Add days of the month
    for day in range(1, last_day.day + 1):
        date_obj = datetime(year, month, day)
        calendar["days"].append({
            "day": day,
            "date": date_obj.strftime("%Y-%m-%d"),
            "weekday": date_obj.strftime("%A"),
            "is_today": date_obj.date() == datetime.now().date(),
            "is_weekend": date_obj.weekday() >= 5,
            "tasks": tasks_by_date[day]
        })
    
    return calendar


def get_upcoming_tasks(state: AssistantState, days: int = 14) -> List[Dict]:
    """Get tasks due in the next N days."""
    today = datetime.now().date()
    cutoff = today + timedelta(days=days)
    
    upcoming = []
    for task in state.tasks:
        if task.due_date and task.status != "DONE":
            try:
                due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                if today <= due_date <= cutoff:
                    upcoming.append({
                        "task": task,
                        "due_date": task.due_date,
                        "days_until": (due_date - today).days,
                        "overdue": due_date < today
                    })
            except Exception:
                continue
    
    return sorted(upcoming, key=lambda x: x["due_date"])


def get_week_view(state: AssistantState, start_date: Optional[datetime] = None) -> Dict:
    """Get a week view of tasks."""
    if not start_date:
        start_date = datetime.now()
    
    # Get Monday of the week
    days_since_monday = start_date.weekday()
    monday = start_date - timedelta(days=days_since_monday)
    
    week = {
        "start_date": monday.strftime("%Y-%m-%d"),
        "days": []
    }
    
    for i in range(7):
        day = monday + timedelta(days=i)
        day_tasks = []
        
        for task in state.tasks:
            if task.due_date and task.status != "DONE":
                try:
                    due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
                    if due_date == day.date():
                        day_tasks.append({
                            "id": task.id,
                            "title": task.title,
                            "priority": task.priority,
                            "status": task.status,
                            "project": task.project
                        })
                except Exception:
                    continue
        
        week["days"].append({
            "date": day.strftime("%Y-%m-%d"),
            "day_name": day.strftime("%A"),
            "day_number": day.day,
            "is_today": day.date() == datetime.now().date(),
            "tasks": day_tasks
        })
    
    return week

