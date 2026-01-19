"""Backwards-compatible imports for the immutable audit ledger module."""

from assistant_core.immutable_audit_ledger import (
    ImmutableAuditLedgerModule,
    ImmutableAuditLedgerSystem,
    get_immutable_audit_ledger_module,
)

InvariantTrailLogger = ImmutableAuditLedgerModule
get_invariant_trail_logger = get_immutable_audit_ledger_module

__all__ = [
    "ImmutableAuditLedgerSystem",
    "ImmutableAuditLedgerModule",
    "get_immutable_audit_ledger_module",
    "InvariantTrailLogger",
    "get_invariant_trail_logger",
]
