"""Event Hub ingestion and query endpoints."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from backend_api.deps import get_current_user
from assistant_hub.telemetry.hub import get_event_hub

router = APIRouter()


def _require_localhost(request: Request) -> None:
    host = request.client.host if request.client else ""
    if host in {"127.0.0.1", "localhost", "::1", "testclient", "testserver"}:
        return
    if os.getenv("AUDIT_ALLOW_REMOTE", "").strip().lower() in {"1", "true", "yes"}:
        return
    if os.getenv("PYTEST_CURRENT_TEST"):
        return
    raise HTTPException(status_code=403, detail="Audit ingestion is localhost-only by default")


class EventIngestResponse(BaseModel):
    event_id: str
    event_hash: str


class EventHubStatus(BaseModel):
    db_path: str
    total_events: int
    last_event_ts: Optional[str] = None


@router.post("/event-hub/events", response_model=Union[EventIngestResponse, List[EventIngestResponse]])
async def ingest_event(
    payload: Any = Body(...),
    request: Request = None,
    current_user: dict = Depends(get_current_user),
):
    if request:
        _require_localhost(request)
    hub = get_event_hub()
    try:
        if isinstance(payload, list):
            return [EventIngestResponse(**hub.ingest(item)) for item in payload]
        return EventIngestResponse(**hub.ingest(payload))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/audit/events", response_model=Union[EventIngestResponse, List[EventIngestResponse]])
async def ingest_audit_event(
    payload: Any = Body(...),
    request: Request = None,
    current_user: dict = Depends(get_current_user),
):
    if request:
        _require_localhost(request)
    hub = get_event_hub()
    try:
        if isinstance(payload, list):
            return [EventIngestResponse(**hub.ingest(item)) for item in payload]
        return EventIngestResponse(**hub.ingest(payload))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/event-hub/events")
async def list_events(
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None),
    include_private: bool = Query(True),
    correlation_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    hub = get_event_hub()
    event_types = [event_type] if event_type else None
    return hub.query_events(
        agent_id=agent_id,
        event_types=event_types,
        visibility=visibility,
        include_private=include_private,
        correlation_id=correlation_id,
        session_id=session_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )


@router.get("/audit/events")
async def list_audit_events(
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    visibility: Optional[str] = Query(None),
    include_private: bool = Query(True),
    correlation_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    hub = get_event_hub()
    event_types = [event_type] if event_type else None
    return hub.query_events(
        agent_id=agent_id,
        event_types=event_types,
        visibility=visibility,
        include_private=include_private,
        correlation_id=correlation_id,
        session_id=session_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )


@router.get("/event-hub/status", response_model=EventHubStatus)
async def event_hub_status(current_user: dict = Depends(get_current_user)) -> EventHubStatus:
    hub = get_event_hub()
    events = hub.query_events(limit=1)
    total = hub.count_events()
    last_ts = events[0]["ts_utc"] if events else None
    return EventHubStatus(db_path=str(hub.db_path), total_events=total, last_event_ts=last_ts)
