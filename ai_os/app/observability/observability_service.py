"""Minimal observability service façade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ObservabilityService:
    """In-process observability façade."""

    def emit_metric(self, name: str, value: float, **labels: str) -> None:
        # Placeholder hook – connect to Prometheus, OTLP, etc.
        pass

    def emit_event(self, name: str, payload: Dict[str, Any]) -> None:
        pass

    def emit_trace(self, name: str, **fields: Any) -> None:
        pass
