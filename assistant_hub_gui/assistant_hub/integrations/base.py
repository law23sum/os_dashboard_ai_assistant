"""Base integration class for external services."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any
import sqlite3

from ..db import record_external_item, ensure_external_source
from ..logging_config import get_logger


@dataclass
class IntegrationStatus:
    """Status of an external integration."""

    connected: bool = False
    last_sync: Optional[str] = None
    error: Optional[str] = None
    item_count: int = 0


class BaseIntegration(ABC):
    """Base class for all external integrations."""

    def __init__(self, conn: sqlite3.Connection, source_name: str, source_kind: str):
        self.conn = conn
        self.source_name = source_name
        self.source_kind = source_kind
        self._status = IntegrationStatus()
        self.logger = get_logger(self.__class__.__name__)

    def available_actions(self) -> Dict[str, Dict[str, Any]]:
        """Return a map of supported actions and their input schemas.

        Each entry should follow the structure::

            {
                "action_name": {
                    "label": "Human readable label",
                    "description": "What the action does",
                    "fields": [
                        {"name": "path", "label": "File Path", "type": "text", "placeholder": "~/Documents/file.txt"}
                    ]
                }
            }
        """

        return {
            "status": {
                "label": "Connection Status",
                "description": "Check whether the integration is connected and when it last synced.",
                "fields": [],
            },
            "sync": {
                "label": "Sync",
                "description": "Sync data from the integration and refresh status.",
                "fields": [],
            },
            "authenticate": {
                "label": "Authenticate",
                "description": "Force an authentication attempt for the integration.",
                "fields": [],
            },
        }

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the external service. Returns True if successful."""
        pass

    @abstractmethod
    def sync(self) -> int:
        """Sync data from external service. Returns number of items synced."""
        pass

    @abstractmethod
    def get_status(self) -> IntegrationStatus:
        """Get current status of the integration."""
        pass

    def invoke_action(
        self, action: str, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Invoke an action exposed by the integration.

        Concrete integrations can override this to support richer behaviors,
        but by default we expose the core lifecycle actions.
        """

        options = options or {}
        if action == "authenticate":
            return self.authenticate()
        if action == "sync":
            return self.sync()
        if action == "status":
            status = self.get_status()
            return {
                "connected": status.connected,
                "last_sync": status.last_sync,
                "error": status.error,
                "item_count": status.item_count,
            }

        # As a fallback, allow calling a method directly if explicitly exposed
        if hasattr(self, action):
            attr = getattr(self, action)
            if callable(attr):
                return attr(**options) if options else attr()

        raise ValueError(f"Unsupported action '{action}' for {self.source_name}")

    def record_item(
        self, external_id: str, item_kind: str, title: str, data: Dict[str, Any]
    ):
        """Record an external item in the database."""
        record_external_item(
            self.conn,
            source_name=self.source_name,
            source_kind=self.source_kind,
            external_id=external_id,
            item_kind=item_kind,
            title=title,
            data=data,
        )

    def ensure_source(self) -> int:
        """Ensure the external source exists in the database."""
        return ensure_external_source(self.conn, self.source_name, self.source_kind)

    def update_status(
        self, connected: bool, error: Optional[str] = None, item_count: int = 0
    ):
        """Update integration status."""
        self._status.connected = connected
        self._status.last_sync = (
            datetime.now().isoformat(timespec="seconds") if connected else None
        )
        self._status.error = error
        self._status.item_count = item_count

        status_text = "connected" if connected else "disconnected"
        if error:
            self.logger.error(
                "%s status updated: %s | error=%s", self.source_name, status_text, error
            )
        else:
            self.logger.info(
                "%s status updated: %s | items=%s",
                self.source_name,
                status_text,
                item_count,
            )

    def _safe_truncate(self, value: Optional[str], length: int = 180) -> Optional[str]:
        """Truncate long strings for status messages."""
        if value is None:
            return None
        return value if len(value) <= length else value[: length - 3] + "..."
