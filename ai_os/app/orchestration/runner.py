"""Orchestrator wiring events to daemons."""
from __future__ import annotations

from ai_os.app.orchestration.events import Event, EventBus


class Orchestrator:
    def __init__(self, bus: EventBus):
        self.bus = bus

    def register_daemon(self, event_name: str, daemon):
        self.bus.subscribe(event_name, daemon.handle_event)

    def emit(self, event_name: str, payload):
        self.bus.publish(Event(name=event_name, payload=payload))
