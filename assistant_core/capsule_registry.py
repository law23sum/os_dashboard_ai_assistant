"""Capsule, Blueprint, and Evidence pack representations."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class EvidencePack:
    """Evidence bundle describing a Capsule execution."""

    id: str
    capsule_id: str
    summary: str
    artifacts: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    regulator_visibility: str = "internal"


@dataclass
class CapsuleSpec:
    """Executable Capsule defined in the spec."""

    id: str
    name: str
    description: str
    drivers: List[str]
    inputs: List[str]
    outputs: List[str]
    status: str = "ready"
    last_run: Optional[datetime] = None
    ledger_reference: Optional[str] = None
    category: str = "automation"


@dataclass
class BlueprintSpec:
    """Templatized Capsule bundle with policy context."""

    id: str
    name: str
    domain: str
    description: str
    capsules: List[str]
    default_drivers: List[str]
    policy_tier: str = "internal"
    marketplace_sku: Optional[str] = None


class CapsuleRegistry:
    """Tracks Capsules, Blueprints, and Evidence Packs."""

    def __init__(self) -> None:
        self.capsules: Dict[str, CapsuleSpec] = {}
        self.blueprints: Dict[str, BlueprintSpec] = {}
        self.evidence_packs: List[EvidencePack] = []
        self._load_defaults()

    def _load_defaults(self) -> None:
        self.add_capsule(
            CapsuleSpec(
                id="shell-capsule",
                name="Shell Capsule",
                description="Executes Unix driver actions with ledger logging and Evidence Packs.",
                drivers=["drv-unix", "drv-os"],
                inputs=["command", "env_manifest"],
                outputs=["stdout", "stderr", "artifacts"],
                category="system",
            )
        )
        self.add_capsule(
            CapsuleSpec(
                id="env-daemon",
                name="EnvDaemon",
                description="Monitors package manifests, repairs drift, and issues ledger notices.",
                drivers=["drv-package", "drv-govern"],
                inputs=["manifest", "policy"],
                outputs=["diff_report", "tickets"],
                category="automation",
            )
        )
        self.add_capsule(
            CapsuleSpec(
                id="git-maintenance",
                name="Git Maintenance Capsule",
                description="Runs Git hygiene operations, dependency scans, and Evidence Pack exports.",
                drivers=["drv-software", "drv-govern"],
                inputs=["repo", "policy"],
                outputs=["issue_report", "evidence_pack"],
                category="code",
            )
        )
        self.add_capsule(
            CapsuleSpec(
                id="document-blueprint",
                name="Document Blueprint Capsule",
                description="Generates meeting notes and project briefs via Software drivers.",
                drivers=["drv-software", "drv-os"],
                inputs=["template", "context"],
                outputs=["docx", "pdf"],
                category="documents",
            )
        )
        self.add_capsule(
            CapsuleSpec(
                id="sim-lab",
                name="Simulation Lab Capsule",
                description="Runs research simulations and captures CIR outputs.",
                drivers=["drv-research", "drv-data"],
                inputs=["model", "parameters"],
                outputs=["results", "plots", "cir"],
                category="research",
            )
        )
        self.add_capsule(
            CapsuleSpec(
                id="digital-twin",
                name="Digital Twin Capsule",
                description="Maintains a live digital twin with telemetry ingestion and scenario planning.",
                drivers=["drv-research", "drv-data"],
                inputs=["telemetry", "scenario"],
                outputs=["forecast", "evidence_pack"],
                category="simulation",
            )
        )

        self.add_blueprint(
            BlueprintSpec(
                id="founder-blueprint",
                name="Founder Blueprint",
                domain="startup",
                description="Capsule pack for a founder: doc automation, git hygiene, finance ledgers.",
                capsules=["git-maintenance", "document-blueprint", "env-daemon"],
                default_drivers=["drv-os", "drv-software", "drv-package"],
                policy_tier="internal",
                marketplace_sku="BP-FOUNDER",
            )
        )
        self.add_blueprint(
            BlueprintSpec(
                id="lab-blueprint",
                name="Research Lab Blueprint",
                domain="research",
                description="Simulation + documentation + ledger pack for labs and auditors.",
                capsules=["sim-lab", "digital-twin", "document-blueprint"],
                default_drivers=["drv-research", "drv-data", "drv-govern"],
                policy_tier="regulated",
                marketplace_sku="BP-LAB",
            )
        )

    # ------------------------------------------------------------------
    # Registry APIs
    # ------------------------------------------------------------------

    def add_capsule(self, capsule: CapsuleSpec) -> None:
        self.capsules[capsule.id] = capsule

    def add_blueprint(self, blueprint: BlueprintSpec) -> None:
        self.blueprints[blueprint.id] = blueprint

    def list_capsules(self) -> List[CapsuleSpec]:
        return list(self.capsules.values())

    def list_blueprints(self) -> List[BlueprintSpec]:
        return list(self.blueprints.values())

    def list_capsules_by_driver(self, driver_id: str) -> List[CapsuleSpec]:
        return [cap for cap in self.capsules.values() if driver_id in cap.drivers]

    def log_capsule_run(
        self, capsule_id: str, summary: str, artifacts: List[str]
    ) -> EvidencePack:
        capsule = self.capsules.get(capsule_id)
        if capsule:
            capsule.last_run = datetime.utcnow()
            capsule.ledger_reference = (
                f"LEDGER-{capsule_id}-{capsule.last_run.strftime('%Y%m%d%H%M%S')}"
            )
        pack = EvidencePack(
            id=f"EVID-{len(self.evidence_packs)+1:04d}",
            capsule_id=capsule_id,
            summary=summary,
            artifacts=artifacts,
        )
        self.evidence_packs.append(pack)
        return pack

    def list_evidence(self, capsule_id: Optional[str] = None) -> List[EvidencePack]:
        if not capsule_id:
            return list(self.evidence_packs)
        return [pack for pack in self.evidence_packs if pack.capsule_id == capsule_id]


_capsule_registry: Optional[CapsuleRegistry] = None


def get_capsule_registry() -> CapsuleRegistry:
    global _capsule_registry
    if _capsule_registry is None:
        _capsule_registry = CapsuleRegistry()
    return _capsule_registry
