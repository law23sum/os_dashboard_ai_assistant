"""Audit & compliance router exposing governance data for the new UI."""

from __future__ import annotations

from datetime import datetime, timedelta
import random
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import load_state
from backend_api.db import db_session

router = APIRouter()


def get_state():
    with db_session() as conn:
        return load_state(conn)


class ComplianceMetric(BaseModel):
    framework: str
    score: int
    issues: int
    status: str
    last_checked: str


class AuditLogEntry(BaseModel):
    id: str
    event: str
    resource: str
    user: str
    level: str
    timestamp: str
    status: str


class AuditSummary(BaseModel):
    risk_score: int
    controls_in_place: int
    controls_healthy: int
    outstanding_actions: int
    last_check: str
    metrics: List[ComplianceMetric]


class AuditCheckResponse(BaseModel):
    started_at: str
    completed_at: str
    issues_found: int
    notes: str


@router.get("/summary", response_model=AuditSummary)
async def audit_summary(state=Depends(get_state)) -> AuditSummary:
    """Return compliance dashboard style stats."""
    tasks = state.tasks or []
    completed = len([t for t in tasks if getattr(t, "status", "").lower() == "done"])
    outstanding_actions = max(0, len(tasks) - completed)

    frameworks = [
        ("SOC 2", "soc2"),
        ("ISO 27001", "iso27001"),
        ("GDPR", "gdpr"),
        ("HIPAA", "hipaa"),
    ]
    metrics = []
    for name, key in frameworks:
        base = 82 + random.randint(-5, 5)
        issues = random.randint(0, 3)
        metrics.append(
            ComplianceMetric(
                framework=name,
                score=min(100, max(60, base - issues * 3)),
                issues=issues,
                status="healthy" if issues == 0 else "investigating",
                last_checked=(datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat() + "Z",
            )
        )

    last_check = max(m.last_checked for m in metrics)
    controls = 24
    healthy = controls - sum(m.issues for m in metrics)
    risk_score = max(5, 100 - (healthy * 3))

    return AuditSummary(
        risk_score=risk_score,
        controls_in_place=controls,
        controls_healthy=max(0, healthy),
        outstanding_actions=outstanding_actions,
        last_check=last_check,
        metrics=metrics,
    )


@router.get("/logs", response_model=List[AuditLogEntry])
async def audit_logs(limit: int = 20, state=Depends(get_state)) -> List[AuditLogEntry]:
    """Return synthetic audit log events derived from tasks/projects."""
    logs: List[AuditLogEntry] = []
    now = datetime.utcnow()

    for idx, task in enumerate(state.tasks or []):
        if len(logs) >= limit:
            break
        logs.append(
            AuditLogEntry(
                id=f"task-{task.id}",
                event="Task Updated",
                resource=task.title,
                user=getattr(task, "owner", "system"),
                level="info",
                timestamp=(now - timedelta(minutes=idx * 7)).isoformat() + "Z",
                status=getattr(task, "status", "unknown"),
            )
        )

    if len(logs) < limit:
        for idx, project in enumerate(state.projects or []):
            if len(logs) >= limit:
                break
            logs.append(
                AuditLogEntry(
                    id=f"project-{idx}",
                    event="Project Accessed",
                    resource=project.name,
                    user="compliance-bot",
                    level="info",
                    timestamp=(now - timedelta(minutes=idx * 11 + 5)).isoformat() + "Z",
                    status=project.status,
                )
            )

    return logs[:limit]


@router.post("/checks/run", response_model=AuditCheckResponse)
async def run_compliance_check() -> AuditCheckResponse:
    """Simulate a compliance run triggered from the UI."""
    started = datetime.utcnow() - timedelta(minutes=1)
    issues = random.randint(0, 4)
    note = (
        "All controls verified."
        if issues == 0
        else f"{issues} control gap(s) detected. See compliance queue."
    )
    return AuditCheckResponse(
        started_at=started.isoformat() + "Z",
        completed_at=datetime.utcnow().isoformat() + "Z",
        issues_found=issues,
        notes=note,
    )
