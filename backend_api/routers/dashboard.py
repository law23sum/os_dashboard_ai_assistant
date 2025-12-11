"""Dashboard API router."""
from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel
import sys
from pathlib import Path
import psutil

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_hub.dashboard_workspace import build_dashboard_snapshot
from assistant_hub_gui.assistant_hub.db import load_state, load_security_status
from backend_api.db import db_session

router = APIRouter()

class DashboardStats(BaseModel):
    total_tasks: int
    tasks_by_status: Dict[str, int]
    tasks_by_priority: Dict[str, int]
    total_projects: int
    active_projects: int
    system_stats: Dict[str, Any]
    security_status: Dict[str, Any]
    persona_load: Dict[str, int]
    active_persona: str

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    with db_session() as db:
        state = load_state(db)
        security_status = load_security_status(db)
        snapshot = build_dashboard_snapshot(state)

        # Count tasks by status
        cursor = db.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        tasks_by_status = {row[0]: row[1] for row in cursor.fetchall()}

        # Count tasks by priority
        cursor = db.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
        tasks_by_priority = {row[0]: row[1] for row in cursor.fetchall()}

        # Count projects
        cursor = db.execute("SELECT COUNT(*) FROM projects")
        total_projects = cursor.fetchone()[0]

        cursor = db.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
        active_projects = cursor.fetchone()[0]

    # System stats
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    system_stats = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": mem.percent,
        "disk_percent": disk.percent,
        "memory": {"used": mem.used, "total": mem.total},
        "disk": {"used": disk.used, "total": disk.total},
    }
    
    return DashboardStats(
        total_tasks=len(state.tasks),
        tasks_by_status=tasks_by_status,
        tasks_by_priority=tasks_by_priority,
        total_projects=total_projects,
        active_projects=active_projects,
        system_stats=system_stats,
        security_status={
            "status": security_status.status,
            "message": security_status.message,
            "updated_at": security_status.updated_at,
            "source": security_status.source,
        },
        persona_load=snapshot.persona_load,
        active_persona=state.active_persona,
    )
