"""Routers for AI OS orchestration and Advanced AI engine features."""

from __future__ import annotations

from datetime import datetime, timedelta
from collections import deque
import asyncio
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

from backend_api.db import db_session  # pylint: disable=wrong-import-position

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


# --- Cognitive reasoning / TRF console ------------------------------------
try:  # pragma: no cover - optional dependency
    from assistant_core.cognitive_framework import CognitiveFrameworkManager, PersonaType
except Exception:  # pragma: no cover - optional
    CognitiveFrameworkManager = None  # type: ignore
    PersonaType = None  # type: ignore

REASONING_MANAGER = CognitiveFrameworkManager() if CognitiveFrameworkManager else None  # type: ignore
REASONING_READY = False
REASONING_LOCK = asyncio.Lock()
RECENT_TRACES: deque[Dict[str, Any]] = deque(maxlen=20)


class ReasoningRequest(BaseModel):
    """Payload for TRF reasoning requests."""

    query: str
    persona: Optional[str] = Field(
        default="aic",
        description="Persona to run the reasoning request (aic, chris, aria, sora).",
    )


def _serialize_trace(trace: Any) -> Dict[str, Any]:
    """Convert a ReasoningTrace into JSON-serializable structure."""
    persona_label: Optional[str] = None
    if REASONING_MANAGER and getattr(trace, "persona_id", None):
        persona = REASONING_MANAGER.personas.get(trace.persona_id)
        if persona:
            persona_label = persona.persona_type.value

    def _serialize_step(step: Any) -> Dict[str, Any]:
        return {
            "id": getattr(step, "id", ""),
            "operator": getattr(getattr(step, "operator", None), "value", str(getattr(step, "operator", ""))),
            "premises": list(getattr(step, "premises", [])),
            "conclusion": getattr(step, "conclusion", ""),
            "confidence": getattr(step, "confidence", 0.0),
            "timestamp": getattr(step, "timestamp", datetime.utcnow()).isoformat(),
        }

    return {
        "id": getattr(trace, "id", ""),
        "query": getattr(trace, "query", ""),
        "persona_type": persona_label,
        "steps": [_serialize_step(step) for step in getattr(trace, "steps", [])],
        "final_conclusion": getattr(trace, "final_conclusion", ""),
        "overall_confidence": getattr(trace, "overall_confidence", 0.0),
        "created_at": getattr(trace, "created_at", datetime.utcnow()).isoformat(),
    }


async def _ensure_reasoning_manager_ready() -> None:
    """Ensure the cognitive framework is initialized before handling requests."""
    global REASONING_READY
    if not REASONING_MANAGER:
        raise HTTPException(status_code=503, detail="Cognitive framework not available on this build.")
    if REASONING_READY:
        return
    async with REASONING_LOCK:
        if REASONING_READY:
            return
        await REASONING_MANAGER.initialize()
        await REASONING_MANAGER.start_cognitive_services()
        REASONING_READY = True


@router.get("/reasoning/status")
async def get_reasoning_status() -> Dict[str, Any]:
    """Return metadata about the cognitive framework so the UI can show readiness."""
    if not REASONING_MANAGER:
        raise HTTPException(status_code=503, detail="Cognitive framework not available on this build.")
    state = REASONING_MANAGER.get_system_status()
    return {
        "available": True,
        "initialized": state.get("initialized", False) or REASONING_READY,
        "personas": [
            {"id": pid, "type": persona_type}
            for pid, persona_type in state.get("personas", {}).items()
        ],
        "daemons": [
            {
                "id": daemon_id,
                "type": info.get("type"),
                "status": info.get("status"),
                "execution_count": info.get("execution_count", 0),
            }
            for daemon_id, info in state.get("daemon_status", {}).items()
        ],
        "recent_traces": len(RECENT_TRACES),
    }


@router.get("/reasoning/traces")
async def list_reasoning_traces() -> List[Dict[str, Any]]:
    """Return recent reasoning traces captured by the TRF."""
    if not REASONING_MANAGER:
        raise HTTPException(status_code=503, detail="Cognitive framework not available on this build.")
    return list(RECENT_TRACES)


@router.post("/reasoning/run")
async def run_reasoning_query(payload: ReasoningRequest) -> Dict[str, Any]:
    """Execute a TRF reasoning request and return the reasoning trace."""
    await _ensure_reasoning_manager_ready()
    assert REASONING_MANAGER  # nosec - ensured above

    persona_value = (payload.persona or "aic").lower()
    if PersonaType:
        try:
            persona_type = PersonaType(persona_value)
        except ValueError:
            supported = ", ".join(sorted({p.value for p in PersonaType}))  # type: ignore
            raise HTTPException(
                status_code=400, detail=f"Unsupported persona '{persona_value}'. Choose from {supported}."
            )
    else:  # pragma: no cover - fallback if enum missing
        persona_type = None

    trace = await REASONING_MANAGER.reason_about(payload.query, persona_type)  # type: ignore[arg-type]
    serialized = _serialize_trace(trace)
    RECENT_TRACES.appendleft(serialized)
    return {
        "trace": serialized,
        "status": await get_reasoning_status(),
    }


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


# --- Driver scheduling instrumentation ---------------------------------------------


class DriverQueueMetric(BaseModel):
    driver_id: str
    label: str
    queue_depth: int
    max_concurrency: int
    avg_latency_ms: int
    backlog_seconds: int
    admission_rate: float
    throttled: bool
    priority_mix: Dict[str, int]
    spec_refs: List[str]


class DriverThrottleRecommendation(BaseModel):
    driver_id: str
    action: str
    recommendation: str
    severity: str


class DriverSchedulingSnapshot(BaseModel):
    updated_at: str
    queues: List[DriverQueueMetric]
    recommendations: List[DriverThrottleRecommendation]
    guardrails: Dict[str, Any]


class DriverThrottleRequest(BaseModel):
    driver_id: str
    mode: Literal["auto", "manual"] = "auto"
    target_rate: float = Field(ge=0.2, le=1.0)


DRIVER_PROFILES = [
    {
        "id": "capsule_driver",
        "label": "Capsule Driver",
        "priority_weights": {"CRITICAL": 2, "HIGH": 1},
        "max_concurrency": 4,
    },
    {
        "id": "automation_mesh",
        "label": "Automation Mesh",
        "priority_weights": {"MEDIUM": 1, "LOW": 1},
        "max_concurrency": 6,
    },
    {
        "id": "regulatory_lane",
        "label": "Regulatory Lane",
        "priority_weights": {"CRITICAL": 1, "MEDIUM": 1},
        "max_concurrency": 2,
    },
]

DRIVER_THROTTLES: Dict[str, Dict[str, Any]] = {
    profile["id"]: {"mode": "auto", "target_rate": 0.85} for profile in DRIVER_PROFILES
}


def _task_inventory() -> List[Dict[str, Any]]:
    with db_session() as conn:
        cursor = conn.execute("SELECT project, priority, status FROM tasks")
        return [
            {
                "project": row["project"] or "General",
                "priority": (row["priority"] or "MEDIUM").upper(),
                "status": (row["status"] or "UNKNOWN").upper(),
            }
            for row in cursor.fetchall()
        ]


def _driver_snapshot() -> DriverSchedulingSnapshot:
    tasks = _task_inventory()
    priority_counts = Counter([task["priority"] for task in tasks])
    status_counts = Counter([task["status"] for task in tasks])
    queues: List[DriverQueueMetric] = []
    recommendations: List[DriverThrottleRecommendation] = []
    now = _iso(_utc_now())

    for profile in DRIVER_PROFILES:
        driver_id = profile["id"]
        weights = profile["priority_weights"]
        queue_depth = 0
        priority_mix: Dict[str, int] = {}
        for priority, weight in weights.items():
            count = priority_counts.get(priority, 0)
            priority_mix[priority] = count
            queue_depth += count * weight

        queue_depth = max(queue_depth, status_counts.get("BLOCKED", 0) if driver_id == "regulatory_lane" else queue_depth)
        max_concurrency = profile["max_concurrency"]
        throttle = DRIVER_THROTTLES.get(driver_id, {"mode": "auto", "target_rate": 0.85})
        admission_rate = throttle.get("target_rate", 0.85)
        throttled = throttle.get("mode", "auto") == "manual" and admission_rate < 0.8

        avg_latency_ms = 120 + queue_depth * 12
        backlog_seconds = queue_depth * 45

        queues.append(
            DriverQueueMetric(
                driver_id=driver_id,
                label=profile["label"],
                queue_depth=queue_depth,
                max_concurrency=max_concurrency,
                avg_latency_ms=avg_latency_ms,
                backlog_seconds=backlog_seconds,
                admission_rate=round(admission_rate, 2),
                throttled=throttled,
                priority_mix=priority_mix,
                spec_refs=["§5.12", "§12.5"],
            )
        )

        if queue_depth > max_concurrency * 2:
            recommendations.append(
                DriverThrottleRecommendation(
                    driver_id=driver_id,
                    action="lower_admission",
                    recommendation="Queue exceeds safe window · reduce admission rate or add burst capacity",
                    severity="high",
                )
            )
        elif queue_depth <= max_concurrency and throttle.get("mode") == "manual":
            recommendations.append(
                DriverThrottleRecommendation(
                    driver_id=driver_id,
                    action="switch_auto",
                    recommendation="Queue normalized · revert to auto mode",
                    severity="info",
                )
            )

    guardrails = {
        "backpressure_window_minutes": 5,
        "max_queue_depth": 24,
        "spec_refs": ["§5.12", "§12.5"],
    }

    return DriverSchedulingSnapshot(
        updated_at=now,
        queues=queues,
        recommendations=recommendations,
        guardrails=guardrails,
    )


@router.get("/drivers/metrics", response_model=DriverSchedulingSnapshot)
async def get_driver_metrics() -> DriverSchedulingSnapshot:
    """Expose queue + throttle telemetry mirroring the Tkinter driver view."""
    return _driver_snapshot()


@router.post("/drivers/throttle", response_model=DriverSchedulingSnapshot)
async def update_driver_throttle(payload: DriverThrottleRequest) -> DriverSchedulingSnapshot:
    """Allow the UI to switch drivers between auto/manual throttling."""
    if payload.driver_id not in DRIVER_THROTTLES:
        raise HTTPException(status_code=404, detail="Unknown driver")
    DRIVER_THROTTLES[payload.driver_id]["mode"] = payload.mode
    DRIVER_THROTTLES[payload.driver_id]["target_rate"] = round(payload.target_rate, 2)
    return _driver_snapshot()
