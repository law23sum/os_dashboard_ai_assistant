"""Lightweight task scheduler placeholder."""
from __future__ import annotations

from collections import deque
from typing import Callable, Deque


class Scheduler:
    def __init__(self) -> None:
        self._queue: Deque[Callable[[], None]] = deque()

    def add(self, fn: Callable[[], None]) -> None:
        self._queue.append(fn)

    def run(self) -> None:
        while self._queue:
            task = self._queue.popleft()
            task()
