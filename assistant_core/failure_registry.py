"""Failure taxonomy, detection, and recovery registry (spec section 14)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from typing import Any, Dict, Iterable, List, Optional

from assistant_core.spec_registry import get_default_registry


class FailurePlane(Enum):
    DATA = "data"
    CONTROL = "control"
    GOVERNANCE = "governance"


class FailureLayer(Enum):
    DRIVER = "driver"
    DOMAIN = "domain"
    COGNITIVE = "cognitive"
    UX = "ux"
    INFRA = "infrastructure"


class FailureScope(Enum):
    LOCAL = "local"
    PROJECT = "project"
    TENANT = "tenant"
    CLUSTER = "cluster"
    FEDERATION = "federation"


class FailureSeverity(Enum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"
    SEV5 = "sev5"


class FailureRootCause(Enum):
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"
    DATA_CORRUPTION = "data_corruption"
    POLICY_MISCONFIGURATION = "policy_misconfiguration"
    ABUSE = "abuse"
    COGNITIVE_MISALIGNMENT = "cognitive_misalignment"
    UX_MISMATCH = "ux_mismatch"


class RiskBand(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


SPEC_REFERENCES = [
    "14.1",
    "14.2",
    "14.3",
    "14.4",
    "14.5",
    "14.6",
    "14.7",
    "14.8",
]


@dataclass
class RiskScore:
    impact: int
    likelihood: int
    scope: int
    control_strength: int
    score: float
    band: RiskBand


@dataclass
class FailureEvent:
    plane: FailurePlane
    layer: FailureLayer
    scope: FailureScope
    severity: FailureSeverity
    root_cause: FailureRootCause
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    recovery_plan: Optional[str] = None
    risk_score: Optional[RiskScore] = None
    spec_refs: List[str] = field(default_factory=lambda: SPEC_REFERENCES.copy())


@dataclass
class DetectionSignal:
    source: str
    metric: str
    value: float
    threshold: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=datetime.utcnow)


class FailureRegistry:
    """Central registry for failure modes, detection signals, and recovery plans."""

    def __init__(self) -> None:
        self.events: List[FailureEvent] = []
        self.signals: List[DetectionSignal] = []
        self.recovery_catalog: Dict[str, Dict[str, Any]] = {}
        registry = get_default_registry()
        registry.register_feature(
            "assistant_core.failure_registry",
            sections=["14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "14.7"],
            metadata={"module": __name__},
        )
        self.register_recovery_plan(
            "workflow_retry",
            capsule_id="capsule.control.workflow.retry",
            description="Regenerate the workflow plan, replay idempotent steps, and request approval for compensations.",
            tags=["14.3.3", "control"],
        )
        self.register_recovery_plan(
            "driver_failover",
            capsule_id="capsule.driver.failover",
            description="Switch to alternate driver or region and place automation into degraded read-only mode until recovery.",
            tags=["14.3.4", "driver"],
        )

    def register_recovery_plan(
        self, key: str, capsule_id: str, description: str, tags: Optional[Iterable[str]] = None
    ) -> None:
        """Register a recovery capsule/playbook reference."""

        self.recovery_catalog[key] = {
            "capsule_id": capsule_id,
            "description": description,
            "tags": list(tags or []),
        }

    def get_recovery_plan(self, key: str) -> Optional[Dict[str, Any]]:
        return self.recovery_catalog.get(key)

    def record_event(
        self,
        plane: FailurePlane,
        layer: FailureLayer,
        scope: FailureScope,
        severity: FailureSeverity,
        root_cause: FailureRootCause,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        recovery_plan: Optional[str] = None,
        risk_inputs: Optional[Dict[str, int]] = None,
    ) -> FailureEvent:
        """Record a failure event and compute optional risk scores."""

        event = FailureEvent(
            plane=plane,
            layer=layer,
            scope=scope,
            severity=severity,
            root_cause=root_cause,
            description=description,
            metadata=metadata or {},
            recovery_plan=recovery_plan,
        )

        if risk_inputs:
            event.risk_score = self.calculate_risk_score(**risk_inputs)

        self.events.append(event)
        return event

    def mark_resolved(self, event_id: str) -> bool:
        for event in self.events:
            if event.event_id == event_id:
                event.resolved = True
                return True
        return False

    def ingest_signal(
        self, source: str, metric: str, value: float, threshold: Optional[float] = None, **metadata: Any
    ) -> DetectionSignal:
        signal = DetectionSignal(
            source=source,
            metric=metric,
            value=value,
            threshold=threshold,
            metadata=metadata,
        )
        self.signals.append(signal)
        return signal

    def calculate_risk_score(
        self,
        impact: int,
        likelihood: int,
        scope: int,
        control_strength: int,
    ) -> RiskScore:
        """Calculate risk score per Section 14.2.3."""

        # Normalize inputs between 1 and 5
        def _clamp(value: int) -> int:
            return max(1, min(5, value))

        impact = _clamp(impact)
        likelihood = _clamp(likelihood)
        scope = _clamp(scope)
        control_strength = _clamp(control_strength)

        raw = (
            impact * 0.35
            + likelihood * 0.35
            + scope * 0.2
            - control_strength * 0.2
        )
        normalized = max(0.0, min(5.0, raw))
        if normalized < 2.0:
            band = RiskBand.GREEN
        elif normalized < 3.0:
            band = RiskBand.YELLOW
        elif normalized < 4.0:
            band = RiskBand.ORANGE
        else:
            band = RiskBand.RED

        return RiskScore(
            impact=impact,
            likelihood=likelihood,
            scope=scope,
            control_strength=control_strength,
            score=round(normalized, 2),
            band=band,
        )

    def summarize_events(self) -> Dict[str, Any]:
        """Return aggregate stats for observability dashboards."""

        summary: Dict[str, Any] = {
            "total": len(self.events),
            "active": len([e for e in self.events if not e.resolved]),
            "by_severity": {},
            "by_plane": {},
            "risk_bands": {band.value: 0 for band in RiskBand},
        }

        for event in self.events:
            summary["by_severity"].setdefault(event.severity.value, 0)
            summary["by_severity"][event.severity.value] += 1

            summary["by_plane"].setdefault(event.plane.value, 0)
            summary["by_plane"][event.plane.value] += 1

            if event.risk_score:
                summary["risk_bands"][event.risk_score.band.value] += 1

        return summary

    def summarize_signals(self) -> Dict[str, Any]:
        return {
            "total": len(self.signals),
            "recent": [signal.__dict__ for signal in self.signals[-10:]],
        }


_DEFAULT_FAILURE_REGISTRY: Optional[FailureRegistry] = None


def get_failure_registry() -> FailureRegistry:
    global _DEFAULT_FAILURE_REGISTRY
    if _DEFAULT_FAILURE_REGISTRY is None:
        _DEFAULT_FAILURE_REGISTRY = FailureRegistry()
    return _DEFAULT_FAILURE_REGISTRY


__all__ = [
    "FailureEvent",
    "FailureLayer",
    "FailurePlane",
    "FailureRegistry",
    "FailureRootCause",
    "FailureScope",
    "FailureSeverity",
    "RiskBand",
    "RiskScore",
    "DetectionSignal",
    "get_failure_registry",
]
