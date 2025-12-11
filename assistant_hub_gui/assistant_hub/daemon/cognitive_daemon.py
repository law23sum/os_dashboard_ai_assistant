"""Core cognitive daemon - the active intelligence layer.

This is the central orchestrator that runs continuously, monitoring
the knowledge workspace and executing automation without being asked.
"""

from __future__ import annotations

import threading
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import os

from ..db import load_state, load_settings, init_db, DB_FILE
from ..versioning import start_git_worker, get_git_manager
from .monitors import (
    DocumentMonitor,
    TaskMonitor,
    IntegrationMonitor,
    FileSystemMonitor,
    OutdatedContentMonitor,
)
from .automators import (
    AutoDraftService,
    AutoUpdateService,
    AutoSuggestService,
    WorkflowExecutor,
)


class CognitiveDaemon:
    """The active cognitive daemon that monitors and automates continuously.

    This daemon embodies the vision: an AI that doesn't just generate text,
    but runs the entire knowledge pipeline - monitoring, drafting, updating,
    organizing, versioning, and suggesting - all automatically.
    """

    def __init__(self, conn: sqlite3.Connection, enabled: bool = True):
        # Store DB file path instead of connection (connections can't be shared across threads)
        self.db_file = DB_FILE
        self.enabled = enabled
        self.running = False
        self.thread: Optional[threading.Thread] = None

        # Initialize git worker for automatic versioning
        start_git_worker()
        get_git_manager().ensure_repo()

        # Don't initialize monitors/automators here - they'll be created in the daemon thread
        # to avoid SQLite threading issues
        self.monitors = None
        self.automators = None

        # Statistics
        self.stats = {
            "cycles": 0,
            "actions_taken": 0,
            "documents_drafted": 0,
            "documents_updated": 0,
            "suggestions_generated": 0,
            "workflows_executed": 0,
            "last_cycle": None,
        }

    def start(self):
        """Start the cognitive daemon."""
        if self.running:
            return

        if not self.enabled:
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._run, daemon=True, name="CognitiveDaemon"
        )
        self.thread.start()

    def stop(self, timeout: float = 5.0):
        """Stop the cognitive daemon."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=timeout)

    def _run(self):
        """Main daemon loop - runs continuously, monitoring and automating."""
        # Create a new database connection in this thread (SQLite connections are thread-specific)
        conn = init_db()

        # Initialize monitors and automators in this thread with the thread-local connection
        self.monitors = {
            "documents": DocumentMonitor(conn),
            "tasks": TaskMonitor(conn),
            "integrations": IntegrationMonitor(conn),
            "filesystem": FileSystemMonitor(conn),
            "outdated": OutdatedContentMonitor(conn),
        }

        self.automators = {
            "draft": AutoDraftService(conn),
            "update": AutoUpdateService(conn),
            "suggest": AutoSuggestService(conn),
            "workflow": WorkflowExecutor(conn),
        }

        cycle_interval = 60  # Check every 60 seconds

        try:
            while self.running:
                try:
                    cycle_start = datetime.now()
                    self.stats["cycles"] += 1

                    # Load current state using thread-local connection
                    state = load_state(conn)
                    settings = load_settings(conn)

                    # Run all monitors to detect opportunities
                    findings = self._run_monitors(state, settings)

                    # Execute automated actions based on findings
                    actions = self._execute_automations(findings, state, settings)

                    # Update statistics
                    self.stats["actions_taken"] += len(actions)
                    self.stats["last_cycle"] = cycle_start.isoformat()

                    # Log cycle completion
                    cycle_duration = (datetime.now() - cycle_start).total_seconds()
                    if cycle_duration > 1.0:  # Only log if cycle took significant time
                        print(
                            f"[CognitiveDaemon] Cycle {self.stats['cycles']} completed: "
                            f"{len(findings)} findings, {len(actions)} actions in {cycle_duration:.2f}s"
                        )

                except Exception as e:
                    print(f"[CognitiveDaemon] Error in daemon cycle: {e}")

                # Sleep until next cycle
                for _ in range(cycle_interval):
                    if not self.running:
                        break
                    time.sleep(1)
        finally:
            # Close the connection when daemon stops
            conn.close()

    def _run_monitors(self, state, settings) -> Dict[str, List]:
        """Run all monitors and collect findings."""
        findings = {}

        # Safety check - monitors should be initialized in _run()
        if not self.monitors:
            return findings

        try:
            findings["documents"] = self.monitors["documents"].check(state, settings)
        except Exception as e:
            print(f"[CognitiveDaemon] DocumentMonitor error: {e}")
            findings["documents"] = []

        try:
            findings["tasks"] = self.monitors["tasks"].check(state, settings)
        except Exception as e:
            print(f"[CognitiveDaemon] TaskMonitor error: {e}")
            findings["tasks"] = []

        try:
            findings["integrations"] = self.monitors["integrations"].check(
                state, settings
            )
        except Exception as e:
            print(f"[CognitiveDaemon] IntegrationMonitor error: {e}")
            findings["integrations"] = []

        try:
            findings["filesystem"] = self.monitors["filesystem"].check(state, settings)
        except Exception as e:
            print(f"[CognitiveDaemon] FileSystemMonitor error: {e}")
            findings["filesystem"] = []

        try:
            findings["outdated"] = self.monitors["outdated"].check(state, settings)
        except Exception as e:
            print(f"[CognitiveDaemon] OutdatedContentMonitor error: {e}")
            findings["outdated"] = []

        return findings

    def _execute_automations(
        self, findings: Dict[str, List], state, settings
    ) -> List[str]:
        """Execute automated actions based on monitor findings."""
        actions = []

        # Safety check - automators should be initialized in _run()
        if not self.automators:
            return actions

        # Auto-draft missing documents
        try:
            draft_actions = self.automators["draft"].process_findings(
                findings, state, settings
            )
            actions.extend(draft_actions)
            self.stats["documents_drafted"] += len(draft_actions)
        except Exception as e:
            print(f"[CognitiveDaemon] AutoDraftService error: {e}")

        # Auto-update outdated content
        try:
            update_actions = self.automators["update"].process_findings(
                findings, state, settings
            )
            actions.extend(update_actions)
            self.stats["documents_updated"] += len(update_actions)
        except Exception as e:
            print(f"[CognitiveDaemon] AutoUpdateService error: {e}")

        # Generate suggestions
        try:
            suggestions = self.automators["suggest"].process_findings(
                findings, state, settings
            )
            actions.extend(suggestions)
            self.stats["suggestions_generated"] += len(suggestions)
        except Exception as e:
            print(f"[CognitiveDaemon] AutoSuggestService error: {e}")

        # Execute workflows
        try:
            workflow_actions = self.automators["workflow"].process_findings(
                findings, state, settings
            )
            actions.extend(workflow_actions)
            self.stats["workflows_executed"] += len(workflow_actions)
        except Exception as e:
            print(f"[CognitiveDaemon] WorkflowExecutor error: {e}")

        return actions

    def get_stats(self) -> Dict:
        """Get daemon statistics."""
        return self.stats.copy()


# Global daemon instance
_daemon_instance: Optional[CognitiveDaemon] = None


def start_daemon_system(
    conn: sqlite3.Connection, enabled: bool = True
) -> CognitiveDaemon:
    """Start the cognitive daemon system globally."""
    global _daemon_instance

    if _daemon_instance is None or not _daemon_instance.running:
        _daemon_instance = CognitiveDaemon(conn, enabled=enabled)
        _daemon_instance.start()
        print("[CognitiveDaemon] Started cognitive daemon system")

    return _daemon_instance


def stop_daemon_system():
    """Stop the cognitive daemon system."""
    global _daemon_instance

    if _daemon_instance and _daemon_instance.running:
        _daemon_instance.stop()
        print("[CognitiveDaemon] Stopped cognitive daemon system")
        _daemon_instance = None


def get_daemon() -> Optional[CognitiveDaemon]:
    """Get the current daemon instance."""
    return _daemon_instance
