from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from assistant_core.audit_system import AuditEventType, AuditSystem
from assistant_hub.audit.sdk import get_default_emitter, new_correlation_id
from assistant_hub.audit.schema import EVENT_TYPES, SEVERITY_LEVELS, normalize_event_type

logger = logging.getLogger(__name__)
_immutable_audit_ledger_module: Optional["ImmutableAuditLedgerModule"] = None


def get_immutable_audit_ledger_module() -> "ImmutableAuditLedgerModule":
    global _immutable_audit_ledger_module
    if _immutable_audit_ledger_module is None:
        _immutable_audit_ledger_module = ImmutableAuditLedgerModule()
    return _immutable_audit_ledger_module


async def _run_with_guard(coro):
    try:
        return await coro
    except Exception:
        logger.exception("Immutable audit ledger logging failed")
        return None


def _schedule(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_run_with_guard(coro))
    else:
        loop.create_task(_run_with_guard(coro))
        return None


def _parse_level(level: Optional[str]) -> str:
    if not level:
        return "info"
    lowered = level.lower()
    if lowered in ("critical", "fatal"):
        return "critical"
    if lowered in ("error", "err"):
        return "error"
    if lowered in ("warn", "warning"):
        return "warning"
    return lowered if lowered in SEVERITY_LEVELS else "info"


class ImmutableAuditLedgerSystem(AuditSystem):
    """Canonical immutable audit ledger system (alias for AuditSystem)."""


class ImmutableAuditLedgerModule:
    """Module bridge between app events and the immutable audit ledger."""

    def __init__(self) -> None:
        self.emitter = get_default_emitter(agent_id="os_dashboard")

    async def ensure_initialized(self) -> None:
        return

    @staticmethod
    def infer_event_type(action: Optional[str]) -> str:
        lowered = (action or "").lower()
        if not lowered:
            return "WRITE_OPERATION"
        keyword_map = [
            ("SESSION_START", ("login", "sign-in", "signin", "auth")),
            ("SESSION_END", ("logout", "sign-out", "signout")),
            ("POLICY_DECISION", ("permission", "role", "grant", "revoke", "access", "policy")),
            ("POLICY_DECISION", ("config", "setting", "preference", "toggle")),
            ("QUESTION", ("search", "query", "lookup")),
            ("POLICY_DECISION", ("compliance", "audit", "governance")),
            ("ERROR", ("security", "breach", "incident", "threat")),
            ("WRITE_OPERATION", ("export", "download", "backup")),
            ("WRITE_OPERATION", ("import", "upload", "ingest", "restore")),
            ("WRITE_OPERATION", ("delete", "remove", "archive", "purge")),
            ("WRITE_OPERATION", ("create", "add", "new", "provision")),
            ("READ_OPERATION", ("read", "view", "get", "list", "fetch")),
            ("DECISION", ("run", "execute", "trigger", "dispatch", "schedule")),
            ("WRITE_OPERATION", ("update", "modify", "edit", "patch", "write")),
        ]
        for event_type, keywords in keyword_map:
            if any(keyword in lowered for keyword in keywords):
                return event_type
        return "WRITE_OPERATION"

    async def record_project_event(
        self,
        *,
        project_id: str,
        event_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Optional[str]:
        await self.ensure_initialized()
        resolved_type = normalize_event_type(event_type) or self.infer_event_type(event_type)
        if resolved_type not in EVENT_TYPES:
            resolved_type = self.infer_event_type(event_type)
        details = {
            "project_id": project_id,
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload": payload or {},
        }
        correlation_id = new_correlation_id()
        event = self.emitter.emit(
            event_type=resolved_type,
            message=event_type,
            payload=details,
            correlation_id=correlation_id,
            project_ref={"project_id": project_id},
        )
        return event.event_id

    def record_project_event_sync(self, **kwargs) -> Optional[str]:
        return _schedule(self.record_project_event(**kwargs))

    async def record_action_step(
        self,
        *,
        action: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        level: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        subject_id: Optional[str] = None,
        subject_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Optional[str]:
        await self.ensure_initialized()
        resolved_type = None
        if event_type is not None:
            resolved_type = getattr(event_type, "value", str(event_type)).upper()
        if resolved_type not in EVENT_TYPES:
            resolved_type = self.infer_event_type(action)
        correlation_id = new_correlation_id()
        event = self.emitter.emit(
            event_type=resolved_type,
            message=action,
            payload={
                "action": action,
                "details": details or {},
                "user_id": user_id,
                "resource_id": resource_id,
                "subject_id": subject_id,
                "subject_type": subject_type,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "level": _parse_level(level),
            },
            correlation_id=correlation_id,
        )
        return event.event_id

    def record_action_step_sync(self, **kwargs) -> Optional[str]:
        return _schedule(self.record_action_step(**kwargs))


InvariantTrailLogger = ImmutableAuditLedgerModule
get_invariant_trail_logger = get_immutable_audit_ledger_module

__all__ = [
    "ImmutableAuditLedgerSystem",
    "ImmutableAuditLedgerModule",
    "get_immutable_audit_ledger_module",
    "InvariantTrailLogger",
    "get_invariant_trail_logger",
]
