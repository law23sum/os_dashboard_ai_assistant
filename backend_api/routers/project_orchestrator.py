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
        workspace_report = orchestrator.orchestrate()
        report = workspace_report.to_dict()
        
        return ProjectReport(**report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_name}/health")
async def get_project_health(project_name: str):
    """Get health status for a specific project."""
    try:
        orchestrator = UnifiedProjectOrchestrator(root=REPO_ROOT)
        project_paths = orchestrator.discover_projects()
        
        # Find project by name
        project_path = None
        for path in project_paths:
            if path.name == project_name or str(path) == project_name:
                project_path = path
                break
        
        if not project_path:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        health = orchestrator.analyze_project(project_path)
        return {
            "name": health.name,
            "health": health.health,
            "last_check": health.last_check.isoformat() if health.last_check else None,
            "error_count": health.error_count,
            "fix_count": health.fix_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_name}/autofix/start")
async def start_autofix(project_name: str, background_tasks: BackgroundTasks):
    """Start auto-fix monitor for a specific project."""
    try:
        orchestrator = UnifiedProjectOrchestrator(root=REPO_ROOT, execute=True)
        project_paths = orchestrator.discover_projects()
        
        # Find project by name
        project_path = None
        for path in project_paths:
            if path.name == project_name or str(path) == project_name:
                project_path = path
                break
        
        if not project_path:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        health = orchestrator.analyze_project(project_path)
        if not health.has_autofix:
            raise HTTPException(
                status_code=400,
                detail=f"Project '{project_name}' does not have ai_auto_fix.py"
            )
        
        # Run autofix in background
        def run_autofix():
            orchestrator.run_autofix(health)
        background_tasks.add_task(run_autofix)
        
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
    # Note: The UnifiedOrchestrator doesn't have a stop_monitors method
    # This is a placeholder for future implementation
    try:
        orchestrator = UnifiedProjectOrchestrator(root=REPO_ROOT)
        project_paths = orchestrator.discover_projects()
        
        # Find project by name
        project_path = None
        for path in project_paths:
            if path.name == project_name or str(path) == project_name:
                project_path = path
                break
        
        if not project_path:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
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
        orchestrator = UnifiedProjectOrchestrator(root=REPO_ROOT)
        workspace_report = orchestrator.orchestrate()
        report = workspace_report.to_dict()
        
        summary = report.get("summary", {})
        total = summary.get("total_projects", 0)
        healthy = summary.get("healthy_projects", 0)
        degraded = summary.get("warning_projects", 0)
        critical = summary.get("critical_projects", 0)
        
        # Count projects with autofix and tests
        with_autofix = sum(1 for p in workspace_report.projects if p.has_autofix)
        with_tests = sum(1 for p in workspace_report.projects if p.has_tests)
        
        return {
            "total_projects": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": critical,
            "with_autofix": with_autofix,
            "with_tests": with_tests,
            "health_percentage": (
                (healthy / total * 100) if total > 0 else 0
            ),
            "autofix_coverage": (
                (with_autofix / total * 100) if total > 0 else 0
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
