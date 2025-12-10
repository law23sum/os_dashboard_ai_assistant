"""HyperDaemon systemic risk monitor bridging Sections 14.7 and 17.x."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from assistant_core.failure_registry import FailureRegistry, RiskBand, get_failure_registry
from assistant_core.spec_registry import get_default_registry


@dataclass
class RiskRecommendation:
    band: RiskBand
    message: str
    suggested_capsule: Optional[str] = None


class HyperDaemonRiskMonitor:
    """Aggregates failure signals into systemic risk recommendations."""

    def __init__(self, failure_registry: Optional[FailureRegistry] = None) -> None:
        self.failure_registry = failure_registry or get_failure_registry()
        registry = get_default_registry()
        registry.register_feature(
            "assistant_core.hyperdaemon.risk_monitor",
            sections=["14.7", "14.8", "17.5.6"],
            metadata={"module": __name__},
        )

    def get_systemic_risk_report(self) -> Dict[str, Any]:
        summary = self.failure_registry.summarize_events()
        recommendations = self._build_recommendations(summary)
        return {
            "summary": summary,
            "recommendations": [
                {**rec.__dict__, "band": rec.band.value} for rec in recommendations
            ],
        }

    def _build_recommendations(self, summary: Dict[str, Any]) -> list[RiskRecommendation]:
        recommendations: list[RiskRecommendation] = []
        risk_bands = summary.get("risk_bands", {})

        if risk_bands.get(RiskBand.RED.value, 0) > 0:
            recommendations.append(
                RiskRecommendation(
                    band=RiskBand.RED,
                    message="Critical failures detected across tenants. Escalate to Law-of-the-OS and enforce driver safety harnesses.",
                    suggested_capsule="capsule.governance.policy.rollback",
                )
            )
        if risk_bands.get(RiskBand.ORANGE.value, 0) > 0:
            recommendations.append(
                RiskRecommendation(
                    band=RiskBand.ORANGE,
                    message="Multiple high-severity automation issues present. Throttle risky workflows and require approvals.",
                    suggested_capsule="capsule.control.workflow.recovery",
                )
            )
        if not recommendations:
            recommendations.append(
                RiskRecommendation(
                    band=RiskBand.GREEN,
                    message="Risk posture nominal. Continue standard monitoring.",
                )
            )
        return recommendations


__all__ = ["HyperDaemonRiskMonitor", "RiskRecommendation"]
