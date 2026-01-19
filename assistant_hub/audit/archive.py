"""Secure archive engine for the audit ledger."""

from __future__ import annotations

import gzip
import hmac
import io
import json
import os
import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .config import get_audit_config, key_id, load_encryption_key, load_hmac_key
from .hashing import canonical_json, compute_event_hash, event_hash_payload
from .ledger import AuditLedgerStore, get_ledger_store


@dataclass(frozen=True)
class ArchiveResult:
    archive_id: str
    archive_path: Path
    start_seq: int
    end_seq: int
    record_count: int
    segment_sha256: str
    sealed_at: str
    encryption_kid: str
    compression: str


class AuditArchiveEngine:
    def __init__(
        self,
        ledger: Optional[AuditLedgerStore] = None,
    ) -> None:
        self.config = get_audit_config()
        self.ledger = ledger or get_ledger_store()

    def rotate(self) -> Optional[ArchiveResult]:
        self.config.ensure_dirs()
        rows = self._select_rotation_rows()
        if not rows:
            return None

        archive_id = str(uuid4())
        start_seq = int(rows[0]["seq"])
        end_seq = int(rows[-1]["seq"])
        start_ts = rows[0]["ts_utc"]
        end_ts = rows[-1]["ts_utc"]
        record_count = len(rows)
        last_event_hash = rows[-1]["event_hash"]

        segment_bytes, segment_name = self._build_segment(rows, archive_id)
        segment_sha256 = sha256(segment_bytes).hexdigest()

        manifest = {
            "archive_id": archive_id,
            "start_seq": start_seq,
            "end_seq": end_seq,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "segment_file": segment_name,
            "segment_sha256": segment_sha256,
            "last_event_hash": last_event_hash,
            "record_count": record_count,
            "schema_version": 1,
            "compression": self.config.compression,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        encryption_key = load_encryption_key()
        encryption_kid = key_id(encryption_key)
        manifest["encryption"] = "aes-gcm"
        manifest["encryption_kid"] = encryption_kid

        sealed_at = datetime.now(timezone.utc).isoformat()
        manifest["sealed_at"] = sealed_at
        seal = self._seal_manifest(manifest)
        manifest["seal"] = seal
        encrypted_path = self.config.archive_dir / f"{archive_id}.zip.enc"
        bundle = self._bundle_manifest(manifest, segment_bytes, segment_name)
        encrypted_blob = self._encrypt_bundle(bundle, encryption_key)
        encrypted_path.write_bytes(encrypted_blob)

        self.ledger.insert_archive_record(
            archive_id=archive_id,
            start_seq=start_seq,
            end_seq=end_seq,
            start_ts=start_ts,
            end_ts=end_ts,
            archive_path=str(encrypted_path),
            segment_sha256=segment_sha256,
            sealed_at=sealed_at,
            encryption_kid=encryption_kid,
            compression=self.config.compression,
        )

        try:
            # Lazy import to avoid circular dependency with sdk -> telemetry.emitter
            from .sdk import get_default_emitter, new_correlation_id
            
            emitter = get_default_emitter(agent_id="os_dashboard")
            correlation_id = new_correlation_id()
            rotation_event = emitter.emit(
                event_type="ARCHIVE_ROTATION",
                message="Archive rotation completed",
                payload={
                    "archive_id": archive_id,
                    "start_seq": start_seq,
                    "end_seq": end_seq,
                    "record_count": record_count,
                    "archive_path": str(encrypted_path),
                },
                correlation_id=correlation_id,
            )
            emitter.emit(
                event_type="ARCHIVE_SEALED",
                message="Archive sealed",
                payload={
                    "archive_id": archive_id,
                    "sealed_at": sealed_at,
                    "segment_sha256": segment_sha256,
                    "encryption_kid": encryption_kid,
                },
                correlation_id=correlation_id,
                causation_id=rotation_event.event_id,
            )
        except Exception:
            pass

        return ArchiveResult(
            archive_id=archive_id,
            archive_path=encrypted_path,
            start_seq=start_seq,
            end_seq=end_seq,
            record_count=record_count,
            segment_sha256=segment_sha256,
            sealed_at=sealed_at,
            encryption_kid=encryption_kid,
            compression=self.config.compression,
        )

    def verify_archive(self, archive_path: Path) -> Dict[str, Any]:
        try:
            data = Path(archive_path).read_bytes()
            encryption_key = load_encryption_key(create_if_missing=False)
            bundle = self._decrypt_bundle(data, encryption_key)

            with zipfile.ZipFile(io.BytesIO(bundle), "r") as zf:
                manifest_bytes = zf.read("manifest.json")
                manifest = json.loads(manifest_bytes.decode("utf-8"))
                segment_name = manifest["segment_file"]
                segment_bytes = zf.read(segment_name)

            if not self._verify_manifest(manifest):
                return {"ok": False, "reason": "manifest_seal_invalid"}
            if sha256(segment_bytes).hexdigest() != manifest.get("segment_sha256"):
                return {"ok": False, "reason": "segment_sha256_mismatch"}

            verify_chain = self._verify_segment_chain(segment_bytes, manifest.get("compression", "none"))
            if not verify_chain["ok"]:
                return verify_chain
            return {"ok": True, "archive_id": manifest.get("archive_id")}
        except Exception as exc:
            return {"ok": False, "reason": f"verify_error: {exc}"}

    def apply_retention(self) -> List[str]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.config.retention_days)
        removed: List[str] = []
        for record in self.ledger.list_archives():
            created_at = record.get("created_at") or ""
            try:
                created_dt = datetime.fromisoformat(created_at)
            except ValueError:
                continue
            if created_dt < cutoff:
                path = record.get("archive_path")
                if path and Path(path).exists():
                    Path(path).unlink()
                    removed.append(record.get("archive_id"))
        if removed:
            try:
                # Lazy import to avoid circular dependency with sdk -> telemetry.emitter
                from .sdk import get_default_emitter, new_correlation_id
                
                emitter = get_default_emitter(agent_id="os_dashboard")
                emitter.emit(
                    event_type="ARCHIVE_RETENTION_APPLIED",
                    message="Archive retention applied",
                    payload={"removed_archives": removed, "retention_days": self.config.retention_days},
                    correlation_id=new_correlation_id(),
                )
            except Exception:
                pass
        return removed

    def _select_rotation_rows(self) -> List[sqlite3.Row]:
        conn = self.ledger._connect()
        try:
            last_row = conn.execute(
                "SELECT end_seq FROM audit_archives ORDER BY end_seq DESC LIMIT 1"
            ).fetchone()
            last_end = int(last_row["end_seq"]) if last_row and last_row["end_seq"] else 0

            if self.config.rotation_mode == "size":
                rows = conn.execute(
                    """
                    SELECT * FROM audit_events
                    WHERE seq > ?
                    ORDER BY seq ASC
                    LIMIT ?
                    """,
                    (last_end, self.config.rotation_max_events),
                ).fetchall()
            else:
                cutoff = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                rows = conn.execute(
                    """
                    SELECT * FROM audit_events
                    WHERE seq > ? AND ts_utc < ?
                    ORDER BY seq ASC
                    """,
                    (last_end, cutoff.isoformat()),
                ).fetchall()
            return rows
        finally:
            conn.close()

    def _build_segment(self, rows: List[sqlite3.Row], archive_id: str) -> Tuple[bytes, str]:
        events = [self.ledger._row_to_event(row) for row in rows]
        serialized = []
        for event in events:
            serialized.append(canonical_json(event))
        payload = "\n".join(serialized) + "\n"
        segment_name = f"{archive_id}.jsonl"
        if self.config.compression == "gzip":
            compressed = gzip.compress(payload.encode("utf-8"))
            return compressed, f"{segment_name}.gz"
        return payload.encode("utf-8"), segment_name

    def _seal_manifest(self, manifest: Dict[str, Any], *, create_if_missing: bool = True) -> str:
        hmac_key = load_hmac_key(create_if_missing=create_if_missing)
        to_sign = dict(manifest)
        to_sign.pop("seal", None)
        encoded = canonical_json(to_sign).encode("utf-8")
        return hmac.new(hmac_key, encoded, sha256).hexdigest()

    def _verify_manifest(self, manifest: Dict[str, Any]) -> bool:
        seal = manifest.get("seal")
        if not seal:
            return False
        expected = self._seal_manifest(manifest, create_if_missing=False)
        return hmac.compare_digest(seal, expected)

    def _bundle_manifest(self, manifest: Dict[str, Any], segment_bytes: bytes, segment_name: str) -> bytes:
        bundle_io = io.BytesIO()
        with zipfile.ZipFile(bundle_io, "w", compression=zipfile.ZIP_STORED) as zf:
            zf.writestr("manifest.json", canonical_json(manifest))
            zf.writestr(segment_name, segment_bytes)
        return bundle_io.getvalue()

    @staticmethod
    def _encrypt_bundle(bundle: bytes, key: bytes) -> bytes:
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        encrypted = aesgcm.encrypt(nonce, bundle, None)
        return nonce + encrypted

    @staticmethod
    def _decrypt_bundle(blob: bytes, key: bytes) -> bytes:
        if len(blob) < 13:
            raise ValueError("Encrypted archive is too small")
        nonce = blob[:12]
        ciphertext = blob[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    def _verify_segment_chain(self, segment_bytes: bytes, compression: str) -> Dict[str, Any]:
        payload = segment_bytes
        if compression == "gzip":
            payload = gzip.decompress(segment_bytes)
        text = payload.decode("utf-8")
        lines = [line for line in text.splitlines() if line.strip()]
        expected_prev = None
        for idx, line in enumerate(lines):
            event = json.loads(line)
            found_prev = event.get("prev_hash") or event.get("prev_event_hash")
            if expected_prev is None:
                expected_prev = found_prev
            elif found_prev != expected_prev:
                return {"ok": False, "reason": "prev_hash_mismatch", "line": idx + 1}
            recomputed = compute_event_hash(event_hash_payload(event))
            if event.get("event_hash") != recomputed:
                return {"ok": False, "reason": "event_hash_mismatch", "line": idx + 1}
            expected_prev = event.get("event_hash")
        return {"ok": True}
