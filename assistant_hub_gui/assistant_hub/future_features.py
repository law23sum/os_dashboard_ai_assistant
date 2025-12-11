"""Structured catalog of future feature pillars for the OS Dashboard."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping


@dataclass(frozen=True)
class FutureFeature:
    """Represents a roadmap feature placeholder."""

    code: str
    title: str
    tier: str
    lifetime_value: str
    summary: str


# NOTE: Summaries are intentionally concise (1–2 lines) so they fit inside
# Tk widgets while still hinting at the economic framing supplied by the user.
FUTURE_FEATURES: List[FutureFeature] = [
    FutureFeature(
        code="10.1",
        title="Master Stack & Project Management Engine",
        tier="Core OS Engines",
        lifetime_value="$45–160B",
        summary="Daily cockpit for files, capsules, and project state; gains power when paired with env drivers and workflow synthesis.",
    ),
    FutureFeature(
        code="10.2",
        title="Code Merge Advisor",
        tier="Core OS Engines",
        lifetime_value="$110–380B",
        summary="Compresses merge risk across repos, eventually orchestrating build/test/deploy pipelines as a change-control plane.",
    ),
    FutureFeature(
        code="10.3",
        title="Commit → Task Generator",
        tier="Core OS Engines",
        lifetime_value="$30–100B",
        summary="Translates diffs into backlog items and keeps them synced with actual repo + environment state.",
    ),
    FutureFeature(
        code="10.4",
        title="Research Orchestrator & Simulation Hub",
        tier="Core OS Engines",
        lifetime_value="$30–130B",
        summary="Coordinates notebooks, HPC jobs, and lab tools so research programs run like automated workflows.",
    ),
    FutureFeature(
        code="10.5",
        title="Writer Workstation Engine",
        tier="Core OS Engines",
        lifetime_value="$15–65B",
        summary="Builds a creator OS where lore, canon, assets, and publishing workflows live in one capsule-aware stack.",
    ),
    FutureFeature(
        code="10.6",
        title="Archive / Continuity / Resonance Engine",
        tier="Core OS Engines",
        lifetime_value="$160–500B",
        summary="Long-memory substrate capturing documents, envs, capsules, and execution traces for institutional knowledge.",
    ),
    FutureFeature(
        code="10.7",
        title="Cybersecurity Guardian",
        tier="Core OS Engines",
        lifetime_value="$35–150B",
        summary="Secure coding + runtime co-pilot that can harden configs, enforce policy, and distribute remediation capsules.",
    ),
    FutureFeature(
        code="10.8",
        title="Business Accounting & Financing Console",
        tier="Core OS Engines",
        lifetime_value="$45–190B",
        summary="Finance cockpit linking banks, ledgers, and automations so creative work can invoice, reconcile, and stay compliant.",
    ),
    FutureFeature(
        code="10.9",
        title="Record Auditor & Logbook",
        tier="Core OS Engines",
        lifetime_value="$35–130B",
        summary="End-to-end audit trail across intent, agent action, Unix commands, env drift, and capsule lineage.",
    ),
    FutureFeature(
        code="10.10",
        title="Executable Capsules & Marketplace",
        tier="Core OS Engines",
        lifetime_value="$230–750B",
        summary="Ecosystem where workflows ship as executable capsules paired with env manifests and monetizable packs.",
    ),
    FutureFeature(
        code="10.11",
        title="Policy & Governance Engine",
        tier="Core OS Engines",
        lifetime_value="$160–450B",
        summary="Enforces who/what may execute which commands, env changes, or capsules across regulated enterprises.",
    ),
    FutureFeature(
        code="10.12",
        title="AI Billing & Usage Fabric",
        tier="Core OS Engines",
        lifetime_value="$30–140B",
        summary="Meters models, drivers, env actions, and capsule runs so automation can be routed, governed, and priced.",
    ),
    FutureFeature(
        code="10.13",
        title="Overall OS Dashboard AI Assistant Platform",
        tier="Core OS Engines",
        lifetime_value="$950B–$2.5T+",
        summary="Full stack (drivers + env + workflows) that orchestrates people, apps, Unix, and governance end-to-end.",
    ),
    FutureFeature(
        code="10.14",
        title="Advanced Research, Simulation & Digital Twin Platform",
        tier="Advanced Horizons",
        lifetime_value="$40–160B",
        summary="Extends the research hub into CAD/CAE/HPC-grade digital twins for complex physical systems.",
    ),
    FutureFeature(
        code="10.15",
        title="Autonomous Research Conductor (ARC)",
        tier="Advanced Horizons",
        lifetime_value="$60–220B",
        summary="Plans and adapts long-horizon research programs, reallocating compute and budget automatically.",
    ),
    FutureFeature(
        code="10.16",
        title="Symbolic–Numeric Theory Discovery Engine",
        tier="Advanced Horizons",
        lifetime_value="$40–180B",
        summary="Searches for governing equations and cross-domain laws, feeding the canon and ontological layers.",
    ),
    FutureFeature(
        code="10.17",
        title="Self-Evolving Capsule Ecosystem",
        tier="Advanced Horizons",
        lifetime_value="$80–260B",
        summary="Monitors capsule usage and proposes safer, faster variants under governance supervision.",
    ),
    FutureFeature(
        code="10.18",
        title="Enterprise & Civilization Knowledge Market",
        tier="Advanced Horizons",
        lifetime_value="$120–400B",
        summary="Marketplace for capsules, blueprints, research packs, and curricula across sectors.",
    ),
    FutureFeature(
        code="10.19",
        title="Agentic Enterprise Twin",
        tier="Super Capabilities",
        lifetime_value="$70–230B",
        summary="Living twin of an org’s structure, workflows, KPIs, and risks for scenario planning and delegation.",
    ),
    FutureFeature(
        code="10.20",
        title="Global Policy & Regulation Fabric",
        tier="Super Capabilities",
        lifetime_value="$90–300B",
        summary="Executable policies shared between regulators and operators with traceable enforcement.",
    ),
    FutureFeature(
        code="10.21",
        title="Temporal Reasoning & Time-Cascade Engine",
        tier="Super Capabilities",
        lifetime_value="$40–150B",
        summary="Models how capsules and policies propagate over quarters, enabling branch-and-bound planning.",
    ),
    FutureFeature(
        code="10.22",
        title="Cross-Domain Knowledge & Law Synthesizer",
        tier="Super Capabilities",
        lifetime_value="$50–180B",
        summary="Finds shared abstractions and capsule templates that generalize across industries.",
    ),
    FutureFeature(
        code="10.23",
        title="Inter-OS Knowledge Network",
        tier="Super Capabilities",
        lifetime_value="$35–140B",
        summary="An anonymized exchange of best practices between separate OS Dashboard deployments.",
    ),
    FutureFeature(
        code="10.24",
        title="Autonomous Knowledge Steward",
        tier="Super Capabilities",
        lifetime_value="$30–110B",
        summary="Always-on curator that prunes contradictions and suggests ontology refactors over years.",
    ),
    FutureFeature(
        code="10.25",
        title="HyperMesh",
        tier="Super Capabilities",
        lifetime_value="$120–380B",
        summary="Federated execution mesh so capsules can span partners, suppliers, and regulators safely.",
    ),
    FutureFeature(
        code="10.26",
        title="HyperFoundry",
        tier="Hyper Network",
        lifetime_value="$60–220B",
        summary="Automation-native venture studio that ideates new capsule bundles from usage telemetry.",
    ),
    FutureFeature(
        code="10.27",
        title="HyperLab",
        tier="Hyper Network",
        lifetime_value="$50–180B",
        summary="Cross-org research grid with shared datasets, compute, and reproducible study capsules.",
    ),
    FutureFeature(
        code="10.28",
        title="HyperRegent",
        tier="Hyper Network",
        lifetime_value="$70–240B",
        summary="Regulators gain tenancy inside the platform, running regulation capsules on live data.",
    ),
    FutureFeature(
        code="10.29",
        title="HyperSymphony",
        tier="Hyper Network",
        lifetime_value="$60–210B",
        summary="Revenue-sharing cross-org capsule flows where each participant owns different steps.",
    ),
    FutureFeature(
        code="10.30",
        title="HyperDaemon",
        tier="Hyper Network",
        lifetime_value="$80–260B",
        summary="Systemic risk sentinel watching capsule networks, markets, and infra for cascading failures.",
    ),
    FutureFeature(
        code="10.31",
        title="HyperContinuity",
        tier="Hyper Network",
        lifetime_value="$40–150B",
        summary="Portable lifetime knowledge + trust graph for individuals and orgs.",
    ),
    FutureFeature(
        code="10.32",
        title="HyperGenesis",
        tier="Hyper Network",
        lifetime_value="$50–190B",
        summary="High-fidelity world simulation layer for macro strategy rehearsals.",
    ),
    FutureFeature(
        code="10.33",
        title="Cognitive Twin Fabric",
        tier="Ultra Scale",
        lifetime_value="$60–210B",
        summary="Living models of people, teams, and roles to optimize staffing and augmentations.",
    ),
    FutureFeature(
        code="10.34",
        title="Strategy Garden & Capsule Fund",
        tier="Ultra Scale",
        lifetime_value="$40–160B",
        summary="Portfolio view where strategies exist as capsule graphs with budget + ROI tracking.",
    ),
    FutureFeature(
        code="10.35",
        title="Reality Twin Mesh",
        tier="Ultra Scale",
        lifetime_value="$70–230B",
        summary="Multi-layer twin of products, infra, markets, and financials for impact simulations.",
    ),
    FutureFeature(
        code="10.36",
        title="Temporal Backtesting Engine",
        tier="Ultra Scale",
        lifetime_value="$40–150B",
        summary="Replays history with alternate capsule graphs to learn from 'ghost' decisions.",
    ),
    FutureFeature(
        code="10.37",
        title="Law-of-the-OS & AI Court",
        tier="Ultra Scale",
        lifetime_value="$50–180B",
        summary="Formal internal law layer that arbitrates responsibility when automation misbehaves.",
    ),
    FutureFeature(
        code="10.38",
        title="Inter-OS Federation",
        tier="Ultra Scale",
        lifetime_value="$60–210B",
        summary="Standards and trust fabric for multiple OS Dashboard networks to interoperate.",
    ),
    FutureFeature(
        code="10.39",
        title="Meta-Design Studio",
        tier="Ultra Scale",
        lifetime_value="$45–160B",
        summary="System that redesigns the platform itself based on telemetry and friction signals.",
    ),
    FutureFeature(
        code="10.40",
        title="Cognitive Economy Engine",
        tier="Ultra Scale",
        lifetime_value="$70–240B",
        summary="Allocator that decides which humans, agents, or capsules tackle work for max ROI.",
    ),
    FutureFeature(
        code="10.41",
        title="Multi-Reality Storyboard",
        tier="Ultra Scale",
        lifetime_value="$40–150B",
        summary="Immersive visualization of branching future strategies and capsule graphs.",
    ),
    FutureFeature(
        code="10.42",
        title="Alignment Monitor",
        tier="Ultra Scale",
        lifetime_value="$50–170B",
        summary="Continuously checks whether automation behaviors still match intent and ethics.",
    ),
    FutureFeature(
        code="10.43",
        title="Ontological Compiler",
        tier="Supreme Tier",
        lifetime_value="$60–220B",
        summary="Compiles an org's worldview into executable ontologies consumed by every capsule and agent.",
    ),
    FutureFeature(
        code="10.44",
        title="Canon of Truth Engine",
        tier="Supreme Tier",
        lifetime_value="$80–260B",
        summary="Maintains living beliefs with evidence, counterexamples, and refutations across time.",
    ),
    FutureFeature(
        code="10.45",
        title="Reality Contract Layer",
        tier="Supreme Tier",
        lifetime_value="$50–180B",
        summary="Links automation to explicit reality triggers so systems can revert or self-correct.",
    ),
    FutureFeature(
        code="10.46",
        title="Human–System Co-Evolution Orchestrator",
        tier="Supreme Tier",
        lifetime_value="$40–150B",
        summary="Plans how roles, skills, and automation evolve together without misalignment.",
    ),
    FutureFeature(
        code="10.47",
        title="Successor Architect & Legacy Seeder",
        tier="Supreme Tier",
        lifetime_value="$30–120B",
        summary="Encodes institutional legacies and doctrines as capsule libraries for future stewards.",
    ),
    FutureFeature(
        code="10.48",
        title="Unified Law of Work & Meaning Engine",
        tier="Supreme Tier",
        lifetime_value="$80–280B",
        summary="Meta-objective layer that defines what 'good' means for work, automation, and society.",
    ),
    FutureFeature(
        code="10.49",
        title="Sovereign Norm & Obligation Stack — Ascend Capabilities Layer",
        tier="Ascend",
        lifetime_value="$120–400B",
        summary="The sovereign governance membrane between automation and the real world: a realtime obligation sentinel + norm-collision engine + constitutional policy VM + decision-proof ledger. Acts as a cross-cutting multiplier over Policy & Governance Engine, Record Auditor & Logbook, Global Policy & Regulation Fabric, HyperRegent, Law-of-the-OS & AI Court, and Inter-OS Federation.",
    ),
    FutureFeature(
        code="10.50",
        title="Full Meta-Stack Envelope",
        tier="Meta Envelope",
        lifetime_value="$1.6T–$5.4T+",
        summary="All layers (advanced + super + hyper + ultra + supreme + ascend) deployed together as civilization-scale fabric.",
    ),
]


def get_features_by_tier(
    features: Iterable[FutureFeature] | None = None,
) -> "OrderedDict[str, List[FutureFeature]]":
    """Return ordered mapping tier -> features (preserves declaration order)."""

    tiers: "OrderedDict[str, List[FutureFeature]]" = OrderedDict()
    for feature in features or FUTURE_FEATURES:
        tiers.setdefault(feature.tier, []).append(feature)
    return tiers


def get_feature_lookup(
    features: Iterable[FutureFeature] | None = None,
) -> Dict[str, FutureFeature]:
    """Fast lookup by code for selection handlers."""

    lookup: Dict[str, FutureFeature] = {}
    for feature in features or FUTURE_FEATURES:
        lookup[feature.code] = feature
    return lookup


def tier_palette() -> Mapping[str, str]:
    """Gentle color accents for cards based on tier name."""

    return {
        "Core OS Engines": "#1f6feb",
        "Advanced Horizons": "#a855f7",
        "Super Capabilities": "#0ea5e9",
        "Hyper Network": "#ec4899",
        "Ultra Scale": "#f97316",
        "Supreme Tier": "#facc15",
        "Ascend": "#8b5cf6",
        "Meta Envelope": "#10b981",
    }
