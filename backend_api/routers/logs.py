"""Unified logs API (endless log ordered by timestamp)."""

from __future__ import annotations

import json
import sqlite3
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
    timestamp: Optional[str] = None,
) -> str:
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    db.execute(
        """
        INSERT INTO event_log (timestamp, source, level, message, user_id, thread, process, metadata_json)
        VALUES (?, ?, ?, ?, ?, NULL, NULL, ?)
        """,
        (ts, source, level, message, user_id, json.dumps(metadata or {}, ensure_ascii=False, default=str)),
    )
    return ts


def _record_audit_event(
    *,
    db,
    timestamp: str,
    action: str,
    user_id: Optional[str],
    resource_id: Optional[str],
    source: str,
    metadata: Optional[Dict[str, Any]],
) -> None:
    meta = metadata or {}
    object_type = meta.get("resource_type") or source
    object_id = resource_id or meta.get("resource_id")
    ip_address = meta.get("ip_address") or meta.get("ip")
    user_agent = meta.get("user_agent")
    try:
        db.execute(
            """
            INSERT INTO audit_events (
                user_id, event_type, object_type, object_id, ip, user_agent, created_at, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                action,
                object_type,
                object_id,
                ip_address,
                user_agent,
                timestamp,
                json.dumps(meta, ensure_ascii=False, default=str),
            ),
        )
    except sqlite3.OperationalError:
        # Table may not exist in older schemas; skip without failing.
        return


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
        timestamp = record_event(
            db=db,
            source=source,
            level=level,
            message=message,
            user_id=user_id,
            metadata=metadata if metadata else None,
        )
        _record_audit_event(
            db=db,
            timestamp=timestamp,
            action=action or message or "log_event",
            user_id=user_id,
            resource_id=resource,
            source=source,
            metadata=metadata,
        )
    _record_immutable_audit_ledger(
        action=action or message or "log_event",
        user_id=user_id,
        resource_id=resource,
        details=metadata,
        level=level,
    )


def _record_immutable_audit_ledger(
    *,
    action: str,
    user_id: Optional[str],
    resource_id: Optional[str],
    details: Optional[Dict[str, Any]],
    level: Optional[str],
) -> None:
    try:
        from assistant_core.immutable_audit_ledger import (
            get_immutable_audit_ledger_module,
        )
    except Exception:
        return

    try:
        meta = details if isinstance(details, dict) else {}
        ledger_module = get_immutable_audit_ledger_module()
        ledger_module.record_action_step_sync(
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            level=level,
            subject_id=resource_id,
            subject_type="resource",
            tenant_id=meta.get("tenant_id"),
            workspace_id=meta.get("workspace_id"),
        )
    except Exception:
        return


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
        timestamp = record_event(
            db=db,
            source=payload.source,
            level=payload.level,
            message=payload.message,
            user_id=user.id,
            metadata=payload.metadata,
        )
        _record_audit_event(
            db=db,
            timestamp=timestamp,
            action=str(payload.metadata.get("action") or payload.message or "log_event"),
            user_id=user.id,
            resource_id=payload.metadata.get("resource") if isinstance(payload.metadata, dict) else None,
            source=payload.source,
            metadata=payload.metadata,
        )
    return {"status": "accepted"}
