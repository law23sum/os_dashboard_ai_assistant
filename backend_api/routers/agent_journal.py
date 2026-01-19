"""Agent journal routes backed by the unified Event Hub."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend_api.deps import get_current_user
from assistant_hub.telemetry.hub import get_event_hub
from assistant_hub.telemetry.models import normalize_event_type

router = APIRouter()

TEAM_EVENT_TYPES = [
    "MESSAGE_SENT",
    "MESSAGE_RECEIVED",
    "HELP_REQUESTED",
    "HELP_PROVIDED",
    "CONSENSUS_REACHED",
    "ESCALATION_TO_MASTER_CHRIS",
    "DEBATE_OPEN",
    "DEBATE_TURN",
    "SUPPORT",
    "REBUTTAL",
    "DISPUTE",
    "RESOLUTION",
]


class AgentJournalEvent(BaseModel):
    entry_hash: Optional[str] = None
    agent_id: Optional[str] = None
    event_type: str
    summary: Optional[str] = None
    timestamp_utc: Optional[str] = None


class AgentJournalStats(BaseModel):
    agents: Dict[str, Dict[str, Any]]
    team: Dict[str, Any]
    totals: Dict[str, int]


def _normalize_filter_event_types(value: Optional[str], *, default_team: bool = False) -> Optional[Sequence[str]]:
    if not value:
        return TEAM_EVENT_TYPES if default_team else None
    if value.strip().lower() == "collaboration":
        return TEAM_EVENT_TYPES
    return [normalize_event_type(value) or value]


@router.get("/agent-journal/status")
async def agent_journal_status(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    hub = get_event_hub()
    return {
        "status": "ready",
        "db_path": str(hub.db_path),
    }


@router.get("/agent-journal/stats", response_model=AgentJournalStats)
async def agent_journal_stats(
    include_sensitive: bool = Query(False),
    current_user: dict = Depends(get_current_user),
) -> AgentJournalStats:
    hub = get_event_hub()
    stats = hub.get_stats(include_private=include_sensitive, team_event_types=TEAM_EVENT_TYPES)
    return AgentJournalStats(**stats)


@router.get("/agent-journal/events", response_model=List[AgentJournalEvent])
async def list_agent_events(
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    include_sensitive: bool = Query(False),
    current_user: dict = Depends(get_current_user),
) -> List[AgentJournalEvent]:
    hub = get_event_hub()
    event_types = _normalize_filter_event_types(event_type)
    events = hub.query_events(
        agent_id=agent_id,
        event_types=event_types,
        include_private=include_sensitive,
        limit=limit,
    )
    return [
        AgentJournalEvent(
            entry_hash=event.get("event_hash"),
            agent_id=event.get("agent_id"),
            event_type=event.get("event_type", ""),
            summary=event.get("message"),
            timestamp_utc=event.get("ts_utc"),
        )
        for event in events
    ]


@router.get("/agent-journal/team", response_model=List[AgentJournalEvent])
async def list_team_events(
    event_type: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    include_sensitive: bool = Query(False),
    current_user: dict = Depends(get_current_user),
) -> List[AgentJournalEvent]:
    hub = get_event_hub()
    event_types = _normalize_filter_event_types(event_type, default_team=True)
    events = hub.query_events(
        event_types=event_types,
        include_private=include_sensitive,
        limit=limit,
    )
    return [
        AgentJournalEvent(
            entry_hash=event.get("event_hash"),
            agent_id=event.get("agent_id"),
            event_type=event.get("event_type", ""),
            summary=event.get("message"),
            timestamp_utc=event.get("ts_utc"),
        )
        for event in events
    ]
