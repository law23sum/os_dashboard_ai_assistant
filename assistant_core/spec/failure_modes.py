"""Failure modes, risk, and resilience data derived from Section 14."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class FailurePrinciples:
    principles: List[str]
    objectives: List[str]


@dataclass(frozen=True)
class FailureAxis:
    name: str
    values: List[str]


@dataclass(frozen=True)
class FailureScenario:
    category: str
    examples: List[str]


@dataclass(frozen=True)
class DetectionMechanism:
    name: str
    techniques: List[str]


@dataclass(frozen=True)
class RecoveryPattern:
    plane_or_layer: str
    strategies: List[str]


@dataclass(frozen=True)
class RiskBand:
    band: str
    description: str


FAILURE_PRINCIPLES = FailurePrinciples(
    principles=[
        "Fail visibly, not silently",
        "Fail bounded, not catastrophically",
        "Fail explainably, not mysteriously",
        "Fail forward",
    ],
    objectives=[
        "Shared taxonomy for failures",
        "Early-warning detection and risk scoring",
        "Capsule/runbook-based recovery",
        "Protect CIR/Ledger/Capsule integrity",
        "Enable BC/DR with measurable RPO/RTO",
        "Surface systemic risk to HyperDaemon and regulators",
    ],
)

FAILURE_AXES = [
    FailureAxis(
        name="Plane",
        values=["Data", "Control", "Governance"],
    ),
    FailureAxis(
        name="Layer",
        values=[
            "Driver & Execution",
            "Application / Domain",
            "Cognitive",
            "UX / Presentation",
        ],
    ),
    FailureAxis(
        name="Scope",
        values=[
            "Local",
            "Project",
            "Tenant",
            "Cluster / Region",
            "Cross-OS / Federation",
        ],
    ),
    FailureAxis(
        name="Severity",
        values=["SEV-1", "SEV-2", "SEV-3", "SEV-4/5"],
    ),
    FailureAxis(
        name="Root Cause",
        values=[
            "Resource exhaustion",
            "Dependency failure",
            "Data corruption",
            "Policy misconfiguration",
            "Misuse / abuse",
            "Cognitive misreasoning",
            "UX mismatch",
        ],
    ),
]

FAILURE_SCENARIOS = [
    FailureScenario(
        category="Data Plane",
        examples=[
            "Storage unavailability",
            "Data corruption/inconsistency",
            "Data loss/truncation",
            "Classification/residency violations",
        ],
    ),
    FailureScenario(
        category="Control Plane",
        examples=[
            "Planner/orchestrator failures",
            "Workflow engine failures",
            "Daemon/scheduler failures",
        ],
    ),
    FailureScenario(
        category="Driver & Execution",
        examples=[
            "Driver unavailability",
            "Driver misconfiguration",
            "System execution errors",
            "Package/env driver failures",
            "Edge/agent failures",
        ],
    ),
    FailureScenario(
        category="Governance & Policy",
        examples=[
            "Over-restrictive policies",
            "Under-restrictive policies",
            "Conflicting policies",
            "Regulator Fabric failures",
            "Law-of-the-OS breakdowns",
        ],
    ),
    FailureScenario(
        category="UX & Interaction",
        examples=[
            "Mismatched expectations",
            "Silent or opaque failures",
            "Alert overload",
            "Collisions with automation",
        ],
    ),
    FailureScenario(
        category="Cognitive / Systemic",
        examples=[
            "Hallucination or fabrication",
            "Goal misalignment",
            "Temporal incoherence",
            "Cross-persona conflict",
            "Cascading failures across HyperMesh",
        ],
    ),
]

DETECTION_MECHANISMS = [
    DetectionMechanism(
        name="Threshold & SLO",
        techniques=["Per-driver thresholds", "SLO burn-rate alerts"],
    ),
    DetectionMechanism(
        name="Statistical & ML",
        techniques=["Time-series anomalies", "Behavioral anomalies"],
    ),
    DetectionMechanism(
        name="Policy-based",
        techniques=["Rule engines watching sequences", "Policy decision spikes"],
    ),
    DetectionMechanism(
        name="Causal & Graph",
        techniques=["Ledger causal motifs", "Capsule-driver correlations"],
    ),
]

RISK_BANDS = [
    RiskBand(band="Green", description="Nominal"),
    RiskBand(band="Yellow", description="Degraded; extra monitoring"),
    RiskBand(band="Orange", description="Serious; throttling, approvals"),
    RiskBand(band="Red", description="Critical; kill-switches, containment"),
]

RECOVERY_PATTERNS = [
    RecoveryPattern(
        plane_or_layer="Data Plane",
        strategies=[
            "Storage failover / read-only mode",
            "Index rebuild Capsules",
            "Schema/data repair Capsules",
            "Local snapshot restore",
        ],
    ),
    RecoveryPattern(
        plane_or_layer="Control Plane",
        strategies=[
            "Plan regeneration with updated constraints",
            "Workflow restart & compensation",
            "Daemon heartbeat replay",
        ],
    ),
    RecoveryPattern(
        plane_or_layer="Driver & Execution",
        strategies=[
            "Driver failover / degraded mode",
            "Bounded retries + host isolation",
            "Environment blueprint reapply",
        ],
    ),
    RecoveryPattern(
        plane_or_layer="Governance & Policy",
        strategies=[
            "Policy rollback Capsules",
            "Governance degradation modes",
        ],
    ),
]


def failure_summary() -> Dict[str, List[str]]:
    return {
        "principles": FAILURE_PRINCIPLES.principles,
        "objectives": FAILURE_PRINCIPLES.objectives,
        "axes": [f"{axis.name}: {', '.join(axis.values)}" for axis in FAILURE_AXES],
        "scenarios": [f"{scenario.category}: {', '.join(scenario.examples)}" for scenario in FAILURE_SCENARIOS],
        "detection": [f"{det.name}: {', '.join(det.techniques)}" for det in DETECTION_MECHANISMS],
        "risk_bands": [f"{band.band} – {band.description}" for band in RISK_BANDS],
        "recovery": [
            f"{pattern.plane_or_layer}: {', '.join(pattern.strategies)}" for pattern in RECOVERY_PATTERNS
        ],
    }
