"""Lightweight job scheduler for daemon operations."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from enum import Enum


class JobType(Enum):
    """Types of scheduled jobs."""
    REPEATING = "repeating"
    ONESHOT = "oneshot"


@dataclass
class Job:
    """A scheduled job."""
    id: str
    job_type: JobType
    func: Callable
    interval_seconds: Optional[int] = None  # For repeating jobs
    run_at: Optional[datetime] = None  # For oneshot jobs
    last_run: Optional[datetime] = None
    enabled: bool = True


class Scheduler:
    """Minimal job scheduler for daemon operations."""

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def add_repeating_job(
        self,
        job_id: str,
        func: Callable,
        interval_seconds: int,
        enabled: bool = True,
    ) -> None:
        """Add a repeating job that runs every interval_seconds."""
        with self._lock:
            self.jobs[job_id] = Job(
                id=job_id,
                job_type=JobType.REPEATING,
                func=func,
                interval_seconds=interval_seconds,
                enabled=enabled,
            )

    def add_oneshot_job(
        self,
        job_id: str,
        func: Callable,
        run_at: datetime,
        enabled: bool = True,
    ) -> None:
        """Add a oneshot job that runs at a specific time."""
        with self._lock:
            self.jobs[job_id] = Job(
                id=job_id,
                job_type=JobType.ONESHOT,
                func=func,
                run_at=run_at,
                enabled=enabled,
            )

    def remove_job(self, job_id: str) -> None:
        """Remove a job from the scheduler."""
        with self._lock:
            self.jobs.pop(job_id, None)

    def enable_job(self, job_id: str) -> None:
        """Enable a job."""
        with self._lock:
            if job_id in self.jobs:
                self.jobs[job_id].enabled = True

    def disable_job(self, job_id: str) -> None:
        """Disable a job."""
        with self._lock:
            if job_id in self.jobs:
                self.jobs[job_id].enabled = False

    def start(self) -> None:
        """Start the scheduler thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop the scheduler thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)

    def _run(self) -> None:
        """Main scheduler loop."""
        while self.running:
            now = datetime.now()
            jobs_to_run: List[Job] = []

            with self._lock:
                for job in self.jobs.values():
                    if not job.enabled:
                        continue

                    if job.job_type == JobType.REPEATING:
                        if job.last_run is None:
                            jobs_to_run.append(job)
                        elif (now - job.last_run).total_seconds() >= job.interval_seconds:
                            jobs_to_run.append(job)
                    elif job.job_type == JobType.ONESHOT:
                        if job.run_at and now >= job.run_at:
                            jobs_to_run.append(job)

            for job in jobs_to_run:
                try:
                    job.func()
                    job.last_run = now
                    if job.job_type == JobType.ONESHOT:
                        self.remove_job(job.id)
                except Exception:
                    # Log error but continue
                    pass

            time.sleep(1)  # Check every second


