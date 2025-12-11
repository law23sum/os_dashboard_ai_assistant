"""Fallback psutil implementation for sandboxed environments."""

from __future__ import annotations

import os
import shutil
import time
from types import SimpleNamespace
from typing import Dict, Iterable, List


def _struct(**kwargs):
    """Return an object mimicking psutil namedtuples."""

    data = dict(kwargs)

    class _Struct(SimpleNamespace):
        def _asdict(self) -> Dict[str, float]:
            return dict(self.__dict__)

    return _Struct(**data)


class PsutilStub:
    """Very small subset of psutil used by the GUI/monitoring layers."""

    class NoSuchProcess(Exception):
        pass

    class AccessDenied(Exception):
        pass

    def cpu_count(self, logical: bool = True) -> int:
        count = os.cpu_count() or 1
        return count if logical else max(1, count // 2)

    def cpu_freq(self):  # pragma: no cover - best effort only
        return _struct(current=0.0, min=0.0, max=0.0)

    def cpu_percent(self, interval: float | None = None) -> float:
        return 0.0

    def virtual_memory(self):  # pragma: no cover - approximation ok
        return _struct(total=0, available=0, used=0, free=0, percent=0.0)

    def disk_usage(self, path: str):
        try:
            usage = shutil.disk_usage(path)
            percent = (usage.used / usage.total * 100) if usage.total else 0.0
            return _struct(total=usage.total, used=usage.used, free=usage.free, percent=percent)
        except FileNotFoundError:
            return _struct(total=0, used=0, free=0, percent=0.0)

    def net_if_addrs(self) -> Dict[str, List[SimpleNamespace]]:
        return {}

    def process_iter(self, attrs: Iterable[str] | None = None):
        return []

    def boot_time(self) -> float:
        return time.time()

    def net_io_counters(self):
        return _struct(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0)

    def disk_io_counters(self):
        return _struct(read_bytes=0, write_bytes=0, read_time=0, write_time=0)


psutil = PsutilStub()

