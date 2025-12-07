"""Background queue for non-blocking git auto-commits.

Long-running integrations (OneNote sync, Excel rewrites, etc.) can push
work onto this queue to avoid blocking the UI or scheduler while git
commands run.
"""

from __future__ import annotations

import threading
from queue import Queue
from typing import Iterable, Optional

from .git_manager import get_git_manager

_job_queue: "Queue[dict]" = Queue()
_worker: Optional[threading.Thread] = None


def _worker_loop():
    manager = get_git_manager()
    while True:
        job = _job_queue.get()
        if job is None:
            break
        manager.auto_commit(**job)
        _job_queue.task_done()


def start_worker() -> None:
    global _worker
    if _worker is None or not _worker.is_alive():
        _worker = threading.Thread(target=_worker_loop, daemon=True)
        _worker.start()


def enqueue_commit(
    paths: Iterable[str],
    actor: str = "AIC",
    reason: Optional[str] = None,
    tag: Optional[str] = None,
    email: str = "ai@local",
) -> None:
    """Place an auto-commit job on the queue."""

    start_worker()
    _job_queue.put(
        {
            "paths": list(paths),
            "actor": actor,
            "reason": reason,
            "tag": tag,
            "email": email,
        }
    )


def shutdown_worker() -> None:
    """Signal the worker to stop after processing queued jobs."""

    if _worker is not None and _worker.is_alive():
        _job_queue.put(None)
