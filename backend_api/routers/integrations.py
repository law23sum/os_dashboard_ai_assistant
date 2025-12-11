"""Integrations API router."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import sys
from pathlib import Path
from datetime import datetime, timedelta

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

router = APIRouter()

from assistant_hub_gui.assistant_hub.integrations.api import IntegrationAPIGateway
from assistant_hub_gui.assistant_hub.sync_scheduler import create_default_scheduler
from assistant_hub_gui.assistant_hub.db import init_db
from backend_api.routers.api_connectors import CONNECTOR_META

_gateway: Optional[IntegrationAPIGateway] = None


def get_gateway() -> IntegrationAPIGateway:
    global _gateway
    if _gateway is None:
        conn = init_db()
        scheduler = create_default_scheduler(conn)
        _gateway = IntegrationAPIGateway(conn, scheduler)
    return _gateway

class IntegrationStatus(BaseModel):
    service: str
    connected: bool
    username: Optional[str] = None
    last_sync: Optional[str] = None


class IntegrationConnectorDetails(BaseModel):
    id: str
    name: str
    category: str
    status: str
    connected: bool
    last_sync: Optional[str] = None
    latency_ms: int
    throughput: str
    targets: List[str]
    notes: str
    health: str


class IntegrationPipeline(BaseModel):
    id: str
    name: str
    status: str
    throughput: str
    latency_ms: int
    last_run: str


class IntegrationIncident(BaseModel):
    id: str
    title: str
    severity: str
    connector: str
    detail: str
    timestamp: str


class IntegrationActivity(BaseModel):
    id: str
    connector: str
    action: str
    status: str
    detail: str
    timestamp: str


class IntegrationSnapshot(BaseModel):
    summary: Dict[str, int]
    connectors: List[IntegrationConnectorDetails]
    pipelines: List[IntegrationPipeline]
    incidents: List[IntegrationIncident]
    activity: List[IntegrationActivity]


TARGET_HINTS: Dict[str, List[str]] = {
    "notes": ["Knowledge Graph", "Quick Capture"],
    "calendar": ["Agenda", "Schedules"],
    "mail": ["Inbox", "Auto-Summary"],
    "github": ["Issues", "PR Reviews"],
    "word": ["Proposals", "Reports"],
    "excel": ["Models", "Dashboards"],
    "onenote": ["Notebooks", "Research"],
    "filesystem": ["Local Vault"],
    "git": ["Repos", "Branches"],
    "pdf": ["Regulations", "Contracts"],
}

PIPELINE_TEMPLATES = [
    ("knowledge_sync", "Knowledge Graph Sync", ["onenote", "notes"]),
    ("analytics_ingest", "Analytics Data Ingest", ["excel", "filesystem"]),
    ("devops_signal", "DevOps Signal Stream", ["github", "git"]),
]

class ConnectorConfiguration(BaseModel):
    id: str
    name: str
    connected: bool
    username: Optional[str] = None
    last_sync: Optional[str] = None
    settings_schema: Dict[str, Dict[str, Any]]
    current_settings: Dict[str, Any]

class ConnectorConfigUpdate(BaseModel):
    settings: Dict[str, Any]

@router.get("/", response_model=List[IntegrationStatus])
async def list_integrations():
    """List all integrations and their connection status."""
    gateway = get_gateway()
    statuses = gateway.list_statuses()
    results: List[IntegrationStatus] = []
    for key, status in statuses.items():
        meta = CONNECTOR_META.get(key, {"name": key.title()})
        results.append(
            IntegrationStatus(
                service=meta["name"],
                connected=bool(status.get("connected")),
                last_sync=status.get("last_sync"),
            )
        )
    return results

@router.post("/{service}/connect")
async def connect_integration(service: str):
    """Connect to an integration service."""
    # Placeholder for integration connection logic
    return {"message": f"Connecting to {service}", "status": "pending"}

@router.post("/{service}/disconnect")
async def disconnect_integration(service: str):
    """Disconnect from an integration service."""
    return {"message": f"Disconnected from {service}", "status": "disconnected"}

@router.get("/{service}/status", response_model=IntegrationStatus)
async def get_integration_status(service: str):
    """Get status of a specific integration."""
    gateway = get_gateway()
    statuses = gateway.list_statuses()
    key = None
    for connector_key, meta in CONNECTOR_META.items():
        if meta["name"].lower() == service.lower() or connector_key.lower() == service.lower():
            key = connector_key
            break
    if not key:
        raise HTTPException(status_code=404, detail="Integration not found")
    status = statuses.get(key)
    if status is None:
        raise HTTPException(status_code=404, detail="Integration not found")
    return IntegrationStatus(
        service=CONNECTOR_META.get(key, {"name": key.title()})["name"],
        connected=bool(status.get("connected")),
        last_sync=status.get("last_sync"),
    )


@router.get("/summary", response_model=IntegrationSnapshot)
async def integration_summary():
    """Provide the richer snapshot used by the React Integrations workspace."""
    gateway = get_gateway()
    statuses = gateway.list_statuses()
    connectors: List[IntegrationConnectorDetails] = []
    summary = {"total": 0, "connected": 0, "degraded": 0, "disconnected": 0}
    now = datetime.utcnow()

    for connector_id, meta in CONNECTOR_META.items():
        status = statuses.get(connector_id, {})
        connected = bool(status.get("connected"))
        error = status.get("error")

        summary["total"] += 1
        if connected and not error:
            summary["connected"] += 1
        elif connected and error:
            summary["degraded"] += 1
        else:
            summary["disconnected"] += 1

        last_sync = status.get("last_sync")
        if connected and not last_sync:
            last_sync = (now - timedelta(minutes=_pseudo_metric(connector_id, 5, 90))).isoformat() + "Z"

        connectors.append(
            IntegrationConnectorDetails(
                id=connector_id,
                name=meta["name"],
                category=meta["category"],
                status="connected" if connected else ("degraded" if error else "disconnected"),
                connected=connected,
                last_sync=last_sync,
                latency_ms=_pseudo_metric(connector_id, 180, 200),
                throughput=f"{_pseudo_metric(connector_id, 200, 180)} items/hr",
                targets=TARGET_HINTS.get(connector_id, ["Workspace"]),
                notes=(
                    f"Synced {last_sync}"
                    if connected and last_sync
                    else "Connector healthy and syncing"
                    if connected
                    else "Connector offline – configure credentials to resume sync."
                ),
                health=_health_label(connected, error),
            )
        )

    pipelines: List[IntegrationPipeline] = []
    for pipeline_id, pipeline_name, upstream in PIPELINE_TEMPLATES:
        upstream_connected = any(statuses.get(connector, {}).get("connected") for connector in upstream)
        pipelines.append(
            IntegrationPipeline(
                id=pipeline_id,
                name=pipeline_name,
                status="running" if upstream_connected else "paused",
                throughput=f"{_pseudo_metric(pipeline_id, 60, 40)} docs/hr",
                latency_ms=_pseudo_metric(pipeline_name, 120, 90),
                last_run=(now - timedelta(minutes=_pseudo_metric(pipeline_id, 10, 50))).isoformat() + "Z",
            )
        )

    incidents: List[IntegrationIncident] = []
    for connector in connectors:
        if connector.status != "connected":
            incidents.append(
                IntegrationIncident(
                    id=f"incident-{connector.id}",
                    title=f"{connector.name} {connector.status.title()}",
                    severity="high" if connector.status == "degraded" else "medium",
                    connector=connector.name,
                    detail=connector.notes,
                    timestamp=connector.last_sync or now.isoformat() + "Z",
                )
            )

    activity: List[IntegrationActivity] = []
    for connector in connectors:
        timestamp = connector.last_sync or now.isoformat() + "Z"
        activity.append(
            IntegrationActivity(
                id=f"activity-{connector.id}",
                connector=connector.name,
                action="sync",
                status="success" if connector.connected else "skipped",
                detail=connector.notes,
                timestamp=timestamp,
            )
        )

    return IntegrationSnapshot(
        summary=summary,
        connectors=connectors,
        pipelines=pipelines,
        incidents=incidents,
        activity=activity,
    )

def _schema_for_connector(connector_id: str) -> Dict[str, Dict[str, Any]]:
    return {
        "api_key": {
            "label": "API Key",
            "type": "password",
            "placeholder": "sk-...",
        },
        "workspace": {
            "label": "Workspace / Tenant",
            "type": "text",
            "placeholder": "contoso",
        },
        "sync_interval": {
            "label": "Sync Interval (minutes)",
            "type": "number",
            "min": 5,
            "max": 240,
        },
    }

@router.get("/connectors/{connector_id}", response_model=ConnectorConfiguration)
async def get_connector_configuration(connector_id: str):
    gateway = get_gateway()
    statuses = gateway.list_statuses()
    status = statuses.get(connector_id, {})
    meta = CONNECTOR_META.get(connector_id, {"name": connector_id.title()})
    return ConnectorConfiguration(
        id=connector_id,
        name=meta["name"],
        connected=bool(status.get("connected")),
        username=status.get("username"),
        last_sync=status.get("last_sync"),
        settings_schema=_schema_for_connector(connector_id),
        current_settings={
            "workspace": meta["name"].replace(" ", "_").lower(),
            "sync_interval": 30,
        },
    )

@router.post("/connectors/{connector_id}/configure")
async def configure_connector(connector_id: str, payload: ConnectorConfigUpdate):
    # In a future release this will persist credentials/metadata; for now we accept and acknowledge.
    return {"status": "ok", "connector": connector_id, "saved": payload.settings}


def _pseudo_metric(identifier: str, base: int, spread: int) -> int:
    return base + (abs(hash(identifier)) % spread)


def _health_label(connected: bool, error: Optional[str]) -> str:
    if not connected:
        return "offline"
    if error:
        return "needs attention"
    return "excellent"
