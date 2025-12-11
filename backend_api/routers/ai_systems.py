"""Routers for AI OS orchestration and Advanced AI engine features."""

from __future__ import annotations

from datetime import datetime, timedelta
import random
import uuid
from typing import List, Optional, Dict, Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

router = APIRouter()

# --- Shared helpers -----------------------------------------------------------------


def _utc_now() -> datetime:
    return datetime.utcnow()


def _iso(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    return dt.isoformat() + "Z"


# --- AI OS state --------------------------------------------------------------------


class WorkflowInstance(BaseModel):
    """Represents a running orchestration workflow."""

    id: str
    name: str
    owner: str
    status: str
    progress: int = Field(ge=0, le=100)
    priority: str
    last_event: str
    eta_minutes: Optional[int] = None


class AIOSOrchestratorStatus(BaseModel):
    """High-level orchestrator status."""

    status: str
    version: str
    last_started: Optional[str] = None
    last_stopped: Optional[str] = None
    workflows_active: int = 0
    nodes_online: int = 0


class StorageStatus(BaseModel):
    """Storage utilization metrics."""

    documents_indexed: int
    vector_embeddings: int
    disk_used_gb: float
    disk_total_gb: float
    last_backup: Optional[str]


class AIOSNode(BaseModel):
    """Distributed AI node."""

    id: str
    location: str
    status: str
    load_percent: int


class AIOSStatus(BaseModel):
    """Combined payload for AI OS page."""

    orchestrator: AIOSOrchestratorStatus
    workflows: List[WorkflowInstance]
    storage: StorageStatus
    nodes: List[AIOSNode]


AI_OS_STATE: Dict[str, Any] = {
    "orchestrator": AIOSOrchestratorStatus(
        status="stopped",
        version="1.3.0-beta",
        last_started=None,
        last_stopped=None,
        workflows_active=0,
        nodes_online=2,
    ),
    "workflows": [],
    "storage": StorageStatus(
        documents_indexed=3425,
        vector_embeddings=128_000,
        disk_used_gb=42.5,
        disk_total_gb=256.0,
        last_backup=_iso(_utc_now() - timedelta(hours=6)),
    ),
    "nodes": [
        AIOSNode(id="edge-sfo-1", location="San Francisco, CA", status="online", load_percent=62),
        AIOSNode(id="edge-nyc-1", location="New York, NY", status="online", load_percent=54),
        AIOSNode(id="edge-lhr-1", location="London, UK", status="maintenance", load_percent=15),
    ],
}


WORKFLOW_LIBRARY = [
    ("Autonomous Research Sweep", "Aria"),
    ("Code Audit & Patch", "Sora"),
    ("Smart Prioritization", "AIC"),
    ("Security Recon", "AIC"),
    ("Knowledge Graph Refresh", "Aria"),
]


def _generate_workflows() -> List[WorkflowInstance]:
    """Return a randomized workflow list."""
    workflows: List[WorkflowInstance] = []
    for name, owner in random.sample(WORKFLOW_LIBRARY, k=min(3, len(WORKFLOW_LIBRARY))):
        status = random.choice(["running", "queued", "monitoring"])
        progress = 0 if status == "queued" else random.randint(10, 95)
        workflows.append(
            WorkflowInstance(
                id=str(uuid.uuid4()),
                name=name,
                owner=owner,
                status=status,
                progress=progress,
                priority=random.choice(["high", "medium", "low"]),
                last_event=_iso(_utc_now() - timedelta(minutes=random.randint(1, 25))),
                eta_minutes=random.randint(2, 20) if status == "running" else None,
            )
        )
    return workflows


def _current_aios_status() -> AIOSStatus:
    orchestrator: AIOSOrchestratorStatus = AI_OS_STATE["orchestrator"]
    workflows: List[WorkflowInstance] = AI_OS_STATE["workflows"]
    if orchestrator.status == "running" and not workflows:
        workflows = _generate_workflows()
        AI_OS_STATE["workflows"] = workflows
        orchestrator.workflows_active = len(
            [wf for wf in workflows if wf.status == "running"]
        )
    return AIOSStatus(
        orchestrator=orchestrator,
        workflows=workflows,
        storage=AI_OS_STATE["storage"],
        nodes=AI_OS_STATE["nodes"],
    )


class OrchestratorCommand(BaseModel):
    """Command payload for orchestrator actions."""

    action: Literal["start", "stop", "restart"]


@router.get("/os/status", response_model=AIOSStatus)
async def get_aios_status() -> AIOSStatus:
    """Return orchestrator + storage status."""
    return _current_aios_status()


@router.post("/os/orchestrator", response_model=AIOSStatus)
async def control_orchestrator(payload: OrchestratorCommand) -> AIOSStatus:
    """Start/stop/restart the orchestrator to mimic Tk buttons."""
    orchestrator: AIOSOrchestratorStatus = AI_OS_STATE["orchestrator"]
    now = _iso(_utc_now())

    if payload.action == "start":
        orchestrator.status = "running"
        orchestrator.last_started = now
        orchestrator.last_stopped = orchestrator.last_stopped or None
        AI_OS_STATE["workflows"] = _generate_workflows()
    elif payload.action == "stop":
        orchestrator.status = "stopped"
        orchestrator.last_stopped = now
        orchestrator.workflows_active = 0
        AI_OS_STATE["workflows"] = []
    elif payload.action == "restart":
        orchestrator.status = "running"
        orchestrator.last_started = now
        orchestrator.last_stopped = now
        AI_OS_STATE["workflows"] = _generate_workflows()
    else:  # pragma: no cover - validated in schema
        raise HTTPException(status_code=400, detail="Unsupported action")

    orchestrator.workflows_active = len(
        [wf for wf in AI_OS_STATE["workflows"] if wf.status == "running"]
    )
    return _current_aios_status()


class WorkflowRefreshRequest(BaseModel):
    """Optional request for forcing new workflows."""

    seed: Optional[int] = None


@router.post("/os/workflows/refresh", response_model=List[WorkflowInstance])
async def refresh_workflows(payload: WorkflowRefreshRequest | None = None) -> List[WorkflowInstance]:
    """Shuffle workflow list so the UI stays lively."""
    if payload and payload.seed is not None:
        random.seed(payload.seed)
    AI_OS_STATE["workflows"] = _generate_workflows()
    orchestrator: AIOSOrchestratorStatus = AI_OS_STATE["orchestrator"]
    orchestrator.workflows_active = len(
        [wf for wf in AI_OS_STATE["workflows"] if wf.status == "running"]
    )
    return AI_OS_STATE["workflows"]


# --- Advanced AI Engine state -------------------------------------------------------


class Capability(BaseModel):
    id: str
    label: str
    description: str
    enabled: bool = True


class AdvancedAIStatus(BaseModel):
    available: bool
    initialized: bool
    last_run: Optional[str]
    health: str
    capabilities: List[Capability]
    metrics: Dict[str, Any]


class AdvancedAIResult(BaseModel):
    title: str
    output: str
    timestamp: str
    metrics: Dict[str, Any]


ADVANCED_AI_STATE: Dict[str, Any] = {
    "available": True,
    "initialized": False,
    "last_run": None,
    "health": "offline",
    "capabilities": [
        Capability(
            id="multimodal",
            label="Multi-modal Understanding",
            description="Understands text, images, audio, and structured data",
        ),
        Capability(
            id="predictive",
            label="Predictive Analytics",
            description="Forecast trends and project completion risk",
        ),
        Capability(
            id="autonomous",
            label="Autonomous Decisioning",
            description="Plans, executes, and optimizes workflows",
        ),
        Capability(
            id="insights",
            label="Real-time Insights",
            description="Streams anomalies, deltas, and KPIs",
        ),
    ],
}


def _ai_metrics() -> Dict[str, Any]:
    return {
        "latency_ms": random.randint(120, 380),
        "tokens_used": random.randint(1500, 3200),
        "confidence": round(random.uniform(0.75, 0.98), 2),
    }


@router.get("/engine/status", response_model=AdvancedAIStatus)
async def get_advanced_ai_status() -> AdvancedAIStatus:
    """Return capability inventory and health."""
    return AdvancedAIStatus(
        available=ADVANCED_AI_STATE["available"],
        initialized=ADVANCED_AI_STATE["initialized"],
        last_run=ADVANCED_AI_STATE.get("last_run"),
        health="online" if ADVANCED_AI_STATE["initialized"] else "offline",
        capabilities=ADVANCED_AI_STATE["capabilities"],
        metrics={
            "requests_today": random.randint(12, 42),
            "insights_generated": random.randint(5, 18),
            "autonomy_level": random.choice(["human-in-the-loop", "semi-autonomous", "autonomous"]),
        },
    )


class AdvancedAICommand(BaseModel):
    """Request payload for running the engine."""

    mode: str = Field(
        pattern="^(initialize|process_request|generate_insights|optimize)$"
    )


@router.post("/engine/run", response_model=AdvancedAIResult)
async def run_advanced_ai(payload: AdvancedAICommand) -> AdvancedAIResult:
    """Simulate the buttons from the Tkinter tab with structured output."""
    now = _iso(_utc_now())
    mode = payload.mode
    title_map = {
        "initialize": "Advanced AI Engine Initialized",
        "process_request": "AI Request Processed",
        "generate_insights": "Real-time Insights Generated",
        "optimize": "Autonomous Optimization Complete",
    }
    paragraphs = {
        "initialize": (
            "Capabilities loaded: multimodal processor, predictive analytics, cognitive automation, "
            "knowledge graph reasoning, and anomaly detection."
        ),
        "process_request": (
            "Request routed through multi-agent planner, fused with knowledge graph context, and "
            "validated against current guardrails."
        ),
        "generate_insights": (
            "Top findings include a 15% spike in system latency, three security anomalies, and two "
            "high-priority opportunities in the sales pipeline."
        ),
        "optimize": (
            "Optimization plan executed with closed-loop monitoring. Recommended actions dispatched to "
            "AI Ops queue and documentation refreshed."
        ),
    }

    if mode == "initialize":
        ADVANCED_AI_STATE["initialized"] = True
    ADVANCED_AI_STATE["last_run"] = now

    return AdvancedAIResult(
        title=title_map[mode],
        output=paragraphs[mode],
        timestamp=now,
        metrics=_ai_metrics(),
    )
