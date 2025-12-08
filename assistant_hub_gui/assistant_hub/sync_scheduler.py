"""Sync scheduler for external integrations."""

import threading
import time
from typing import Dict, List
import sqlite3

from .db import init_db, load_settings

# Import integrations with graceful fallbacks for missing dependencies
def _create_dummy_integration(name: str):
    """Create a dummy integration class for missing dependencies."""
    class DummyIntegration:
        def __init__(self, conn):
            self.conn = conn
            self.logger = type('Logger', (), {'info': lambda x: None, 'error': lambda x: None, 'warning': lambda x: None})()

        def sync(self):
            """Dummy sync method that does nothing."""
            self.logger.info(f"{name} integration not available - skipping sync")
            return 0

        async def sync(self):
            """Async version of dummy sync method."""
            return self.sync()

    return DummyIntegration

# Try to import integrations, create dummies for missing ones
try:
    from .integrations import (
        AppleCalendarIntegration,
        EmailIntelligenceIntegration,
        GmailIntegration,
        GitHubIntegration,
        NotesIntegration,
    )
except ImportError:
    try:
        # Fall back to main assistant_hub integrations
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        from assistant_hub.integrations import (
            AppleCalendarIntegration,
            GmailIntegration,
            GitHubIntegration,
            NotesIntegration,
        )

        # Create dummies for integrations that may not be available
        EmailIntelligenceIntegration = _create_dummy_integration("EmailIntelligence")

    except ImportError:
        # Create dummies for all integrations if main imports also fail
        AppleCalendarIntegration = _create_dummy_integration("AppleCalendar")
        EmailIntelligenceIntegration = _create_dummy_integration("EmailIntelligence")
        GmailIntegration = _create_dummy_integration("Gmail")
        GitHubIntegration = _create_dummy_integration("GitHub")
        NotesIntegration = _create_dummy_integration("Notes")


class SyncScheduler:
    """Manages periodic syncing of external integrations."""
    
    def __init__(self, conn: sqlite3.Connection, interval: int = 300):
        self.conn = conn
        self.interval = interval  # seconds
        self.running = False
        self.thread = None
        self.integrations: Dict[str, object] = {}
    
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
                if settings.data_preferences.get("notes", False):
                    if "notes" in self.integrations:
                        try:
                            self.integrations["notes"].sync()
                        except Exception:
                            pass
                
                if settings.data_preferences.get("calendar", False):
                    if "calendar" in self.integrations:
                        try:
                            self.integrations["calendar"].sync()
                        except Exception:
                            pass
                
                if settings.data_preferences.get("mail", False):
                    if "mail" in self.integrations:
                        try:
                            self.integrations["mail"].sync()
                        except Exception:
                            pass
                
                # GitHub doesn't have a preference yet, sync if registered
                if "github" in self.integrations:
                    try:
                        self.integrations["github"].sync()
                    except Exception:
                        pass
                
            except Exception:
                pass
            
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
    scheduler.register_integration("calendar", AppleCalendarIntegration(conn))
    scheduler.register_integration("mail", GmailIntegration(conn))
    scheduler.register_integration("github", GitHubIntegration(conn))
    
    return scheduler
