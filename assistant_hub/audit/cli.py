"""CLI helpers for the audit ledger and archive engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .archive import AuditArchiveEngine
from .config import load_encryption_key
from .ledger import get_ledger_store
from .sdk import new_correlation_id
from assistant_hub.telemetry.hub import get_event_hub


def emit_event(
    *,
    event_type: str,
    message: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    hub = get_event_hub()
    event = {
        "event_type": event_type,
        "message": message,
        "payload": payload or {},
        "agent_id": "os_dashboard",
        "correlation_id": new_correlation_id(),
    }
    return hub.ingest(event)


def verify_ledger(from_seq: Optional[int] = None, to_seq: Optional[int] = None) -> Dict[str, Any]:
    ledger = get_ledger_store()
    return ledger.verify_chain(from_seq=from_seq, to_seq=to_seq)


def rotate_archive_now() -> Dict[str, Any]:
    engine = AuditArchiveEngine()
    result = engine.rotate()
    if not result:
        return {"rotated": False}
    return {
        "rotated": True,
        "archive_id": result.archive_id,
        "archive_path": str(result.archive_path),
        "start_seq": result.start_seq,
        "end_seq": result.end_seq,
        "record_count": result.record_count,
        "segment_sha256": result.segment_sha256,
    }


def list_archives() -> list[Dict[str, Any]]:
    ledger = get_ledger_store()
    return ledger.list_archives()


def verify_archive(path: Path) -> Dict[str, Any]:
    engine = AuditArchiveEngine()
    return engine.verify_archive(path)


def restore_archive(path: Path, output_dir: Path) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = path.read_bytes()
    key = load_encryption_key(create_if_missing=False)
    nonce = data[:12]
    ciphertext = data[12:]
    bundle = AESGCM(key).decrypt(nonce, ciphertext, None)
    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(bundle), "r") as zf:
        for name in zf.namelist():
            dest = output_dir / name
            dest.write_bytes(zf.read(name))
    return {"restored": True, "output_dir": str(output_dir)}
