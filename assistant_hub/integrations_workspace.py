"""Shared state for integrations + infrastructure surfaces."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class IntegrationConnector:
    id: str
    name: str
    category: str
    status: str
    connected: bool
    last_sync: str
    latency_ms: int
    throughput: str
    targets: List[str] = field(default_factory=list)
    notes: str = ""
    health: str = "healthy"


@dataclass
class IntegrationPipeline:
    id: str
    name: str
    status: str
    throughput: str
    latency_ms: int
    last_run: str


@dataclass
class IntegrationIncident:
    id: str
    title: str
    severity: str
    connector: str
    detail: str
    timestamp: str


@dataclass
class IntegrationActivity:
    id: str
    connector: str
    action: str
    status: str
    detail: str
    timestamp: str


class IntegrationsWorkspaceState:
    """Mutable in-memory model for integrations dashboard."""

    def __init__(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.connectors: List[IntegrationConnector] = [
            IntegrationConnector(
                id="graph",
                name="Microsoft Graph",
                category="Productivity",
                status="connected",
                connected=True,
                last_sync=now,
                latency_ms=210,
                throughput="6.2 MB/s",
                targets=["Outlook", "SharePoint", "OneDrive"],
                notes="Used for calendar + mail ingest",
            ),
            IntegrationConnector(
                id="github",
                name="GitHub",
                category="DevOps",
                status="degraded",
                connected=True,
                last_sync=now,
                latency_ms=480,
                throughput="1.8 MB/s",
                targets=["Repos", "Actions"],
                notes="PAT rotating in 3 days",
                health="warning",
            ),
            IntegrationConnector(
                id="gmail",
                name="Gmail",
                category="Comms",
                status="disconnected",
                connected=False,
                last_sync="",
                latency_ms=0,
                throughput="0",
                targets=["Inbox", "Calendar"],
                notes="Waiting for OAuth consent",
                health="critical",
            ),
            IntegrationConnector(
                id="slack",
                name="Slack",
                category="Collaboration",
                status="connected",
                connected=True,
                last_sync=now,
                latency_ms=134,
                throughput="3.1 MB/s",
                targets=["Channels", "Apps"],
            ),
        ]
        self.pipelines: List[IntegrationPipeline] = [
            IntegrationPipeline(
                id="etl-1",
                name="Notes ↔️ Knowledge Lake",
                status="healthy",
                throughput="12 docs/min",
                latency_ms=320,
                last_run=now,
            ),
            IntegrationPipeline(
                id="etl-2",
                name="Calendar Sync",
                status="warning",
                throughput="3 events/min",
                latency_ms=850,
                last_run=now,
            ),
        ]
        self.incidents: List[IntegrationIncident] = [
            IntegrationIncident(
                id="inc-1",
                title="API quota nearing limit",
                severity="warning",
                connector="github",
                detail="90% of hourly quota consumed",
                timestamp=now,
            ),
        ]
        self.activity: List[IntegrationActivity] = []

    # -- helpers -------------------------------------------------------------
    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def snapshot(self) -> Dict[str, object]:
        connected = sum(1 for c in self.connectors if c.connected)
        degraded = sum(1 for c in self.connectors if c.status == "degraded")
        summary = {
            "total": len(self.connectors),
            "connected": connected,
            "degraded": degraded,
            "disconnected": len(self.connectors) - connected,
        }
        activity = [activity.__dict__ for activity in reversed(self.activity[-20:])]
        return {
            "summary": summary,
            "connectors": [connector.__dict__ for connector in self.connectors],
            "pipelines": [pipeline.__dict__ for pipeline in self.pipelines],
            "incidents": [incident.__dict__ for incident in self.incidents],
            "activity": activity,
        }

    def toggle_connection(self, connector_id: str, connect: bool) -> IntegrationConnector | None:
        connector = self._find(connector_id)
        if not connector:
            return None
        connector.connected = connect
        connector.status = "connected" if connect else "disconnected"
        connector.health = "healthy" if connect else "critical"
        connector.last_sync = self._timestamp() if connect else ""
        connector.latency_ms = random.randint(120, 500) if connect else 0
        connector.throughput = f"{random.uniform(1.0, 6.5):.1f} MB/s" if connect else "0"
        self.activity.append(
            IntegrationActivity(
                id=f"act-{connector_id}-{len(self.activity)+1}",
                connector=connector_id,
                action="connect" if connect else "disconnect",
                status="success",
                detail=f"Connector {'enabled' if connect else 'disabled'} via UI",
                timestamp=self._timestamp(),
            )
        )
        return connector

    def test_connector(self, connector_id: str) -> Dict[str, object] | None:
        connector = self._find(connector_id)
        if not connector:
            return None
        success = random.choice([True, True, False])
        detail = "Heartbeat OK" if success else "Timeout contacting endpoint"
        status = "success" if success else "error"
        self.activity.append(
            IntegrationActivity(
                id=f"act-{connector_id}-{len(self.activity)+1}",
                connector=connector_id,
                action="test",
                status=status,
                detail=detail,
                timestamp=self._timestamp(),
            )
        )
        return {"success": success, "detail": detail}

    def _find(self, connector_id: str) -> IntegrationConnector | None:
        for connector in self.connectors:
            if connector.id == connector_id:
                return connector
        return None
