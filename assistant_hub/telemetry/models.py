"""Shared event models for the unified event journal."""

from __future__ import annotations

from assistant_hub.audit.schema import (
    AuditArtifactRef as EventArtifactRef,
    AuditEvent as Event,
    AuditProjectRef as EventProjectRef,
    AuditResourceSnapshot as EventResourceSnapshot,
    normalize_event_type,
    utc_now_iso,
)

__all__ = [
    "Event",
    "EventArtifactRef",
    "EventProjectRef",
    "EventResourceSnapshot",
    "normalize_event_type",
    "utc_now_iso",
]
