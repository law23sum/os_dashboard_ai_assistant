"""Minimal event bus used by daemons and orchestrations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Callable


@dataclass
class Event:
    name: str
    payload: Dict[str, Any]
    created_at: datetime = datetime.utcnow()


class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_name: str, handler: Callable[[Event], None]):
        self.subscribers.setdefault(event_name, []).append(handler)

    def publish(self, event: Event):
        for handler in self.subscribers.get(event.name, []):
            handler(event)
