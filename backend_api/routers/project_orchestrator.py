"""
Backend API router for unified project orchestrator.

Provides REST endpoints for:
- Discovering Git projects in the workspace
- Monitoring project health
- Managing auto-fix monitors
- Cross-project analytics
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys
import subprocess
import json
from datetime import datetime

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))

from scripts.unified_project_orchestrator import (
    UnifiedProjectOrchestrator,
    discover_git_repos,
    create_project_status,
    detect_project_capabilities,
)

router = APIRouter()

REPO_ROOT = parent_dir


class ProjectInfo(BaseModel):
    """Project information model."""
    name: str
    path: str
    health: str
    has_autofix: bool
    has_tests: bool
    language: str
    last_check: Optional[str] = None
    error_count: int = 0
    fix_count: int = 0
    metadata: Dict[str, Any] = {}


class ProjectDiscoveryRequest(BaseModel):
    """Request model for project discovery."""
    root: Optional[str] = None
    max_depth: int = 5


class ProjectReport(BaseModel):
    """Comprehensive project report."""
    timestamp: str
    total_projects: int
    projects: List[ProjectInfo]
    summary: Dict[str, int]


@router.get("/projects/discover", response_model=List[ProjectInfo])
async def discover_projects(
    root: Optional[str] = None,
    max_depth: int = 5,
):
    """Discover all Git projects in the workspace."""
    try:
        search_root = Path(root) if root else REPO_ROOT
        repos = discover_git_repos(search_root, max_depth)
        
        projects = []
        for repo_path in repos:
            status = create_project_status(repo_path)
            projects.append(ProjectInfo(
                name=status.name,
                path=str(status.path),
                health=status.health,
                has_autofix=status.has_autofix,
                has_tests=status.metadata.get("has_tests", False),
                language=status.metadata.get("language", "unknown"),
                last_check=status.last_check.isoformat() if status.last_check else None,
                error_count=status.error_count,
                fix_count=status.fix_count,
                metadata=status.metadata,
            ))
        
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/report", response_model=ProjectReport)
async def get_project_report(
    root: Optional[str] = None,
    max_depth: int = 5,
):
    """Get comprehensive report of all projects."""
    try:
        search_root = Path(root) if root else REPO_ROOT
        orchestrator = UnifiedProjectOrchestrator(root=search_root, max_depth=max_depth)
        orchestrator.discover_projects()
        report = orchestrator.generate_report()
        
        return ProjectReport(**report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_name}/health")
async def get_project_health(project_name: str):
    """Get health status for a specific project."""
    try:
        orchestrator = UnifiedProjectOrchestrator()
        orchestrator.discover_projects()
        
        if project_name not in orchestrator.discovered_projects:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        project = orchestrator.discovered_projects[project_name]
        return {
            "name": project.name,
            "health": project.health,
            "last_check": project.last_check.isoformat() if project.last_check else None,
            "error_count": project.error_count,
            "fix_count": project.fix_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_name}/autofix/start")
async def start_autofix(project_name: str, background_tasks: BackgroundTasks):
    """Start auto-fix monitor for a specific project."""
    try:
        orchestrator = UnifiedProjectOrchestrator(auto_fix=True)
        orchestrator.discover_projects()
        
        if project_name not in orchestrator.discovered_projects:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        project = orchestrator.discovered_projects[project_name]
        if not project.has_autofix:
            raise HTTPException(
                status_code=400,
                detail=f"Project '{project_name}' does not have ai_auto_fix.py"
            )
        
        # Start monitor in background
        background_tasks.add_task(orchestrator.start_monitors)
        
        return {
            "status": "started",
            "project": project_name,
            "message": f"Auto-fix monitor started for {project_name}",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_name}/autofix/stop")
async def stop_autofix(project_name: str):
    """Stop auto-fix monitor for a specific project."""
    try:
        orchestrator = UnifiedProjectOrchestrator()
        orchestrator.discover_projects()
        
        if project_name not in orchestrator.discovered_projects:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        orchestrator.stop_monitors()
        
        return {
            "status": "stopped",
            "project": project_name,
            "message": f"Auto-fix monitor stopped for {project_name}",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/analytics/summary")
async def get_analytics_summary():
    """Get cross-project analytics summary."""
    try:
        orchestrator = UnifiedProjectOrchestrator()
        orchestrator.discover_projects()
        report = orchestrator.generate_report()
        
        summary = report.get("summary", {})
        total = report.get("total_projects", 0)
        
        return {
            "total_projects": total,
            "healthy": summary.get("healthy", 0),
            "degraded": summary.get("degraded", 0),
            "unhealthy": summary.get("unhealthy", 0),
            "with_autofix": summary.get("with_autofix", 0),
            "with_tests": summary.get("with_tests", 0),
            "health_percentage": (
                (summary.get("healthy", 0) / total * 100) if total > 0 else 0
            ),
            "autofix_coverage": (
                (summary.get("with_autofix", 0) / total * 100) if total > 0 else 0
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
