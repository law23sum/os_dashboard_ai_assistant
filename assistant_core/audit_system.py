"""

Audit and Governance System with Git Integration

Provides comprehensive audit trails, compliance tracking, and version control integration

"""

import asyncio
import base64
import hmac
import json
import hashlib
import logging
import shutil
import subprocess
import uuid

from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union, TYPE_CHECKING

from config.logging_config import setup_logger

from assistant_core.cir.schema import (
    CIRDocument,
    ContentType,
    SourceSystem,
    ProvenanceEvent as Provenance,
)
from api_connectors.universal_connector import (
    BaseConnector,
    OperationResult,
    GitConnector,
)

if TYPE_CHECKING:
    from config.config import AuditSettings


class AuditEventType(Enum):
    """Types of audit events"""

    RESOURCE_READ = "resource_read"
    RESOURCE_WRITE = "resource_write"
    RESOURCE_CREATE = "resource_create"
    RESOURCE_DELETE = "resource_delete"
    WORKFLOW_EXECUTE = "workflow_execute"
    SEARCH_QUERY = "search_query"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_CONFIG = "system_config"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    COMPLIANCE_CHECK = "compliance_check"
    SECURITY_EVENT = "security_event"


class AuditLevel(Enum):
    """Audit event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventFamily(Enum):
    """Canonical audit event families."""

    DATA_CHANGE = "data_change"
    ACTION_STEP = "action_step"
    CRITICAL_EVENT = "critical_event"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    CUSTOM = "custom"


@dataclass
class AuditEvent:
    """Individual audit event record."""

    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    action: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    connector_name: Optional[str] = None
    resource_id: Optional[str] = None
    level: AuditLevel = AuditLevel.INFO
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    data_hash: Optional[str] = None
    tenant_id: Optional[str] = None
    workspace_id: Optional[str] = None
    actor_id: Optional[str] = None
    subject_id: Optional[str] = None
    subject_type: Optional[str] = None
    event_family: EventFamily = EventFamily.ACTION_STEP
    rule_id: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    segment_id: Optional[str] = None
    prev_event_hash: Optional[str] = None
    event_hash: Optional[str] = None
    payload_ref: Optional[str] = None
    payload_hash: Optional[str] = None
    retention_policy_id: Optional[str] = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow()
        if not self.actor_id and self.user_id:
            self.actor_id = self.user_id
        if not self.subject_id and self.resource_id:
            self.subject_id = self.resource_id
        if not self.payload_hash and self.data_hash:
            self.payload_hash = self.data_hash


@dataclass
class SegmentManifest:
    """Metadata for a sealed audit segment."""

    version: str
    tenant_id: str
    segment_id: str
    start_ts: str
    end_ts: str
    record_count: int
    first_event_hash: Optional[str]
    last_event_hash: Optional[str]
    prev_segment_hash: Optional[str]
    merkle_root: Optional[str]
    events_file_sha256: str
    compression: str
    encryption: str
    retention_policy_id: str
    created_at: str
    segment_hash: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class SegmentIndex:
    """Derived index for a segment (rebuildable)."""

    actors: Dict[str, List[int]] = field(default_factory=dict)
    subjects: Dict[str, List[int]] = field(default_factory=dict)
    event_types: Dict[str, List[int]] = field(default_factory=dict)
    event_families: Dict[str, List[int]] = field(default_factory=dict)

    def add_event(self, event: AuditEvent, position: int) -> None:
        self._append(self.actors, event.actor_id, position)
        self._append(self.subjects, event.subject_id, position)
        self._append(self.event_types, event.event_type.value, position)
        self._append(self.event_families, event.event_family.value, position)

    @staticmethod
    def _append(store: Dict[str, List[int]], key: Optional[str], value: int) -> None:
        if not key:
            return
        store.setdefault(key, []).append(value)

    def to_storage_dict(self, encoding: str = "delta") -> Dict[str, Any]:
        return {
            "encoding": encoding,
            "actors": self._encode_map(self.actors, encoding),
            "subjects": self._encode_map(self.subjects, encoding),
            "event_types": self._encode_map(self.event_types, encoding),
            "event_families": self._encode_map(self.event_families, encoding),
        }

    @classmethod
    def from_storage_dict(cls, payload: Dict[str, Any]) -> "SegmentIndex":
        encoding = payload.get("encoding", "raw")
        instance = cls()
        instance.actors = cls._decode_map(payload.get("actors", {}), encoding)
        instance.subjects = cls._decode_map(payload.get("subjects", {}), encoding)
        instance.event_types = cls._decode_map(payload.get("event_types", {}), encoding)
        instance.event_families = cls._decode_map(payload.get("event_families", {}), encoding)
        return instance

    @staticmethod
    def _encode_map(store: Dict[str, List[int]], encoding: str) -> Dict[str, List[int]]:
        if encoding == "delta":
            return {key: _delta_encode(values) for key, values in store.items()}
        return {key: list(values) for key, values in store.items()}

    @staticmethod
    def _decode_map(store: Dict[str, List[int]], encoding: str) -> Dict[str, List[int]]:
        if encoding == "delta":
            return {key: _delta_decode(values) for key, values in store.items()}
        return {key: list(values) for key, values in store.items()}


@dataclass(frozen=True)
class EventRef:
    """Reference pointer for indexed lookups."""

    segment_id: str
    position: int
    event_id: str
    event_hash: str


@dataclass
class SnapshotRecord:
    """Snapshot metadata linked to the event log."""

    snapshot_id: str
    created_at: str
    state_hash: str
    segment_id: Optional[str]
    event_hash: Optional[str]
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpenSegmentState:
    """Mutable state for an open segment."""

    tenant_id: str
    segment_id: str
    bucket: str
    sequence: int
    events_path: Path
    manifest_path: Path
    index_path: Path
    start_ts: datetime
    end_ts: datetime
    record_count: int
    prev_segment_hash: Optional[str]
    last_event_hash: Optional[str]
    event_hashes: List[str] = field(default_factory=list)
    events_hasher: Any = field(default_factory=hashlib.sha256)
    index: SegmentIndex = field(default_factory=SegmentIndex)
    retention_policy_id: str = "default"


def _stable_json_dumps(payload: Dict[str, Any]) -> str:
    return json.dumps(
        payload or {},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _delta_encode(values: List[int]) -> List[int]:
    if not values:
        return []
    encoded = [values[0]]
    prev = values[0]
    for value in values[1:]:
        encoded.append(value - prev)
        prev = value
    return encoded


def _delta_decode(values: List[int]) -> List[int]:
    if not values:
        return []
    decoded = [values[0]]
    total = values[0]
    for delta in values[1:]:
        total += delta
        decoded.append(total)
    return decoded


def _compute_merkle_root(hashes: List[str]) -> Optional[str]:
    if not hashes:
        return None
    layer = list(hashes)
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        next_layer = []
        for idx in range(0, len(layer), 2):
            combined = layer[idx] + layer[idx + 1]
            next_layer.append(hashlib.sha256(combined.encode("utf-8")).hexdigest())
        layer = next_layer
    return layer[0]


@dataclass
class ComplianceRule:
    """Compliance rule definition"""

    rule_id: str
    framework: ComplianceFramework
    name: str
    description: str
    rule_type: str  # 'data_retention', 'access_control', 'encryption', etc.
    config: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class ComplianceViolation:
    """Compliance violation record"""

    violation_id: str
    rule_id: str
    event_id: str
    severity: AuditLevel
    description: str
    detected_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    def __post_init__(self):
        if not self.violation_id:
            self.violation_id = str(uuid.uuid4())
        if not self.detected_at:
            self.detected_at = datetime.utcnow()


@dataclass
class DataLineage:
    """Data lineage tracking"""

    lineage_id: str
    resource_id: str
    connector_name: str
    source_resources: List[str]
    transformations: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if not self.lineage_id:
            self.lineage_id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()


class AuditStorage:
    """Storage backend for audit events."""

    def __init__(
        self,
        storage_path: str = "audit_data",
        segment_time_format: str = "%Y%m%d%H%M",
        segment_time_window_minutes: int = 5,
        segment_max_events: int = 5000,
        storage_tiers: Optional[Dict[str, Path]] = None,
        signing_key: Optional[Union[str, bytes]] = None,
        retention_defaults: Optional[Dict[str, int]] = None,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.storage_path / "events").mkdir(exist_ok=True)
        (self.storage_path / "segments").mkdir(exist_ok=True)
        (self.storage_path / "compliance").mkdir(exist_ok=True)
        (self.storage_path / "lineage").mkdir(exist_ok=True)
        (self.storage_path / "exports").mkdir(exist_ok=True)

        self.segment_time_format = segment_time_format
        self.segment_time_window_minutes = max(1, segment_time_window_minutes)
        self.segment_max_events = segment_max_events
        self.signing_key = signing_key.encode("utf-8") if isinstance(signing_key, str) else signing_key
        self.retention_defaults = retention_defaults or {
            "hot_days": 30,
            "archive_days": 395,
            "backup_years": 7,
            "cloud_years": 7,
        }

        tiers_root = self.storage_path / "tiers"
        default_tiers: Dict[str, Path] = {
            "remote_archive": tiers_root / "remote_archive",
            "hardware_backup": tiers_root / "hardware_backup",
            "cloud_backup": tiers_root / "cloud_backup",
        }
        self.storage_tiers = storage_tiers or default_tiers
        for tier_path in self.storage_tiers.values():
            if tier_path is None:
                continue
            Path(tier_path).mkdir(parents=True, exist_ok=True)

        self.critical_events_path = self.storage_path / "critical_events.jsonl"
        self.snapshots_path = self.storage_path / "snapshots.jsonl"

        self.events_cache: Dict[str, AuditEvent] = {}
        self.cache_size = 10000

        self._open_segments: Dict[str, OpenSegmentState] = {}
        self._segment_sequences: Dict[Tuple[str, str], int] = defaultdict(int)
        self._segment_chain: Dict[str, Optional[str]] = defaultdict(lambda: None)
        self._global_indexes: Dict[str, Dict[str, List[EventRef]]] = {
            "actors": defaultdict(list),
            "subjects": defaultdict(list),
            "event_types": defaultdict(list),
            "event_families": defaultdict(list),
        }

    async def store_event(self, event: AuditEvent):
        """Store audit event."""
        if not event.event_family:
            event.event_family = EventFamily.ACTION_STEP

        tenant_id = event.tenant_id or "default"
        segment_state = await self._get_open_segment(tenant_id, event.timestamp, event.retention_policy_id)

        payload_hash = event.payload_hash or self._hash_payload(event.details)
        event.payload_hash = payload_hash
        event.prev_event_hash = segment_state.last_event_hash
        event.event_hash = self._compute_event_hash(event)
        event.segment_id = segment_state.segment_id

        event_data = self._serialize_event(event)
        line = json.dumps(event_data, default=str) + "\n"

        segment_state.events_path.parent.mkdir(parents=True, exist_ok=True)
        with segment_state.events_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
        segment_state.events_hasher.update(line.encode("utf-8"))

        segment_state.event_hashes.append(event.event_hash)
        segment_state.record_count += 1
        segment_state.end_ts = event.timestamp
        segment_state.last_event_hash = event.event_hash
        segment_state.index.add_event(event, segment_state.record_count - 1)
        self._update_global_indexes(event, segment_state.segment_id, segment_state.record_count - 1)

        self._append_critical_event(event)
        self._write_legacy_daily_event(event_data, event.timestamp)

        # Add to cache
        self.events_cache[event.event_id] = event

        # Trim cache if too large
        if len(self.events_cache) > self.cache_size:
            sorted_events = sorted(
                self.events_cache.items(), key=lambda x: x[1].timestamp
            )
            for event_id, _ in sorted_events[: len(sorted_events) - self.cache_size]:
                del self.events_cache[event_id]

        if segment_state.record_count >= self.segment_max_events:
            await self._seal_segment(segment_state)

    async def get_events(
        self, start_date: datetime, end_date: datetime, filters: Dict[str, Any] = None
    ) -> List[AuditEvent]:
        """Retrieve audit events within date range."""
        events: List[AuditEvent] = []
        tenant_filter = filters.get("tenant_id") if filters else None

        for events_file in self._iter_segment_event_files(tenant_filter):
            if not events_file.exists():
                continue
            with events_file.open("r", encoding="utf-8") as handle:
                for line in handle:
                    try:
                        event_data = json.loads(line.strip())
                        event = self._deserialize_event(event_data)
                        if start_date <= event.timestamp <= end_date:
                            if self._event_matches_filters(event, filters):
                                events.append(event)
                    except Exception:
                        continue

        events.sort(key=lambda evt: evt.timestamp)
        return events

    def get_critical_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return critical events for fast singularity lookups."""
        if not self.critical_events_path.exists():
            return []
        results: List[Dict[str, Any]] = []
        with self.critical_events_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                if tenant_id and record.get("tenant_id") != tenant_id:
                    continue
                timestamp = record.get("timestamp")
                if timestamp:
                    try:
                        record_time = datetime.fromisoformat(timestamp)
                    except ValueError:
                        record_time = None
                else:
                    record_time = None
                if start_date and record_time and record_time < start_date:
                    continue
                if end_date and record_time and record_time > end_date:
                    continue
                results.append(record)
        return results

    def _iter_segment_event_files(self, tenant_id: Optional[str]) -> Iterable[Path]:
        base = self.storage_path / "segments"
        if tenant_id:
            base = base / tenant_id
        if not base.exists():
            return []
        return sorted(base.rglob("*.events.jsonl"))

    async def _get_open_segment(
        self,
        tenant_id: str,
        timestamp: datetime,
        retention_policy_id: Optional[str],
    ) -> OpenSegmentState:
        bucket = self._segment_bucket(timestamp)
        open_state = self._open_segments.get(tenant_id)

        if open_state:
            if open_state.bucket != bucket or open_state.record_count >= self.segment_max_events:
                await self._seal_segment(open_state)
                open_state = None

        if open_state is None:
            sequence = self._segment_sequences[(tenant_id, bucket)]
            segment_id = f"{bucket}-{sequence:04d}"
            self._segment_sequences[(tenant_id, bucket)] += 1
            segment_dir = self._segment_dir(tenant_id, bucket)
            events_path = segment_dir / f"{segment_id}.events.jsonl"
            manifest_path = segment_dir / f"{segment_id}.manifest.json"
            index_path = segment_dir / f"{segment_id}.index.json"
            open_state = OpenSegmentState(
                tenant_id=tenant_id,
                segment_id=segment_id,
                bucket=bucket,
                sequence=sequence,
                events_path=events_path,
                manifest_path=manifest_path,
                index_path=index_path,
                start_ts=timestamp,
                end_ts=timestamp,
                record_count=0,
                prev_segment_hash=self._segment_chain[tenant_id],
                last_event_hash=None,
                retention_policy_id=retention_policy_id or "default",
            )
            self._open_segments[tenant_id] = open_state
        return open_state

    def _segment_bucket(self, timestamp: datetime) -> str:
        window = self.segment_time_window_minutes
        minute = (timestamp.minute // window) * window
        bucket_time = timestamp.replace(minute=minute, second=0, microsecond=0)
        return bucket_time.strftime(self.segment_time_format)

    def _segment_dir(self, tenant_id: str, bucket: str) -> Path:
        date_prefix = bucket[:8]
        if len(date_prefix) < 8:
            return self.storage_path / "segments" / tenant_id
        return (
            self.storage_path
            / "segments"
            / tenant_id
            / date_prefix[:4]
            / date_prefix[4:6]
            / date_prefix[6:8]
        )

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        serialized = _stable_json_dumps(payload)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _compute_event_hash(self, event: AuditEvent) -> str:
        seed = "|".join(
            [
                event.event_id,
                event.event_type.value,
                event.timestamp.isoformat(),
                event.actor_id or "",
                event.subject_id or "",
                event.payload_hash or "",
                event.prev_event_hash or "",
            ]
        )
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

    def _serialize_event(self, event: AuditEvent) -> Dict[str, Any]:
        event_data = asdict(event)
        event_data["timestamp"] = event.timestamp.isoformat()
        event_data["event_type"] = event.event_type.value
        event_data["level"] = event.level.value
        event_data["event_family"] = event.event_family.value if event.event_family else None
        return event_data

    def _write_legacy_daily_event(self, event_data: Dict[str, Any], timestamp: datetime) -> None:
        date_str = timestamp.strftime("%Y-%m-%d")
        events_file = self.storage_path / "events" / f"{date_str}.jsonl"
        with events_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event_data, default=str) + "\n")

    def _append_critical_event(self, event: AuditEvent) -> None:
        if event.event_family != EventFamily.CRITICAL_EVENT and event.level != AuditLevel.CRITICAL:
            return
        record = {
            "event_id": event.event_id,
            "segment_id": event.segment_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "event_family": event.event_family.value,
            "rule_id": event.rule_id,
            "evidence_refs": event.evidence_refs,
            "actor_id": event.actor_id,
            "subject_id": event.subject_id,
            "subject_type": event.subject_type,
            "tenant_id": event.tenant_id,
            "workspace_id": event.workspace_id,
            "event_hash": event.event_hash,
            "severity": event.level.value,
        }
        with self.critical_events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def _update_global_indexes(self, event: AuditEvent, segment_id: str, position: int) -> None:
        ref = EventRef(
            segment_id=segment_id,
            position=position,
            event_id=event.event_id,
            event_hash=event.event_hash or "",
        )
        if event.actor_id:
            self._global_indexes["actors"][event.actor_id].append(ref)
        if event.subject_id:
            self._global_indexes["subjects"][event.subject_id].append(ref)
        self._global_indexes["event_types"][event.event_type.value].append(ref)
        self._global_indexes["event_families"][event.event_family.value].append(ref)

    async def _seal_segment(self, segment_state: OpenSegmentState) -> None:
        if segment_state.record_count == 0:
            self._open_segments.pop(segment_state.tenant_id, None)
            return

        merkle_root = _compute_merkle_root(segment_state.event_hashes)
        manifest = SegmentManifest(
            version="1.0",
            tenant_id=segment_state.tenant_id,
            segment_id=segment_state.segment_id,
            start_ts=segment_state.start_ts.isoformat(),
            end_ts=segment_state.end_ts.isoformat(),
            record_count=segment_state.record_count,
            first_event_hash=segment_state.event_hashes[0] if segment_state.event_hashes else None,
            last_event_hash=segment_state.last_event_hash,
            prev_segment_hash=segment_state.prev_segment_hash,
            merkle_root=merkle_root,
            events_file_sha256=segment_state.events_hasher.hexdigest(),
            compression="none",
            encryption="none",
            retention_policy_id=segment_state.retention_policy_id,
            created_at=datetime.utcnow().isoformat(),
        )
        manifest_payload = asdict(manifest)
        manifest_payload.pop("segment_hash", None)
        manifest_payload.pop("signature", None)
        segment_hash = self._hash_manifest(manifest_payload)
        manifest_payload["segment_hash"] = segment_hash
        signature = self._sign_manifest(manifest_payload)
        if signature:
            manifest_payload["signature"] = signature

        segment_state.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with segment_state.manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(manifest_payload, handle, indent=2, sort_keys=True)

        index_payload = segment_state.index.to_storage_dict()
        with segment_state.index_path.open("w", encoding="utf-8") as handle:
            json.dump(index_payload, handle, indent=2, sort_keys=True)

        self._segment_chain[segment_state.tenant_id] = segment_hash
        self._open_segments.pop(segment_state.tenant_id, None)

        self._replicate_segment(segment_state)

    def _hash_manifest(self, manifest_payload: Dict[str, Any]) -> str:
        encoded = json.dumps(manifest_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _sign_manifest(self, manifest_payload: Dict[str, Any]) -> Optional[str]:
        if not self.signing_key:
            return None
        payload = json.dumps(manifest_payload, sort_keys=True, separators=(",", ":"))
        return hmac.new(self.signing_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def _write_archive_bundle(self, segment_state: OpenSegmentState, tier_root: Path) -> None:
        import zipfile

        sources = [segment_state.events_path, segment_state.manifest_path, segment_state.index_path]
        relative_dir = segment_state.events_path.parent.relative_to(self.storage_path)
        archive_dir = tier_root / relative_dir
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / f"{segment_state.segment_id}.zip"

        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source in sources:
                if not source.exists():
                    continue
                archive.write(source, arcname=source.name)

        manifest_payload: Dict[str, Any] = {}
        if segment_state.manifest_path.exists():
            try:
                manifest_payload = json.loads(segment_state.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                manifest_payload = {}

        archive_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        archive_manifest = {
            "segment_id": segment_state.segment_id,
            "tenant_id": segment_state.tenant_id,
            "created_at": datetime.utcnow().isoformat(),
            "archive_sha256": archive_hash,
            "compression": "zip",
            "segment_hash": manifest_payload.get("segment_hash"),
            "events_file_sha256": manifest_payload.get("events_file_sha256"),
            "files": [source.name for source in sources if source.exists()],
        }
        archive_manifest_path = archive_dir / f"{segment_state.segment_id}.archive.json"
        archive_manifest_path.write_text(
            json.dumps(archive_manifest, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _replicate_segment(self, segment_state: OpenSegmentState) -> None:
        sources = [segment_state.events_path, segment_state.manifest_path, segment_state.index_path]
        for tier_name, tier_root in self.storage_tiers.items():
            if tier_root is None:
                continue
            tier_root = Path(tier_root)
            if tier_name == "remote_archive":
                self._write_archive_bundle(segment_state, tier_root)
                continue
            for source in sources:
                if not source.exists():
                    continue
                relative = source.relative_to(self.storage_path)
                destination = tier_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

    async def seal_all(self) -> None:
        for segment_state in list(self._open_segments.values()):
            await self._seal_segment(segment_state)

    async def record_snapshot(
        self,
        snapshot_id: str,
        state_hash: str,
        segment_id: Optional[str],
        event_hash: Optional[str],
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        record = SnapshotRecord(
            snapshot_id=snapshot_id,
            created_at=datetime.utcnow().isoformat(),
            state_hash=state_hash,
            segment_id=segment_id,
            event_hash=event_hash,
            source=source,
            metadata=metadata or {},
        )
        with self.snapshots_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record)) + "\n")

    async def export_pack(
        self,
        start_date: datetime,
        end_date: datetime,
        tenant_id: Optional[str] = None,
    ) -> Path:
        await self.seal_all()
        segments = self._collect_segments(start_date, end_date, tenant_id)
        pack_id = f"audit-pack-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        pack_path = self.storage_path / "exports" / f"{pack_id}.zip"

        import zipfile

        segment_hashes = []
        pack_manifest = {
            "pack_id": pack_id,
            "generated_at": datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "segments": [],
        }
        with zipfile.ZipFile(pack_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for selection in segments:
                archive.write(selection["events"], arcname=selection["events"].relative_to(self.storage_path).as_posix())
                archive.write(selection["manifest"], arcname=selection["manifest"].relative_to(self.storage_path).as_posix())
                archive.write(selection["index"], arcname=selection["index"].relative_to(self.storage_path).as_posix())
                segment_hashes.append(selection["segment_hash"])
                pack_manifest["segments"].append(
                    {
                        "segment_id": selection["segment_id"],
                        "segment_hash": selection["segment_hash"],
                        "start_ts": selection["start_ts"],
                        "end_ts": selection["end_ts"],
                    }
                )
            pack_manifest["pack_hash"] = hashlib.sha256("".join(segment_hashes).encode("utf-8")).hexdigest()
            archive.writestr("pack_manifest.json", json.dumps(pack_manifest, indent=2))

        return pack_path

    async def export_parquet(
        self,
        start_date: datetime,
        end_date: datetime,
        tenant_id: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Export audit events to parquet for cold, columnar storage."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError("pandas is required for parquet export") from exc

        output_dir = output_dir or (self.storage_path / "parquet")
        output_dir.mkdir(parents=True, exist_ok=True)

        events = await self.get_events(start_date, end_date, {"tenant_id": tenant_id} if tenant_id else None)
        rows: List[Dict[str, Any]] = []
        for event in events:
            payload = asdict(event)
            payload["timestamp"] = event.timestamp.isoformat()
            payload["event_type"] = event.event_type.value
            payload["level"] = event.level.value
            if event.event_family:
                payload["event_family"] = event.event_family.value
            rows.append(payload)

        columns = list(AuditEvent.__dataclass_fields__.keys())
        frame = pd.DataFrame(rows, columns=columns)
        filename = f"audit_events_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.parquet"
        output_path = output_dir / filename
        try:
            frame.to_parquet(output_path, compression="zstd", index=False)
        except Exception as exc:
            raise RuntimeError("parquet export requires pyarrow/fastparquet with zstd support") from exc
        return output_path

    def compact_daily_indexes(
        self,
        date: datetime,
        tenant_id: Optional[str] = None,
    ) -> Optional[Path]:
        """Build a daily rollup index from per-segment indexes."""
        date_key = date.strftime("%Y%m%d")
        base = self.storage_path / "segments"
        if tenant_id:
            base = base / tenant_id
        day_dir = base / date_key[:4] / date_key[4:6] / date_key[6:8]
        if not day_dir.exists():
            return None

        index_files = sorted(day_dir.glob("*.index.json"))
        if not index_files:
            return None

        rollup: Dict[str, Any] = {
            "generated_at": datetime.utcnow().isoformat(),
            "date": date.strftime("%Y-%m-%d"),
            "encoding": "delta",
            "segments": [],
            "actors": {},
            "subjects": {},
            "event_types": {},
            "event_families": {},
        }

        for index_file in index_files:
            segment_id = index_file.name.replace(".index.json", "")
            manifest_file = index_file.with_name(f"{segment_id}.manifest.json")
            manifest_payload = {}
            if manifest_file.exists():
                try:
                    manifest_payload = json.loads(manifest_file.read_text(encoding="utf-8"))
                except Exception:
                    manifest_payload = {}
            rollup["segments"].append(
                {
                    "segment_id": segment_id,
                    "segment_hash": manifest_payload.get("segment_hash"),
                    "start_ts": manifest_payload.get("start_ts"),
                    "end_ts": manifest_payload.get("end_ts"),
                }
            )

            try:
                index_payload = json.loads(index_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            index = SegmentIndex.from_storage_dict(index_payload)
            for key, positions in index.actors.items():
                rollup["actors"].setdefault(key, []).append(
                    {"segment_id": segment_id, "positions": _delta_encode(positions)}
                )
            for key, positions in index.subjects.items():
                rollup["subjects"].setdefault(key, []).append(
                    {"segment_id": segment_id, "positions": _delta_encode(positions)}
                )
            for key, positions in index.event_types.items():
                rollup["event_types"].setdefault(key, []).append(
                    {"segment_id": segment_id, "positions": _delta_encode(positions)}
                )
            for key, positions in index.event_families.items():
                rollup["event_families"].setdefault(key, []).append(
                    {"segment_id": segment_id, "positions": _delta_encode(positions)}
                )

        rollup_dir = day_dir / "rollups"
        rollup_dir.mkdir(parents=True, exist_ok=True)
        rollup_path = rollup_dir / f"{date_key}.rollup.json"
        rollup_path.write_text(json.dumps(rollup, indent=2, sort_keys=True), encoding="utf-8")
        return rollup_path

    def plan_retention(
        self,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
        apply: bool = False,
    ) -> Dict[str, Any]:
        """Plan or apply hot-tier retention pruning."""
        as_of = as_of or datetime.utcnow()
        cutoff = as_of - timedelta(days=self.retention_defaults.get("hot_days", 30))
        candidates: List[Dict[str, str]] = []
        deleted: List[Dict[str, str]] = []

        for events_file in self._iter_segment_event_files(tenant_id):
            manifest_file = self._manifest_for_events(events_file)
            index_file = self._index_for_events(events_file)
            if not manifest_file.exists():
                continue
            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                end_ts = datetime.fromisoformat(manifest["end_ts"])
            except Exception:
                continue
            if end_ts >= cutoff:
                continue
            entry = {
                "events": str(events_file),
                "manifest": str(manifest_file),
                "index": str(index_file),
            }
            candidates.append(entry)
            if apply:
                for path in (events_file, manifest_file, index_file):
                    if path.exists():
                        path.unlink()
                deleted.append(entry)

        return {
            "cutoff": cutoff.isoformat(),
            "candidates": candidates,
            "deleted": deleted,
            "applied": apply,
        }

    def _collect_segments(
        self,
        start_date: datetime,
        end_date: datetime,
        tenant_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        selections: List[Dict[str, Any]] = []
        for events_file in self._iter_segment_event_files(tenant_id):
            manifest_file = self._manifest_for_events(events_file)
            index_file = self._index_for_events(events_file)
            if not manifest_file.exists() or not index_file.exists():
                continue
            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                start_ts = datetime.fromisoformat(manifest["start_ts"])
                end_ts = datetime.fromisoformat(manifest["end_ts"])
            except Exception:
                continue
            if end_ts < start_date or start_ts > end_date:
                continue
            selections.append(
                {
                    "segment_id": manifest.get("segment_id"),
                    "segment_hash": manifest.get("segment_hash"),
                    "start_ts": manifest.get("start_ts"),
                    "end_ts": manifest.get("end_ts"),
                    "events": events_file,
                    "manifest": manifest_file,
                    "index": index_file,
                }
            )
        return selections

    def _manifest_for_events(self, events_file: Path) -> Path:
        name = events_file.name.replace(".events.jsonl", ".manifest.json")
        return events_file.with_name(name)

    def _index_for_events(self, events_file: Path) -> Path:
        name = events_file.name.replace(".events.jsonl", ".index.json")
        return events_file.with_name(name)

    async def store_compliance_rule(self, rule: ComplianceRule):
        """Store compliance rule"""
        rules_file = self.storage_path / "compliance" / "rules.json"

        # Load existing rules
        rules = {}
        if rules_file.exists():
            with open(rules_file, "r") as f:
                rules = json.load(f)

        # Add/update rule
        rule_data = asdict(rule)
        rule_data["created_at"] = rule.created_at.isoformat()
        rule_data["framework"] = rule.framework.value  # Convert enum to string
        rules[rule.rule_id] = rule_data

        # Save rules
        with open(rules_file, "w") as f:
            json.dump(rules, f, indent=2)

    async def get_compliance_rules(
        self, framework: ComplianceFramework = None
    ) -> List[ComplianceRule]:
        """Get compliance rules"""
        rules_file = self.storage_path / "compliance" / "rules.json"

        if not rules_file.exists():
            return []

        with open(rules_file, "r") as f:
            rules_data = json.load(f)

        rules = []
        for rule_data in rules_data.values():
            rule = self._deserialize_compliance_rule(rule_data)
            if framework is None or rule.framework == framework:
                rules.append(rule)

        return rules

    async def store_violation(self, violation: ComplianceViolation):
        """Store compliance violation"""
        violations_file = self.storage_path / "compliance" / "violations.jsonl"

        violation_data = asdict(violation)
        violation_data["detected_at"] = violation.detected_at.isoformat()
        violation_data["severity"] = violation.severity.value  # Convert enum to string
        if violation.resolved_at:
            violation_data["resolved_at"] = violation.resolved_at.isoformat()

        with open(violations_file, "a") as f:
            f.write(json.dumps(violation_data) + "\n")

    async def store_lineage(self, lineage: DataLineage):
        """Store data lineage"""
        lineage_file = self.storage_path / "lineage" / f"{lineage.resource_id}.json"

        lineage_data = asdict(lineage)
        lineage_data["created_at"] = lineage.created_at.isoformat()
        lineage_data["updated_at"] = lineage.updated_at.isoformat()

        with open(lineage_file, "w") as f:
            json.dump(lineage_data, f, indent=2)

    def _deserialize_event(self, data: Dict[str, Any]) -> AuditEvent:
        """Deserialize audit event from JSON data"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["event_type"] = AuditEventType(data["event_type"])
        data["level"] = AuditLevel(data["level"])
        if data.get("event_family"):
            data["event_family"] = EventFamily(data["event_family"])
        return AuditEvent(**data)

    def _deserialize_compliance_rule(self, data: Dict[str, Any]) -> ComplianceRule:
        """Deserialize compliance rule from JSON data"""
        data["framework"] = ComplianceFramework(data["framework"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return ComplianceRule(**data)

    def _event_matches_filters(
        self, event: AuditEvent, filters: Dict[str, Any]
    ) -> bool:
        """Check if event matches the given filters"""
        if not filters:
            return True

        for key, value in filters.items():
            if key == "event_type":
                target = value if isinstance(value, AuditEventType) else AuditEventType(value)
                if event.event_type != target:
                    return False
            elif key == "user_id" and event.user_id != value:
                return False
            elif key == "actor_id" and event.actor_id != value:
                return False
            elif key == "subject_id" and event.subject_id != value:
                return False
            elif key == "tenant_id" and event.tenant_id != value:
                return False
            elif key == "workspace_id" and event.workspace_id != value:
                return False
            elif key == "event_family":
                target = value if isinstance(value, EventFamily) else EventFamily(value)
                if event.event_family != target:
                    return False
            elif key == "connector_name" and event.connector_name != value:
                return False
            elif key == "level":
                target = value if isinstance(value, AuditLevel) else AuditLevel(value)
                if event.level != target:
                    return False
            elif key == "success" and event.success != value:
                return False

        return True


class ComplianceEngine:
    """Compliance monitoring and enforcement engine"""

    def __init__(self, storage: AuditStorage):
        self.storage = storage
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations: List[ComplianceViolation] = []
        self.logger = setup_logger(__name__)

    async def load_rules(self):
        """Load compliance rules from storage"""
        rules = await self.storage.get_compliance_rules()
        self.rules = {rule.rule_id: rule for rule in rules}

    async def add_rule(self, rule: ComplianceRule):
        """Add new compliance rule"""
        await self.storage.store_compliance_rule(rule)
        self.rules[rule.rule_id] = rule

    async def check_compliance(self, event: AuditEvent) -> List[ComplianceViolation]:
        """Check event against compliance rules"""
        violations = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            violation = await self._check_rule(rule, event)
            if violation:
                violations.append(violation)
                await self.storage.store_violation(violation)
                self.violations.append(violation)

        return violations

    async def _check_rule(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check a specific rule against an event"""
        if rule.rule_type == "data_retention":
            return await self._check_data_retention(rule, event)
        elif rule.rule_type == "access_control":
            return await self._check_access_control(rule, event)
        elif rule.rule_type == "encryption":
            return await self._check_encryption(rule, event)
        elif rule.rule_type == "data_export":
            return await self._check_data_export(rule, event)
        elif rule.rule_type == "sensitive_data":
            return await self._check_sensitive_data(rule, event)

        return None

    async def _check_data_retention(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check data retention compliance"""
        if event.event_type not in [
            AuditEventType.RESOURCE_CREATE,
            AuditEventType.RESOURCE_WRITE,
        ]:
            return None

        max_retention_days = rule.config.get("max_retention_days")
        if not max_retention_days:
            return None

        # Check if data is older than retention period
        retention_cutoff = datetime.utcnow() - timedelta(days=max_retention_days)

        if event.timestamp < retention_cutoff:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                event_id=event.event_id,
                severity=AuditLevel.WARNING,
                description=f"Data retention violation: Resource {event.resource_id} exceeds {max_retention_days} day retention policy",
            )

        return None

    async def _check_access_control(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check access control compliance"""
        if event.event_type not in [
            AuditEventType.RESOURCE_READ,
            AuditEventType.RESOURCE_WRITE,
        ]:
            return None

        # Check for unauthorized access patterns
        allowed_users = rule.config.get("allowed_users", [])
        restricted_resources = rule.config.get("restricted_resources", [])

        if allowed_users and event.user_id not in allowed_users:
            if any(
                pattern in (event.resource_id or "") for pattern in restricted_resources
            ):
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    event_id=event.event_id,
                    severity=AuditLevel.ERROR,
                    description=f"Access control violation: User {event.user_id} accessed restricted resource {event.resource_id}",
                )

        return None

    async def _check_encryption(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check encryption compliance"""
        if event.event_type != AuditEventType.DATA_EXPORT:
            return None

        require_encryption = rule.config.get("require_encryption", True)
        if require_encryption and not event.details.get("encrypted", False):
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                event_id=event.event_id,
                severity=AuditLevel.CRITICAL,
                description="Encryption violation: Unencrypted data export detected",
            )

        return None

    async def _check_data_export(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check data export compliance"""
        if event.event_type != AuditEventType.DATA_EXPORT:
            return None

        max_export_size = rule.config.get("max_export_size_mb")
        if max_export_size:
            export_size_mb = event.details.get("size_mb", 0)
            if export_size_mb > max_export_size:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    event_id=event.event_id,
                    severity=AuditLevel.WARNING,
                    description=f"Data export size violation: {export_size_mb}MB exceeds limit of {max_export_size}MB",
                )

        return None

    async def _check_sensitive_data(
        self, rule: ComplianceRule, event: AuditEvent
    ) -> Optional[ComplianceViolation]:
        """Check sensitive data handling compliance"""
        sensitive_patterns = rule.config.get("sensitive_patterns", [])
        if not sensitive_patterns:
            return None

        # Check event details for sensitive data patterns
        event_text = json.dumps(event.details).lower()

        for pattern in sensitive_patterns:
            if pattern.lower() in event_text:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    event_id=event.event_id,
                    severity=AuditLevel.ERROR,
                    description=f"Sensitive data violation: Pattern '{pattern}' detected in event",
                )

        return None


class GitIntegration:
    """Git integration for audit trail versioning"""

    def __init__(
        self, git_connector: GitConnector, audit_repo_path: str = "audit_repository"
    ):
        self.git_connector = git_connector
        self.audit_repo_path = Path(audit_repo_path)
        self.logger = setup_logger(__name__)

    async def initialize_repository(self):
        """Initialize audit repository"""
        if not self.audit_repo_path.exists():
            self.audit_repo_path.mkdir(parents=True)

            # Initialize git repository
            import subprocess

            subprocess.run(["git", "init"], cwd=self.audit_repo_path)
            subprocess.run(
                ["git", "config", "user.name", "AI OS Audit System"],
                cwd=self.audit_repo_path,
            )
            subprocess.run(
                ["git", "config", "user.email", "audit@osdashboard.local"],
                cwd=self.audit_repo_path,
            )

    async def commit_audit_data(self, date: datetime, description: str = None):
        """Commit audit data for a specific date"""
        try:
            date_str = date.strftime("%Y-%m-%d")
            commit_message = description or f"Audit data for {date_str}"

            # Stage all changes
            import subprocess

            subprocess.run(["git", "add", "."], cwd=self.audit_repo_path)

            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.audit_repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.logger.info(f"Committed audit data: {commit_message}")
                return True
            else:
                self.logger.warning(f"No changes to commit for {date_str}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to commit audit data: {e}")
            return False

    async def create_audit_branch(self, branch_name: str, base_date: datetime):
        """Create audit branch for specific investigation"""
        try:
            import subprocess

            # Create and checkout new branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name], cwd=self.audit_repo_path
            )

            # Add investigation metadata
            metadata = {
                "branch_name": branch_name,
                "created_at": datetime.utcnow().isoformat(),
                "base_date": base_date.isoformat(),
                "purpose": "audit_investigation",
            }

            metadata_file = self.audit_repo_path / f"investigation_{branch_name}.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            # Commit metadata
            subprocess.run(["git", "add", str(metadata_file)], cwd=self.audit_repo_path)
            subprocess.run(
                ["git", "commit", "-m", f"Start audit investigation: {branch_name}"],
                cwd=self.audit_repo_path,
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to create audit branch: {e}")
            return False

    async def get_audit_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get git history for audit file"""
        try:
            import subprocess

            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--pretty=format:%H|%an|%ad|%s",
                    "--date=iso",
                    "--",
                    file_path,
                ],
                cwd=self.audit_repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return []

            history = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        history.append(
                            {
                                "commit_hash": parts[0],
                                "author": parts[1],
                                "date": parts[2],
                                "message": parts[3],
                            }
                        )

            return history

        except Exception as e:
            self.logger.error(f"Failed to get audit history: {e}")
            return []


class AuditSystem:
    """Main audit and governance system"""

    def __init__(
        self,
        storage_path: str = "audit_data",
        git_repo_path: str = "audit_repository",
        audit_settings: Optional["AuditSettings"] = None,
    ):
        if audit_settings is None:
            try:
                from config.config import get_audit_config

                audit_settings = get_audit_config()
            except Exception:
                audit_settings = None

        effective_storage_path = storage_path
        storage_kwargs: Dict[str, Any] = {}
        if audit_settings:
            if storage_path == "audit_data":
                effective_storage_path = audit_settings.storage_path or storage_path
            tier_paths = [
                audit_settings.remote_archive_path,
                audit_settings.hardware_backup_path,
                audit_settings.cloud_backup_path,
            ]
            if any(tier_paths):
                storage_kwargs["storage_tiers"] = {
                    "remote_archive": Path(audit_settings.remote_archive_path)
                    if audit_settings.remote_archive_path
                    else None,
                    "hardware_backup": Path(audit_settings.hardware_backup_path)
                    if audit_settings.hardware_backup_path
                    else None,
                    "cloud_backup": Path(audit_settings.cloud_backup_path)
                    if audit_settings.cloud_backup_path
                    else None,
                }
            storage_kwargs.update(
                {
                    "segment_time_format": audit_settings.segment_time_format,
                    "segment_time_window_minutes": audit_settings.segment_time_window_minutes,
                    "segment_max_events": audit_settings.segment_max_events,
                    "signing_key": audit_settings.signing_key,
                    "retention_defaults": {
                        "hot_days": audit_settings.retention_hot_days,
                        "archive_days": audit_settings.retention_archive_days,
                        "backup_years": audit_settings.retention_backup_years,
                        "cloud_years": audit_settings.retention_cloud_years,
                    },
                }
            )

        self.storage = AuditStorage(effective_storage_path, **storage_kwargs)
        self.compliance_engine = ComplianceEngine(self.storage)
        self.git_integration = None
        self.connectors: Dict[str, BaseConnector] = {}
        self.lineage_tracker = {}
        self.logger = setup_logger(__name__)

        # Event hooks
        self.event_hooks: List[Callable] = []

    async def initialize(
        self, enable_git: bool = True, git_connector: GitConnector = None
    ):
        """Initialize audit system"""
        await self.compliance_engine.load_rules()

        if enable_git and git_connector:
            self.git_integration = GitIntegration(git_connector)
            await self.git_integration.initialize_repository()

        self.logger.info("Audit system initialized")

    def register_connector(self, name: str, connector: BaseConnector):
        """Register connector for audit tracking"""
        self.connectors[name] = connector

    def add_event_hook(self, hook: Callable[[AuditEvent], None]):
        """Add event hook for custom processing"""
        self.event_hooks.append(hook)

    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: str = None,
        connector_name: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        level: AuditLevel = AuditLevel.INFO,
        event_family: EventFamily = EventFamily.ACTION_STEP,
        actor_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        rule_id: Optional[str] = None,
        evidence_refs: Optional[List[str]] = None,
        payload_ref: Optional[str] = None,
        payload_hash: Optional[str] = None,
        retention_policy_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Log audit event"""
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            connector_name=connector_name,
            resource_id=resource_id,
            action=action,
            details=details or {},
            level=level,
            event_family=event_family,
            actor_id=actor_id,
            subject_id=subject_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            rule_id=rule_id,
            evidence_refs=evidence_refs or [],
            payload_ref=payload_ref,
            payload_hash=payload_hash,
            retention_policy_id=retention_policy_id,
            **kwargs,
        )

        # Store event
        await self.storage.store_event(event)

        # Check compliance
        violations = await self.compliance_engine.check_compliance(event)
        if violations:
            self.logger.warning(
                f"Compliance violations detected for event {event.event_id}: {len(violations)}"
            )

        # Call event hooks
        for hook in self.event_hooks:
            try:
                await hook(event) if asyncio.iscoroutinefunction(hook) else hook(event)
            except Exception as e:
                self.logger.error(f"Event hook failed: {e}")

        return event.event_id

    async def log_data_change(
        self,
        action: str,
        user_id: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        **kwargs,
    ) -> str:
        return await self.log_event(
            event_type=AuditEventType.RESOURCE_WRITE,
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            event_family=EventFamily.DATA_CHANGE,
            **kwargs,
        )

    async def log_action_step(
        self,
        action: str,
        user_id: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        **kwargs,
    ) -> str:
        return await self.log_event(
            event_type=AuditEventType.WORKFLOW_EXECUTE,
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            event_family=EventFamily.ACTION_STEP,
            **kwargs,
        )

    async def log_critical_event(
        self,
        action: str,
        rule_id: str,
        evidence_refs: List[str],
        user_id: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        **kwargs,
    ) -> str:
        return await self.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            level=AuditLevel.CRITICAL,
            event_family=EventFamily.CRITICAL_EVENT,
            rule_id=rule_id,
            evidence_refs=evidence_refs,
            **kwargs,
        )

    async def track_data_lineage(
        self,
        resource_id: str,
        connector_name: str,
        source_resources: List[str] = None,
        transformations: List[Dict[str, Any]] = None,
    ):
        """Track data lineage"""
        lineage = DataLineage(
            lineage_id=str(uuid.uuid4()),
            resource_id=resource_id,
            connector_name=connector_name,
            source_resources=source_resources or [],
            transformations=transformations or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        await self.storage.store_lineage(lineage)
        self.lineage_tracker[resource_id] = lineage

    async def get_audit_trail(
        self, start_date: datetime, end_date: datetime, filters: Dict[str, Any] = None
    ) -> List[AuditEvent]:
        """Get audit trail for date range"""
        return await self.storage.get_events(start_date, end_date, filters)

    async def generate_compliance_report(
        self, framework: ComplianceFramework, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        # Get relevant events
        events = await self.get_audit_trail(start_date, end_date)

        # Get compliance rules for framework
        rules = await self.storage.get_compliance_rules(framework)

        # Analyze compliance
        total_events = len(events)
        violation_count = 0
        rule_violations = {}

        for event in events:
            violations = await self.compliance_engine.check_compliance(event)
            violation_count += len(violations)

            for violation in violations:
                if violation.rule_id not in rule_violations:
                    rule_violations[violation.rule_id] = 0
                rule_violations[violation.rule_id] += 1

        # Calculate compliance score
        compliance_score = (
            ((total_events - violation_count) / total_events * 100)
            if total_events > 0
            else 100
        )

        report = {
            "framework": framework.value,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": {
                "total_events": total_events,
                "total_violations": violation_count,
                "compliance_score": round(compliance_score, 2),
                "rules_evaluated": len(rules),
            },
            "rule_violations": rule_violations,
            "recommendations": self._generate_compliance_recommendations(
                rule_violations, rules
            ),
        }

        return report

    async def export_audit_data(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = "json",
        encrypt: bool = True,
    ) -> str:
        """Export audit data"""
        events = await self.get_audit_trail(start_date, end_date)

        # Log export event
        await self.log_event(
            AuditEventType.DATA_EXPORT,
            "export_audit_data",
            details={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "format": format,
                "encrypted": encrypt,
                "event_count": len(events),
                "size_mb": len(json.dumps([asdict(e) for e in events])) / (1024 * 1024),
            },
        )

        # Export data
        if format == "json":
            export_data = [asdict(event) for event in events]
            # Convert datetime objects to ISO strings
            for event_data in export_data:
                event_data["timestamp"] = event_data["timestamp"].isoformat()
                event_data["event_type"] = event_data["event_type"].value
                event_data["level"] = event_data["level"].value
                if event_data.get("event_family"):
                    event_data["event_family"] = event_data["event_family"].value

            export_content = json.dumps(export_data, indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            if events:
                fieldnames = asdict(events[0]).keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()

                for event in events:
                    event_dict = asdict(event)
                    event_dict["timestamp"] = event.timestamp.isoformat()
                    event_dict["event_type"] = event.event_type.value
                    event_dict["level"] = event.level.value
                    if event.event_family:
                        event_dict["event_family"] = event.event_family.value
                    writer.writerow(event_dict)

            export_content = output.getvalue()

        else:
            raise ValueError(f"Unsupported export format: {format}")

        # Save export file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_export_{timestamp}.{format}"
        export_path = self.storage.storage_path / filename

        if encrypt:
            # Simple encryption (in production, use proper encryption)
            export_content = self._encrypt_content(export_content)
            filename += ".encrypted"
            export_path = self.storage.storage_path / filename

        with open(export_path, "w") as f:
            f.write(export_content)

        return str(export_path)

    async def export_audit_pack(
        self, start_date: datetime, end_date: datetime, tenant_id: Optional[str] = None
    ) -> str:
        """Export a verifier-friendly audit pack."""
        pack_path = await self.storage.export_pack(start_date, end_date, tenant_id)
        await self.log_event(
            AuditEventType.DATA_EXPORT,
            "export_audit_pack",
            details={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "tenant_id": tenant_id,
                "format": "audit_pack",
            },
        )
        return str(pack_path)

    async def export_audit_parquet(
        self, start_date: datetime, end_date: datetime, tenant_id: Optional[str] = None
    ) -> str:
        """Export audit events as a parquet archive."""
        parquet_path = await self.storage.export_parquet(start_date, end_date, tenant_id)
        await self.log_event(
            AuditEventType.DATA_EXPORT,
            "export_audit_parquet",
            details={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "tenant_id": tenant_id,
                "format": "parquet",
            },
        )
        return str(parquet_path)

    async def get_critical_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return critical events for fast singularity lookups."""
        return self.storage.get_critical_events(start_date, end_date, tenant_id)

    def compact_daily_indexes(
        self, date: datetime, tenant_id: Optional[str] = None
    ) -> Optional[str]:
        path = self.storage.compact_daily_indexes(date, tenant_id)
        return str(path) if path else None

    def plan_retention(
        self,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
        apply: bool = False,
    ) -> Dict[str, Any]:
        return self.storage.plan_retention(as_of=as_of, tenant_id=tenant_id, apply=apply)

    async def daily_audit_commit(self, date: datetime = None):
        """Commit daily audit data to git"""
        if not self.git_integration:
            return False

        if date is None:
            date = datetime.utcnow() - timedelta(days=1)  # Previous day

        return await self.git_integration.commit_audit_data(date)

    def _generate_compliance_recommendations(
        self, violations: Dict[str, int], rules: List[ComplianceRule]
    ) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []

        # Find most violated rules
        if violations:
            most_violated = max(violations.items(), key=lambda x: x[1])
            rule_id, count = most_violated

            # Find the rule
            rule = next((r for r in rules if r.rule_id == rule_id), None)
            if rule:
                recommendations.append(
                    f"Address frequent violations of rule '{rule.name}' ({count} violations)"
                )

        # General recommendations
        if len(violations) > 0:
            recommendations.append("Review and update access control policies")
            recommendations.append(
                "Implement additional monitoring for sensitive operations"
            )
            recommendations.append("Provide compliance training to users")

        return recommendations

    def _encrypt_content(self, content: str) -> str:
        """Simple content encryption (placeholder)"""
        # In production, use proper encryption like Fernet
        return base64.b64encode(content.encode()).decode()

    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get audit system statistics"""
        # Get recent events (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        recent_events = await self.get_audit_trail(start_date, end_date)

        # Event type distribution
        event_type_counts = {}
        for event in recent_events:
            event_type = event.event_type.value
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        # Compliance statistics
        total_rules = len(self.compliance_engine.rules)
        active_rules = sum(
            1 for rule in self.compliance_engine.rules.values() if rule.enabled
        )

        return {
            "total_events_30_days": len(recent_events),
            "event_type_distribution": event_type_counts,
            "compliance_rules": {"total": total_rules, "active": active_rules},
            "registered_connectors": len(self.connectors),
            "data_lineage_tracked": len(self.lineage_tracker),
            "git_integration_enabled": self.git_integration is not None,
        }
