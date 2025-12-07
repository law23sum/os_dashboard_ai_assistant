"""Base integration class for external services."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import sqlite3

from ..db import record_external_item, ensure_external_source


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

