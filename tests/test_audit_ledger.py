"""Tests for the immutable audit ledger and archive engine."""

from __future__ import annotations

import json
import sqlite3
import uuid

import pytest
from fastapi.testclient import TestClient

from assistant_hub.audit.config import get_audit_config
from assistant_hub.audit.ledger import get_ledger_store, reset_ledger_store
from assistant_hub.audit.archive import AuditArchiveEngine
from assistant_hub.telemetry.hub import get_event_hub, reset_event_hub


def _setup_audit_env(tmp_path, monkeypatch) -> None:
    base_dir = tmp_path / "audit"
    monkeypatch.setenv("AUDIT_BASE_DIR", str(base_dir))
    monkeypatch.setenv("AUDIT_LEDGER_DB_PATH", str(base_dir / "audit_ledger.db"))
    monkeypatch.setenv("AUDIT_ARCHIVE_DIR", str(base_dir / "archives"))
    monkeypatch.setenv("AUDIT_ARTIFACT_DIR", str(base_dir / "artifacts"))
    monkeypatch.setenv("AUDIT_HMAC_KEY_PATH", str(base_dir / "keys" / "audit_hmac.key"))
    monkeypatch.setenv("AUDIT_ENCRYPTION_KEY_PATH", str(base_dir / "keys" / "audit_enc.key"))
    monkeypatch.setenv("AUDIT_ARCHIVE_ROTATION_MODE", "size")
    monkeypatch.setenv("AUDIT_ARCHIVE_ROTATION_MAX_EVENTS", "2")
    monkeypatch.setenv("AUDIT_ARCHIVE_COMPRESSION", "none")
    get_audit_config(reload=True)
    reset_ledger_store()
    reset_event_hub()


def _emit_sample_events(count: int) -> None:
    hub = get_event_hub()
    for idx in range(count):
        hub.ingest(
            {
                "event_type": "DECISION",
                "message": f"event-{idx}",
                "payload": {"index": idx},
                "agent_id": "test-agent",
                "session_id": "test-session",
                "correlation_id": str(uuid.uuid4()),
            }
        )


def test_hash_chain_verification_ok(tmp_path, monkeypatch):
    _setup_audit_env(tmp_path, monkeypatch)
    _emit_sample_events(3)
    ledger = get_ledger_store()
    report = ledger.verify_chain()
    assert report["ok"] is True


def test_hash_chain_detects_tamper(tmp_path, monkeypatch):
    _setup_audit_env(tmp_path, monkeypatch)
    _emit_sample_events(2)
    ledger = get_ledger_store()
    conn = sqlite3.connect(ledger.db_path)
    try:
        conn.execute("DROP TRIGGER audit_events_no_update")
        conn.execute("UPDATE audit_events SET message = 'tampered' WHERE seq = 2")
        conn.commit()
    finally:
        conn.close()
    report = ledger.verify_chain()
    assert report["ok"] is False
    assert report["first_bad_seq"] == 2


def test_append_only_triggers_block_modifications(tmp_path, monkeypatch):
    _setup_audit_env(tmp_path, monkeypatch)
    _emit_sample_events(1)
    ledger = get_ledger_store()
    conn = sqlite3.connect(ledger.db_path)
    try:
        with pytest.raises(sqlite3.DatabaseError) as exc:
            conn.execute("UPDATE audit_events SET message = 'blocked' WHERE seq = 1")
        assert "append-only" in str(exc.value)
        with pytest.raises(sqlite3.DatabaseError) as exc:
            conn.execute("DELETE FROM audit_events WHERE seq = 1")
        assert "append-only" in str(exc.value)
    finally:
        conn.close()


def test_archive_rotation_and_verify(tmp_path, monkeypatch):
    _setup_audit_env(tmp_path, monkeypatch)
    _emit_sample_events(3)
    engine = AuditArchiveEngine()
    result = engine.rotate()
    assert result is not None
    report = engine.verify_archive(result.archive_path)
    assert report["ok"] is True


def test_audit_events_api(tmp_path, monkeypatch):
    _setup_audit_env(tmp_path, monkeypatch)
    from backend_api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/audit/events",
        json={
            "event_type": "DECISION",
            "message": "api audit event",
            "payload": {"source": "test"},
            "agent_id": "api-test",
            "session_id": "api-session",
            "correlation_id": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "event_id" in data
    assert "event_hash" in data
