from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from assistant_hub.ui.terminal import harness

router = APIRouter()


class WorkspaceCheckRequest(BaseModel):
    root: Optional[str] = Field(None, description="Workspace root to scan for repos")
    max_depth: int = Field(2, description="Directory depth to scan for git repos")
    categories: List[str] = Field(default_factory=lambda: ["lint", "test"], description="Check categories to run")
    autofix: bool = Field(False, description="Trigger autofix script when available")
    dry_run: bool = Field(True, description="Plan commands without executing them")


@router.get("/workspace/scan")
async def workspace_scan(root: str | None = Query(None), max_depth: int = Query(2)) -> dict:
    """Discover git repos and return inferred command profiles."""

    base = Path(root) if root else harness.REPO_ROOT
    return harness.scan_summary(base, max_depth=max_depth)


@router.get("/workspace/doctor")
async def workspace_doctor(root: str | None = Query(None)) -> dict:
    """Lightweight environment diagnostics for the workspace."""

    base = Path(root) if root else harness.REPO_ROOT
    return harness.doctor(base)


@router.post("/workspace/checks")
async def workspace_checks(payload: WorkspaceCheckRequest) -> dict:
    """Run (or dry-run) standardized workspace checks and return a consolidated report."""

    base = Path(payload.root) if payload.root else harness.REPO_ROOT
    return harness.run_workspace_checks(
        base,
        payload.categories,
        max_depth=payload.max_depth,
        autofix=payload.autofix,
        dry_run=payload.dry_run,
    )
