"""Dynamic Cybersecurity Engine for breach-aware governance logging."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from assistant_core.audit_system import (
    AuditSystem,
    AuditEventType,
    AuditLevel,
    EventFamily,
)


class BreachState(Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    LIKELY_COMPROMISE = "likely_compromise"
    CONFIRMED_COMPROMISE = "confirmed_compromise"
    RECOVERY = "recovery"
    POST_INCIDENT = "post_incident"


@dataclass
class BreachTransition:
    transition_id: str
    from_state: BreachState
    to_state: BreachState
    trigger: str
    timestamp: str
    notes: str = ""
    evidence_refs: List[str] = field(default_factory=list)


class DynamicCybersecurityEngine:
    """Breach-aware security engine that writes to the canonical audit log."""

    def __init__(self, audit_system: Optional[AuditSystem] = None):
        self.name = "Dynamic Cybersecurity Engine"
        self.audit_system = audit_system or AuditSystem()
        self.state = BreachState.NORMAL
        self.transitions: List[BreachTransition] = []

    async def initialize(self) -> None:
        await self.audit_system.initialize(enable_git=False)

    async def record_data_change(
        self,
        action: str,
        user_id: Optional[str],
        resource_id: Optional[str],
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        return await self.audit_system.log_event(
            event_type=AuditEventType.RESOURCE_WRITE,
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details or {},
            event_family=EventFamily.DATA_CHANGE,
            **kwargs,
        )

    async def record_action_step(
        self,
        action: str,
        user_id: Optional[str],
        resource_id: Optional[str],
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        return await self.audit_system.log_event(
            event_type=AuditEventType.WORKFLOW_EXECUTE,
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details or {},
            event_family=EventFamily.ACTION_STEP,
            **kwargs,
        )

    async def record_critical_event(
        self,
        action: str,
        rule_id: str,
        evidence_refs: List[str],
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        return await self.audit_system.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details or {},
            level=AuditLevel.CRITICAL,
            event_family=EventFamily.CRITICAL_EVENT,
            rule_id=rule_id,
            evidence_refs=evidence_refs,
            **kwargs,
        )

    async def transition_state(
        self,
        to_state: BreachState,
        trigger: str,
        evidence_refs: Optional[List[str]] = None,
        notes: str = "",
    ) -> Optional[Dict[str, str]]:
        if to_state == self.state:
            return None

        transition = BreachTransition(
            transition_id=str(uuid.uuid4()),
            from_state=self.state,
            to_state=to_state,
            trigger=trigger,
            timestamp=datetime.utcnow().isoformat(),
            notes=notes,
            evidence_refs=evidence_refs or [],
        )
        self.transitions.append(transition)
        self.state = to_state

        event_id = await self.record_critical_event(
            action="breach_mode_transition",
            rule_id=trigger,
            evidence_refs=transition.evidence_refs,
            details={
                "from_state": transition.from_state.value,
                "to_state": transition.to_state.value,
                "notes": transition.notes,
            },
        )
        return {
            "transition_id": transition.transition_id,
            "event_id": event_id,
            "from_state": transition.from_state.value,
            "to_state": transition.to_state.value,
            "timestamp": transition.timestamp,
        }

    async def record_snapshot(
        self,
        snapshot_id: str,
        payload: Dict[str, Any],
        source: str,
        segment_id: Optional[str] = None,
        event_hash: Optional[str] = None,
    ) -> None:
        state_hash = hashlib.sha256(
            json.dumps(payload or {}, sort_keys=True).encode("utf-8")
        ).hexdigest()
        await self.audit_system.storage.record_snapshot(
            snapshot_id=snapshot_id,
            state_hash=state_hash,
            segment_id=segment_id,
            event_hash=event_hash,
            source=source,
            metadata={"engine": self.name},
        )
