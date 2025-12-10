"""Backend capability discovery for wiring services into the GUI."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .spec_registry import SpecRegistry, SpecDocument


@dataclass
class BackendAction:
    label: str
    description: str
    handler: Callable[[], Any]


@dataclass
class BackendCapability:
    key: str
    title: str
    description: str
    available: bool
    tags: List[str]
    actions: List[BackendAction] = field(default_factory=list)
    documents: List[SpecDocument] = field(default_factory=list)

    def serialize(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "available": self.available,
            "tags": self.tags,
            "documents": [str(doc.relative_path) for doc in self.documents],
            "actions": [action.label for action in self.actions],
        }


class BackendRegistry:
    """Discover backend modules and expose friendly metadata + actions."""

    def __init__(self, spec_registry: Optional[SpecRegistry] = None):
        self.spec_registry = spec_registry
        self.capabilities: List[BackendCapability] = []
        self._capability_index: Dict[str, BackendCapability] = {}
        self._discover_capabilities()

    # Public API -----------------------------------------------------------------
    def list_capabilities(self) -> List[BackendCapability]:
        return self.capabilities

    def get_capability(self, key: str) -> Optional[BackendCapability]:
        return self._capability_index.get(key)

    def run_action(self, capability_key: str, action_label: str) -> Any:
        capability = self.get_capability(capability_key)
        if not capability:
            return f"Capability '{capability_key}' not found"

        action = next((a for a in capability.actions if a.label == action_label), None)
        if not action:
            return f"Action '{action_label}' not found"

        try:
            result = action.handler()
            if asyncio.iscoroutine(result):
                return asyncio.run(result)
            return result
        except Exception as exc:  # noqa: BLE001 - Show failure to the UI
            return {"error": str(exc), "capability": capability_key, "action": action_label}

    # Discovery ------------------------------------------------------------------
    def _discover_capabilities(self):
        self._register_automation_orchestrator()
        self._register_predictive_analytics()
        self._register_search_engine()
        self._register_audit_system()

    def _register_capability(self, capability: BackendCapability):
        self.capabilities.append(capability)
        self._capability_index[capability.key] = capability

    def _docs_for(self, keywords: List[str]) -> List[SpecDocument]:
        if not self.spec_registry:
            return []
        return self.spec_registry.find_docs_for_keywords(keywords)

    def _register_automation_orchestrator(self):
        try:
            from assistant_core.automation_orchestrator import AutomationOrchestrator

            orchestrator_cls = AutomationOrchestrator
            available = True
        except ImportError:
            orchestrator_cls = None
            available = False

        def _summary():
            if not orchestrator_cls:
                return "Automation orchestrator module unavailable."
            orchestrator = orchestrator_cls()
            return {
                "workflows": len(orchestrator.workflows),
                "automation_rules": len(orchestrator.automation_rules),
                "executions": len(orchestrator.executions),
                "tags": sorted({tag for wf in orchestrator.workflows.values() for tag in wf.tags}),
            }

        async def _create_samples():
            if not orchestrator_cls:
                return "Automation orchestrator module unavailable."
            orchestrator = orchestrator_cls()
            return await orchestrator.create_sample_workflows()

        async def _dashboard_snapshot():
            if not orchestrator_cls:
                return "Automation orchestrator module unavailable."
            orchestrator = orchestrator_cls()
            return await orchestrator.get_system_dashboard()

        actions = [
            BackendAction("Summarize", "Show orchestrator state", _summary),
            BackendAction("Sample workflows", "Create sample workflows", _create_samples),
            BackendAction("Dashboard snapshot", "Generate system dashboard", _dashboard_snapshot),
        ]

        capability = BackendCapability(
            key="automation",
            title="Automation Orchestrator",
            description="Workflow + agent orchestration engine",
            available=available,
            tags=["automation", "workflow", "agents"],
            actions=actions,
            documents=self._docs_for(["automation", "workflow"]),
        )
        self._register_capability(capability)

    def _register_predictive_analytics(self):
        try:
            from assistant_core.predictive_analytics import AdvancedPredictiveAnalytics

            analytics_cls = AdvancedPredictiveAnalytics
            available = True
        except ImportError:
            analytics_cls = None
            available = False

        def _config_snapshot():
            if not analytics_cls:
                return "Predictive analytics module unavailable."
            analytics = analytics_cls()
            return {
                "models": list(analytics.feature_extractors.keys()),
                "config": analytics.config,
            }

        def _describe_models():
            if not analytics_cls:
                return "Predictive analytics module unavailable."
            analytics = analytics_cls()
            return {
                "stored_models": list(analytics.models.keys()),
                "prediction_cache": list(analytics.predictions.keys()),
            }

        capability = BackendCapability(
            key="predictive",
            title="Predictive Analytics",
            description="Productivity forecasting engine",
            available=available,
            tags=["analytics", "forecast", "vision"],
            actions=[
                BackendAction("Config", "Show model configuration", _config_snapshot),
                BackendAction("Model cache", "List cached models/predictions", _describe_models),
            ],
            documents=self._docs_for(["vision", "predictive", "analytics"]),
        )
        self._register_capability(capability)

    def _register_search_engine(self):
        try:
            from assistant_core.search_engine import UnifiedSearchEngine

            search_cls = UnifiedSearchEngine
            available = True
        except ImportError:
            search_cls = None
            available = False

        async def _initialize_search():
            if not search_cls:
                return "Search engine module unavailable."
            engine = search_cls()
            await engine.initialize()
            return {
                "connectors": list(engine.connectors.keys()),
                "index_size": len(engine.search_index.documents),
                "initialized": engine.is_initialized,
            }

        capability = BackendCapability(
            key="search",
            title="Unified Search",
            description="Semantic + metadata search engine",
            available=available,
            tags=["search", "embedding", "documents"],
            actions=[BackendAction("Initialize", "Initialize engine + summarize", _initialize_search)],
            documents=self._docs_for(["search", "document", "cir"]),
        )
        self._register_capability(capability)

    def _register_audit_system(self):
        try:
            from assistant_core.audit_system import AuditSystem

            audit_cls = AuditSystem
            available = True
        except ImportError:
            audit_cls = None
            available = False

        def _audit_snapshot():
            if not audit_cls:
                return "Audit system module unavailable."
            audit = audit_cls()
            return {
                "connectors": list(audit.connectors.keys()),
                "lineage_tracked": len(audit.lineage_tracker),
                "event_hooks": len(audit.event_hooks),
                "storage_path": str(audit.storage.storage_path),
            }

        capability = BackendCapability(
            key="audit",
            title="Audit & Compliance",
            description="Governance + compliance service",
            available=available,
            tags=["audit", "compliance", "security"],
            actions=[BackendAction("Snapshot", "Summarize audit system state", _audit_snapshot)],
            documents=self._docs_for(["security", "compliance", "audit"]),
        )
        self._register_capability(capability)
