"""Git version control integration wrapper for GUI."""

import os
import subprocess
from pathlib import Path
from typing import Dict
import sqlite3

from .base import BaseIntegration, IntegrationStatus
from ..versioning.git_manager import GitManager, get_git_manager


class GitIntegration(BaseIntegration):
    """Integration for Git version control."""

    def __init__(self, conn: sqlite3.Connection, repo_root: str = None):
        super().__init__(conn, "Git", "git")
        self.repo_root = repo_root or os.getcwd()
        self.manager = None

    def authenticate(self) -> bool:
        """Check if git is available and repository exists or can be initialized."""
        try:
            # Check if git is installed
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                self.update_status(False, "Git is not installed")
                return False

            # Initialize git manager
            self.manager = get_git_manager()
            if self.manager:
                self.manager.ensure_repo()

            self.update_status(True)
            return True
        except FileNotFoundError:
            self.update_status(False, "Git is not installed or not in PATH")
            return False
        except Exception as e:
            self.update_status(False, str(e))
            return False

    def sync(self) -> int:
        """Get git repository status and recent commits."""
        if not self.authenticate():
            return 0

        count = 0
        try:
            git_dir = os.path.join(self.repo_root, ".git")
            if not os.path.exists(git_dir):
                self.update_status(True, item_count=0)
                return 0

            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                for commit_line in commits:
                    if not commit_line:
                        continue
                    parts = commit_line.split(" ", 1)
                    if len(parts) == 2:
                        commit_hash, message = parts
                        self.record_item(
                            external_id=commit_hash,
                            item_kind="commit",
                            title=message[:50],
                            data={"hash": commit_hash, "message": message},
                        )
                        count += 1

            # Get branch info
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if branch_result.returncode == 0:
                branch_name = branch_result.stdout.strip()
                if branch_name:
                    self.record_item(
                        external_id="current_branch",
                        item_kind="branch",
                        title=f"Current Branch: {branch_name}",
                        data={"branch": branch_name},
                    )
                    count += 1

            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            self.update_status(False, str(e))
            return 0

    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, "_status") or not self._status:
            self._status = IntegrationStatus()
        return self._status
