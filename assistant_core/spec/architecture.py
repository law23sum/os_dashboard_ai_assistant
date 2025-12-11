"""Architectural layers and plane definitions aligned with the OS Dashboard TOC."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LayerDefinition:
    name: str
    description: str
    responsibilities: List[str]
    representative_components: List[str]


@dataclass(frozen=True)
class PlaneDefinition:
    name: str
    description: str
    responsibilities: List[str]
    invariants: List[str]


ARCHITECTURE_LAYERS: List[LayerDefinition] = [
    LayerDefinition(
        name="Presentation Layer",
        description="Desktop GUI, workspaces, dashboards, and CLI surfaces that expose the assistant to humans.",
        responsibilities=[
            "Render dashboards, workspaces, and task monitors",
            "Collect intent through chat/voice/CLI",
            "Surface plan previews, approvals, and regulator views",
        ],
        representative_components=[
            "assistant_core/dashboard/main_interface.py",
            "ui/terminal",
            "assistant_hub_gui",
        ],
    ),
    LayerDefinition(
        name="Application Layer",
        description="assistant_core services that coordinate data collection, content generation, and system operations.",
        responsibilities=[
            "Task orchestration and workflow execution",
            "Integrations with system operations, deployments, and APIs",
            "Plugin/capsule lifecycle management",
        ],
        representative_components=[
            "assistant_core/operations",
            "assistant_core/system/operations.py",
            "assistant_core/integrations",
        ],
    ),
    LayerDefinition(
        name="Cognitive / Reasoning Layer",
        description="Personas, daemons, and reasoning frameworks that drive planning, critique, and governance.",
        responsibilities=[
            "Persona-specific strategy bundles",
            "Daemon scheduling (Echo, Oracle, Critic, Archivist, Security Monitor)",
            "Intent → plan → execution loops with guardrails",
        ],
        representative_components=[
            "assistant_core/daemon",
            "assistant_core/personalization_engine.py",
            "OS Dashboard TOC-driven persona definitions",
        ],
    ),
    LayerDefinition(
        name="Domain / Model Layer",
        description="Projects, tasks, CIR documents, capsules, ledgers, and policy objects.",
        responsibilities=[
            "Maintain CIR schemas and ledger state",
            "Track project graphs, dependencies, and environment profiles",
            "Persist policies, capsules, and governance artifacts",
        ],
        representative_components=[
            "assistant_core/cir",
            "assistant_core/task_automation.py",
            "assistant_core/spec/technical_spec.py",
        ],
    ),
    LayerDefinition(
        name="Infrastructure Layer",
        description="Storage, queues, search engines, compute resources, and runtime envelopes.",
        responsibilities=[
            "Expose storage (workspace, S3/Azure) and compute contexts",
            "Provide search/vector indices and observability stores",
            "Deliver queueing and daemon runtimes for capsules",
        ],
        representative_components=[
            "config/default_config.yaml (storage settings)",
            "assistant_core/search_engine.py",
            "deployments (docker-compose, cloud deploy scripts)",
        ],
    ),
    LayerDefinition(
        name="Security / Governance / Billing Layer",
        description="Policy enforcement, auditing, billing, and regulator-facing surfaces.",
        responsibilities=[
            "Enforce policy packs, cost/budget guardrails, and RBAC",
            "Maintain audit ledgers and compliance exports",
            "Expose regulator portals and billing hooks",
        ],
        representative_components=[
            "security_monitor.py",
            "assistant_core/security_framework.py",
            "audit + ledger integrations",
        ],
    ),
]


PLANES: List[PlaneDefinition] = [
    PlaneDefinition(
        name="Data Plane",
        description="Covers content, CIR, knowledge stores, and observability data flows.",
        responsibilities=[
            "Ingest multi-source data (APIs, web, files)",
            "Persist CIR documents, project ledgers, knowledge graphs",
            "Maintain indices (search, vector, graph) plus telemetry stores",
        ],
        invariants=[
            "Lossless capture of mission-critical artifacts",
            "Versioned, auditable storage for reconstruction",
            "Zero-trust boundaries per tenant/workspace",
        ],
    ),
    PlaneDefinition(
        name="Control Plane",
        description="Orchestrates assistants, daemons, workflows, and resource scheduling.",
        responsibilities=[
            "Scheduler for workflows, capsules, and driver invocations",
            "Agent state machines (assistants, daemons, TRF ops)",
            "Automation of deployments, system operations, and driver calls",
        ],
        invariants=[
            "Plan → execute → observe loops must remain traceable",
            "Capsules and drivers must declare budgets/policies",
            "Failure domains isolated via workspace + daemon scopes",
        ],
    ),
    PlaneDefinition(
        name="Governance & Policy Plane",
        description="Security, compliance, risk, and economic guardrails controlling every other plane.",
        responsibilities=[
            "Policy engine with regulator packs and cost governance",
            "Budgeting and billing hooks tied to capsule execution",
            "Risk surfaces and escalation workflows",
        ],
        invariants=[
            "Every control-plane action must reference applicable policies",
            "Auditable ledger entries for cross-plane flows",
            "Regulator access scopes enforced per tenant",
        ],
    ),
]


def architecture_summary() -> Dict[str, List[str]]:
    """Return a textual summary for UI/CLI display."""
    return {
        layer.name: layer.responsibilities for layer in ARCHITECTURE_LAYERS
    }


def planes_summary() -> Dict[str, Dict[str, List[str]]]:
    return {
        plane.name: {
            "responsibilities": plane.responsibilities,
            "invariants": plane.invariants,
        }
        for plane in PLANES
    }
