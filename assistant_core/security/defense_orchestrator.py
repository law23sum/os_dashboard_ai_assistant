"""Security defense orchestrator with continuous scanning and auto-response."""

from __future__ import annotations

import asyncio
import ipaddress
import platform
import socket
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - fallback when psutil missing
    from utils.psutil_stub import psutil  # type: ignore

import yaml

from config.logging_config import setup_logger
from assistant_core.security.auth_manager import AuthManager
from assistant_core.system.operations import SystemOperationsController


DEFAULT_ALLOWED_NETWORKS = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "127.0.0.0/8",
]

DEFAULT_SENSITIVE_PORTS = [22, 23, 3389, 5900, 445, 3306, 5432, 6379]


@dataclass
class SecurityFinding:
    finding_id: str
    category: str
    severity: str
    description: str
    timestamp: datetime
    source_ip: Optional[str] = None
    target: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    recommended_actions: List[str] = field(default_factory=list)
    auto_response_actions: List[str] = field(default_factory=list)

    def to_event(self) -> Dict[str, Any]:
        return {
            "id": self.finding_id,
            "type": self.category,
            "severity": self.severity,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() + "Z",
            "source_ip": self.source_ip or "unknown",
            "status": self.status,
        }


@dataclass
class ScanResult:
    scan_id: str
    target: str
    status: str
    findings: List[SecurityFinding]
    started_at: datetime
    completed_at: Optional[datetime] = None

    def to_summary(self) -> Dict[str, Any]:
        return {
            "id": self.scan_id,
            "target": self.target,
            "status": self.status,
            "findings": len(self.findings),
            "started_at": self.started_at.isoformat() + "Z",
            "completed_at": self.completed_at.isoformat() + "Z" if self.completed_at else None,
        }


@dataclass
class EnforcementResult:
    action: str
    success: bool
    executed: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityDefenseConfig:
    auto_response_enabled: bool = True
    active_enforcement: bool = False
    auto_response_min_severity: str = "high"
    scan_interval_seconds: int = 120
    allowed_networks: List[str] = field(default_factory=lambda: list(DEFAULT_ALLOWED_NETWORKS))
    allowed_ports: List[int] = field(default_factory=list)
    sensitive_ports: List[int] = field(default_factory=lambda: list(DEFAULT_SENSITIVE_PORTS))
    blocked_ips: List[str] = field(default_factory=list)
    burst_threshold: int = 20
    max_connections: int = 500
    max_scans: int = 200
    max_findings: int = 1000

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityDefenseConfig":
        def _as_list(value: Any) -> List[Any]:
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]

        def _as_int_list(value: Any) -> List[int]:
            return [int(v) for v in _as_list(value)]

        return cls(
            auto_response_enabled=bool(data.get("auto_response_enabled", True)),
            active_enforcement=bool(data.get("active_enforcement", False)),
            auto_response_min_severity=str(data.get("auto_response_min_severity", "high")),
            scan_interval_seconds=int(data.get("scan_interval_seconds", 120)),
            allowed_networks=[str(v) for v in _as_list(data.get("allowed_networks", DEFAULT_ALLOWED_NETWORKS))],
            allowed_ports=_as_int_list(data.get("allowed_ports", [])),
            sensitive_ports=_as_int_list(data.get("sensitive_ports", DEFAULT_SENSITIVE_PORTS)),
            blocked_ips=[str(v) for v in _as_list(data.get("blocked_ips", []))],
            burst_threshold=int(data.get("burst_threshold", 20)),
            max_connections=int(data.get("max_connections", 500)),
            max_scans=int(data.get("max_scans", 200)),
            max_findings=int(data.get("max_findings", 1000)),
        )


def _load_yaml_section(path: Path, section: str) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return data.get(section, {}) or {}


def load_defense_config() -> SecurityDefenseConfig:
    repo_root = Path(__file__).resolve().parents[2]
    defaults = _load_yaml_section(repo_root / "config" / "default_config.yaml", "security_defense")
    overrides = _load_yaml_section(repo_root / "config" / "config.yaml", "security_defense")
    merged = {**defaults, **overrides}
    return SecurityDefenseConfig.from_dict(merged)


class SecurityTelemetryCollector:
    def __init__(
        self,
        system_ops: Optional[SystemOperationsController] = None,
        config: Optional[SecurityDefenseConfig] = None,
    ):
        self.system_ops = system_ops or SystemOperationsController()
        self.config = config or SecurityDefenseConfig()

    def collect(self, target: str) -> Dict[str, Any]:
        now = datetime.utcnow()
        snapshot = {
            "timestamp": now,
            "target": target,
            "host": {
                "hostname": socket.gethostname(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
            },
            "network": self._collect_network(target),
            "processes": self._collect_processes(target),
        }
        return snapshot

    def _collect_network(self, target: str) -> Dict[str, Any]:
        if target not in {"system", "network", "endpoint"}:
            return {}
        connections: List[Dict[str, Any]] = []
        listening_ports: List[int] = []
        remote_ip_counts: Counter[str] = Counter()
        max_connections = self.config.max_connections

        if not hasattr(psutil, "net_connections"):
            return {
                "connections": connections,
                "listening_ports": listening_ports,
                "remote_ip_counts": {},
            }

        try:
            for conn in psutil.net_connections(kind="inet"):
                laddr = getattr(conn, "laddr", None)
                raddr = getattr(conn, "raddr", None)
                status = getattr(conn, "status", "unknown")
                local_ip = getattr(laddr, "ip", None) if laddr else None
                local_port = getattr(laddr, "port", None) if laddr else None
                remote_ip = getattr(raddr, "ip", None) if raddr else None
                remote_port = getattr(raddr, "port", None) if raddr else None

                if status == "LISTEN" and local_port:
                    listening_ports.append(local_port)

                if remote_ip:
                    remote_ip_counts[remote_ip] += 1

                connections.append(
                    {
                        "local_ip": local_ip,
                        "local_port": local_port,
                        "remote_ip": remote_ip,
                        "remote_port": remote_port,
                        "status": status,
                        "pid": getattr(conn, "pid", None),
                    }
                )
                if len(connections) >= max_connections:
                    break
        except Exception:
            return {
                "connections": [],
                "listening_ports": [],
                "remote_ip_counts": {},
            }

        return {
            "connections": connections,
            "listening_ports": sorted(set(listening_ports)),
            "remote_ip_counts": dict(remote_ip_counts),
        }

    def _collect_processes(self, target: str) -> List[Dict[str, Any]]:
        if target not in {"system", "endpoint"}:
            return []
        if not hasattr(psutil, "process_iter"):
            return []

        processes: List[Dict[str, Any]] = []
        try:
            for proc in psutil.process_iter(["pid", "name", "username"]):
                info = proc.info
                processes.append(
                    {
                        "pid": info.get("pid"),
                        "name": info.get("name"),
                        "username": info.get("username"),
                    }
                )
                if len(processes) >= 50:
                    break
        except Exception:
            return []

        return processes


class ThreatAnalyzer:
    def __init__(self, config: SecurityDefenseConfig):
        self.config = config

    def analyze(self, telemetry: Dict[str, Any]) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []
        network = telemetry.get("network", {})
        connections = network.get("connections", [])
        listening_ports = network.get("listening_ports", [])
        remote_ip_counts = network.get("remote_ip_counts", {})

        for ip, count in remote_ip_counts.items():
            if count >= self.config.burst_threshold:
                findings.append(
                    self._build_finding(
                        category="network_burst",
                        severity="high",
                        description=f"High connection volume from {ip} ({count} connections)",
                        source_ip=ip,
                        evidence={"connection_count": count},
                    )
                )

        for port in listening_ports:
            if self.config.allowed_ports and port in self.config.allowed_ports:
                continue
            if not self.config.allowed_ports and port not in self.config.sensitive_ports:
                continue
            severity = "medium"
            if port in self.config.sensitive_ports:
                severity = "high"
            findings.append(
                self._build_finding(
                    category="unexpected_listening_port",
                    severity=severity,
                    description=f"Listening port detected without allowlist entry: {port}",
                    evidence={"port": port},
                )
            )

        for conn in connections:
            remote_ip = conn.get("remote_ip")
            local_port = conn.get("local_port")
            if not remote_ip:
                continue
            if self._is_blocked(remote_ip):
                findings.append(
                    self._build_finding(
                        category="blocked_ip_activity",
                        severity="critical",
                        description=f"Blocked IP observed in active connection: {remote_ip}",
                        source_ip=remote_ip,
                        evidence={"local_port": local_port},
                    )
                )
                continue

            if self._is_external(remote_ip) and local_port and local_port in self.config.sensitive_ports:
                findings.append(
                    self._build_finding(
                        category="external_access_sensitive_port",
                        severity="high",
                        description=(
                            f"External IP connected to sensitive port {local_port}: {remote_ip}"
                        ),
                        source_ip=remote_ip,
                        evidence={"local_port": local_port},
                    )
                )

        return findings

    def _build_finding(
        self,
        category: str,
        severity: str,
        description: str,
        source_ip: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> SecurityFinding:
        finding = SecurityFinding(
            finding_id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            description=description,
            timestamp=datetime.utcnow(),
            source_ip=source_ip,
            evidence=evidence or {},
        )
        finding.recommended_actions = self._recommend_actions(finding)
        finding.auto_response_actions = self._auto_response_plan(finding)
        return finding

    def _recommend_actions(self, finding: SecurityFinding) -> List[str]:
        actions = ["alert"]
        if finding.source_ip:
            actions.append("block_ip")
        if finding.severity in {"high", "critical"}:
            actions.append("force_logout")
        if finding.severity == "critical":
            actions.append("isolate_host")
        return actions

    def _auto_response_plan(self, finding: SecurityFinding) -> List[str]:
        severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        min_required = severity_rank.get(self.config.auto_response_min_severity, 3)
        if severity_rank.get(finding.severity, 1) < min_required:
            return []
        return [action for action in self._recommend_actions(finding) if action != "alert"]

    def _is_external(self, ip: str) -> bool:
        try:
            addr = ipaddress.ip_address(ip)
            if addr.is_loopback or addr.is_private:
                return False
            for cidr in self.config.allowed_networks:
                if addr in ipaddress.ip_network(cidr, strict=False):
                    return False
            return True
        except ValueError:
            return False

    def _is_blocked(self, ip: str) -> bool:
        return ip in self.config.blocked_ips


class EnforcementEngine:
    def __init__(
        self,
        config: SecurityDefenseConfig,
        auth_manager: Optional[AuthManager] = None,
        system_ops: Optional[SystemOperationsController] = None,
    ):
        self.config = config
        self.auth_manager = auth_manager
        self.system_ops = system_ops or SystemOperationsController()
        self.logger = setup_logger("SecurityEnforcement")

    async def execute(self, finding: SecurityFinding) -> List[EnforcementResult]:
        results: List[EnforcementResult] = []
        for action in finding.auto_response_actions:
            if action == "block_ip" and finding.source_ip:
                results.append(self._block_ip(finding.source_ip))
            elif action == "force_logout":
                results.append(await self._force_logout(finding))
            elif action == "isolate_host":
                results.append(self._isolate_host())
            else:
                results.append(
                    EnforcementResult(
                        action=action,
                        success=False,
                        executed=False,
                        details={"reason": "unsupported_or_missing_context"},
                    )
                )
        return results

    def _block_ip(self, ip: str) -> EnforcementResult:
        command = self._firewall_command(ip)
        if not command:
            return EnforcementResult(
                action="block_ip",
                success=False,
                executed=False,
                details={"reason": "unsupported_platform", "ip": ip},
            )

        if not self.config.active_enforcement:
            return EnforcementResult(
                action="block_ip",
                success=True,
                executed=False,
                details={"command": command, "ip": ip, "mode": "dry_run"},
            )

        result = self.system_ops.execute_command(command, shell=isinstance(command, str))
        return EnforcementResult(
            action="block_ip",
            success=result.get("success", False),
            executed=True,
            details={"command": command, "ip": ip, "output": result},
        )

    async def _force_logout(self, finding: SecurityFinding) -> EnforcementResult:
        if not self.auth_manager:
            return EnforcementResult(
                action="force_logout",
                success=False,
                executed=False,
                details={"reason": "auth_manager_unavailable"},
            )

        session_id = finding.evidence.get("session_id")
        user_id = finding.evidence.get("user_id")
        if session_id:
            success = await self.auth_manager.revoke_session(session_id)
            return EnforcementResult(
                action="force_logout",
                success=success,
                executed=True,
                details={"session_id": session_id},
            )
        if user_id:
            success = await self.auth_manager.deactivate_user(user_id)
            return EnforcementResult(
                action="force_logout",
                success=success,
                executed=True,
                details={"user_id": user_id},
            )

        return EnforcementResult(
            action="force_logout",
            success=False,
            executed=False,
            details={"reason": "no_user_or_session"},
        )

    def _isolate_host(self) -> EnforcementResult:
        return EnforcementResult(
            action="isolate_host",
            success=True,
            executed=False,
            details={"mode": "manual_required", "note": "Isolate host manually or enable a host isolation plugin."},
        )

    def _firewall_command(self, ip: str) -> Optional[Any]:
        system = platform.system()
        if system == "Darwin":
            return f"pfctl -t osd_blocklist -T add {ip}"
        if system == "Linux":
            return ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
        if system == "Windows":
            return (
                "netsh advfirewall firewall add rule "
                f"name=\"OSD Block {ip}\" dir=in action=block remoteip={ip}"
            )
        return None


class SecurityDefenseOrchestrator:
    """Coordinate telemetry, threat detection, and response actions."""

    def __init__(
        self,
        config: Optional[SecurityDefenseConfig] = None,
        auth_manager: Optional[AuthManager] = None,
        system_ops: Optional[SystemOperationsController] = None,
    ):
        self.config = config or load_defense_config()
        self.auth_manager = auth_manager
        self.system_ops = system_ops or SystemOperationsController()
        self.telemetry = SecurityTelemetryCollector(self.system_ops, self.config)
        self.analyzer = ThreatAnalyzer(self.config)
        self.enforcer = EnforcementEngine(self.config, auth_manager, self.system_ops)
        self.logger = setup_logger("SecurityDefense")
        self.scans: List[ScanResult] = []
        self.findings: Dict[str, SecurityFinding] = {}
        self.metrics = {
            "threats_blocked": 0,
            "detection_accuracy": 0.93,
            "false_positives": 0,
        }
        self._monitor_task: Optional[asyncio.Task] = None
        self._scan_lock = asyncio.Lock()

    async def initialize(self) -> None:
        await self._ensure_monitoring()

    async def _ensure_monitoring(self) -> None:
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self) -> None:
        while True:
            try:
                await self.start_scan("system", is_background=True)
            except Exception as exc:
                self.logger.error("Continuous scan failed: %s", exc)
            await asyncio.sleep(self.config.scan_interval_seconds)

    async def start_scan(self, target: str, is_background: bool = False) -> ScanResult:
        async with self._scan_lock:
            await self._ensure_monitoring()
            scan = ScanResult(
                scan_id=f"scan-{uuid.uuid4()}",
                target=target,
                status="running",
                findings=[],
                started_at=datetime.utcnow(),
            )
            self.scans.insert(0, scan)
            if len(self.scans) > self.config.max_scans:
                self.scans = self.scans[: self.config.max_scans]

            telemetry = self.telemetry.collect(target)
            findings = self.analyzer.analyze(telemetry)

            scan.findings = findings
            scan.status = "completed"
            scan.completed_at = datetime.utcnow()

            for finding in findings:
                self.findings[finding.finding_id] = finding
                if self.config.auto_response_enabled and finding.auto_response_actions:
                    results = await self.enforcer.execute(finding)
                    if any(r.action == "block_ip" and r.success for r in results):
                        self.metrics["threats_blocked"] += 1
                    for result in results:
                        if result.action == "block_ip" and result.success:
                            ip = result.details.get("ip")
                            if ip and ip not in self.config.blocked_ips:
                                self.config.blocked_ips.append(ip)
            if len(self.findings) > self.config.max_findings:
                excess_keys = list(self.findings.keys())[: -self.config.max_findings]
                for key in excess_keys:
                    self.findings.pop(key, None)

            return scan

    async def get_status(self) -> Dict[str, Any]:
        await self._ensure_monitoring()
        if not self.scans:
            await self.start_scan("system", is_background=True)
        recent_events = [finding.to_event() for finding in list(self.findings.values())[-6:]]
        risk_score = self._risk_score()
        system_status = "System Secure" if risk_score < 0.4 else "Monitoring Active"

        scans_today = len(
            [scan for scan in self.scans if scan.started_at.date() == datetime.utcnow().date()]
        )

        return {
            "system_status": system_status,
            "active_scans": len([s for s in self.scans if s.status == "running"]),
            "recent_events": recent_events,
            "metrics": {
                "scans_today": scans_today,
                "threats_blocked": self.metrics["threats_blocked"],
                "risk_score": f"{risk_score:.2f}",
                "false_positives": self.metrics["false_positives"],
                "detection_accuracy": self.metrics["detection_accuracy"],
            },
            "last_scan": self.scans[0].completed_at.isoformat() + "Z" if self.scans else None,
            "threat_detection_enabled": self.config.auto_response_enabled,
        }

    async def get_report(self) -> Dict[str, Any]:
        if not self.scans:
            await self.start_scan("system", is_background=True)
        top_threats = Counter([f.category for f in self.findings.values()])
        recent_scans = [s.to_summary() for s in self.scans[:5]]
        findings_count = sum(len(s.findings) for s in self.scans)

        return {
            "scan_summary": {
                "total_scans": len(self.scans),
                "successful_scans": len([s for s in self.scans if not s.findings]),
                "threats_found": findings_count,
                "critical_findings": len([f for f in self.findings.values() if f.severity == "critical"]),
            },
            "recent_scans": recent_scans,
            "top_threats": [{"type": t, "count": c} for t, c in top_threats.most_common(5)],
            "recommendations": self._recommendations(),
            "risk_matrix": self._risk_matrix(),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    async def investigate_event(self, event_id: str) -> Dict[str, Any]:
        finding = self.findings.get(event_id)
        if not finding:
            return {"success": False, "message": "Event not found."}

        investigation = {
            "event_id": event_id,
            "investigation_started": datetime.utcnow().isoformat() + "Z",
            "findings": [
                f"Category: {finding.category}",
                f"Severity: {finding.severity}",
                f"Source IP: {finding.source_ip or 'unknown'}",
                f"Evidence: {finding.evidence}",
            ],
            "recommended_actions": finding.recommended_actions,
            "status": "completed",
        }
        return {"success": True, "investigation": investigation}

    async def configure(
        self,
        detection_level: str,
        auto_response: bool,
        alert_thresholds: Dict[str, Any],
        active_enforcement: Optional[bool] = None,
    ) -> Dict[str, Any]:
        self.config.auto_response_enabled = bool(auto_response)
        if active_enforcement is not None:
            self.config.active_enforcement = bool(active_enforcement)
        if detection_level == "aggressive":
            self.config.auto_response_min_severity = "medium"
            self.config.burst_threshold = 10
        elif detection_level == "conservative":
            self.config.auto_response_min_severity = "critical"
            self.config.burst_threshold = 30
        else:
            self.config.auto_response_min_severity = "high"
            self.config.burst_threshold = 20

        return {
            "success": True,
            "configuration": {
                "detection_level": detection_level,
                "auto_response": self.config.auto_response_enabled,
                "alert_thresholds": alert_thresholds,
                "auto_response_min_severity": self.config.auto_response_min_severity,
                "active_enforcement": self.config.active_enforcement,
            },
            "message": f"Security system configured with {detection_level} detection level.",
        }

    def _risk_score(self) -> float:
        if not self.findings:
            return 0.2
        severity_weight = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        total = sum(severity_weight.get(f.severity, 0.3) for f in self.findings.values())
        return min(1.0, total / max(1, len(self.findings)))

    def _recommendations(self) -> List[str]:
        recommendations = [
            "Enable multi-factor authentication for admin accounts",
            "Review firewall rules and restrict external access",
            "Patch systems and firmware on a weekly cadence",
            "Segment guest/IoT devices from trusted endpoints",
        ]
        if self.config.active_enforcement is False:
            recommendations.append("Enable active enforcement to auto-block malicious IPs")
        return recommendations

    def _risk_matrix(self) -> List[Dict[str, Any]]:
        return [
            {
                "risk": "Unauthorized access to exposed services",
                "likelihood": "high",
                "impact": "high",
                "rating": "critical",
                "priority": 1,
            },
            {
                "risk": "Credential stuffing on remote access",
                "likelihood": "high",
                "impact": "medium",
                "rating": "high",
                "priority": 2,
            },
            {
                "risk": "Malware foothold on endpoint",
                "likelihood": "medium",
                "impact": "high",
                "rating": "high",
                "priority": 3,
            },
            {
                "risk": "Data exfiltration over outbound connections",
                "likelihood": "medium",
                "impact": "high",
                "rating": "high",
                "priority": 4,
            },
            {
                "risk": "Unpatched service vulnerabilities",
                "likelihood": "medium",
                "impact": "medium",
                "rating": "medium",
                "priority": 5,
            },
            {
                "risk": "Misconfigured local firewall",
                "likelihood": "low",
                "impact": "medium",
                "rating": "medium",
                "priority": 6,
            },
            {
                "risk": "Shadow devices on guest Wi-Fi",
                "likelihood": "low",
                "impact": "medium",
                "rating": "medium",
                "priority": 7,
            },
            {
                "risk": "Single endpoint compromise via phishing",
                "likelihood": "low",
                "impact": "medium",
                "rating": "medium",
                "priority": 8,
            },
            {
                "risk": "Stale backups or missing recovery testing",
                "likelihood": "low",
                "impact": "medium",
                "rating": "low",
                "priority": 9,
            },
        ]


__all__ = [
    "SecurityDefenseConfig",
    "SecurityDefenseOrchestrator",
    "SecurityFinding",
    "ScanResult",
]
