"""Auto-Fix & self-healing API (Spec §8.13, §11.8)."""
from __future__ import annotations

from datetime import datetime, timedelta
import random
import uuid
from typing import Dict, List, Literal, Optional, Union

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class AutoFixConfig(BaseModel):
    enabled: bool = True
    auto_apply_threshold: float = 0.9
    scan_interval_seconds: int = 3600
    target_directories: List[str] = Field(default_factory=list)
    issue_types: List[str] = Field(default_factory=lambda: ["error", "warning", "lint", "security", "performance"])


class AutoFixIssue(BaseModel):
    id: str
    file_path: str
    line_number: Optional[int] = None
    issue_type: Literal["error", "warning", "lint", "security", "performance"]
    description: str
    severity: Literal["critical", "error", "warning", "info"]
    detected_at: str
    status: Literal["pending", "analyzing", "fixing", "applied", "failed", "skipped"] = "pending"
    ai_analysis: Optional[str] = None
    proposed_fix: Optional[str] = None
    confidence: float = 0.9


class AutoFixReport(BaseModel):
    id: str
    started_at: str
    completed_at: Optional[str]
    status: Literal["running", "completed", "failed"]
    issues_detected: int
    issues_fixed: int
    issues_skipped: int
    summary: str


_AUTOFIX_STATUS: Dict[str, Optional[Union[str, bool]]] = {
    "enabled": True,
    "last_scan": (datetime.utcnow() - timedelta(minutes=45)).isoformat() + "Z",
}
_AUTOFIX_CONFIG = AutoFixConfig(
    target_directories=["frontend/", "backend_api/", "assistant_core/"],
)
_AUTOFIX_ISSUES: Dict[str, AutoFixIssue] = {}
_AUTOFIX_REPORTS: List[AutoFixReport] = []


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _seed_demo_issues() -> None:
    if _AUTOFIX_ISSUES:
        return
    examples = [
        AutoFixIssue(
            id="issue-1",
            file_path="frontend/src/pages/Dashboard.tsx",
            line_number=142,
            issue_type="lint",
            description="Missing dependency in useEffect dependency array",
            severity="warning",
            detected_at=_timestamp(),
            status="pending",
            ai_analysis="The hook references `settings` but not listed in dependency array.",
            proposed_fix="Add `settings` to the dependency array",
            confidence=0.92,
        ),
        AutoFixIssue(
            id="issue-2",
            file_path="backend_api/routers/projects.py",
            line_number=87,
            issue_type="security",
            description="Potential SQL injection vulnerability in dynamic query",
            severity="critical",
            detected_at=_timestamp(),
            status="pending",
            ai_analysis="User input interpolated into SQL; use parameter binding.",
            proposed_fix="Replace f-strings with SQLAlchemy bind parameters",
            confidence=0.98,
        ),
        AutoFixIssue(
            id="issue-3",
            file_path="assistant_core/automation_orchestrator.py",
            line_number=234,
            issue_type="error",
            description="Unhandled exception in async task runner",
            severity="error",
            detected_at=_timestamp(),
            status="analyzing",
            ai_analysis="Async function lacks exception handling",
            proposed_fix="Wrap await call in try/except with structured logging",
            confidence=0.85,
        ),
    ]
    for issue in examples:
        _AUTOFIX_ISSUES[issue.id] = issue
    _AUTOFIX_REPORTS.append(
        AutoFixReport(
            id="report-1",
            started_at=(datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
            completed_at=(datetime.utcnow() - timedelta(days=1, minutes=-5)).isoformat() + "Z",
            status="completed",
            issues_detected=12,
            issues_fixed=8,
            issues_skipped=4,
            summary="Fixed 8 lint issues and 2 performance regressions across 15 files.",
        )
    )


_seed_demo_issues()


@router.get("/status")
async def autofix_status() -> Dict[str, Optional[Union[str, bool]]]:
    """Return Auto-Fix status block."""

    return _AUTOFIX_STATUS


@router.get("/config", response_model=AutoFixConfig)
async def autofix_config() -> AutoFixConfig:
    return _AUTOFIX_CONFIG


class AutoFixConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    auto_apply_threshold: Optional[float] = None
    scan_interval_seconds: Optional[int] = None
    target_directories: Optional[List[str]] = None
    issue_types: Optional[List[str]] = None


@router.put("/config", response_model=AutoFixConfig)
async def update_autofix_config(payload: AutoFixConfigUpdate) -> AutoFixConfig:
    global _AUTOFIX_CONFIG  # noqa: PLW0603
    data = _AUTOFIX_CONFIG.model_dump()
    for field, value in payload.model_dump(exclude_unset=True).items():
        data[field] = value
    _AUTOFIX_CONFIG = AutoFixConfig(**data)
    if payload.enabled is not None:
        _AUTOFIX_STATUS["enabled"] = payload.enabled
    return _AUTOFIX_CONFIG


@router.get("/issues", response_model=List[AutoFixIssue])
async def list_autofix_issues(status: Optional[str] = None) -> List[AutoFixIssue]:
    issues = list(_AUTOFIX_ISSUES.values())
    if status:
        issues = [issue for issue in issues if issue.status == status]
    return issues


def _touch_last_scan() -> None:
    _AUTOFIX_STATUS["last_scan"] = _timestamp()


@router.post("/scan")
async def start_autofix_scan() -> Dict[str, str]:
    """Simulate a scan by generating 1-2 additional issues."""

    _touch_last_scan()
    new_issue = AutoFixIssue(
        id=f"issue-{len(_AUTOFIX_ISSUES) + 1}",
        file_path="frontend/src/components/Layout.tsx",
        line_number=random.randint(30, 250),
        issue_type=random.choice(["lint", "performance", "warning"]),
        description="Layout re-render detected without memoization",
        severity=random.choice(["warning", "error"]),
        detected_at=_timestamp(),
        status="pending",
        ai_analysis="Component recalculates nav tree on each render. Use memoization.",
        proposed_fix="Memoize navSections with useMemo + key inputs",
        confidence=round(random.uniform(0.8, 0.97), 2),
    )
    _AUTOFIX_ISSUES[new_issue.id] = new_issue
    report = AutoFixReport(
        id=str(uuid.uuid4()),
        started_at=_AUTOFIX_STATUS["last_scan"],
        completed_at=None,
        status="running",
        issues_detected=len(_AUTOFIX_ISSUES),
        issues_fixed=len([i for i in _AUTOFIX_ISSUES.values() if i.status == "applied"]),
        issues_skipped=len([i for i in _AUTOFIX_ISSUES.values() if i.status == "skipped"]),
        summary="Scan running",
    )
    _AUTOFIX_REPORTS.insert(0, report)
    return {"status": "running", "report_id": report.id}


def _update_report_counts() -> None:
    if not _AUTOFIX_REPORTS:
        return
    report = _AUTOFIX_REPORTS[0]
    report.issues_detected = len(_AUTOFIX_ISSUES)
    report.issues_fixed = len([i for i in _AUTOFIX_ISSUES.values() if i.status == "applied"])
    report.issues_skipped = len([i for i in _AUTOFIX_ISSUES.values() if i.status == "skipped"])
    if report.status == "running" and report.issues_fixed + report.issues_skipped >= report.issues_detected:
        report.status = "completed"
        report.completed_at = _timestamp()
        report.summary = "Auto-Fix run completed"


def _mutate_issue(issue_id: str, next_status: Literal["applied", "skipped", "failed"]) -> AutoFixIssue:
    issue = _AUTOFIX_ISSUES.get(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.status = next_status
    if next_status == "applied":
        issue.ai_analysis = issue.ai_analysis or "Applied automatically"
        issue.proposed_fix = issue.proposed_fix or "Patched"
    _update_report_counts()
    return issue


@router.post("/issues/{issue_id}/apply", response_model=AutoFixIssue)
async def apply_autofix(issue_id: str) -> AutoFixIssue:
    issue = _mutate_issue(issue_id, "applied")
    return issue


@router.post("/issues/{issue_id}/skip", response_model=AutoFixIssue)
async def skip_autofix(issue_id: str) -> AutoFixIssue:
    issue = _mutate_issue(issue_id, "skipped")
    return issue


@router.get("/reports", response_model=List[AutoFixReport])
async def list_reports(limit: int = 10) -> List[AutoFixReport]:
    return _AUTOFIX_REPORTS[:limit]
