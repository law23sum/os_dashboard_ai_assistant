"""Analytics API router."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from pathlib import Path
import sys

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import load_state
from assistant_hub_gui.assistant_hub.analytics import (
    get_task_completion_stats,
    get_project_stats,
    get_time_tracking_stats,
    get_productivity_metrics,
    get_recent_activity,
    generate_report,
)

from backend_api.db import db_session

router = APIRouter()


class TaskStats(BaseModel):
    total: int
    done: int
    in_progress: int
    todo: int
    blocked: int
    completion_rate: float


class ProjectStats(BaseModel):
    total: int
    done: int
    in_progress: int
    todo: int
    completion_rate: float
    priority: str


class TimeTrackingStats(BaseModel):
    total_estimated_minutes: int
    total_logged_minutes: int
    tasks_with_time: int
    estimated_hours: float
    logged_hours: float


class ProductivityMetrics(BaseModel):
    completion_rate: float
    tasks_completed: int
    tasks_in_progress: int
    total_time_logged_hours: float
    average_time_per_task_minutes: float


class RecentActivityItem(BaseModel):
    id: int
    title: str
    project: str
    status: str
    created_at: str


class AnalyticsSummary(BaseModel):
    tasks: TaskStats
    projects: Dict[str, ProjectStats]
    time_tracking: TimeTrackingStats
    productivity: ProductivityMetrics
    recent_activity: List[RecentActivityItem]


class AnalyticsReport(BaseModel):
    report: str


@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary():
    """Return aggregated analytics for dashboard and reports."""
    with db_session() as db:
        state = load_state(db)
    task_stats = get_task_completion_stats(state)
    project_stats = get_project_stats(state)
    time_stats = get_time_tracking_stats(state)
    productivity = get_productivity_metrics(state)
    recent = get_recent_activity(state)

    return AnalyticsSummary(
        tasks=task_stats,
        projects=project_stats,
        time_tracking=time_stats,
        productivity=productivity,
        recent_activity=recent,
    )


@router.get("/report", response_model=AnalyticsReport)
async def analytics_report():
    """Return the printable analytics report."""
    with db_session() as db:
        state = load_state(db)
    report = generate_report(state)
    return AnalyticsReport(report=report)
