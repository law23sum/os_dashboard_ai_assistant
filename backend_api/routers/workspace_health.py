"""Workspace Health Monitoring API Router.

Provides endpoints for monitoring workspace health, project status,
TODO tracking, and automation orchestration per Technical Spec V6:
- Section 7.10: Operator & SRE Workspace
- Section 8.16: Health & Drift Monitoring
- Section 11.9: Dashboards, Alerting & On-Call Operations

Endpoints:
    GET  /api/workspace/health          - Full workspace health report
    GET  /api/workspace/projects        - List all projects with status
    GET  /api/workspace/todos           - Aggregated TODO items
    GET  /api/workspace/metrics         - Health metrics summary
    POST /api/workspace/scan            - Trigger new workspace scan
    POST /api/workspace/autofix/{name}  - Trigger auto-fix for project
    GET  /api/workspace/continuation    - Get pending continuation payload
    POST /api/workspace/continue        - Trigger continuation daemon
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

# Determine workspace root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

router = APIRouter(prefix="/workspace", tags=["Workspace Health"])


# ============================================================================
# Pydantic Models
# ============================================================================

class TodoItemResponse(BaseModel):
    """A single TODO item."""
    id: str
    content: str
    source_file: str
    line_number: int
    priority: str = "normal"
    status: str = "pending"
    category: str = "general"


class ProjectHealthResponse(BaseModel):
    """Health status for a single project."""
    path: str
    name: str
    has_git: bool = True
    has_autofix_script: bool = False
    has_tests: bool = False
    has_manifest: bool = False
    todos: List[TodoItemResponse] = Field(default_factory=list)
    autofix_status: str = "not_run"
    test_status: str = "not_run"
    lint_status: str = "not_run"
    last_checked: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    health_score: int = 50


class WorkspaceSummary(BaseModel):
    """Summary statistics for workspace health."""
    total_projects: int = 0
    healthy_projects: int = 0
    warning_projects: int = 0
    critical_projects: int = 0
    total_todos: int = 0
    average_health: int = 50


class WorkspaceHealthResponse(BaseModel):
    """Complete workspace health report."""
    root: str
    scan_timestamp: str
    summary: WorkspaceSummary
    projects: List[ProjectHealthResponse] = Field(default_factory=list)


class ScanRequest(BaseModel):
    """Request to trigger a workspace scan."""
    root: Optional[str] = None
    max_depth: int = 4
    execute: bool = False
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)


class AutofixRequest(BaseModel):
    """Request to trigger auto-fix for a project."""
    project_path: str
    timeout_seconds: int = 120


class ContinuationPayload(BaseModel):
    """Payload for continuation between AI sessions."""
    timestamp: str
    workspace_root: str
    continuation_required: bool = False
    priority_todos: List[Dict[str, Any]] = Field(default_factory=list)
    failed_projects: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_actions: List[Dict[str, Any]] = Field(default_factory=list)
    context_for_next_session: str = ""


class ContinuationTriggerRequest(BaseModel):
    """Request to trigger continuation daemon."""
    method: str = "manual"  # manual, cursor, vscode, terminal, api


class MetricsResponse(BaseModel):
    """Workspace metrics for dashboards."""
    timestamp: str
    workspace_root: str
    projects: Dict[str, Any]
    todos: Dict[str, Any]
    automation: Dict[str, Any]
    health: Dict[str, Any]


# ============================================================================
# State Management (in-memory cache)
# ============================================================================

_workspace_cache: Dict[str, Any] = {
    "last_scan": None,
    "report": None,
    "scan_in_progress": False,
}


# ============================================================================
# Helper Functions
# ============================================================================

async def run_orchestrator(
    root: Path,
    max_depth: int = 4,
    execute: bool = False,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Run the unified project orchestrator and return results."""
    script_path = REPO_ROOT / "scripts" / "unified_project_orchestrator.py"
    
    if not script_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Unified project orchestrator script not found"
        )
    
    cmd = [
        sys.executable,
        str(script_path),
        "--root", str(root),
        "--max-depth", str(max_depth),
        "--quiet",
    ]
    
    if execute:
        cmd.append("--execute")
    
    if include:
        for pattern in include:
            cmd.extend(["--include", pattern])
    
    if exclude:
        for pattern in exclude:
            cmd.extend(["--exclude", pattern])
    
    # Run asynchronously
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=REPO_ROOT,
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator failed: {stderr.decode()}"
        )
    
    try:
        return json.loads(stdout.decode())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse orchestrator output"
        )


def load_continuation_payload() -> Optional[ContinuationPayload]:
    """Load the continuation payload from file."""
    continuation_file = REPO_ROOT / ".osdash-continuation.json"
    
    if not continuation_file.exists():
        return None
    
    try:
        data = json.loads(continuation_file.read_text())
        return ContinuationPayload(**data)
    except Exception:
        return None


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/health", response_model=WorkspaceHealthResponse)
async def get_workspace_health(
    refresh: bool = Query(False, description="Force refresh of cached data"),
) -> WorkspaceHealthResponse:
    """Get the full workspace health report.
    
    Returns cached data unless refresh=true is specified.
    """
    global _workspace_cache
    
    # Return cached data if available and refresh not requested
    if not refresh and _workspace_cache["report"]:
        return WorkspaceHealthResponse(**_workspace_cache["report"])
    
    # Run orchestrator for fresh data
    result = await run_orchestrator(REPO_ROOT, execute=False)
    
    # Cache the result
    _workspace_cache["report"] = result
    _workspace_cache["last_scan"] = datetime.now(timezone.utc).isoformat()
    
    return WorkspaceHealthResponse(**result)


@router.get("/projects", response_model=List[ProjectHealthResponse])
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status: healthy, warning, critical"),
    has_todos: Optional[bool] = Query(None, description="Filter by TODO presence"),
) -> List[ProjectHealthResponse]:
    """List all projects with their health status."""
    # Get or refresh workspace data
    health = await get_workspace_health(refresh=False)
    
    projects = health.projects
    
    # Apply filters
    if status:
        if status == "healthy":
            projects = [p for p in projects if p.health_score >= 70]
        elif status == "warning":
            projects = [p for p in projects if 40 <= p.health_score < 70]
        elif status == "critical":
            projects = [p for p in projects if p.health_score < 40]
    
    if has_todos is not None:
        if has_todos:
            projects = [p for p in projects if len(p.todos) > 0]
        else:
            projects = [p for p in projects if len(p.todos) == 0]
    
    return projects


@router.get("/todos", response_model=List[TodoItemResponse])
async def list_todos(
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, description="Maximum items to return"),
) -> List[TodoItemResponse]:
    """Get aggregated TODO items from all projects."""
    health = await get_workspace_health(refresh=False)
    
    # Collect all TODOs
    todos = []
    for project in health.projects:
        todos.extend(project.todos)
    
    # Apply filters
    if priority:
        todos = [t for t in todos if t.priority == priority]
    
    if status:
        todos = [t for t in todos if t.status == status]
    
    if category:
        todos = [t for t in todos if t.category == category]
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
    todos.sort(key=lambda t: priority_order.get(t.priority, 2))
    
    return todos[:limit]


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Get workspace metrics for dashboards."""
    health = await get_workspace_health(refresh=False)
    
    # Calculate metrics
    total_todos = sum(len(p.todos) for p in health.projects)
    pending_todos = sum(
        len([t for t in p.todos if t.status == "pending"])
        for p in health.projects
    )
    critical_todos = sum(
        len([t for t in p.todos if t.priority == "critical"])
        for p in health.projects
    )
    
    autofix_passed = sum(1 for p in health.projects if p.autofix_status == "passed")
    autofix_failed = sum(1 for p in health.projects if p.autofix_status == "failed")
    tests_passed = sum(1 for p in health.projects if p.test_status == "passed")
    tests_failed = sum(1 for p in health.projects if p.test_status == "failed")
    
    return MetricsResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        workspace_root=health.root,
        projects={
            "total": health.summary.total_projects,
            "healthy": health.summary.healthy_projects,
            "warning": health.summary.warning_projects,
            "critical": health.summary.critical_projects,
            "with_autofix": sum(1 for p in health.projects if p.has_autofix_script),
            "with_tests": sum(1 for p in health.projects if p.has_tests),
            "with_manifest": sum(1 for p in health.projects if p.has_manifest),
        },
        todos={
            "total": total_todos,
            "pending": pending_todos,
            "critical": critical_todos,
            "by_category": _count_by_field(health.projects, "category"),
            "by_priority": _count_by_field(health.projects, "priority"),
        },
        automation={
            "autofix_passed": autofix_passed,
            "autofix_failed": autofix_failed,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
        },
        health={
            "average_score": health.summary.average_health,
            "min_score": min((p.health_score for p in health.projects), default=0),
            "max_score": max((p.health_score for p in health.projects), default=100),
        },
    )


def _count_by_field(projects: List[ProjectHealthResponse], field: str) -> Dict[str, int]:
    """Count TODOs by a specific field."""
    counts: Dict[str, int] = {}
    for project in projects:
        for todo in project.todos:
            value = getattr(todo, field, "unknown")
            counts[value] = counts.get(value, 0) + 1
    return counts


@router.post("/scan")
async def trigger_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """Trigger a new workspace scan."""
    global _workspace_cache
    
    if _workspace_cache["scan_in_progress"]:
        raise HTTPException(
            status_code=409,
            detail="A scan is already in progress"
        )
    
    root = Path(request.root) if request.root else REPO_ROOT
    
    async def run_scan():
        global _workspace_cache
        _workspace_cache["scan_in_progress"] = True
        try:
            result = await run_orchestrator(
                root=root,
                max_depth=request.max_depth,
                execute=request.execute,
                include=request.include_patterns,
                exclude=request.exclude_patterns,
            )
            _workspace_cache["report"] = result
            _workspace_cache["last_scan"] = datetime.now(timezone.utc).isoformat()
        finally:
            _workspace_cache["scan_in_progress"] = False
    
    background_tasks.add_task(run_scan)
    
    return {
        "status": "scan_started",
        "message": "Workspace scan initiated in background",
        "root": str(root),
    }


@router.post("/autofix/{project_name}")
async def trigger_autofix(
    project_name: str,
    request: AutofixRequest,
) -> Dict[str, Any]:
    """Trigger auto-fix for a specific project."""
    project_path = Path(request.project_path).expanduser().resolve()
    
    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Project path not found: {project_path}"
        )
    
    autofix_script = project_path / "scripts" / "ai_auto_fix.py"
    
    if not autofix_script.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Auto-fix script not found in project: {project_name}"
        )
    
    # Run auto-fix
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(autofix_script),
            "--logs-only",
            "--no-daemon",
            "--verify-seconds", "10",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_path,
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=request.timeout_seconds,
        )
        
        return {
            "status": "completed" if process.returncode == 0 else "failed",
            "project": project_name,
            "return_code": process.returncode,
            "stdout": stdout.decode()[-1000:],  # Last 1000 chars
            "stderr": stderr.decode()[-500:] if stderr else "",
        }
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Auto-fix timed out after {request.timeout_seconds} seconds"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Auto-fix failed: {str(e)}"
        )


@router.get("/continuation", response_model=Optional[ContinuationPayload])
async def get_continuation_payload() -> Optional[ContinuationPayload]:
    """Get the pending continuation payload if available."""
    return load_continuation_payload()


@router.post("/continue")
async def trigger_continuation(
    request: ContinuationTriggerRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """Trigger the continuation daemon."""
    daemon_script = REPO_ROOT / "scripts" / "codex_continuation_daemon.py"
    
    if not daemon_script.exists():
        raise HTTPException(
            status_code=500,
            detail="Continuation daemon script not found"
        )
    
    payload = load_continuation_payload()
    
    if not payload or not payload.continuation_required:
        return {
            "status": "no_continuation_needed",
            "message": "No pending continuation payload found",
        }
    
    async def run_daemon():
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(daemon_script),
            "--once",
            "--method", request.method,
            "--workspace", str(REPO_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
    
    background_tasks.add_task(run_daemon)
    
    return {
        "status": "continuation_triggered",
        "method": request.method,
        "payload_timestamp": payload.timestamp,
        "priority_todos": len(payload.priority_todos),
        "failed_projects": len(payload.failed_projects),
    }


@router.get("/status")
async def get_workspace_status() -> Dict[str, Any]:
    """Get current workspace monitoring status."""
    global _workspace_cache
    
    continuation = load_continuation_payload()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workspace_root": str(REPO_ROOT),
        "last_scan": _workspace_cache["last_scan"],
        "scan_in_progress": _workspace_cache["scan_in_progress"],
        "has_cached_report": _workspace_cache["report"] is not None,
        "continuation_pending": continuation is not None and continuation.continuation_required,
        "orchestrator_available": (REPO_ROOT / "scripts" / "unified_project_orchestrator.py").exists(),
        "daemon_available": (REPO_ROOT / "scripts" / "codex_continuation_daemon.py").exists(),
    }
