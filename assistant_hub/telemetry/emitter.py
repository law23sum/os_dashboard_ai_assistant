"""Event emitter for the unified event journal."""

from __future__ import annotations

import os
import socket
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional

from .models import Event, normalize_event_type
from .sinks import EventSink, HubSink, LocalAppendOnlySink, default_journal_dir


def _detect_os_family() -> str:
    platform = sys.platform.lower()
    if platform.startswith("darwin"):
        return "macos"
    if platform.startswith("win"):
        return "windows"
    return "linux"


def _default_runtime_scope() -> str:
    return os.getenv("OSDASH_RUNTIME_SCOPE", "host")


def _default_host_id() -> str:
    return os.getenv("OSDASH_HOST_ID", socket.gethostname())


@dataclass
class EventEmitterConfig:
    agent_id: str = "os_dashboard"
    session_id: Optional[str] = None
    host_id: Optional[str] = None
    os_family: Optional[str] = None
    runtime_scope: Optional[str] = None
    default_visibility: str = "team"
    default_severity: str = "info"


@dataclass
class OperationContext:
    intent_event_id: str
    correlation_id: Optional[str]
    outcome_payload: Dict[str, Any] = field(default_factory=dict)

    def add_outcome(self, **kwargs: Any) -> None:
        self.outcome_payload.update(kwargs)


class EventEmitter:
    def __init__(self, config: EventEmitterConfig, sinks: Iterable[EventSink]) -> None:
        self.config = config
        self.sinks = list(sinks)
        if not self.config.session_id:
            self.config.session_id = str(uuid.uuid4())
        if not self.config.host_id:
            self.config.host_id = _default_host_id()
        if not self.config.os_family:
            self.config.os_family = _detect_os_family()
        if not self.config.runtime_scope:
            self.config.runtime_scope = _default_runtime_scope()

    def emit(
        self,
        *,
        event_type: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        severity: Optional[str] = None,
        visibility: Optional[str] = None,
        project_ref: Optional[Dict[str, Any]] = None,
        resource_snapshot: Optional[Dict[str, Any]] = None,
        artifact_refs: Optional[list[Dict[str, Any]]] = None,
        correlation_id: Optional[str] = None,
        operation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> Event:
        event = Event(
            event_type=normalize_event_type(event_type) or "UNKNOWN",
            message=message,
            payload=payload or {},
            severity=severity or self.config.default_severity,
            visibility=visibility or self.config.default_visibility,
            agent_id=self.config.agent_id,
            session_id=self.config.session_id,
            host_id=self.config.host_id,
            os_family=self.config.os_family,
            runtime_scope=self.config.runtime_scope,
            project_ref=project_ref,
            resource_snapshot=resource_snapshot,
            artifact_refs=artifact_refs,
            correlation_id=correlation_id,
            operation_id=operation_id,
            causation_id=causation_id,
        )

        for sink in self.sinks:
            sink.write(event)
        return event

    def emit_intent(self, *, event_type: str, message: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> Event:
        enriched = dict(payload or {})
        enriched.setdefault("phase", "intent")
        return self.emit(event_type=event_type, message=message, payload=enriched, **kwargs)

    def emit_outcome(self, *, event_type: str, message: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> Event:
        enriched = dict(payload or {})
        enriched.setdefault("phase", "outcome")
        return self.emit(event_type=event_type, message=message, payload=enriched, **kwargs)

    def emit_error(self, *, message: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> Event:
        return self.emit(event_type="ERROR", message=message, payload=payload, severity="error", **kwargs)

    def emit_question(self, *, message: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> Event:
        return self.emit(event_type="QUESTION", message=message, payload=payload, **kwargs)

    def emit_debate_turn(self, *, message: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> Event:
        return self.emit(event_type="DEBATE_TURN", message=message, payload=payload, **kwargs)

    @contextmanager
    def operation(
        self,
        name: str,
        *,
        intent_type: str = "COMMAND_INTENT",
        outcome_type: str = "COMMAND_OUTCOME",
        message: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        **kwargs: Any,
    ):
        start = time.time()
        corr_id = correlation_id or new_correlation_id()
        intent_payload = dict(payload or {})
        intent_payload.setdefault("operation", name)
        intent = self.emit_intent(
            event_type=intent_type,
            message=message or name,
            payload=intent_payload,
            correlation_id=corr_id,
            **kwargs,
        )
        ctx = OperationContext(intent_event_id=intent.event_id, correlation_id=corr_id)
        success = True
        error = None
        try:
            yield ctx
        except Exception as exc:
            success = False
            error = str(exc)
            raise
        finally:
            duration_ms = int((time.time() - start) * 1000)
            outcome_payload = {
                "operation": name,
                "duration_ms": duration_ms,
                "success": success,
            }
            if error:
                outcome_payload["error"] = error
            outcome_payload.update(ctx.outcome_payload)
            self.emit_outcome(
                event_type=outcome_type,
                message=f"{name} outcome",
                payload=outcome_payload,
                correlation_id=corr_id,
                causation_id=intent.event_id,
                **kwargs,
            )


def new_correlation_id() -> str:
    return str(uuid.uuid4())


def get_default_emitter(agent_id: str = "os_dashboard") -> EventEmitter:
    # Lazy import to avoid circular dependency with hub -> audit -> sdk -> emitter
    from .hub import get_event_hub
    
    hub = get_event_hub()
    sinks: list[EventSink] = [HubSink(hub), LocalAppendOnlySink(default_journal_dir())]
    config = EventEmitterConfig(agent_id=agent_id)
    return EventEmitter(config, sinks)
