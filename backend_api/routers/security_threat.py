"""AI Security Threat Detection router."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from assistant_core.security.defense_orchestrator import SecurityDefenseOrchestrator

router = APIRouter()
security_orchestrator = SecurityDefenseOrchestrator()


class SecurityEvent(BaseModel):
    """Security threat event."""

    id: str
    type: str
    severity: str
    description: str
    timestamp: str
    source_ip: str
    status: str


class SecurityMetrics(BaseModel):
    """Security monitoring metrics."""

    scans_today: int
    threats_blocked: int
    risk_score: str
    false_positives: int
    detection_accuracy: float


class SecurityScan(BaseModel):
    """Security scan result."""

    id: str
    target: str
    status: str
    findings: int
    started_at: str
    completed_at: Optional[str]


class SecurityStatus(BaseModel):
    """Overall security system status."""

    system_status: str
    active_scans: int
    recent_events: List[SecurityEvent]
    metrics: SecurityMetrics
    last_scan: Optional[str]
    threat_detection_enabled: bool


class ScanRequest(BaseModel):
    target: str = "system"


class ConfigureRequest(BaseModel):
    detection_level: str = "balanced"
    auto_response: bool = True
    active_enforcement: bool = False
    alert_thresholds: Dict[str, Any] = Field(default_factory=dict)


class InvestigateRequest(BaseModel):
    event_id: str


@router.get("/security/status", response_model=SecurityStatus)
async def get_security_status() -> SecurityStatus:
    """Get AI security system status."""
    await security_orchestrator.initialize()
    status = await security_orchestrator.get_status()

    return SecurityStatus(
        system_status=status["system_status"],
        active_scans=status["active_scans"],
        recent_events=[SecurityEvent(**event) for event in status["recent_events"]],
        metrics=SecurityMetrics(**status["metrics"]),
        last_scan=status["last_scan"],
        threat_detection_enabled=status["threat_detection_enabled"],
    )


@router.post("/security/scan/start")
async def start_threat_scan(payload: ScanRequest) -> Dict[str, Any]:
    """Start a security threat scan."""
    scan = await security_orchestrator.start_scan(payload.target)

    return {
        "success": True,
        "scan_id": scan.scan_id,
        "message": f"Security threat scan completed for {scan.target}.",
        "estimated_completion_minutes": 0,
    }


@router.post("/security/report/view")
async def view_security_report() -> Dict[str, Any]:
    """View security report."""
    await security_orchestrator.initialize()
    return await security_orchestrator.get_report()


@router.post("/security/configure")
async def configure_security(payload: ConfigureRequest) -> Dict[str, Any]:
    """Configure security system settings."""
    return await security_orchestrator.configure(
        detection_level=payload.detection_level,
        auto_response=payload.auto_response,
        alert_thresholds=payload.alert_thresholds,
        active_enforcement=payload.active_enforcement,
    )


@router.post("/security/event/investigate")
async def investigate_threat(payload: InvestigateRequest) -> Dict[str, Any]:
    """Investigate a specific security event."""
    return await security_orchestrator.investigate_event(payload.event_id)


@router.post("/security/status/refresh")
async def refresh_security_status() -> SecurityStatus:
    """Refresh security system status."""
    return await get_security_status()
