"""Asynchronous wrappers for Git versioning operations."""

from __future__ import annotations

import threading
from queue import Queue
from typing import Iterable

from .git_manager import auto_commit

_commit_queue: "Queue[dict]" = Queue()
_worker_started = False


def _worker() -> None:
    while True:
        job = _commit_queue.get()
        if job is None:
            break
        auto_commit(**job)
        _commit_queue.task_done()


def start_worker() -> None:
    """Launch the background worker if it is not running."""

    global _worker_started
    if not _worker_started:
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        _worker_started = True


def enqueue_commit(
    paths: Iterable[str],
    *,
    actor: str = "AIC",
    reason: str = "",
    tag: str = "",
) -> None:
    """Queue an auto-commit task for the background worker."""

    start_worker()
    _commit_queue.put({"paths": list(paths), "actor": actor, "reason": reason, "tag": tag})
