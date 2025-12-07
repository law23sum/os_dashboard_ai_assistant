"""Lightweight API gateway for external integrations.

This module exposes a simple, code-level API surface so other parts of the
assistant (and future HTTP layers) can programmatically talk to the connected
third-party services without needing to know their concrete implementations.
"""

from __future__ import annotations

from typing import Dict, Optional, Any
import sqlite3

from . import (
    GoogleCalendarIntegration,
    GmailIntegration,
    GitHubIntegration,
    NotesIntegration,
    WordIntegration,
    ExcelIntegration,
    OneNoteIntegration,
    FilesystemIntegration,
    GitIntegration,
    PDFIntegration,
)
from ..logging_config import get_logger
from ..sync_scheduler import create_default_scheduler, SyncScheduler


class IntegrationAPIGateway:
    """Provide a thin API façade over all available integrations."""

    def __init__(self, conn: sqlite3.Connection, scheduler: Optional[SyncScheduler] = None):
        self.conn = conn
        self.scheduler = scheduler or create_default_scheduler(conn)
        self.logger = get_logger(self.__class__.__name__)

    def _ensure_clients(self) -> Dict[str, object]:
        """Ensure all known integrations are instantiated and registered."""
        integrations = self.scheduler.integrations
        if not integrations:
            integrations.update({
                "notes": NotesIntegration(self.conn),
                "calendar": GoogleCalendarIntegration(self.conn),
                "mail": GmailIntegration(self.conn),
                "github": GitHubIntegration(self.conn),
            })

        # Lazily add optional integrations without impacting scheduler loops
        optional_clients = {
            "word": WordIntegration(self.conn),
            "excel": ExcelIntegration(self.conn),
            "onenote": OneNoteIntegration(self.conn),
            "filesystem": FilesystemIntegration(self.conn),
            "git": GitIntegration(self.conn),
            "pdf": PDFIntegration(self.conn),
        }
        for key, client in optional_clients.items():
            integrations.setdefault(key, client)

        return integrations

    def available_integrations(self) -> Dict[str, object]:
        """Return the integration client map keyed by slug."""
        return self._ensure_clients()

    def list_statuses(self) -> Dict[str, Any]:
        """Return status dictionaries for all integrations."""
        statuses = {}
        for name, client in self._ensure_clients().items():
            try:
                status = client.get_status()
                statuses[name] = {
                    "connected": status.connected,
                    "last_sync": status.last_sync,
                    "error": status.error,
                    "item_count": status.item_count,
                }
            except Exception as exc:  # pragma: no cover - defensive
                statuses[name] = {"connected": False, "error": str(exc), "item_count": 0}
                self.logger.error("Failed to read status for %s: %s", name, exc)
        return statuses

    def call_action(self, name: str, action: str = "status") -> Any:
        """Call a supported action on an integration or all integrations."""
        name = name or "all"
        action = action or "status"

        if action == "sync":
            return self.scheduler.sync_now(None if name == "all" else name)

        if action == "status":
            if name == "all":
                return self.list_statuses()
            client = self._ensure_clients().get(name)
            if not client:
                raise ValueError(f"Integration '{name}' is not available")
            status = client.get_status()
            return {
                "connected": status.connected,
                "last_sync": status.last_sync,
                "error": status.error,
                "item_count": status.item_count,
            }

        raise ValueError(f"Unsupported action '{action}' for integration API")

