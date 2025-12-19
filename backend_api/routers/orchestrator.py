"""Master Orchestrator API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATUS_REPORT_PATH = REPO_ROOT / "logs" / "status_report.json"


@router.get("/status")
async def get_orchestrator_status() -> Dict[str, Any]:
    """
    Get the current status of the Master Orchestrator.
    
    Returns:
        JSON status report containing:
        - timestamp: When the report was generated
        - root: Workspace root path
        - total_projects: Number of discovered projects
        - projects: Dictionary of project information
        - todos: TODO statistics
        - monitors: Monitor status counts
    """
    if not STATUS_REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Master Orchestrator status report not found. "
                "Ensure os_dashboard_ai_assistant.py is running."
            )
        )
    
    try:
        with STATUS_REPORT_PATH.open("r", encoding="utf-8") as f:
            status = json.load(f)
        return status
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse status report: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading status report: {e}"
        )


@router.get("/projects")
async def get_projects() -> Dict[str, Dict[str, Any]]:
    """Get all discovered projects."""
    if not STATUS_REPORT_PATH.exists():
        return {}
    
    try:
        with STATUS_REPORT_PATH.open("r", encoding="utf-8") as f:
            status = json.load(f)
        return status.get("projects", {})
    except Exception:
        return {}


@router.get("/projects/{project_name}")
async def get_project(project_name: str) -> Dict[str, Any]:
    """Get information about a specific project."""
    if not STATUS_REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Status report not found"
        )
    
    try:
        with STATUS_REPORT_PATH.open("r", encoding="utf-8") as f:
            status = json.load(f)
        
        projects = status.get("projects", {})
        if project_name not in projects:
            raise HTTPException(
                status_code=404,
                detail=f"Project '{project_name}' not found"
            )
        
        return projects[project_name]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading project info: {e}"
        )


@router.get("/todos")
async def get_todos() -> Dict[str, Any]:
    """Get TODO statistics."""
    if not STATUS_REPORT_PATH.exists():
        return {
            "total": 0,
            "by_priority": {
                "critical": 0,
                "high": 0,
                "normal": 0,
                "low": 0,
            },
            "completed": 0,
        }
    
    try:
        with STATUS_REPORT_PATH.open("r", encoding="utf-8") as f:
            status = json.load(f)
        return status.get("todos", {})
    except Exception:
        return {
            "total": 0,
            "by_priority": {
                "critical": 0,
                "high": 0,
                "normal": 0,
                "low": 0,
            },
            "completed": 0,
        }


@router.get("/monitors")
async def get_monitors() -> Dict[str, int]:
    """Get monitor status counts."""
    if not STATUS_REPORT_PATH.exists():
        return {
            "running": 0,
            "healthy": 0,
            "stopped": 0,
            "error": 0,
        }
    
    try:
        with STATUS_REPORT_PATH.open("r", encoding="utf-8") as f:
            status = json.load(f)
        return status.get("monitors", {})
    except Exception:
        return {
            "running": 0,
            "healthy": 0,
            "stopped": 0,
            "error": 0,
        }


@router.get("/logs/{project_name}")
async def get_project_logs(project_name: str, lines: int = 100) -> Dict[str, Any]:
    """
    Get recent log entries for a project's monitor.
    
    Args:
        project_name: Name of the project
        lines: Number of recent lines to return (default: 100)
    """
    log_file = REPO_ROOT / "logs" / f"{project_name}_monitor.log"
    
    if not log_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Log file for project '{project_name}' not found"
        )
    
    try:
        with log_file.open("r", encoding="utf-8") as f:
            all_lines = f.readlines()
        
        # Get the last N lines
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "project": project_name,
            "total_lines": len(all_lines),
            "returned_lines": len(recent_lines),
            "logs": [line.rstrip() for line in recent_lines],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading logs: {e}"
        )


@router.post("/spawn-codex")
async def spawn_codex(
    priority: Optional[str] = None,
    project: Optional[str] = None,
    max_sessions: int = 1,
) -> Dict[str, Any]:
    """
    Spawn codex sessions for pending TODOs.
    
    Args:
        priority: Filter by priority (low, normal, high, critical)
        project: Filter by project name
        max_sessions: Maximum number of sessions to spawn
    """
    import subprocess
    import sys
    
    codex_script = REPO_ROOT / "scripts" / "codex_spawner.py"
    
    if not codex_script.exists():
        raise HTTPException(
            status_code=404,
            detail="Codex spawner script not found"
        )
    
    cmd = [sys.executable, str(codex_script), f"--max-sessions={max_sessions}"]
    
    if priority:
        cmd.append(f"--priority={priority}")
    
    if project:
        cmd.append(f"--project={project}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output": result.stdout,
            "error": result.stderr,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Codex spawner timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error spawning codex: {e}"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the orchestrator.
    
    Returns basic information about orchestrator status.
    """
    orchestrator_running = STATUS_REPORT_PATH.exists()
    
    if orchestrator_running:
        try:
            with STATUS_REPORT_PATH.open("r", encoding="utf-8") as f:
                status = json.load(f)
            
            return {
                "status": "healthy",
                "orchestrator_running": True,
                "timestamp": status.get("timestamp"),
                "total_projects": status.get("total_projects", 0),
                "active_monitors": status.get("monitors", {}).get("running", 0) + status.get("monitors", {}).get("healthy", 0),
            }
        except Exception:
            pass
    
    return {
        "status": "not_running",
        "orchestrator_running": False,
        "message": "Master Orchestrator is not active",
    }
