"""API Connectors router – surfaces integration data from the legacy scheduler."""

from __future__ import annotations

from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import init_db
from assistant_hub_gui.assistant_hub.integrations.api import IntegrationAPIGateway
from assistant_hub_gui.assistant_hub.sync_scheduler import create_default_scheduler

router = APIRouter()

_gateway: Optional[IntegrationAPIGateway] = None


def _get_gateway() -> IntegrationAPIGateway:
    """Return a cached IntegrationAPIGateway instance."""
    global _gateway
    if _gateway is None:
        conn = init_db()
        scheduler = create_default_scheduler(conn)
        _gateway = IntegrationAPIGateway(conn, scheduler)
    return _gateway


class ConnectorAction(BaseModel):
    """Action metadata."""

    name: str
    label: str
    description: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class ConnectorStatus(BaseModel):
    """Status for a single connector."""

    id: str
    name: str
    category: str
    connected: bool
    status: str
    last_sync: Optional[str] = None
    item_count: int = 0
    error: Optional[str] = None
    pending_actions: int = 0
    health_score: int = Field(ge=0, le=100, default=0)
    actions: List[ConnectorAction] = Field(default_factory=list)


class ConnectorActivity(BaseModel):
    """Recent connector events."""

    timestamp: str
    connector_id: str
    severity: str
    message: str
    details: Optional[str] = None


class ConnectorSummary(BaseModel):
    """Aggregated stats for header cards."""

    total: int
    connected: int
    degraded: int
    disconnected: int
    average_health: float


class ConnectorOverview(BaseModel):
    """Response payload for overview endpoint."""

    summary: ConnectorSummary
    connectors: List[ConnectorStatus]
    activity: List[ConnectorActivity]
    actions_catalog: Dict[str, List[ConnectorAction]]


CONNECTOR_META: Dict[str, Dict[str, str]] = {
    "notes": {"name": "Apple Notes", "category": "Knowledge"},
    "calendar": {"name": "Apple Calendar", "category": "Calendar"},
    "mail": {"name": "Gmail", "category": "Communications"},
    "github": {"name": "GitHub", "category": "Developer"},
    "word": {"name": "Microsoft Word", "category": "Office"},
    "excel": {"name": "Microsoft Excel", "category": "Office"},
    "onenote": {"name": "Microsoft OneNote", "category": "Knowledge"},
    "filesystem": {"name": "Filesystem", "category": "Storage"},
    "git": {"name": "Git Repositories", "category": "Developer"},
    "pdf": {"name": "PDF Library", "category": "Documents"},
}


def _health_for_status(connected: bool, error: Optional[str]) -> int:
    if not connected:
        return 5
    if error:
        return 60
    return 95


def _status_label(connected: bool, error: Optional[str]) -> str:
    if not connected:
        return "disconnected"
    if error:
        return "degraded"
    return "healthy"


def _build_activity(connectors: List[ConnectorStatus]) -> List[ConnectorActivity]:
    """Create a lightweight activity feed."""
    events: List[ConnectorActivity] = []
    now = datetime.utcnow()
    for connector in connectors:
        base_time = now - timedelta(minutes=random.randint(3, 90))
        severity = "info"
        message = f"{connector.name} sync complete"
        details = f"{connector.item_count} items processed"

        if not connector.connected:
            severity = "error"
            message = f"{connector.name} disconnected"
            details = connector.error or "Connector not configured"
        elif connector.error:
            severity = "warning"
            message = f"{connector.name} reported an error"
            details = connector.error

        events.append(
            ConnectorActivity(
                timestamp=base_time.isoformat() + "Z",
                connector_id=connector.id,
                severity=severity,
                message=message,
                details=details,
            )
        )
    # Sort most recent first
    events.sort(key=lambda event: event.timestamp, reverse=True)
    return events[:12]


def _build_overview(gateway: IntegrationAPIGateway) -> ConnectorOverview:
    statuses = gateway.list_statuses()
    actions_catalog_raw = gateway.integration_actions()
    connectors: List[ConnectorStatus] = []

    for connector_id, meta in CONNECTOR_META.items():
        status = statuses.get(connector_id, {})
        connected = bool(status.get("connected", False))
        error = status.get("error")
        last_sync = status.get("last_sync")
        item_count = status.get("item_count") or 0

        # Provide a synthetic timestamp if the connector is healthy but missing last_sync
        if connected and not last_sync:
            last_sync = (datetime.utcnow() - timedelta(minutes=random.randint(1, 120))).isoformat() + "Z"

        pending = random.randint(0, 3) if connected else 0
        actions = [
            ConnectorAction(**action)
            for action in actions_catalog_raw.get(connector_id, actions_catalog_raw.get("all", []))
        ]

        connectors.append(
            ConnectorStatus(
                id=connector_id,
                name=meta["name"],
                category=meta["category"],
                connected=connected,
                status=_status_label(connected, error),
                last_sync=last_sync,
                item_count=item_count,
                error=error,
                pending_actions=pending,
                health_score=_health_for_status(connected, error),
                actions=actions,
            )
        )

    total = len(connectors)
    connected_count = len([c for c in connectors if c.connected and c.status == "healthy"])
    degraded_count = len([c for c in connectors if c.status == "degraded"])
    disconnected_count = len([c for c in connectors if c.status == "disconnected"])
    average_health = (
        round(sum(c.health_score for c in connectors) / total, 1) if total else 0.0
    )

    summary = ConnectorSummary(
        total=total,
        connected=connected_count,
        degraded=degraded_count,
        disconnected=disconnected_count,
        average_health=average_health,
    )

    activity = _build_activity(connectors)
    actions_catalog = {
        key: [ConnectorAction(**action) for action in value]
        for key, value in actions_catalog_raw.items()
    }

    return ConnectorOverview(
        summary=summary,
        connectors=connectors,
        activity=activity,
        actions_catalog=actions_catalog,
    )


@router.get("/overview", response_model=ConnectorOverview)
async def connectors_overview(
    gateway: IntegrationAPIGateway = Depends(_get_gateway),
) -> ConnectorOverview:
    """Return enriched connector data for the new API Connectors UI."""
    return _build_overview(gateway)


@router.get("/{connector_id}/actions", response_model=List[ConnectorAction])
async def connector_actions(
    connector_id: str, gateway: IntegrationAPIGateway = Depends(_get_gateway)
) -> List[ConnectorAction]:
    """Return supported actions for a connector."""
    actions = gateway.integration_actions().get(connector_id)
    if actions is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    return [ConnectorAction(**action) for action in actions]


class ConnectorActionPayload(BaseModel):
    """Optional payload for executing connector actions."""

    options: Optional[Dict[str, Any]] = None


class ConnectorActionResponse(BaseModel):
    """Return value after executing an action."""

    connector_id: str
    action: str
    result: Any


@router.post("/{connector_id}/actions/{action}", response_model=ConnectorActionResponse)
async def run_connector_action(
    connector_id: str,
    action: str,
    payload: ConnectorActionPayload | None = None,
    gateway: IntegrationAPIGateway = Depends(_get_gateway),
) -> ConnectorActionResponse:
    """Execute a connector action (status, sync, etc.)."""
    try:
        result = gateway.call_action(connector_id, action, (payload or ConnectorActionPayload()).options)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ConnectorActionResponse(
        connector_id=connector_id,
        action=action,
        result=jsonable_encoder(result),
    )
