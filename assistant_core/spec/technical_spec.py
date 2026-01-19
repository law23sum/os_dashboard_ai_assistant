"""Canonical technical specification data for AI OS."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class MissionProfile:
    objectives: List[str]
    design_principles: List[str]
    constraints: List[str]
    non_goals: List[str]


@dataclass(frozen=True)
class DeploymentMode:
    name: str
    description: str
    capabilities: List[str]


@dataclass(frozen=True)
class IdentitySurface:
    label: str
    description: str
    actors: List[str]


@dataclass(frozen=True)
class CognitiveAgent:
    name: str
    role: str
    focus: str


@dataclass(frozen=True)
class DaemonFamily:
    name: str
    responsibilities: List[str]


@dataclass(frozen=True)
class ModelProvider:
    name: str
    modalities: List[str]
    notes: str


@dataclass(frozen=True)
class TechnicalSpec:
    mission: MissionProfile
    deployment_modes: List[DeploymentMode]
    identity_surfaces: List[IdentitySurface]
    cognitive_agents: List[CognitiveAgent]
    daemon_families: List[DaemonFamily]
    model_providers: List[ModelProvider]


SPEC = TechnicalSpec(
    mission=MissionProfile(
        objectives=[
            "Deliver an enterprise-grade AI assistant that fuses data intelligence, project automation, and governance.",
            "Operate across desktop, cloud, and hybrid environments with offline-first workflows.",
        ],
        design_principles=[
            "Auditable-by-design",
            "Extensible driver fabric",
            "Self-healing and fault-tolerant",
            "Human-in-the-loop approvals",
        ],
        constraints=[
            "Must respect tenant and workspace isolation boundaries.",
            "Must operate when disconnected by falling back to cached intelligence and local models.",
        ],
        non_goals=[
            "Replacing enterprise identity or billing systems.",
            "Providing GPU orchestration beyond project automation scope.",
        ],
    ),
    deployment_modes=[
        DeploymentMode(
            name="Local",
            description="Single-user desktop install with optional offline caches.",
            capabilities=["Desktop GUI", "Local daemons", "Offline-first"],
        ),
        DeploymentMode(
            name="Cloud",
            description="Managed SaaS deployment with centralized services.",
            capabilities=["Multi-tenant", "Elastic scaling", "Federated drivers"],
        ),
        DeploymentMode(
            name="Enterprise",
            description="Self-hosted environment with policy packs and regulator fabric.",
            capabilities=["RBAC", "Policy enforcement", "Custom capsules"],
        ),
        DeploymentMode(
            name="Hybrid",
            description="Combination of local workspaces and enterprise control plane.",
            capabilities=["Selective sync", "Mixed deployments", "Offline overlays"],
        ),
    ],
    identity_surfaces=[
        IdentitySurface(
            label="Users",
            description="Operators interacting via GUI or CLI",
            actors=["Creators", "Analysts", "Developers"],
        ),
        IdentitySurface(
            label="Tenants",
            description="Enterprise organizations with dedicated policy envelopes",
            actors=["Enterprise tenants", "Partners"],
        ),
        IdentitySurface(
            label="Regulators",
            description="External reviewers auditing compliance surfaces",
            actors=["Auditors", "Governance bots"],
        ),
    ],
    cognitive_agents=[
        CognitiveAgent(name="Chris", role="Primary operator", focus="Product orchestration"),
        CognitiveAgent(name="AIC", role="Meta-governor", focus="Architecture & policy"),
        CognitiveAgent(name="Sora", role="Research strategist", focus="Simulation & analysis"),
        CognitiveAgent(name="Aria", role="Narrative and documentation", focus="Writer workspace"),
    ],
    daemon_families=[
        DaemonFamily(
            name="Echo",
            responsibilities=["Observability", "Health telemetry", "Alerting"],
        ),
        DaemonFamily(
            name="Oracle",
            responsibilities=["Reasoning cues", "Forecasts", "Scenario planning"],
        ),
        DaemonFamily(
            name="Critic",
            responsibilities=["Plan validation", "Risk assessment"],
        ),
        DaemonFamily(
            name="Archivist",
            responsibilities=["Ledger", "Continuity", "Temporal reconstruction"],
        ),
        DaemonFamily(
            name="Security Monitor",
            responsibilities=["Threat detection", "Access enforcement"],
        ),
    ],
    model_providers=[
        ModelProvider(
            name="GPT-5.1",
            modalities=["text", "code", "vision"],
            notes="Primary cloud model with TRF hooks",
        ),
        ModelProvider(
            name="Local/TRF-compliant",
            modalities=["text"],
            notes="Fallback when offline; integrates capsules and driver stack",
        ),
    ],
)


def spec_summary() -> Dict[str, List[str]]:
    """Return a summary dictionary for UI display."""
    return {
        "Mission": SPEC.mission.objectives,
        "DesignPrinciples": SPEC.mission.design_principles,
        "DeploymentModes": [f"{mode.name}: {mode.description}" for mode in SPEC.deployment_modes],
        "IdentitySurfaces": [f"{surface.label}: {surface.description}" for surface in SPEC.identity_surfaces],
        "CognitiveAgents": [f"{agent.name} – {agent.role}" for agent in SPEC.cognitive_agents],
        "DaemonFamilies": [f"{daemon.name}: {', '.join(daemon.responsibilities)}" for daemon in SPEC.daemon_families],
        "ModelProviders": [f"{model.name}: {model.notes}" for model in SPEC.model_providers],
    }
