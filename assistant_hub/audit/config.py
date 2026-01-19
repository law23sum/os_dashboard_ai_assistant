"""Configuration helpers for the audit ledger and archive engine."""

from __future__ import annotations

import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Optional

from assistant_hub.config import DATA_DIR


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    raw = os.getenv(name)
    return raw if raw is not None else default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass
class AuditConfig:
    ledger_db_path: Path
    archive_dir: Path
    artifact_dir: Path
    rotation_mode: str
    rotation_max_events: int
    retention_days: int
    hmac_key_path: Path
    encryption_key_path: Path
    max_event_bytes: int
    compression: str

    def ensure_dirs(self) -> None:
        self.ledger_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.hmac_key_path.parent.mkdir(parents=True, exist_ok=True)
        self.encryption_key_path.parent.mkdir(parents=True, exist_ok=True)


_CONFIG: Optional[AuditConfig] = None


def get_audit_config(*, reload: bool = False) -> AuditConfig:
    global _CONFIG
    if _CONFIG is not None and not reload:
        return _CONFIG

    base_dir = Path(_env("AUDIT_BASE_DIR", str(DATA_DIR / "audit_ledger"))).expanduser()
    key_dir = Path(_env("AUDIT_KEY_DIR", str(base_dir / "keys"))).expanduser()
    ledger_db_path = Path(
        _env("AUDIT_LEDGER_DB_PATH", str(base_dir / "audit_ledger.db"))
    ).expanduser()
    archive_dir = Path(_env("AUDIT_ARCHIVE_DIR", str(base_dir / "archives"))).expanduser()
    artifact_dir = Path(
        _env("AUDIT_ARTIFACT_DIR", str(base_dir / "artifacts"))
    ).expanduser()
    rotation_mode = (_env("AUDIT_ARCHIVE_ROTATION_MODE", "daily") or "daily").lower()
    rotation_max_events = _env_int("AUDIT_ARCHIVE_ROTATION_MAX_EVENTS", 10000)
    retention_days = _env_int("AUDIT_ARCHIVE_RETENTION_DAYS", 365)
    hmac_key_path = Path(
        _env("AUDIT_HMAC_KEY_PATH", _env("AUDIT_SIGNING_KEY_PATH", str(key_dir / "audit_hmac.key")))
        or str(key_dir / "audit_hmac.key")
    ).expanduser()
    encryption_key_path = Path(
        _env("AUDIT_ENCRYPTION_KEY_PATH", str(key_dir / "audit_encryption.key"))
    ).expanduser()
    max_event_bytes = _env_int("AUDIT_MAX_EVENT_BYTES", 256 * 1024)
    compression = (_env("AUDIT_ARCHIVE_COMPRESSION", "none") or "none").lower()
    if rotation_mode not in {"daily", "size"}:
        rotation_mode = "daily"
    if compression not in {"none", "gzip"}:
        compression = "none"

    _CONFIG = AuditConfig(
        ledger_db_path=ledger_db_path,
        archive_dir=archive_dir,
        artifact_dir=artifact_dir,
        rotation_mode=rotation_mode,
        rotation_max_events=rotation_max_events,
        retention_days=retention_days,
        hmac_key_path=hmac_key_path,
        encryption_key_path=encryption_key_path,
        max_event_bytes=max_event_bytes,
        compression=compression,
    )
    _CONFIG.ensure_dirs()
    return _CONFIG


def _load_key(path: Path, *, bytes_len: int, create_if_missing: bool) -> bytes:
    if path.exists():
        return path.read_bytes()
    if not create_if_missing:
        raise FileNotFoundError(f"Key not found at {path}")
    key = os.urandom(bytes_len)
    path.write_bytes(key)
    if os.name != "nt":
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    return key


def load_hmac_key(*, create_if_missing: bool = True) -> bytes:
    config = get_audit_config()
    return _load_key(config.hmac_key_path, bytes_len=32, create_if_missing=create_if_missing)


def load_encryption_key(*, create_if_missing: bool = True) -> bytes:
    config = get_audit_config()
    return _load_key(
        config.encryption_key_path, bytes_len=32, create_if_missing=create_if_missing
    )


def key_id(key: bytes) -> str:
    return sha256(key).hexdigest()[:16]
