"""Background git queue placeholder."""
from __future__ import annotations

from queue import Queue
from threading import Thread
from typing import Iterable

from assistant_hub.versioning.git_manager import GitManager


class GitAsyncQueue:
    def __init__(self, manager: GitManager):
        self.manager = manager
        self.queue: Queue[tuple[str, Iterable[str] | None]] = Queue()
        self.worker = Thread(target=self._loop, daemon=True)
        self.worker.start()

    def enqueue(self, message: str, paths: Iterable[str] | None = None) -> None:
        self.queue.put((message, paths))

    def _loop(self) -> None:
        while True:
            message, paths = self.queue.get()
            self.manager.add_and_commit(message, paths)
            self.queue.task_done()
