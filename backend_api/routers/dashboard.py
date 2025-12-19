"""Dashboard API router.

Provides comprehensive dashboard statistics and database access endpoints
for the frontend to fetch all necessary data.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import sys
import logging
from pathlib import Path
from datetime import datetime
import psutil

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_hub.dashboard_workspace import build_dashboard_snapshot
from assistant_hub_gui.assistant_hub.db import (
    load_state, 
    load_security_status, 
    load_settings,
    db_list_document_operations,
    db_get_note_links,
    db_list_project_events,
    PERSONAS,
)
from backend_api.db import db_session

logger = logging.getLogger(__name__)
router = APIRouter()


class TaskSummary(BaseModel):
    """Condensed task info for dashboard views."""
    id: int
    title: str
    project: str
    status: str
    priority: str
    owner: str
    due_date: Optional[str] = None
    created_at: str


class ProjectSummary(BaseModel):
    """Condensed project info for dashboard views."""
    name: str
    description: str
    status: str
    priority: str
    task_count: int = 0
    completed_count: int = 0


class DocumentOperationSummary(BaseModel):
    """Summary of a document operation."""
    id: int
    title: str
    project_id: str
    integration_type: str
    operation: str
    status: str
    persona: str
    started_at: str
    completed_at: Optional[str] = None


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


class FullDataSnapshot(BaseModel):
    """Complete database snapshot for frontend hydration.
    
    This provides all the data the frontend needs in a single request,
    reducing network overhead and ensuring consistency.
    """
    # Core data
    tasks: List[TaskSummary]
    projects: List[ProjectSummary]
    
    # Dashboard metrics
    stats: DashboardStats
    
    # Document operations (AI ops)
    recent_operations: List[DocumentOperationSummary]
    
    # Settings
    settings: Dict[str, Any]
    
    # Metadata
    personas: List[str]
    fetched_at: str


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
            tasks_by_status = {row[0] or "UNKNOWN": row[1] for row in cursor.fetchall()}

            # Count tasks by priority
            cursor = db.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
            tasks_by_priority = {row[0] or "MEDIUM": row[1] for row in cursor.fetchall()}

            # Count projects
            cursor = db.execute("SELECT COUNT(*) FROM projects")
            total_projects = cursor.fetchone()[0]

            cursor = db.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
            active_projects = cursor.fetchone()[0]

        # System stats (with error handling)
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            system_stats = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": mem.percent,
                "disk_percent": disk.percent,
                "memory": {"used": mem.used, "total": mem.total},
                "disk": {"used": disk.used, "total": disk.total},
            }
        except Exception as e:
            logger.warning(f"Failed to get system stats: {e}")
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
        logger.error(f"Failed to get dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


@router.get("/full-data", response_model=FullDataSnapshot)
async def get_full_data_snapshot(
    operations_limit: int = Query(50, ge=1, le=200, description="Max document operations to return"),
):
    """Get a complete data snapshot for frontend hydration.
    
    This endpoint returns all core data in a single request, which is more
    efficient than making multiple API calls, especially on initial page load.
    """
    try:
        with db_session() as db:
            state = load_state(db)
            security_status = load_security_status(db)
            settings = load_settings(db)
            snapshot = build_dashboard_snapshot(state)
            
            # Build task summaries
            tasks: List[TaskSummary] = []
            for task in state.tasks:
                tasks.append(TaskSummary(
                    id=task.id,
                    title=task.title,
                    project=task.project,
                    status=task.status,
                    priority=task.priority,
                    owner=task.owner,
                    due_date=task.due_date if task.due_date else None,
                    created_at=task.created_at,
                ))
            
            # Build project summaries with task counts
            projects: List[ProjectSummary] = []
            task_by_project: Dict[str, Dict[str, int]] = {}
            for task in state.tasks:
                proj = task.project or "General"
                if proj not in task_by_project:
                    task_by_project[proj] = {"total": 0, "completed": 0}
                task_by_project[proj]["total"] += 1
                if task.status.upper() == "DONE":
                    task_by_project[proj]["completed"] += 1
            
            for proj in state.projects:
                counts = task_by_project.get(proj.name, {"total": 0, "completed": 0})
                projects.append(ProjectSummary(
                    name=proj.name,
                    description=proj.description,
                    status=proj.status,
                    priority=proj.priority,
                    task_count=counts["total"],
                    completed_count=counts["completed"],
                ))
            
            # Get recent document operations
            operations = db_list_document_operations(db, limit=operations_limit)
            recent_operations: List[DocumentOperationSummary] = []
            for op in operations:
                recent_operations.append(DocumentOperationSummary(
                    id=op.id,
                    title=op.title,
                    project_id=op.project_id,
                    integration_type=op.integration_type,
                    operation=op.operation,
                    status=op.status,
                    persona=op.persona,
                    started_at=op.started_at,
                    completed_at=op.completed_at,
                ))
            
            # Collect stats
            cursor = db.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            tasks_by_status = {row[0] or "UNKNOWN": row[1] for row in cursor.fetchall()}
            
            cursor = db.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
            tasks_by_priority = {row[0] or "MEDIUM": row[1] for row in cursor.fetchall()}
            
            cursor = db.execute("SELECT COUNT(*) FROM projects")
            total_projects = cursor.fetchone()[0]
            
            cursor = db.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
            active_projects = cursor.fetchone()[0]
        
        # System stats
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            system_stats = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": mem.percent,
                "disk_percent": disk.percent,
                "memory": {"used": mem.used, "total": mem.total},
                "disk": {"used": disk.used, "total": disk.total},
            }
        except Exception:
            system_stats = {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0,
                "memory": {"used": 0, "total": 0},
                "disk": {"used": 0, "total": 0},
            }
        
        stats = DashboardStats(
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
        
        # Build settings dict
        settings_dict = {
            "theme": settings.theme,
            "default_view": settings.default_view,
            "show_system_status": settings.show_system_status,
            "font_scale": settings.font_scale,
            "data_preferences": settings.data_preferences,
            "change_permission_mode": getattr(settings, "change_permission_mode", "ask_when_unsure"),
            "continuity_mode": getattr(settings, "continuity_mode", "full"),
            "risk_appetite": getattr(settings, "risk_appetite", "balanced"),
        }
        
        return FullDataSnapshot(
            tasks=tasks,
            projects=projects,
            stats=stats,
            recent_operations=recent_operations,
            settings=settings_dict,
            personas=list(PERSONAS),
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        logger.error(f"Failed to get full data snapshot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
