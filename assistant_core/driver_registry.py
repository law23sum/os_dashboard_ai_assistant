"""Driver registry derived from the Driver Layer canon."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class DriverCapability:
    """High level action that a driver can take."""

    name: str
    description: str
    actions: List[str] = field(default_factory=list)


@dataclass
class DriverSpec:
    """Metadata captured for each driver defined in the spec."""

    id: str
    name: str
    layer: str
    driver_type: str
    description: str
    status: str = "ready"
    risk_tier: str = "medium"
    policy_tier: str = "internal"
    capabilities: List[DriverCapability] = field(default_factory=list)
    linked_capsules: List[str] = field(default_factory=list)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    manifest_path: Optional[str] = None
    notes: str = ""

    def heartbeat_age(self) -> timedelta:
        return datetime.utcnow() - self.last_heartbeat


class DriverRegistry:
    """In-memory registry capturing drivers defined by the AI OS spec."""

    def __init__(self) -> None:
        self._drivers: Dict[str, DriverSpec] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        add = self.register
        add(
            DriverSpec(
                id="drv-os",
                name="OS Driver",
                layer="OS",
                driver_type="os",
                description="Controls filesystem, processes, notifications, and host telemetry.",
                status="ready",
                risk_tier="medium",
                capabilities=[
                    DriverCapability(
                        name="Process orchestration",
                        description="Start/stop binaries, snapshot logs, capture evidence.",
                        actions=["spawn_process", "capture_stdout", "collect_logs"],
                    ),
                    DriverCapability(
                        name="Filesystem",
                        description="Read/write project trees with policy enforcement.",
                        actions=["read_file", "write_file", "watch_path"],
                    ),
                ],
                linked_capsules=["shell-capsule", "env-daemon"],
                notes="Primary bridge for local mode deployments.",
            )
        )
        add(
            DriverSpec(
                id="drv-software",
                name="Software Driver",
                layer="Software",
                driver_type="software",
                description="Controls Office/Google suites, browsers, Git, and SaaS APIs.",
                status="ready",
                risk_tier="high",
                capabilities=[
                    DriverCapability(
                        name="Document automation",
                        description="Generate briefs, reports, and spreadsheets via Office APIs.",
                        actions=["create_word_doc", "update_excel_range", "export_pdf"],
                    ),
                    DriverCapability(
                        name="Code systems",
                        description="Interact with Git repos, CI/CD, and package feeds.",
                        actions=["clone_repo", "open_pr", "trigger_ci"],
                    ),
                ],
                linked_capsules=["git-maintenance", "document-blueprint"],
                notes="Requires tenant-scoped secrets and audit policies.",
            )
        )
        add(
            DriverSpec(
                id="drv-ui",
                name="UI Automation Driver",
                layer="UI",
                driver_type="ui",
                description="Automates GUIs when APIs are unavailable (RPA-style).",
                status="calibrating",
                risk_tier="high",
                capabilities=[
                    DriverCapability(
                        name="Automation macros",
                        description="Replay clicks/keystrokes with safety checks.",
                        actions=["focus_window", "click", "type_text"],
                    )
                ],
                linked_capsules=["ui-repair"],
                notes="Used sparingly — requires Recorder evidence for auditors.",
            )
        )
        add(
            DriverSpec(
                id="drv-unix",
                name="Unix/System Execution Driver",
                layer="Unix",
                driver_type="unix",
                description="Runs shell commands, binaries, and scripts via policy-aware sandboxing.",
                status="ready",
                risk_tier="medium",
                capabilities=[
                    DriverCapability(
                        name="Shell orchestration",
                        description="Execute commands with env manifests and capture outputs.",
                        actions=["run_command", "apply_env", "capture_artifact"],
                    )
                ],
                linked_capsules=["shell-capsule", "ledger-audit"],
                notes="Tied directly to ledger logging and Evidence Packs.",
            )
        )
        add(
            DriverSpec(
                id="drv-package",
                name="Package & Environment Driver",
                layer="Package",
                driver_type="package",
                description="Installs, versions, and audits tools (brew, choco, apt, poetry).",
                status="ready",
                risk_tier="medium",
                capabilities=[
                    DriverCapability(
                        name="Manifest enforcement",
                        description="Install/update packages per Environment Manifest.",
                        actions=["install_package", "remove_package", "diff_env"],
                    ),
                    DriverCapability(
                        name="Drift detection",
                        description="Detect banned versions, vulnerability advisories, and drift.",
                        actions=["scan_versions", "report_vuln"],
                    ),
                ],
                linked_capsules=["env-daemon", "sim-lab"],
                notes="Feeds the EnvDaemon and ledger Evidence Packs.",
            )
        )
        add(
            DriverSpec(
                id="drv-data",
                name="Data/API Driver",
                layer="Data",
                driver_type="data",
                description="Connects databases, warehouses, telemetry feeds, and file APIs.",
                status="ready",
                risk_tier="medium",
                capabilities=[
                    DriverCapability(
                        name="Query execution",
                        description="Run param-safe queries and capture result sets.",
                        actions=["run_query", "export_dataset"],
                    ),
                    DriverCapability(
                        name="Telemetry ingestion",
                        description="Stream metrics/logs into CIRs.",
                        actions=["open_stream", "buffer_records"],
                    ),
                ],
                linked_capsules=["digital-twin", "finance-ledger"],
            )
        )
        add(
            DriverSpec(
                id="drv-research",
                name="Research & Simulation Driver",
                layer="Research",
                driver_type="research",
                description="Runs notebooks, MATLAB/Python/R simulations, CAD/CAE pipelines.",
                status="ready",
                risk_tier="medium",
                capabilities=[
                    DriverCapability(
                        name="Notebook execution",
                        description="Execute research notebooks with captured inputs/outputs.",
                        actions=["run_notebook", "capture_plot"],
                    ),
                    DriverCapability(
                        name="Simulation",
                        description="Trigger simulation capsules with digital twin hooks.",
                        actions=["launch_sim", "collect_results"],
                    ),
                ],
                linked_capsules=["sim-lab", "digital-twin"],
            )
        )
        add(
            DriverSpec(
                id="drv-govern",
                name="Governance Driver",
                layer="Governance",
                driver_type="governance",
                description="Enforces policies, audits, regulator feeds, and ledger exports.",
                status="ready",
                risk_tier="low",
                capabilities=[
                    DriverCapability(
                        name="Ledger evidence",
                        description="Attach Evidence Packs to regulators and subscribers.",
                        actions=["publish_evidence", "subscribe_regulator"],
                    )
                ],
                linked_capsules=["ledger-audit", "regulation"],
            )
        )

    # ------------------------------------------------------------------
    # Registry APIs
    # ------------------------------------------------------------------

    def register(self, spec: DriverSpec) -> None:
        self._drivers[spec.id] = spec

    def list_drivers(self) -> List[DriverSpec]:
        return list(self._drivers.values())

    def list_by_layer(self, layer: str) -> List[DriverSpec]:
        return [
            drv for drv in self._drivers.values() if drv.layer.lower() == layer.lower()
        ]

    def search(self, keyword: str) -> List[DriverSpec]:
        keyword = keyword.lower()
        matches = []
        for driver in self._drivers.values():
            haystack = " ".join(
                [
                    driver.name,
                    driver.layer,
                    driver.driver_type,
                    driver.description,
                    driver.notes,
                    " ".join(cap.name for cap in driver.capabilities),
                ]
            ).lower()
            if keyword in haystack:
                matches.append(driver)
        return matches

    def heartbeat(self, driver_id: str) -> None:
        if driver_id in self._drivers:
            self._drivers[driver_id].last_heartbeat = datetime.utcnow()

    def update_status(self, driver_id: str, status: str) -> None:
        if driver_id in self._drivers:
            self._drivers[driver_id].status = status

    def get(self, driver_id: str) -> Optional[DriverSpec]:
        return self._drivers.get(driver_id)


_driver_registry: Optional[DriverRegistry] = None


def get_driver_registry() -> DriverRegistry:
    global _driver_registry
    if _driver_registry is None:
        _driver_registry = DriverRegistry()
    return _driver_registry
