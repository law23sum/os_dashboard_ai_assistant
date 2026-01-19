"""Audit event schema and controlled vocabularies."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

try:  # Pydantic v2
    from pydantic import ConfigDict
    _HAS_CONFIG = True
except Exception:  # pragma: no cover - pydantic v1 fallback
    ConfigDict = None
    _HAS_CONFIG = False


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


EVENT_TYPES = {
    "SESSION_START",
    "SESSION_END",
    "CAPABILITY_REQUEST",
    "CAPABILITY_GRANTED",
    "CAPABILITY_DENIED",
    "POLICY_LOAD",
    "POLICY_DECISION",
    "POLICY_DENY_ACTION",
    "THOUGHT",
    "PLAN",
    "QUESTION",
    "DECISION",
    "RATIONALE",
    "RISK_NOTE",
    "SAFETY_NOTE",
    "TASK_CLAIM",
    "TASK_HANDOFF",
    "TASK_COMPLETE",
    "TASK_BLOCKED",
    "MESSAGE_SENT",
    "MESSAGE_RECEIVED",
    "HELP_REQUESTED",
    "HELP_PROVIDED",
    "READ_OPERATION",
    "WRITE_OPERATION",
    "COMMAND_INTENT",
    "COMMAND_OUTCOME",
    "RESOURCE_POLICY_APPLIED",
    "THROTTLE_APPLIED",
    "THROTTLE_RELEASED",
    "FREEZE_DETECTED",
    "WATCHDOG_TRIGGERED",
    "ERROR",
    "RECOVERY_ATTEMPT",
    "RECOVERY_SUCCESS",
    "RECOVERY_FAIL",
    "ARCHIVE_ROTATION",
    "ARCHIVE_SEALED",
    "ARCHIVE_VERIFY_OK",
    "ARCHIVE_VERIFY_FAIL",
    # Extra operational events already referenced in docs.
    "OPERATION_START",
    "OPERATION_END",
    "ARCHIVE_RETENTION_APPLIED",
    "DEBATE_OPEN",
    "DEBATE_TURN",
    "SUPPORT",
    "REBUTTAL",
    "DISPUTE",
    "RESOLUTION",
    "CONSENSUS_REACHED",
    "ESCALATION_TO_MASTER_CHRIS",
    "FILE_DIFF_CREATED",
    "ARTIFACT_CREATED",
    "ARTIFACT_UPDATED",
    "ARTIFACT_DELETED",
    "BUG_DETECTED",
    "CRASH_DETECTED",
    "IO_PRESSURE",
    "MEMORY_PRESSURE",
    "CPU_PRESSURE",
}

SEVERITY_LEVELS = {"debug", "info", "notice", "warning", "error", "critical"}
VISIBILITY_LEVELS = {"private", "team", "admin"}


class AuditProjectRef(BaseModel):
    project_id: Optional[str] = None
    epic_id: Optional[str] = None
    task_id: Optional[str] = None


class AuditResourceSnapshot(BaseModel):
    cpu_pct: Optional[float] = None
    ram_mb: Optional[float] = None
    io_read_mb: Optional[float] = None
    io_write_mb: Optional[float] = None
    net_in_kb: Optional[float] = None
    net_out_kb: Optional[float] = None


class AuditArtifactRef(BaseModel):
    kind: Optional[str] = None
    path_or_uri: Optional[str] = None
    hash: Optional[str] = None
    size_bytes: Optional[int] = None


class AuditEvent(BaseModel):
    schema_version: int = Field(default=1)
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts_utc: str = Field(default_factory=utc_now_iso)
    host_id: Optional[str] = None
    os_family: Optional[str] = None
    runtime_scope: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    operation_id: Optional[str] = None
    event_type: str
    severity: str = "info"
    visibility: str = "team"
    message: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)
    artifact_refs: Optional[List[AuditArtifactRef]] = None
    resource_snapshot: Optional[AuditResourceSnapshot] = None
    project_ref: Optional[AuditProjectRef] = None
    prev_hash: Optional[str] = Field(default=None, alias="prev_event_hash")
    event_hash: Optional[str] = None

    if _HAS_CONFIG:
        model_config = ConfigDict(extra="allow", populate_by_name=True)
    else:  # pragma: no cover - pydantic v1 fallback
        class Config:
            extra = "allow"
            allow_population_by_field_name = True

    def to_dict(self) -> Dict[str, Any]:
        if hasattr(self, "model_dump"):
            return self.model_dump(by_alias=False)
        return self.dict(by_alias=False)


def normalize_event_type(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value.strip().upper()
