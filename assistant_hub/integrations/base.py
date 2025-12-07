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
    
    def record_item(
        self,
        external_id: str,
        item_kind: str,
        title: str,
        data: Dict[str, Any]
    ):
        """Record an external item in the database."""
        record_external_item(
            self.conn,
            source_name=self.source_name,
            source_kind=self.source_kind,
            external_id=external_id,
            item_kind=item_kind,
            title=title,
            data=data
        )
    
    def ensure_source(self) -> int:
        """Ensure the external source exists in the database."""
        return ensure_external_source(self.conn, self.source_name, self.source_kind)
    
    def update_status(self, connected: bool, error: Optional[str] = None, item_count: int = 0):
        """Update integration status."""
        self._status.connected = connected
        self._status.last_sync = datetime.now().isoformat(timespec="seconds") if connected else None
        self._status.error = error
        self._status.item_count = item_count

        status_text = "connected" if connected else "disconnected"
        if error:
            self.logger.error("%s status updated: %s | error=%s", self.source_name, status_text, error)
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

