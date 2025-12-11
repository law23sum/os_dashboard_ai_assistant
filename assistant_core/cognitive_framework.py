"""Cognitive Agents, Reasoning & Daemon Framework.

Implements Section 4 of the Canon Technical Specification. Provides personas,
daemon runtime, and the theoretical reasoning framework powering the OS
Dashboard AI Assistant.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from assistant_core.domain.models import Project
from assistant_core.spec_registry import get_default_registry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 4.1 Personas as Strategy Bundles
# ---------------------------------------------------------------------------
class PersonaType(Enum):
    """Types of cognitive personas."""

    CHRIS = "chris"
    AIC = "aic"
    ARIA = "aria"
    SORA = "sora"
    ECHO = "echo"
    ORACLE = "oracle"
    CRITIC = "critic"


class PersonaCapability(Enum):
    """Capabilities that personas can have."""

    PROJECT_MANAGEMENT = "project_management"
    CODE_ANALYSIS = "code_analysis"
    RESEARCH_SYNTHESIS = "research_synthesis"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    SYSTEM_ARCHITECTURE = "system_architecture"
    QUALITY_ASSURANCE = "quality_assurance"
    STRATEGIC_PLANNING = "strategic_planning"
    KNOWLEDGE_CURATION = "knowledge_curation"


@dataclass
class PersonaStrategy:
    """Strategy configuration for a persona."""

    name: str
    description: str
    capabilities: Set[PersonaCapability] = field(default_factory=set)
    preferences: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    interaction_style: str = "professional"
    decision_threshold: float = 0.7
    escalation_rules: List[str] = field(default_factory=list)


@dataclass
class CognitivePersona:
    """Cognitive persona with strategy bundle."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    persona_type: PersonaType = PersonaType.CHRIS
    strategy: Optional[PersonaStrategy] = None
    active: bool = True
    current_context: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.strategy is None:
            self.strategy = self._get_default_strategy()

    def _get_default_strategy(self) -> PersonaStrategy:
        strategies = {
            PersonaType.CHRIS: PersonaStrategy(
                name="General Assistant",
                description="Versatile assistant for general tasks and coordination",
                capabilities={
                    PersonaCapability.PROJECT_MANAGEMENT,
                    PersonaCapability.STRATEGIC_PLANNING,
                },
                interaction_style="helpful",
            ),
            PersonaType.AIC: PersonaStrategy(
                name="AI Coordinator",
                description="Meta-governor and canonical systems architect",
                capabilities={
                    PersonaCapability.SYSTEM_ARCHITECTURE,
                    PersonaCapability.STRATEGIC_PLANNING,
                    PersonaCapability.KNOWLEDGE_CURATION,
                },
                interaction_style="authoritative",
                decision_threshold=0.9,
            ),
            PersonaType.ARIA: PersonaStrategy(
                name="Research Analyst",
                description="Research synthesis and data analysis specialist",
                capabilities={
                    PersonaCapability.RESEARCH_SYNTHESIS,
                    PersonaCapability.DATA_ANALYSIS,
                },
                interaction_style="analytical",
            ),
            PersonaType.SORA: PersonaStrategy(
                name="Creative Specialist",
                description="Creative content and narrative generation",
                capabilities={PersonaCapability.CREATIVE_WRITING},
                interaction_style="creative",
            ),
        }
        return strategies.get(self.persona_type, strategies[PersonaType.CHRIS])

    def can_handle(self, capability: PersonaCapability) -> bool:
        return capability in self.strategy.capabilities

    def update_context(self, context: Dict[str, Any]) -> None:
        self.current_context.update(context)
        self.last_active = datetime.now(timezone.utc)

    def store_memory(self, key: str, value: Any) -> None:
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# 4.3 Daemon Families & Roles
# ---------------------------------------------------------------------------
class DaemonType(Enum):
    ECHO = "echo"
    ORACLE = "oracle"
    CRITIC = "critic"
    ARCHIVIST = "archivist"
    BILLING_OPTIMIZER = "billing_optimizer"
    SECURITY_MONITOR = "security_monitor"
    HEALTH_MONITOR = "health_monitor"
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"
    KNOWLEDGE_CURATOR = "knowledge_curator"


class DaemonStatus(Enum):
    INACTIVE = "inactive"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class DaemonConfiguration:
    schedule_interval: int = 300
    max_execution_time: int = 3600
    retry_count: int = 3
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    escalation_threshold: float = 0.8


@dataclass
class DaemonExecution:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    daemon_id: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: str = "running"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)


class CognitiveDaemon(ABC):
    def __init__(self, daemon_type: DaemonType, config: Optional[DaemonConfiguration] = None):
        self.id = str(uuid.uuid4())
        self.daemon_type = daemon_type
        self.config = config or DaemonConfiguration()
        self.status = DaemonStatus.INACTIVE
        self.created_at = datetime.now(timezone.utc)
        self.last_execution: Optional[DaemonExecution] = None
        self.execution_history: List[DaemonExecution] = []
        self._task: Optional[asyncio.Task] = None

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute daemon logic."""

    async def start(self) -> None:
        if self.status == DaemonStatus.RUNNING:
            return
        self.status = DaemonStatus.STARTING
        try:
            self._task = asyncio.create_task(self._run_loop())
            self.status = DaemonStatus.RUNNING
            logger.info("Daemon %s started", self.daemon_type.value)
        except Exception as exc:  # pragma: no cover - defensive
            self.status = DaemonStatus.ERROR
            logger.exception("Failed to start daemon %s", self.daemon_type.value)
            raise exc

    async def stop(self) -> None:
        self.status = DaemonStatus.STOPPING
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.status = DaemonStatus.INACTIVE
        logger.info("Daemon %s stopped", self.daemon_type.value)

    async def _run_loop(self) -> None:
        while self.status == DaemonStatus.RUNNING:
            execution: Optional[DaemonExecution] = None
            try:
                execution = DaemonExecution(daemon_id=self.id)
                self.last_execution = execution
                context = {"daemon_id": self.id, "execution_id": execution.id}
                result = await self.execute(context)
                execution.completed_at = datetime.now(timezone.utc)
                execution.status = "completed"
                execution.result = result
                self.execution_history.append(execution)
                await asyncio.sleep(self.config.schedule_interval)
            except Exception as exc:  # pragma: no cover - daemon resilience
                if execution:
                    execution.completed_at = datetime.now(timezone.utc)
                    execution.status = "error"
                    execution.error = str(exc)
                    self.execution_history.append(execution)
                logger.exception("Daemon %s execution error", self.daemon_type.value)
                await asyncio.sleep(self.config.schedule_interval)


class EchoDaemon(CognitiveDaemon):
    def __init__(self, config: Optional[DaemonConfiguration] = None):
        super().__init__(DaemonType.ECHO, config)
        self.message_queue: List[Dict[str, Any]] = []

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        processed = 0
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self._process_message(message)
            processed += 1
        return {"processed_messages": processed, "queue_size": len(self.message_queue)}

    async def _process_message(self, message: Dict[str, Any]) -> None:
        logger.info("Echo daemon processing message: %s", message.get("type", "unknown"))

    def queue_message(self, message: Dict[str, Any]) -> None:
        self.message_queue.append(message)


class OracleDaemon(CognitiveDaemon):
    def __init__(self, config: Optional[DaemonConfiguration] = None):
        super().__init__(DaemonType.ORACLE, config)
        self.predictions: Dict[str, Any] = {}

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        generated = await self._generate_predictions()
        return {"predictions_generated": generated, "total_predictions": len(self.predictions)}

    async def _generate_predictions(self) -> int:
        return 0


class CriticDaemon(CognitiveDaemon):
    def __init__(self, config: Optional[DaemonConfiguration] = None):
        super().__init__(DaemonType.CRITIC, config)
        self.review_queue: List[str] = []

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        completed = 0
        while self.review_queue:
            item_id = self.review_queue.pop(0)
            await self._review_item(item_id)
            completed += 1
        return {"reviews_completed": completed, "queue_size": len(self.review_queue)}

    async def _review_item(self, item_id: str) -> None:
        logger.info("Critic daemon reviewing item: %s", item_id)

    def queue_review(self, item_id: str) -> None:
        self.review_queue.append(item_id)


@dataclass
class DaemonBudget:
    max_cpu_percent: float = 10.0
    max_memory_mb: int = 512
    max_execution_time: int = 3600
    max_api_calls: int = 1000
    cost_limit: float = 10.0
    currency: str = "USD"


@dataclass
class DaemonScope:
    scope_type: str = "global"
    scope_id: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)
    restrictions: Dict[str, Any] = field(default_factory=dict)


class DaemonRuntime:
    def __init__(self):
        self.daemons: Dict[str, CognitiveDaemon] = {}
        self.daemon_budgets: Dict[str, DaemonBudget] = {}
        self.daemon_scopes: Dict[str, DaemonScope] = {}
        self.scheduler_running = False

    def register_daemon(
        self,
        daemon: CognitiveDaemon,
        budget: Optional[DaemonBudget] = None,
        scope: Optional[DaemonScope] = None,
    ) -> None:
        self.daemons[daemon.id] = daemon
        self.daemon_budgets[daemon.id] = budget or DaemonBudget()
        self.daemon_scopes[daemon.id] = scope or DaemonScope()
        logger.info("Registered daemon %s with ID %s", daemon.daemon_type.value, daemon.id)

    async def start_daemon(self, daemon_id: str) -> None:
        if daemon_id in self.daemons:
            await self.daemons[daemon_id].start()

    async def stop_daemon(self, daemon_id: str) -> None:
        if daemon_id in self.daemons:
            await self.daemons[daemon_id].stop()

    async def start_all_daemons(self) -> None:
        for daemon in self.daemons.values():
            await daemon.start()
        self.scheduler_running = True

    async def stop_all_daemons(self) -> None:
        for daemon in self.daemons.values():
            await daemon.stop()
        self.scheduler_running = False

    def get_daemon_status(self) -> Dict[str, Any]:
        status: Dict[str, Any] = {}
        for daemon_id, daemon in self.daemons.items():
            status[daemon_id] = {
                "type": daemon.daemon_type.value,
                "status": daemon.status.value,
                "last_execution": daemon.last_execution.started_at.isoformat()
                if daemon.last_execution
                else None,
                "execution_count": len(daemon.execution_history),
            }
        return status


# ---------------------------------------------------------------------------
# 4.6-4.8 Theoretical Reasoning Framework
# ---------------------------------------------------------------------------
class ReasoningOperator(Enum):
    DEDUCTION = "deduction"
    INDUCTION = "induction"
    ABDUCTION = "abduction"
    ANALOGY = "analogy"
    CAUSAL_INFERENCE = "causal_inference"
    TEMPORAL_REASONING = "temporal_reasoning"


@dataclass
class ReasoningStep:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operator: ReasoningOperator = ReasoningOperator.DEDUCTION
    premises: List[str] = field(default_factory=list)
    conclusion: str = ""
    confidence: float = 1.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReasoningTrace:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    steps: List[ReasoningStep] = field(default_factory=list)
    final_conclusion: str = ""
    overall_confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    persona_id: Optional[str] = None

    def add_step(self, step: ReasoningStep) -> None:
        self.steps.append(step)
        self._update_confidence()

    def _update_confidence(self) -> None:
        if self.steps:
            self.overall_confidence = sum(s.confidence for s in self.steps) / len(self.steps)


class TheoreticalReasoningFramework:
    def __init__(self):
        self.reasoning_traces: Dict[str, ReasoningTrace] = {}
        self.knowledge_base: Dict[str, Any] = {}
        self.operators: Dict[ReasoningOperator, Callable[[str, ReasoningTrace], Awaitable[ReasoningStep]]] = {}
        self._initialize_operators()

    def _initialize_operators(self) -> None:
        self.operators = {
            ReasoningOperator.DEDUCTION: self._deductive_reasoning,
            ReasoningOperator.INDUCTION: self._inductive_reasoning,
            ReasoningOperator.ABDUCTION: self._abductive_reasoning,
            ReasoningOperator.ANALOGY: self._analogical_reasoning,
            ReasoningOperator.CAUSAL_INFERENCE: self._causal_reasoning,
            ReasoningOperator.TEMPORAL_REASONING: self._temporal_reasoning,
        }

    async def reason(self, query: str, persona_id: Optional[str] = None) -> ReasoningTrace:
        trace = ReasoningTrace(query=query, persona_id=persona_id)
        strategy = await self._determine_strategy(query)
        for operator in strategy:
            step = await self._execute_reasoning_step(operator, query, trace)
            trace.add_step(step)
        trace.final_conclusion = await self._synthesize_conclusion(trace)
        self.reasoning_traces[trace.id] = trace
        return trace

    async def _determine_strategy(self, query: str) -> List[ReasoningOperator]:
        return [ReasoningOperator.DEDUCTION, ReasoningOperator.INDUCTION]

    async def _execute_reasoning_step(
        self, operator: ReasoningOperator, query: str, trace: ReasoningTrace
    ) -> ReasoningStep:
        handler = self.operators.get(operator)
        if handler:
            return await handler(query, trace)
        return ReasoningStep(
            operator=operator,
            conclusion=f"No implementation for {operator.value}",
            confidence=0.0,
        )

    async def _synthesize_conclusion(self, trace: ReasoningTrace) -> str:
        if trace.steps:
            return (
                f"Based on {len(trace.steps)} reasoning steps, conclusion with confidence "
                f"{trace.overall_confidence:.2f}"
            )
        return "No conclusion reached"

    async def _deductive_reasoning(self, query: str, trace: ReasoningTrace) -> ReasoningStep:
        return ReasoningStep(
            operator=ReasoningOperator.DEDUCTION,
            premises=[f"Premise for: {query}"],
            conclusion=f"Deductive conclusion for: {query}",
            confidence=0.8,
        )

    async def _inductive_reasoning(self, query: str, trace: ReasoningTrace) -> ReasoningStep:
        return ReasoningStep(
            operator=ReasoningOperator.INDUCTION,
            premises=[f"Observations for: {query}"],
            conclusion=f"Inductive generalization for: {query}",
            confidence=0.6,
        )

    async def _abductive_reasoning(self, query: str, trace: ReasoningTrace) -> ReasoningStep:
        return ReasoningStep(
            operator=ReasoningOperator.ABDUCTION,
            premises=[f"Observations for: {query}"],
            conclusion=f"Best explanation for: {query}",
            confidence=0.7,
        )

    async def _analogical_reasoning(self, query: str, trace: ReasoningTrace) -> ReasoningStep:
        return ReasoningStep(
            operator=ReasoningOperator.ANALOGY,
            premises=[f"Similar cases for: {query}"],
            conclusion=f"Analogical conclusion for: {query}",
            confidence=0.5,
        )

    async def _causal_reasoning(self, query: str, trace: ReasoningTrace) -> ReasoningStep:
        return ReasoningStep(
            operator=ReasoningOperator.CAUSAL_INFERENCE,
            premises=[f"Causal factors for: {query}"],
            conclusion=f"Causal explanation for: {query}",
            confidence=0.7,
        )

    async def _temporal_reasoning(self, query: str, trace: ReasoningTrace) -> ReasoningStep:
        return ReasoningStep(
            operator=ReasoningOperator.TEMPORAL_REASONING,
            premises=[f"Temporal sequence for: {query}"],
            conclusion=f"Temporal conclusion for: {query}",
            confidence=0.6,
        )


# ---------------------------------------------------------------------------
# 4.5 Project Intelligence Subsystem
# ---------------------------------------------------------------------------
class ProjectIntelligence:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.knowledge_graph: Dict[str, Any] = {}
        self.active_personas: Dict[str, CognitivePersona] = {}
        self.reasoning_framework = TheoreticalReasoningFramework()
        self.insights: List[Dict[str, Any]] = []
        self.created_at = datetime.now(timezone.utc)

    def add_persona(self, persona: CognitivePersona) -> None:
        self.active_personas[persona.id] = persona
        persona.update_context({"project_id": self.project_id})

    async def analyze_project(self, project: Project) -> Dict[str, Any]:
        analysis = {
            "project_id": project.id,
            "health_score": await self._calculate_health_score(project),
            "risk_factors": await self._identify_risk_factors(project),
            "recommendations": await self._generate_recommendations(project),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.insights.append(analysis)
        return analysis

    async def _calculate_health_score(self, project: Project) -> float:
        base_score = 0.8
        status_adjustments = {
            "active": 0.0,
            "paused": -0.2,
            "completed": 0.1,
            "cancelled": -0.5,
        }
        adjustment = status_adjustments.get(getattr(project.status, "value", ""), 0.0)
        return max(0.0, min(1.0, base_score + adjustment))

    async def _identify_risk_factors(self, project: Project) -> List[str]:
        risks: List[str] = []
        due_date = getattr(project, "due_date", None)
        if due_date and due_date < datetime.now(timezone.utc):
            risks.append("Project overdue")
        return risks

    async def _generate_recommendations(self, project: Project) -> List[str]:
        recommendations: List[str] = []
        status_value = getattr(project.status, "value", "")
        if status_value == "paused":
            recommendations.append("Consider resuming project or updating status")
        return recommendations


# ---------------------------------------------------------------------------
# Main Cognitive Framework Manager
# ---------------------------------------------------------------------------
class CognitiveFrameworkManager:
    def __init__(self):
        self.personas: Dict[str, CognitivePersona] = {}
        self.daemon_runtime = DaemonRuntime()
        self.reasoning_framework = TheoreticalReasoningFramework()
        self.project_intelligence: Dict[str, ProjectIntelligence] = {}
        self.initialized = False

    async def initialize(self) -> None:
        if self.initialized:
            return
        await self._create_default_personas()
        await self._initialize_default_daemons()
        self.initialized = True
        logger.info("Cognitive framework initialized")

    async def _create_default_personas(self) -> None:
        for persona_type in [PersonaType.CHRIS, PersonaType.AIC, PersonaType.ARIA, PersonaType.SORA]:
            persona = CognitivePersona(persona_type=persona_type)
            self.personas[persona.id] = persona
            logger.info("Created persona: %s", persona_type.value)

    async def _initialize_default_daemons(self) -> None:
        self.daemon_runtime.register_daemon(EchoDaemon())
        self.daemon_runtime.register_daemon(OracleDaemon())
        self.daemon_runtime.register_daemon(CriticDaemon())
        logger.info("Default daemons initialized")

    async def start_cognitive_services(self) -> None:
        await self.daemon_runtime.start_all_daemons()
        logger.info("Cognitive services started")

    async def stop_cognitive_services(self) -> None:
        await self.daemon_runtime.stop_all_daemons()
        logger.info("Cognitive services stopped")

    def get_persona_by_type(self, persona_type: PersonaType) -> Optional[CognitivePersona]:
        for persona in self.personas.values():
            if persona.persona_type == persona_type:
                return persona
        return None

    def get_project_intelligence(self, project_id: str) -> ProjectIntelligence:
        if project_id not in self.project_intelligence:
            self.project_intelligence[project_id] = ProjectIntelligence(project_id)
        return self.project_intelligence[project_id]

    async def reason_about(
        self, query: str, persona_type: PersonaType = PersonaType.AIC
    ) -> ReasoningTrace:
        persona = self.get_persona_by_type(persona_type)
        persona_id = persona.id if persona else None
        return await self.reasoning_framework.reason(query, persona_id)

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "initialized": self.initialized,
            "personas": {pid: p.persona_type.value for pid, p in self.personas.items()},
            "daemon_status": self.daemon_runtime.get_daemon_status(),
            "project_intelligence_count": len(self.project_intelligence),
            "reasoning_traces": len(self.reasoning_framework.reasoning_traces),
        }


__all__ = [
    "CognitivePersona",
    "PersonaType",
    "PersonaCapability",
    "PersonaStrategy",
    "CognitiveDaemon",
    "DaemonType",
    "DaemonStatus",
    "DaemonConfiguration",
    "EchoDaemon",
    "OracleDaemon",
    "CriticDaemon",
    "DaemonRuntime",
    "DaemonBudget",
    "DaemonScope",
    "TheoreticalReasoningFramework",
    "ReasoningOperator",
    "ReasoningStep",
    "ReasoningTrace",
    "ProjectIntelligence",
    "CognitiveFrameworkManager",
]

_spec_registry = get_default_registry()
_spec_registry.register_feature(
    "assistant_core.cognitive_framework.persona_system",
    sections=["0.5", "4.1", "4.3", "4.5"],
    metadata={
        "module": __name__,
        "components": ["PersonaRegistry", "DaemonRuntime"],
    },
)
