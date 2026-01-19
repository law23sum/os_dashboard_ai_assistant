"""Event Hub storage and query surface."""

from __future__ import annotations

import json
import os
import socket
import sqlite3
import sys
import uuid
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

if TYPE_CHECKING:
    from assistant_hub.audit.ledger import AuditLedgerStore
    from assistant_hub.audit.schema import AuditEvent

_EVENT_HUB_SINGLETON: "EventHub | None" = None


def _default_db_path() -> Path:
    # Lazy import to avoid circular dependency with audit -> sdk -> telemetry.emitter
    from assistant_hub.audit.config import get_audit_config
    
    config = get_audit_config()
    return config.ledger_db_path


def _default_host_id() -> str:
    return os.getenv("OSDASH_HOST_ID", socket.gethostname())


def _default_os_family() -> str:
    platform = sys.platform.lower()
    if platform.startswith("darwin"):
        return "macos"
    if platform.startswith("win"):
        return "windows"
    return "linux"


def _default_runtime_scope() -> str:
    return os.getenv("OSDASH_RUNTIME_SCOPE", "host")


class EventHub:
    def __init__(self, ledger: AuditLedgerStore) -> None:
        self.ledger = ledger
        self.db_path = ledger.db_path

    def ingest(self, event: AuditEvent | Dict[str, Any]) -> Dict[str, str]:
        # Lazy imports to avoid circular dependency with audit -> sdk -> telemetry.emitter
        from assistant_hub.audit.config import get_audit_config
        from assistant_hub.audit.redaction import redact_payload
        from assistant_hub.audit.schema import (
            EVENT_TYPES,
            SEVERITY_LEVELS,
            VISIBILITY_LEVELS,
            AuditEvent,
            normalize_event_type,
        )
        
        config = get_audit_config()
        event_model = event if isinstance(event, AuditEvent) else AuditEvent(**event)
        payload = event_model.to_dict()
        payload["event_type"] = normalize_event_type(payload.get("event_type")) or "UNKNOWN"
        payload.setdefault("severity", "info")
        payload.setdefault("visibility", "team")
        payload.setdefault("host_id", _default_host_id())
        payload.setdefault("os_family", _default_os_family())
        payload.setdefault("runtime_scope", _default_runtime_scope())
        payload.setdefault("schema_version", 1)
        if not payload.get("session_id"):
            payload["session_id"] = str(uuid.uuid4())
        if not payload.get("correlation_id"):
            payload["correlation_id"] = str(uuid.uuid4())

        event_type = payload.get("event_type")
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Invalid event_type: {event_type}")
        severity = str(payload.get("severity") or "info").lower()
        if severity not in SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity: {severity}")
        visibility = str(payload.get("visibility") or "team").lower()
        if visibility not in VISIBILITY_LEVELS:
            raise ValueError(f"Invalid visibility: {visibility}")
        payload["severity"] = severity
        payload["visibility"] = visibility

        payload["payload"] = redact_payload(payload.get("payload") or {})
        payload["artifact_refs"] = redact_payload(payload.get("artifact_refs") or [])

        payload_json = json.dumps(payload.get("payload") or {}, ensure_ascii=False, default=str).encode("utf-8")
        if len(payload_json) > config.max_event_bytes:
            artifact_id = f"payload_{payload.get('event_id')}.json"
            artifact_path = config.artifact_dir / artifact_id
            artifact_path.write_bytes(payload_json)
            artifact_hash = sha256(payload_json).hexdigest()
            payload["artifact_refs"] = [
                {
                    "kind": "payload_overflow",
                    "path_or_uri": str(artifact_path),
                    "hash": artifact_hash,
                    "size_bytes": len(payload_json),
                }
            ]
            payload["payload"] = {"overflow": True, "artifact_ref": artifact_id}

        stored = self.ledger.append_event(payload)
        return {
            "event_id": stored.get("event_id", ""),
            "event_hash": stored.get("event_hash", ""),
        }

    def query_events(
        self,
        *,
        agent_id: Optional[str] = None,
        event_types: Optional[Sequence[str]] = None,
        visibility: Optional[str] = None,
        include_private: bool = True,
        correlation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        return self.ledger.query_events(
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

    def get_stats(self, *, include_private: bool, team_event_types: Sequence[str]) -> Dict[str, Any]:
        self.ledger._ensure_schema()
        conn = self.ledger._connect()
        try:
            visibility_filters: list[str] = []
            params: list[Any] = []
            if not include_private:
                visibility_filters.append("visibility != ?")
                params.append("private")

            agent_filters = list(visibility_filters)
            agent_filters.append("agent_id IS NOT NULL")
            agent_where = "WHERE " + " AND ".join(agent_filters)

            agent_rows = conn.execute(
                f"""
                SELECT agent_id, COUNT(*) AS total, MAX(ts_utc) AS last_timestamp
                FROM audit_events
                {agent_where}
                GROUP BY agent_id
                """,
                params,
            ).fetchall()

            team_where = ""
            if visibility_filters:
                team_where = "WHERE " + " AND ".join(visibility_filters)

            team_row = conn.execute(
                f"""
                SELECT COUNT(*) AS total, MAX(ts_utc) AS last_timestamp
                FROM audit_events
                {team_where}
                """,
                params,
            ).fetchone()

            # Lazy import to avoid circular dependency
            from assistant_hub.audit.schema import normalize_event_type
            
            team_event_types = [normalize_event_type(t) for t in team_event_types if t]
            team_event_types = [t for t in team_event_types if t]
            team_count = 0
            if team_event_types:
                placeholders = ",".join("?" for _ in team_event_types)
                filters = list(visibility_filters)
                filters.append(f"event_type IN ({placeholders})")
                team_where = "WHERE " + " AND ".join(filters)
                team_params = list(params) + team_event_types
                row = conn.execute(
                    f"SELECT COUNT(*) AS total FROM audit_events {team_where}",
                    team_params,
                ).fetchone()
                team_count = int(row["total"]) if row else 0

            agents: Dict[str, Dict[str, Any]] = {}
            for row in agent_rows:
                agent_id = row["agent_id"]
                if not agent_id:
                    continue
                agents[str(agent_id)] = {
                    "total": int(row["total"]),
                    "last_timestamp": row["last_timestamp"],
                }

            team = {
                "total": int(team_row["total"]) if team_row else 0,
                "last_timestamp": team_row["last_timestamp"] if team_row else None,
            }
            return {
                "agents": agents,
                "team": team,
                "totals": {"team_interactions": team_count},
            }
        finally:
            conn.close()

    def count_events(self) -> int:
        return self.ledger.count_events()


def get_event_hub() -> EventHub:
    # Lazy import to avoid circular dependency with audit -> sdk -> telemetry.emitter
    from assistant_hub.audit.ledger import get_ledger_store
    
    global _EVENT_HUB_SINGLETON
    if _EVENT_HUB_SINGLETON is None:
        _EVENT_HUB_SINGLETON = EventHub(get_ledger_store())
    return _EVENT_HUB_SINGLETON


def reset_event_hub() -> None:
    global _EVENT_HUB_SINGLETON
    _EVENT_HUB_SINGLETON = None
