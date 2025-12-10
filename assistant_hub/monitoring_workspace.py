"""Shared monitoring workspace for desktop + web surfaces."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class MonitoringEvent:
    id: str
    action: str
    status: str
    detail: str
    timestamp: str


@dataclass
class MonitoringAlert:
    metric: str
    severity: str
    value: float
    threshold: float
    timestamp: str


class MonitoringWorkspaceState:
    """Synthetic monitoring state used by Tkinter + FastAPI + React."""

    def __init__(self) -> None:
        self.metrics: Dict[str, float] = {
            "cpu": 62.5,
            "memory": 74.3,
            "disk": 48.1,
            "network": 35.2,
        }
        self.thresholds: Dict[str, float] = {"cpu": 80, "memory": 85, "disk": 90, "network": 70}
        self.window_hours: int = 24
        self.alerts: List[MonitoringAlert] = []
        self.events: List[MonitoringEvent] = []
        self._seed_events()

    def _seed_events(self) -> None:
        now = datetime.now(timezone.utc)
        for idx in range(4):
            self.events.append(
                MonitoringEvent(
                    id=f"evt-{idx+1}",
                    action="check_health" if idx % 2 == 0 else "detect_anomalies",
                    status="success",
                    detail="Baseline telemetry collected" if idx % 2 == 0 else "No anomalies detected",
                    timestamp=(now).isoformat(),
                )
            )

    def snapshot(self) -> Dict[str, object]:
        score = max(0, 100 - ((self.metrics["cpu"] + self.metrics["memory"]) / 2) * 0.6)
        return {
            "window_hours": self.window_hours,
            "metrics": dict(self.metrics),
            "thresholds": dict(self.thresholds),
            "health_score": round(score, 1),
            "alerts": [alert.__dict__ for alert in self.alerts[-10:]],
            "events": [event.__dict__ for event in self.events[-25:]],
        }

    def run_action(
        self,
        action: str,
        system_metrics: Dict[str, float] | None = None,
        monitoring_window: int | None = None,
        alert_thresholds: Dict[str, float] | None = None,
    ) -> Dict[str, object]:
        if system_metrics:
            self.metrics.update(system_metrics)
        if alert_thresholds:
            self.thresholds.update(alert_thresholds)
        if monitoring_window:
            self.window_hours = monitoring_window

        result = {
            "action": action,
            "status": "success",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "notes": [],
        }

        if action == "detect_anomalies":
            anomalies = self._detect_anomalies()
            result["anomalies"] = anomalies
            result["notes"].append(
                f"Detected {len(anomalies)} potential anomalies" if anomalies else "No anomalies detected"
            )
        elif action == "predictive_maintenance":
            prediction = self._predict_failure()
            result["maintenance_window"] = prediction
            result["notes"].append("Scheduled maintenance window updated")
        elif action == "self_heal":
            actions = self._self_heal()
            result["remediation_steps"] = actions
            result["notes"].append("Self-healing actions applied")
        else:  # check_health
            health = self._calculate_health()
            result["health_snapshot"] = health
            result["notes"].append("Health metrics recalculated")

        outcome = json.dumps(result, default=str)
        self.events.append(
            MonitoringEvent(
                id=f"evt-{len(self.events)+1}",
                action=action,
                status="success",
                detail=outcome[:120] + ("…" if len(outcome) > 120 else ""),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        )
        self._trim_history()
        return result

    def _detect_anomalies(self) -> List[Dict[str, object]]:
        anomalies = []
        for metric, value in self.metrics.items():
            threshold = self.thresholds.get(metric, 90)
            if value >= threshold:
                alert = MonitoringAlert(
                    metric=metric,
                    severity="critical" if value >= threshold + 10 else "warning",
                    value=value,
                    threshold=threshold,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
                self.alerts.append(alert)
                anomalies.append(alert.__dict__)
        return anomalies

    def _predict_failure(self) -> Dict[str, object]:
        window = random.randint(4, 24)
        metric = max(self.metrics, key=self.metrics.get)
        return {
            "metric": metric,
            "window_hours": window,
            "confidence": round(random.uniform(70, 95), 1),
        }

    def _self_heal(self) -> List[str]:
        actions = [
            "Rebalanced workload across nodes",
            "Restarted degraded container",
            "Cleared cache on compute cluster",
        ]
        random.shuffle(actions)
        return actions[:2]

    def _calculate_health(self) -> Dict[str, object]:
        load = sum(self.metrics.values()) / len(self.metrics)
        return {
            "average_load": round(load, 2),
            "max_metric": max(self.metrics, key=self.metrics.get),
            "min_metric": min(self.metrics, key=self.metrics.get),
        }

    def _trim_history(self) -> None:
        self.events = self.events[-50:]
        self.alerts = self.alerts[-50:]
