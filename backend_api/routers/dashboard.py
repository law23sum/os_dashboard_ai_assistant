"""Dashboard API router."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import sys
from pathlib import Path
import psutil
import logging

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
    try:
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
            total_projects_row = cursor.fetchone()
            total_projects = total_projects_row[0] if total_projects_row else 0

            cursor = db.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
            active_projects_row = cursor.fetchone()
            active_projects = active_projects_row[0] if active_projects_row else 0

        # System stats with error handling
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            system_stats = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": mem.percent,
                "disk_percent": disk.percent,
                "memory": {"used": mem.used, "total": mem.total},
                "disk": {"used": disk.used, "total": disk.total},
            }
        except Exception as e:
            logging.warning(f"Failed to get system stats: {e}")
            system_stats = {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "memory": {"used": 0, "total": 0},
                "disk": {"used": 0, "total": 0},
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
    except Exception as e:
        logging.error(f"Error fetching dashboard stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard statistics: {str(e)}")
