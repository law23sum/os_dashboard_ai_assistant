"""Append-only SQLite ledger for audit events."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .config import get_audit_config
from .hashing import compute_event_hash, event_hash_payload
from .schema import AuditEvent, normalize_event_type


class AuditLedgerStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._initialized = False

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = FULL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def _ensure_schema(self) -> None:
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            conn = self._connect()
            try:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS audit_events (
                        seq INTEGER PRIMARY KEY AUTOINCREMENT,
                        schema_version INTEGER NOT NULL,
                        event_id TEXT NOT NULL,
                        ts_utc TEXT NOT NULL,
                        host_id TEXT,
                        os_family TEXT,
                        runtime_scope TEXT,
                        agent_id TEXT,
                        session_id TEXT,
                        correlation_id TEXT,
                        operation_id TEXT,
                        causation_id TEXT,
                        event_type TEXT,
                        severity TEXT,
                        visibility TEXT,
                        project_id TEXT,
                        epic_id TEXT,
                        task_id TEXT,
                        message TEXT,
                        payload_json TEXT,
                        artifact_refs_json TEXT,
                        resource_snapshot_json TEXT,
                        prev_hash TEXT,
                        event_hash TEXT
                    );
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_events_id ON audit_events(event_id);
                    CREATE INDEX IF NOT EXISTS idx_audit_events_seq ON audit_events(seq);
                    CREATE INDEX IF NOT EXISTS idx_audit_events_ts ON audit_events(ts_utc);
                    CREATE INDEX IF NOT EXISTS idx_audit_events_agent ON audit_events(agent_id);
                    CREATE INDEX IF NOT EXISTS idx_audit_events_type ON audit_events(event_type);
                    CREATE INDEX IF NOT EXISTS idx_audit_events_corr ON audit_events(correlation_id);

                    CREATE TABLE IF NOT EXISTS audit_meta (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    );

                    CREATE TABLE IF NOT EXISTS audit_archives (
                        archive_id TEXT PRIMARY KEY,
                        start_seq INTEGER,
                        end_seq INTEGER,
                        start_ts TEXT,
                        end_ts TEXT,
                        archive_path TEXT,
                        segment_sha256 TEXT,
                        sealed_at TEXT,
                        encryption_kid TEXT,
                        compression TEXT,
                        created_at TEXT
                    );

                    CREATE TRIGGER IF NOT EXISTS audit_events_no_update
                    BEFORE UPDATE ON audit_events
                    BEGIN
                        SELECT RAISE(ABORT, 'append-only');
                    END;
                    CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
                    BEFORE DELETE ON audit_events
                    BEGIN
                        SELECT RAISE(ABORT, 'append-only');
                    END;
                    """
                )
                if not self._meta_value(conn, "created_at"):
                    conn.execute(
                        "INSERT OR REPLACE INTO audit_meta (key, value) VALUES (?, ?)",
                        ("created_at", datetime.now(timezone.utc).isoformat()),
                    )
                if not self._meta_value(conn, "ledger_version"):
                    conn.execute(
                        "INSERT OR REPLACE INTO audit_meta (key, value) VALUES (?, ?)",
                        ("ledger_version", "1"),
                    )
                conn.commit()
                self._initialized = True
            finally:
                conn.close()

    @staticmethod
    def _meta_value(conn: sqlite3.Connection, key: str) -> Optional[str]:
        row = conn.execute("SELECT value FROM audit_meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def _last_event_hash(self, conn: sqlite3.Connection) -> Optional[str]:
        row = conn.execute(
            "SELECT event_hash FROM audit_events ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row["event_hash"] if row else None

    def append_event(self, event: AuditEvent | Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_schema()
        event_model = event if isinstance(event, AuditEvent) else AuditEvent(**event)
        payload = event_model.to_dict()
        payload["event_type"] = normalize_event_type(payload.get("event_type")) or "UNKNOWN"

        resource_snapshot = payload.get("resource_snapshot")
        if hasattr(resource_snapshot, "model_dump"):
            resource_snapshot = resource_snapshot.model_dump()
        elif hasattr(resource_snapshot, "dict"):
            resource_snapshot = resource_snapshot.dict()
        if resource_snapshot is None:
            resource_snapshot = {}
        payload["resource_snapshot"] = resource_snapshot

        artifact_refs = payload.get("artifact_refs")
        if artifact_refs is not None:
            serialized_refs = []
            for ref in artifact_refs:
                if hasattr(ref, "model_dump"):
                    serialized_refs.append(ref.model_dump())
                elif hasattr(ref, "dict"):
                    serialized_refs.append(ref.dict())
                else:
                    serialized_refs.append(ref)
            artifact_refs = serialized_refs
        if artifact_refs is None:
            artifact_refs = []
        payload["artifact_refs"] = artifact_refs

        project_ref = payload.get("project_ref")
        if hasattr(project_ref, "model_dump"):
            project_ref = project_ref.model_dump()
        elif hasattr(project_ref, "dict"):
            project_ref = project_ref.dict()
        if not isinstance(project_ref, dict):
            project_ref = {}
        project_ref = {
            "project_id": project_ref.get("project_id"),
            "epic_id": project_ref.get("epic_id"),
            "task_id": project_ref.get("task_id"),
        }
        payload["project_ref"] = project_ref
        project_id = project_ref.get("project_id")
        epic_id = project_ref.get("epic_id")
        task_id = project_ref.get("task_id")

        conn = self._connect()
        try:
            with conn:
                prev_hash = payload.get("prev_hash") or payload.get("prev_event_hash")
                if not prev_hash:
                    last_hash = self._meta_value(conn, "last_event_hash") or self._last_event_hash(conn)
                    prev_hash = last_hash or "GENESIS"
                payload["prev_hash"] = prev_hash

                if payload.get("event_hash"):
                    hash_payload = event_hash_payload(payload)
                    expected_hash = compute_event_hash(hash_payload)
                    if payload["event_hash"] != expected_hash:
                        raise ValueError("event_hash does not match canonical payload")
                    event_hash = payload["event_hash"]
                else:
                    hash_payload = event_hash_payload(payload)
                    event_hash = compute_event_hash(hash_payload)
                    payload["event_hash"] = event_hash

                conn.execute(
                    """
                    INSERT INTO audit_events (
                        schema_version, event_id, ts_utc, host_id, os_family, runtime_scope,
                        agent_id, session_id, correlation_id, operation_id, causation_id,
                        event_type, severity, visibility, project_id, epic_id, task_id, message,
                        payload_json, artifact_refs_json, resource_snapshot_json, prev_hash, event_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload.get("schema_version", 1),
                        payload.get("event_id"),
                        payload.get("ts_utc"),
                        payload.get("host_id"),
                        payload.get("os_family"),
                        payload.get("runtime_scope"),
                        payload.get("agent_id"),
                        payload.get("session_id"),
                        payload.get("correlation_id"),
                        payload.get("operation_id"),
                        payload.get("causation_id"),
                        payload.get("event_type"),
                        payload.get("severity"),
                        payload.get("visibility"),
                        project_id,
                        epic_id,
                        task_id,
                        payload.get("message"),
                        json.dumps(payload.get("payload") or {}, ensure_ascii=False, default=str),
                        json.dumps(artifact_refs or [], ensure_ascii=False, default=str),
                        json.dumps(resource_snapshot or {}, ensure_ascii=False, default=str),
                        payload.get("prev_hash"),
                        payload.get("event_hash"),
                    ),
                )
                conn.execute(
                    "INSERT OR REPLACE INTO audit_meta (key, value) VALUES (?, ?)",
                    ("last_event_hash", payload.get("event_hash")),
                )
            return payload
        finally:
            conn.close()

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
        self._ensure_schema()
        filters: list[str] = []
        params: list[Any] = []

        if agent_id:
            filters.append("agent_id = ?")
            params.append(agent_id)
        if event_types:
            normalized = [normalize_event_type(val) for val in event_types if val]
            normalized = [val for val in normalized if val]
            if normalized:
                filters.append(f"event_type IN ({','.join('?' for _ in normalized)})")
                params.extend(normalized)
        if visibility:
            filters.append("visibility = ?")
            params.append(visibility)
        if not include_private:
            filters.append("visibility != ?")
            params.append("private")
        if correlation_id:
            filters.append("correlation_id = ?")
            params.append(correlation_id)
        if session_id:
            filters.append("session_id = ?")
            params.append(session_id)
        if start_time:
            filters.append("ts_utc >= ?")
            params.append(start_time)
        if end_time:
            filters.append("ts_utc <= ?")
            params.append(end_time)

        where_clause = " AND ".join(filters)
        if where_clause:
            where_clause = "WHERE " + where_clause

        query = (
            "SELECT * FROM audit_events "
            f"{where_clause} "
            "ORDER BY ts_utc DESC "
            "LIMIT ?"
        )
        params.append(limit)

        conn = self._connect()
        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        finally:
            conn.close()

        return [self._row_to_event(row) for row in rows]

    def count_events(self) -> int:
        self._ensure_schema()
        conn = self._connect()
        try:
            row = conn.execute("SELECT COUNT(*) AS total FROM audit_events").fetchone()
            return int(row["total"]) if row else 0
        finally:
            conn.close()

    def verify_chain(
        self, *, from_seq: Optional[int] = None, to_seq: Optional[int] = None
    ) -> Dict[str, Any]:
        self._ensure_schema()
        conn = self._connect()
        try:
            params: list[Any] = []
            clauses: list[str] = []
            if from_seq is not None:
                clauses.append("seq >= ?")
                params.append(from_seq)
            if to_seq is not None:
                clauses.append("seq <= ?")
                params.append(to_seq)
            where_clause = " AND ".join(clauses)
            if where_clause:
                where_clause = "WHERE " + where_clause
            rows = conn.execute(
                f"SELECT * FROM audit_events {where_clause} ORDER BY seq ASC", params
            ).fetchall()

            expected_prev = None
            if from_seq and from_seq > 1:
                prev_row = conn.execute(
                    "SELECT event_hash FROM audit_events WHERE seq = ?",
                    (from_seq - 1,),
                ).fetchone()
                expected_prev = prev_row["event_hash"] if prev_row else None
            else:
                expected_prev = "GENESIS"

            for row in rows:
                found_prev = row["prev_hash"]
                if expected_prev and found_prev != expected_prev:
                    return {
                        "ok": False,
                        "first_bad_seq": int(row["seq"]),
                        "expected_hash": expected_prev,
                        "found_hash": found_prev,
                    }
                event_payload = self._row_to_event(row)
                recomputed = compute_event_hash(event_hash_payload(event_payload))
                if row["event_hash"] != recomputed:
                    return {
                        "ok": False,
                        "first_bad_seq": int(row["seq"]),
                        "expected_hash": recomputed,
                        "found_hash": row["event_hash"],
                    }
                expected_prev = row["event_hash"]

            return {"ok": True, "first_bad_seq": None, "expected_hash": None, "found_hash": None}
        finally:
            conn.close()

    def insert_archive_record(
        self,
        *,
        archive_id: str,
        start_seq: int,
        end_seq: int,
        start_ts: str,
        end_ts: str,
        archive_path: str,
        segment_sha256: str,
        sealed_at: str,
        encryption_kid: Optional[str],
        compression: str,
    ) -> None:
        self._ensure_schema()
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO audit_archives (
                    archive_id, start_seq, end_seq, start_ts, end_ts, archive_path,
                    segment_sha256, sealed_at, encryption_kid, compression, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    archive_id,
                    start_seq,
                    end_seq,
                    start_ts,
                    end_ts,
                    archive_path,
                    segment_sha256,
                    sealed_at,
                    encryption_kid,
                    compression,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def list_archives(self) -> List[Dict[str, Any]]:
        self._ensure_schema()
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM audit_archives ORDER BY created_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def _row_to_event(self, row: sqlite3.Row) -> Dict[str, Any]:
        resource_snapshot = json.loads(row["resource_snapshot_json"] or "{}")
        artifact_refs = json.loads(row["artifact_refs_json"] or "[]")
        payload = json.loads(row["payload_json"] or "{}")
        project_ref = {
            "project_id": row["project_id"],
            "epic_id": row["epic_id"],
            "task_id": row["task_id"],
        }
        return {
            "schema_version": row["schema_version"],
            "event_id": row["event_id"],
            "ts_utc": row["ts_utc"],
            "host_id": row["host_id"],
            "os_family": row["os_family"],
            "runtime_scope": row["runtime_scope"],
            "agent_id": row["agent_id"],
            "session_id": row["session_id"],
            "correlation_id": row["correlation_id"],
            "operation_id": row["operation_id"],
            "causation_id": row["causation_id"],
            "event_type": row["event_type"],
            "severity": row["severity"],
            "visibility": row["visibility"],
            "project_ref": project_ref,
            "resource_snapshot": resource_snapshot,
            "artifact_refs": artifact_refs,
            "message": row["message"],
            "payload": payload,
            "prev_hash": row["prev_hash"],
            "prev_event_hash": row["prev_hash"],
            "event_hash": row["event_hash"],
        }


_LEDGER_SINGLETON: Optional[AuditLedgerStore] = None


def get_ledger_store() -> AuditLedgerStore:
    global _LEDGER_SINGLETON
    if _LEDGER_SINGLETON is None:
        config = get_audit_config()
        _LEDGER_SINGLETON = AuditLedgerStore(config.ledger_db_path)
    return _LEDGER_SINGLETON


def reset_ledger_store() -> None:
    global _LEDGER_SINGLETON
    _LEDGER_SINGLETON = None
