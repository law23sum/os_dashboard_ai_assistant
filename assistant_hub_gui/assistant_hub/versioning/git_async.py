"""Background queue for non-blocking git auto-commits."""
from __future__ import annotations

import threading
from queue import Empty, Queue
from typing import Iterable

from .git_manager import git_autocommit

_commit_queue: "Queue[dict]" = Queue()
_worker_started = False


def _worker() -> None:
    while True:
        job = _commit_queue.get()
        if job is None:
            break
        git_autocommit(**job)
        _commit_queue.task_done()


def start_git_worker() -> None:
    global _worker_started
    if _worker_started:
        return
    worker = threading.Thread(target=_worker, daemon=True)
    worker.start()
    _worker_started = True


def enqueue_git_commit(
    paths: Iterable[str],
    *,
    actor: str,
    reason: str = "",
    tag: str = "",
) -> None:
    """Schedule a git auto-commit without blocking UI threads."""
    start_git_worker()
    _commit_queue.put({"paths": list(paths), "actor": actor, "reason": reason, "tag": tag})


def shutdown_worker(timeout: float = 2.0) -> None:
    """Signal the worker to exit and drain the queue."""
    if not _worker_started:
        return
    _commit_queue.put(None)
    try:
        _commit_queue.join()
    except Empty:
        return
