"""Driver-aware orchestration architecture primitives.

This module translates the high level reference design for the OS Dashboard AI Assistant
into importable Python skeletons. The focus is on infrastructure-centric data structures
and coordinator components (intent processing, driver registry, planning), enabling the
rest of the codebase to experiment with advanced orchestration ideas without breaking
existing flows.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

# =============================================================================
# 0. CORE PRIMITIVES
# =============================================================================


@dataclass
class Intent:
    """Represents user/system intent with full context."""

    id: str
    source: str
    content: str
    project_id: Optional[str] = None
    capsule_id: Optional[str] = None
    user_id: str = ""
    tenant_id: str = ""
    priority: int = 5
    deadline: Optional[datetime] = None
    budget_limit: Optional[float] = None
    risk_threshold: str = "medium"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ActionSchema:
    """Schema for a single driver action."""

    name: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    description: str
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExecutionStep:
    """Single step in execution plan."""

    id: str
    driver_name: str
    action: str
    parameters: Dict[str, Any]
    preconditions: Dict[str, Any]
    postconditions: Dict[str, Any]
    timeout: timedelta
    retry_policy: Dict[str, Any]


@dataclass
class ExecutionPlan:
    """Concrete plan with ordered driver calls."""

    id: str
    intent_id: str
    steps: List[ExecutionStep]
    estimated_cost: float
    estimated_duration: timedelta
    risk_assessment: str
    approval_checkpoints: List[int]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Result of driver execution pipeline."""

    step_id: str
    success: bool
    output: Any
    logs: List[str]
    metrics: Dict[str, float]
    traces: List[Dict[str, Any]]
    duration: timedelta
    cost: float
    error: Optional[str] = None


@dataclass
class DriverManifest:
    """Complete driver specification with capabilities and constraints."""

    name: str
    version: str
    vendor: str
    trust_level: str
    actions: Dict[str, ActionSchema]
    side_effects: List[str]
    rate_limits: Dict[str, int]
    cost_model: Dict[str, float]
    latency_profile: Dict[str, float]
    security_class: str
    preconditions: List[str]
    postconditions: List[str]
    logs_schema: Dict[str, Any] = field(default_factory=dict)
    metrics_exposed: List[str] = field(default_factory=list)
    trace_points: List[str] = field(default_factory=list)


# =============================================================================
# 1. SUPPORTING UTILITIES
# =============================================================================


class DriverMetrics:
    """Minimal metrics recorder used by driver skeletons."""

    def __init__(self) -> None:
        self.operations: List[Dict[str, Any]] = []

    async def record_operation(self, name: str, payload: Dict[str, Any]) -> None:
        self.operations.append({"name": name, "payload": payload, "timestamp": datetime.now()})


class PolicyEngine:
    """Base policy engine interface used in the skeleton."""

    async def check_permission(self, action: str, resource: str, context: Dict[str, Any]) -> bool:
        return True

    async def check_file_write_permission(self, path: str) -> bool:
        return True

    async def check_repo_access(self, repo: str) -> bool:
        return True

    async def check_table_access(self, table: str) -> bool:
        return True


class RateLimiter:
    """In-memory rate limiter placeholder."""

    def __init__(self, limits: Dict[str, int]):
        self.limits = limits

    async def acquire(self) -> None:
        await asyncio.sleep(0)

    def release(self) -> None:
        return


class CostEstimator:
    """Estimates costs for driver operations."""

    async def estimate_cost(self, manifest: DriverManifest, operation_description: str) -> float:
        base = manifest.cost_model.get("per_call", 0.0)
        modifier = min(len(operation_description.split()) / 10.0, 5)
        return base * (1 + modifier)


class EmbeddingsModel:
    """Simple text embedding mock used by the capability index."""

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [[float(len(text) + idx)] for idx, text in enumerate(texts)]

    async def embed_text(self, text: str) -> List[float]:
        return [float(len(text))]


# =============================================================================
# 2. DRIVER TAXONOMY
# =============================================================================


class DriverType(Enum):
    OS = "os"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    DATA = "data"
    WORKFLOW = "workflow"
    GOVERNANCE = "governance"


class BaseDriver:
    """Abstract base for all driver types."""

    driver_type: DriverType = DriverType.SOFTWARE

    def __init__(self, manifest: DriverManifest) -> None:
        self.manifest = manifest
        self.metrics = DriverMetrics()
        self.policy_engine = PolicyEngine()

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        raise NotImplementedError

    async def validate_preconditions(self, action: str, context: Dict[str, Any]) -> bool:
        schema = self.manifest.actions[action].input_schema
        for condition in schema.get("preconditions", []):
            if condition == "auth_token_present" and "auth_token" not in context:
                return False
        return True


class OSDriver(BaseDriver):
    """OS-level operations: filesystem, processes, networking."""

    driver_type = DriverType.OS

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        if action == "create_file":
            return await self._create_file(params["path"], params.get("content", ""))
        if action == "run_process":
            return await self._run_process(params["command"], params.get("env", {}))
        raise ValueError(f"Unknown OS action: {action}")

    async def _create_file(self, path: str, content: str) -> Dict[str, Any]:
        if not await self.policy_engine.check_file_write_permission(path):
            raise PermissionError(f"Cannot write to {path}")
        temp_path = f"{path}.tmp.{uuid.uuid4()}"
        with open(temp_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(temp_path, path)
        await self.metrics.record_operation("file_created", {"path": path})
        return {"success": True, "path": path, "size": len(content)}

    async def _run_process(self, command: str, env: Dict[str, str]) -> Dict[str, Any]:
        await self.metrics.record_operation("process_run", {"command": command, "env": env})
        return {"success": True, "command": command, "env": env}


class SoftwareDriver(BaseDriver):
    """Driver that wraps remote services/APIs."""

    driver_type = DriverType.SOFTWARE

    def __init__(self, manifest: DriverManifest, api_client: Callable[..., Any]) -> None:
        super().__init__(manifest)
        self.api_client = api_client
        self.rate_limiter = RateLimiter(manifest.rate_limits)

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        await self.rate_limiter.acquire()
        try:
            handler = getattr(self, f"_action_{action}", None)
            if not handler:
                raise ValueError(f"Unknown software action: {action}")
            return await handler(params)
        finally:
            self.rate_limiter.release()

    async def _action_create_pull_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        repo = params["repository"]
        if not await self.policy_engine.check_repo_access(repo):
            raise PermissionError(f"No repo access for {repo}")
        await self.metrics.record_operation("pr_created", {"repo": repo})
        return {"repo": repo, "title": params.get("title", ""), "number": uuid.uuid4().hex[:6]}


class DataDriver(BaseDriver):
    """Structured data access with schema awareness."""

    driver_type = DriverType.DATA

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        if action == "query":
            return await self._execute_query(params["sql"], params.get("parameters", {}))
        raise ValueError(f"Unknown data action: {action}")

    async def _execute_query(self, sql: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        await self.metrics.record_operation("query", {"sql": sql})
        return [{"row": 1, "sql": sql, "parameters": parameters}]


# =============================================================================
# 3. DRIVER MANIFESTS & DISCOVERY
# =============================================================================


class CapabilityIndex:
    """Semantic index of driver capabilities for discovery."""

    def __init__(self) -> None:
        self.embeddings_model = EmbeddingsModel()
        self.capability_vectors: Dict[str, List[List[float]]] = {}
        self.action_descriptions: Dict[str, List[str]] = {}

    async def index_driver(self, manifest: DriverManifest) -> None:
        descriptions: List[str] = []
        for action in manifest.actions.values():
            descriptions.append(action.description)
            descriptions.extend(example.get("description", "") for example in action.examples)
        embeddings = await self.embeddings_model.embed_texts(descriptions)
        self.capability_vectors[manifest.name] = embeddings
        self.action_descriptions[manifest.name] = descriptions

    async def semantic_search(self, query: str, top_k: int = 10) -> List[str]:
        if not self.capability_vectors:
            return []
        query_embedding = await self.embeddings_model.embed_text(query)
        scores: List[Tuple[str, float]] = []
        for driver_name, vectors in self.capability_vectors.items():
            similarities = [self._cosine_similarity(query_embedding, vec) for vec in vectors]
            scores.append((driver_name, max(similarities)))
        scores.sort(key=lambda item: item[1], reverse=True)
        return [name for name, _ in scores[:top_k]]

    @staticmethod
    def _cosine_similarity(left: List[float], right: List[float]) -> float:
        if not left or not right:
            return 0.0
        return (left[0] * right[0]) / ((abs(left[0]) or 1.0) * (abs(right[0]) or 1.0))


class DriverRegistry:
    """Central registry for driver manifests and discovery."""

    def __init__(self) -> None:
        self.manifests: Dict[str, DriverManifest] = {}
        self.driver_instances: Dict[str, BaseDriver] = {}
        self.capability_index = CapabilityIndex()
        self.cost_estimator = CostEstimator()

    async def register_driver(self, manifest: DriverManifest, driver_instance: BaseDriver) -> None:
        await self._validate_manifest(manifest)
        self.manifests[manifest.name] = manifest
        self.driver_instances[manifest.name] = driver_instance
        await self.capability_index.index_driver(manifest)

    async def get_available_drivers(self, user_id: str, tenant_id: str) -> List[str]:
        return list(self.manifests.keys())

    async def get_manifests(self, driver_names: List[str]) -> List[DriverManifest]:
        return [self.manifests[name] for name in driver_names if name in self.manifests]

    async def discover_drivers_for_task(self, task_description: str, constraints: Dict[str, Any]) -> List[str]:
        candidates = await self.capability_index.semantic_search(task_description)
        filtered: List[str] = []
        for driver_name in candidates:
            manifest = self.manifests[driver_name]
            if constraints.get("max_cost"):
                cost = await self.cost_estimator.estimate_cost(manifest, task_description)
                if cost > constraints["max_cost"]:
                    continue
            if constraints.get("security_class") and manifest.security_class != constraints["security_class"]:
                continue
            filtered.append(driver_name)
        return filtered or list(self.manifests.keys())

    async def _validate_manifest(self, manifest: DriverManifest) -> None:
        if not manifest.actions:
            raise ValueError("Driver must declare at least one action")
        if manifest.security_class not in {"public", "internal", "restricted"}:
            raise ValueError("Invalid security class")


# =============================================================================
# 4. INTENT → PLAN → EXECUTION LOOP
# =============================================================================


@dataclass
class TaskStep:
    id: str
    description: str
    required_capabilities: List[str]
    input_requirements: Dict[str, Any]
    output_expectations: Dict[str, Any]
    risk_level: str


@dataclass
class TaskDecomposition:
    intent_id: str
    steps: List[TaskStep]
    dependencies: Dict[str, List[str]]
    estimated_duration: timedelta
    confidence_score: float


@dataclass
class TaskHypothesis:
    steps: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskDecomposer:
    async def refine_hypothesis(self, hypothesis: TaskHypothesis, context: Dict[str, Any]) -> TaskDecomposition:
        steps: List[TaskStep] = []
        for idx, step_description in enumerate(hypothesis.steps):
            steps.append(
                TaskStep(
                    id=f"step_{idx}",
                    description=step_description,
                    required_capabilities=["generic"],
                    input_requirements={},
                    output_expectations={},
                    risk_level="medium",
                )
            )
        return TaskDecomposition(
            intent_id=context.get("intent_id", "unknown"),
            steps=steps,
            dependencies={step.id: [] for step in steps},
            estimated_duration=timedelta(minutes=5 * len(steps)),
            confidence_score=0.6,
        )


class ConstraintSolver:
    async def score_driver_option(self, driver_name: str, task_step: TaskStep, intent: Intent) -> float:
        base = 1.0
        if task_step.risk_level == "low":
            base += 0.1
        if intent.priority <= 3:
            base += 0.1
        return base


class HypothesisGenerator:
    async def generate_hypotheses(self, intent: Intent, context: Dict[str, Any]) -> List[TaskHypothesis]:
        return [TaskHypothesis(steps=[intent.content])]


class AICReasoningEngine:
    """AIC + TRF for intent decomposition and planning."""

    def __init__(self) -> None:
        self.task_decomposer = TaskDecomposer()
        self.constraint_solver = ConstraintSolver()
        self.hypothesis_generator = HypothesisGenerator()

    async def decompose_task(self, intent: Intent, context: Dict[str, Any]) -> TaskDecomposition:
        hypotheses = await self.hypothesis_generator.generate_hypotheses(intent, context)
        best = hypotheses[0]
        context["intent_id"] = intent.id
        return await self.task_decomposer.refine_hypothesis(best, context)


class ExecutionPlanner:
    """Converts task decomposition into concrete driver execution plan."""

    def __init__(self, driver_registry: DriverRegistry) -> None:
        self.driver_registry = driver_registry
        self.constraint_solver = ConstraintSolver()

    async def create_execution_plan(self, decomposition: TaskDecomposition, intent: Intent) -> ExecutionPlan:
        execution_steps: List[ExecutionStep] = []
        for step in decomposition.steps:
            candidates = await self.driver_registry.discover_drivers_for_task(
                step.description,
                {
                    "max_cost": intent.budget_limit,
                    "security_class": intent.metadata.get("security_class", "internal"),
                },
            )
            if not candidates:
                raise ValueError(f"No drivers available for {step.description}")
            selected_driver = await self._select_optimal_driver(candidates, step, intent)
            execution_steps.append(
                ExecutionStep(
                    id=f"exec_{step.id}",
                    driver_name=selected_driver,
                    action="generic_action",
                    parameters={"description": step.description},
                    preconditions=step.input_requirements,
                    postconditions=step.output_expectations,
                    timeout=timedelta(minutes=5),
                    retry_policy={"max_retries": 3},
                )
            )
        total_cost = sum(idx * 0.5 for idx, _ in enumerate(execution_steps, start=1))
        return ExecutionPlan(
            id=str(uuid.uuid4()),
            intent_id=intent.id,
            steps=execution_steps,
            estimated_cost=total_cost,
            estimated_duration=decomposition.estimated_duration,
            risk_assessment="medium",
            approval_checkpoints=[],
        )

    async def _select_optimal_driver(
        self, candidate_drivers: List[str], task_step: TaskStep, intent: Intent
    ) -> str:
        scores: List[Tuple[float, str]] = []
        for driver_name in candidate_drivers:
            score = await self.constraint_solver.score_driver_option(driver_name, task_step, intent)
            scores.append((score, driver_name))
        scores.sort(key=lambda item: item[0])
        return scores[-1][1]


# =============================================================================
# 5. SUPPORT INFRASTRUCTURE COMPONENTS
# =============================================================================


class ExecutionFabric:
    async def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        logs: List[str] = []
        for step in plan.steps:
            logs.append(f"Executed {step.driver_name}.{step.action}")
        return ExecutionResult(
            step_id=plan.steps[-1].id if plan.steps else plan.id,
            success=True,
            output={"steps": len(plan.steps)},
            logs=logs,
            metrics={"duration_ms": len(plan.steps) * 100},
            traces=[{"plan_id": plan.id}],
            duration=timedelta(seconds=len(plan.steps)),
            cost=plan.estimated_cost,
        )


class ProjectLedger:
    async def get_context(self, project_id: Optional[str]) -> Dict[str, Any]:
        return {"project_id": project_id, "status": "active"}

    async def get_conversation_history(self, project_id: Optional[str], limit: int) -> List[str]:
        return [f"conversation_{idx}" for idx in range(min(limit, 3))]

    async def get_execution_history(self, project_id: Optional[str], limit: int) -> List[str]:
        return [f"execution_{idx}" for idx in range(min(limit, 3))]


class DaemonManager:
    async def list_daemons(self) -> List[str]:
        return []


class IntentProcessor:
    """Handles the stack from Intent → Driver Execution."""

    def __init__(self) -> None:
        self.reasoning_engine = AICReasoningEngine()
        self.driver_registry = DriverRegistry()
        self.execution_fabric = ExecutionFabric()
        self.project_ledger = ProjectLedger()
        self.daemon_manager = DaemonManager()
        self.execution_planner = ExecutionPlanner(self.driver_registry)
        self._drivers_initialized = False

    async def process_intent(self, intent: Intent) -> ExecutionResult:
        await self._ensure_driver_catalog()
        enriched_intent = await self._enrich_intent(intent)
        context = await self._build_reasoning_context(enriched_intent)
        decomposition = await self.reasoning_engine.decompose_task(enriched_intent, context)
        plan = await self.execution_planner.create_execution_plan(decomposition, enriched_intent)
        result = await self.execution_fabric.execute_plan(plan)
        await self._integrate_feedback(result, enriched_intent)
        return result

    async def _ensure_driver_catalog(self) -> None:
        if self._drivers_initialized:
            return
        try:
            from assistant_core.drivers import register_builtin_drivers
        except ImportError:
            self._drivers_initialized = True
            return
        await register_builtin_drivers(self.driver_registry)
        self._drivers_initialized = True

    async def _enrich_intent(self, intent: Intent) -> Intent:
        project_context = await self.project_ledger.get_context(intent.project_id)
        user_permissions = await self._get_user_permissions(intent.user_id)
        budget = await self._get_budget_constraints(intent.tenant_id)
        intent.metadata.update(
            {
                "project_context": project_context,
                "user_permissions": user_permissions,
                "budget_constraints": budget,
                "available_drivers": await self.driver_registry.get_available_drivers(intent.user_id, intent.tenant_id),
            }
        )
        return intent

    async def _build_reasoning_context(self, intent: Intent) -> Dict[str, Any]:
        return {
            "prior_conversations": await self.project_ledger.get_conversation_history(intent.project_id, limit=5),
            "execution_traces": await self.project_ledger.get_execution_history(intent.project_id, limit=5),
            "current_system_state": await self._get_system_state(intent),
        }

    async def _get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        return {"user_id": user_id, "roles": ["builder"]}

    async def _get_budget_constraints(self, tenant_id: str) -> Dict[str, Any]:
        return {"tenant_id": tenant_id, "monthly_budget": 1000}

    async def _get_system_state(self, intent: Intent) -> Dict[str, Any]:
        return {"active_daemons": await self.daemon_manager.list_daemons(), "intent": intent.id}

    async def _integrate_feedback(self, result: ExecutionResult, intent: Intent) -> None:
        _ = (result, intent)
        return


# =============================================================================
# MODULE EXPORT
# =============================================================================

__all__ = [
    "Intent",
    "ActionSchema",
    "ExecutionStep",
    "ExecutionPlan",
    "ExecutionResult",
    "DriverManifest",
    "IntentProcessor",
    "DriverRegistry",
    "DriverType",
]
