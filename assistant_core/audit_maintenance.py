"""Audit maintenance runner for retention, compaction, and cold export tasks."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from assistant_core.audit_system import AuditLevel, AuditSystem
from config.config import AuditSettings, get_audit_config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuditMaintenanceConfig:
    enabled: bool
    retention_apply: bool
    retention_interval_hours: int
    compaction_interval_hours: int
    parquet_enabled: bool
    parquet_interval_hours: int
    parquet_range_days: int
    tenant_id: Optional[str] = None

    @classmethod
    def from_settings(cls, settings: AuditSettings) -> "AuditMaintenanceConfig":
        return cls(
            enabled=settings.maintenance_enabled,
            retention_apply=settings.maintenance_retention_apply,
            retention_interval_hours=settings.maintenance_retention_interval_hours,
            compaction_interval_hours=settings.maintenance_compact_interval_hours,
            parquet_enabled=settings.maintenance_parquet_enabled,
            parquet_interval_hours=settings.maintenance_parquet_interval_hours,
            parquet_range_days=settings.maintenance_parquet_range_days,
            tenant_id=settings.maintenance_tenant_id,
        )


class AuditMaintenanceRunner:
    """Schedules audit retention, index compaction, and parquet exports."""

    def __init__(
        self,
        audit_system: Optional[AuditSystem] = None,
        settings: Optional[AuditSettings] = None,
    ) -> None:
        self.settings = settings or get_audit_config()
        self.config = AuditMaintenanceConfig.from_settings(self.settings)
        self.audit_system = audit_system or AuditSystem(audit_settings=self.settings)
        self._tasks: List[asyncio.Task] = []
        self._stop_event = asyncio.Event()
        self._lock = asyncio.Lock()
        self._started = False

    async def start(self) -> None:
        if self._started or not self.config.enabled:
            return
        self._started = True
        await self.audit_system.initialize(enable_git=False)

        if self.config.retention_interval_hours > 0:
            self._tasks.append(
                asyncio.create_task(
                    self._run_periodic(
                        "retention",
                        self.config.retention_interval_hours * 3600,
                        self._run_retention,
                    )
                )
            )
        if self.config.compaction_interval_hours > 0:
            self._tasks.append(
                asyncio.create_task(
                    self._run_periodic(
                        "compaction",
                        self.config.compaction_interval_hours * 3600,
                        self._run_compaction,
                    )
                )
            )
        if self.config.parquet_enabled and self.config.parquet_interval_hours > 0:
            self._tasks.append(
                asyncio.create_task(
                    self._run_periodic(
                        "parquet_export",
                        self.config.parquet_interval_hours * 3600,
                        self._run_parquet_export,
                    )
                )
            )

    async def stop(self) -> None:
        if not self._started:
            return
        self._stop_event.set()
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._started = False
        self._stop_event = asyncio.Event()

    async def _run_periodic(self, name: str, interval_seconds: int, func) -> None:
        while not self._stop_event.is_set():
            started_at = datetime.utcnow()
            try:
                await func()
            except asyncio.CancelledError:
                return
            except Exception:
                logger.exception("Audit maintenance task failed: %s", name)
            elapsed = (datetime.utcnow() - started_at).total_seconds()
            sleep_for = max(1.0, interval_seconds - elapsed)
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=sleep_for)
            except asyncio.TimeoutError:
                continue

    async def _run_retention(self) -> None:
        async with self._lock:
            plan = self.audit_system.plan_retention(
                as_of=datetime.utcnow(),
                tenant_id=self.config.tenant_id,
                apply=self.config.retention_apply,
            )
            await self.audit_system.log_action_step(
                action="audit_retention",
                details={
                    "cutoff": plan.get("cutoff"),
                    "candidates": len(plan.get("candidates", [])),
                    "deleted": len(plan.get("deleted", [])),
                    "applied": plan.get("applied"),
                    "tenant_id": self.config.tenant_id,
                },
                level=AuditLevel.WARNING if plan.get("applied") else AuditLevel.INFO,
            )

    async def _run_compaction(self) -> None:
        async with self._lock:
            now = datetime.now(timezone.utc)
            target_date = (now - timedelta(days=1)).date()
            target_dt = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
            rollup_path = self.audit_system.compact_daily_indexes(
                target_dt, tenant_id=self.config.tenant_id
            )
            await self.audit_system.log_action_step(
                action="audit_compaction",
                details={
                    "date": target_date.isoformat(),
                    "rollup_path": rollup_path,
                    "tenant_id": self.config.tenant_id,
                },
            )

    async def _run_parquet_export(self) -> None:
        async with self._lock:
            now = datetime.now(timezone.utc)
            end = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
            start = end - timedelta(days=max(1, self.config.parquet_range_days))
            try:
                path = await self.audit_system.export_audit_parquet(
                    start_date=start,
                    end_date=end,
                    tenant_id=self.config.tenant_id,
                )
                await self.audit_system.log_action_step(
                    action="audit_parquet_export",
                    details={
                        "start_date": start.isoformat(),
                        "end_date": end.isoformat(),
                        "output_path": path,
                        "tenant_id": self.config.tenant_id,
                    },
                )
            except Exception as exc:
                await self.audit_system.log_action_step(
                    action="audit_parquet_export_failed",
                    details={
                        "start_date": start.isoformat(),
                        "end_date": end.isoformat(),
                        "error": str(exc),
                        "tenant_id": self.config.tenant_id,
                    },
                    level=AuditLevel.ERROR,
                )
