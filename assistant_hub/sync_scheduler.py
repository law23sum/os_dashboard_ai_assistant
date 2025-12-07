"""Sync scheduler for external integrations."""

import threading
import time
from typing import Dict, List
import sqlite3

from .db import init_db, load_settings
from .integrations import (
    GoogleCalendarIntegration,
    GmailIntegration,
    GitHubIntegration,
    NotesIntegration,
)
from .logging_config import get_logger


class SyncScheduler:
    """Manages periodic syncing of external integrations."""
    
    def __init__(self, conn: sqlite3.Connection, interval: int = 300):
        self.conn = conn
        self.interval = interval  # seconds
        self.running = False
        self.thread = None
        self.integrations: Dict[str, object] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def register_integration(self, name: str, integration):
        """Register an integration for syncing."""
        self.integrations[name] = integration
    
    def start(self):
        """Start the sync scheduler."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the sync scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _run(self):
        """Main sync loop."""
        while self.running:
            try:
                settings = load_settings(self.conn)

                # Sync based on preferences
                if settings.data_preferences.get("notes", False) and "notes" in self.integrations:
                    try:
                        self.integrations["notes"].sync()
                    except Exception as exc:
                        self.logger.error("Notes sync failed: %s", exc)

                if settings.data_preferences.get("calendar", False) and "calendar" in self.integrations:
                    try:
                        self.integrations["calendar"].sync()
                    except Exception as exc:
                        self.logger.error("Calendar sync failed: %s", exc)

                if settings.data_preferences.get("mail", False) and "mail" in self.integrations:
                    try:
                        self.integrations["mail"].sync()
                    except Exception as exc:
                        self.logger.error("Mail sync failed: %s", exc)

                # GitHub doesn't have a preference yet, sync if registered
                if "github" in self.integrations:
                    try:
                        self.integrations["github"].sync()
                    except Exception as exc:
                        self.logger.error("GitHub sync failed in loop: %s", exc)

            except Exception as exc:
                self.logger.exception("Sync scheduler loop error: %s", exc)
            
            # Sleep for interval
            for _ in range(self.interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def sync_now(self, integration_name: str = None) -> Dict[str, int]:
        """Manually trigger sync for all or specific integration."""
        results = {}
        
        if integration_name:
            if integration_name in self.integrations:
                try:
                    count = self.integrations[integration_name].sync()
                    results[integration_name] = count
                except Exception as e:
                    results[integration_name] = -1
        else:
            for name, integration in self.integrations.items():
                try:
                    count = integration.sync()
                    results[name] = count
                except Exception as e:
                    results[name] = -1
        
        return results


def create_default_scheduler(conn: sqlite3.Connection) -> SyncScheduler:
    """Create scheduler with default integrations."""
    scheduler = SyncScheduler(conn)
    
    # Register default integrations
    scheduler.register_integration("notes", NotesIntegration(conn))
    scheduler.register_integration("calendar", GoogleCalendarIntegration(conn))
    scheduler.register_integration("mail", GmailIntegration(conn))
    scheduler.register_integration("github", GitHubIntegration(conn))
    
    return scheduler

