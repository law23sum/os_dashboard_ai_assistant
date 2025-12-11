"""System monitoring utilities reused by web/dashboard layers.

This module satisfies portions of the canon spec:
- 1.7.2 / 1.7.4 – Driver-aware orchestrator exposing OS telemetry for UI/agents
- 5.2 / 5.3 – OS driver hooks + kernel execution surface observability
- 6.6 – Metrics/log observability feed wired into the control plane
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil optional
    psutil = None  # type: ignore


@dataclass
class SystemStats:
    """Structured stats block (aligns with spec section 6.6 observability)."""

    cpu_percent: float
    memory: Dict[str, Any]
    disk: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


SPEC_REFERENCES = ["1.7.2", "1.7.4", "5.2", "5.3", "6.6"]


def get_system_stats() -> Dict[str, Any]:
    """Return CPU/memory/disk stats similar to the legacy Flask dashboard."""

    if psutil is None:
        return {
            "cpu_percent": 0.0,
            "memory": {"error": "psutil not installed"},
            "disk": {"error": "psutil not installed"},
            "spec_refs": SPEC_REFERENCES,
        }

    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()._asdict()
    disk = psutil.disk_usage("/")._asdict()
    stats = SystemStats(cpu_percent=cpu, memory=memory, disk=disk).to_dict()
    stats["spec_refs"] = SPEC_REFERENCES
    return stats
