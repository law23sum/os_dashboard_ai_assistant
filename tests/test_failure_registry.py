from assistant_core.failure_registry import (
    FailureLayer,
    FailurePlane,
    FailureRegistry,
    FailureRootCause,
    FailureScope,
    FailureSeverity,
    RiskBand,
)
from assistant_core.hyperdaemon.risk_monitor import HyperDaemonRiskMonitor


def test_failure_registry_records_events_and_risk_scores() -> None:
    registry = FailureRegistry()
    registry.register_recovery_plan(
        "test_plan", "capsule.test.recovery", "Test recovery capsule", tags=["unit"]
    )

    event = registry.record_event(
        plane=FailurePlane.CONTROL,
        layer=FailureLayer.DOMAIN,
        scope=FailureScope.PROJECT,
        severity=FailureSeverity.SEV2,
        root_cause=FailureRootCause.DEPENDENCY_FAILURE,
        description="Workflow stuck due to dependency outage",
        metadata={"workflow_id": "wf-123"},
        recovery_plan="test_plan",
        risk_inputs={"impact": 4, "likelihood": 3, "scope": 2, "control_strength": 3},
    )

    assert event.risk_score is not None
    assert event.risk_score.band in (RiskBand.GREEN, RiskBand.YELLOW, RiskBand.ORANGE, RiskBand.RED)
    summary = registry.summarize_events()
    assert summary["total"] == 1
    assert summary["by_plane"]["control"] == 1
    assert registry.get_recovery_plan("test_plan")["capsule_id"] == "capsule.test.recovery"


def test_failure_registry_signals_are_tracked() -> None:
    registry = FailureRegistry()
    registry.ingest_signal(
        source="policy_engine",
        metric="deny_rate",
        value=0.45,
        threshold=0.3,
        tenant_id="tenant-123",
    )
    summary = registry.summarize_signals()
    assert summary["total"] == 1
    assert summary["recent"][0]["metric"] == "deny_rate"


def test_hyperdaemon_monitor_reports_nominal_when_no_events() -> None:
    registry = FailureRegistry()
    monitor = HyperDaemonRiskMonitor(registry)
    report = monitor.get_systemic_risk_report()
    assert report["summary"]["total"] == 0
    assert report["recommendations"][0]["band"] == RiskBand.GREEN.value
