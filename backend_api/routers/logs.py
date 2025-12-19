"""Unified logs API (endless log ordered by timestamp)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.security import AuthUser

router = APIRouter()


class LogEvent(BaseModel):
    id: int
    timestamp: str
    source: str
    level: str
    message: str
    user_id: Optional[str] = None
    thread: Optional[str] = None
    process: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LogStreamResponse(BaseModel):
    cursor: int
    events: List[LogEvent]


def record_event(
    *,
    db,
    source: str,
    level: str,
    message: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    db.execute(
        """
        INSERT INTO event_log (timestamp, source, level, message, user_id, thread, process, metadata_json)
        VALUES (?, ?, ?, ?, ?, NULL, NULL, ?)
        """,
        (ts, source, level, message, user_id, json.dumps(metadata or {}, ensure_ascii=False)),
    )


def log_event(
    *,
    level: str = "INFO",
    message: str = "",
    service: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Convenience function to log events with automatic db connection."""
    source = service or "ai_assistant"
    metadata: Dict[str, Any] = {}
    if action:
        metadata["action"] = action
    if resource:
        metadata["resource"] = resource
    metadata.update(kwargs)
    
    with db_session() as db:
        record_event(
            db=db,
            source=source,
            level=level,
            message=message,
            user_id=user_id,
            metadata=metadata if metadata else None,
        )


@router.get("/logs/stream", response_model=LogStreamResponse)
async def stream_logs(
    cursor: int = Query(0, ge=0, description="Return events with id > cursor"),
    limit: int = Query(200, ge=1, le=1000),
    include_all: bool = Query(False, description="Admins only: include all users' events"),
    user: AuthUser = Depends(get_current_user),
) -> LogStreamResponse:
    with db_session() as db:
        params: List[Any] = [cursor]
        where = "WHERE id > ?"
        if include_all and user.is_admin:
            pass
        else:
            where += " AND (user_id IS NULL OR user_id = ?)"
            params.append(user.id)

        rows = db.execute(
            f"""
            SELECT id, timestamp, source, level, message, user_id, thread, process, metadata_json
            FROM event_log
            {where}
            ORDER BY id ASC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()

    events: List[LogEvent] = []
    new_cursor = cursor
    for r in rows:
        new_cursor = max(new_cursor, int(r["id"]))
        raw_meta = r["metadata_json"] or "{}"
        try:
            meta = json.loads(raw_meta) if raw_meta else {}
        except Exception:
            meta = {"raw": raw_meta}
        events.append(
            LogEvent(
                id=int(r["id"]),
                timestamp=r["timestamp"],
                source=r["source"],
                level=r["level"],
                message=r["message"],
                user_id=r["user_id"],
                thread=r["thread"],
                process=r["process"],
                metadata=meta if isinstance(meta, dict) else {"value": meta},
            )
        )
    return LogStreamResponse(cursor=new_cursor, events=events)


class LogIngestRequest(BaseModel):
    source: str = Field(default="client")
    level: str = Field(default="info")
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.post("/logs/event", status_code=202)
async def ingest_log_event(payload: LogIngestRequest, user: AuthUser = Depends(get_current_user)) -> Dict[str, str]:
    with db_session() as db:
        record_event(
            db=db,
            source=payload.source,
            level=payload.level,
            message=payload.message,
            user_id=user.id,
            metadata=payload.metadata,
        )
    return {"status": "accepted"}
