"""Audit log primitives for tracking AI operations."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class OperationRecord:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor: str = "unknown"
    intent: str = "unspecified"
    triggered_by: str = "manual"
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None

    touched: List[Dict[str, Any]] = field(default_factory=list)
    diffs: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def close(self):
        self.finished_at = datetime.utcnow()


class AuditLog:
    def __init__(self):
        self.records: Dict[str, OperationRecord] = {}

    def start(
        self,
        actor: str,
        intent: str,
        triggered_by: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OperationRecord:
        record = OperationRecord(actor=actor, intent=intent, triggered_by=triggered_by, metadata=metadata or {})
        self.records[record.id] = record
        return record

    def add_touch(self, op_id: str, system: str, resource_id: str, action: str):
        self.records[op_id].touched.append({"system": system, "resource_id": resource_id, "action": action})

    def add_diff(self, op_id: str, diff: Dict[str, Any]):
        self.records[op_id].diffs.append(diff)

    def finish(self, op_id: str):
        self.records[op_id].close()

    def get(self, op_id: str) -> OperationRecord:
        return self.records[op_id]
