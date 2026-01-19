"""Immutable Audit Ledger Module/System and Secure Archive Engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from .archive import AuditArchiveEngine
from .config import AuditConfig, get_audit_config
from .ledger import AuditLedgerStore, get_ledger_store, reset_ledger_store
from .schema import (
    AuditArtifactRef,
    AuditEvent,
    AuditProjectRef,
    AuditResourceSnapshot,
    EVENT_TYPES,
    SEVERITY_LEVELS,
    VISIBILITY_LEVELS,
    normalize_event_type,
)

_SDK_EXPORTS = (
    "EventEmitter",
    "EventEmitterConfig",
    "OperationContext",
    "get_default_emitter",
    "new_correlation_id",
)

if TYPE_CHECKING:
    from .sdk import EventEmitter, EventEmitterConfig, OperationContext, get_default_emitter, new_correlation_id


def __getattr__(name: str):
    if name in _SDK_EXPORTS:
        from . import sdk

        return getattr(sdk, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> Iterable[str]:
    return sorted(tuple(globals().keys()) + _SDK_EXPORTS)


__all__ = [
    "AuditArchiveEngine",
    "AuditConfig",
    "AuditLedgerStore",
    "AuditArtifactRef",
    "AuditEvent",
    "AuditProjectRef",
    "AuditResourceSnapshot",
    "EVENT_TYPES",
    "SEVERITY_LEVELS",
    "VISIBILITY_LEVELS",
    "EventEmitter",
    "EventEmitterConfig",
    "OperationContext",
    "get_audit_config",
    "get_default_emitter",
    "get_ledger_store",
    "reset_ledger_store",
    "new_correlation_id",
    "normalize_event_type",
]
