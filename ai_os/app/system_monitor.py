"""System monitoring utilities reused by web/dashboard layers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil optional
    psutil = None  # type: ignore


@dataclass
class SystemStats:
    cpu_percent: float
    memory: Dict[str, Any]
    disk: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_system_stats() -> Dict[str, Any]:
    """Return CPU/memory/disk stats similar to the legacy Flask dashboard."""

    if psutil is None:
        return {
            "cpu_percent": 0.0,
            "memory": {"error": "psutil not installed"},
            "disk": {"error": "psutil not installed"},
        }

    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()._asdict()
    disk = psutil.disk_usage("/")._asdict()
    return SystemStats(cpu_percent=cpu, memory=memory, disk=disk).to_dict()
