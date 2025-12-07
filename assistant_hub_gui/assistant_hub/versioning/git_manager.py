"""Git versioning utilities for automated AI changes.

This module provides a thin wrapper around git commands so that any
integration or workflow that mutates files can stage and commit those
changes with minimal boilerplate. It is intentionally simple and uses
``subprocess`` instead of heavier dependencies to keep the assistant
portable.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional


@dataclass
class GitIdentity:
    """Identity metadata for commits authored by agents or users."""

    name: str
    email: str = "ai@local"


class GitManager:
    """Manage basic git operations inside the assistant workspace."""

    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)

    def _run(self, args: List[str], env: Optional[dict] = None, check: bool = True):
        subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            check=check,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

    def ensure_repo(self) -> None:
        """Initialize a git repository if one does not exist."""
        if not os.path.isdir(os.path.join(self.repo_root, ".git")):
            self._run(["init"])

    def add(self, paths: Iterable[str]) -> None:
        """Stage files relative to the repository root."""
        rel_paths = [os.path.relpath(path, self.repo_root) for path in paths]
        if rel_paths:
            self._run(["add", *rel_paths])

    def commit(self, message: str, identity: Optional[GitIdentity] = None) -> None:
        """Create a commit with an optional author identity.

        The commit will be skipped quietly if there are no staged changes.
        """

        env = os.environ.copy()
        if identity:
            env["GIT_AUTHOR_NAME"] = identity.name
            env["GIT_COMMITTER_NAME"] = identity.name
            env.setdefault("GIT_AUTHOR_EMAIL", identity.email)
            env.setdefault("GIT_COMMITTER_EMAIL", identity.email)

        # ``git commit`` exits with status 1 when there is nothing to commit;
        # we suppress the exception to keep the background workflow quiet.
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.repo_root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

    def auto_commit(
        self,
        paths: Iterable[str],
        actor: str = "AIC",
        reason: str | None = None,
        tag: str | None = None,
        email: str = "ai@local",
    ) -> None:
        """Stage paths and create a standardized commit message."""

        filtered = [path for path in paths if os.path.exists(path)]
        if not filtered:
            return

        self.add(filtered)
        timestamp = datetime.now().isoformat(timespec="seconds")
        tag_block = f"[{tag}] " if tag else ""
        reason_block = f" - {reason}" if reason else ""
        message = f"{tag_block}{actor} auto-commit @ {timestamp}{reason_block}"
        self.commit(message, identity=GitIdentity(name=actor, email=email))


_global_manager: Optional[GitManager] = None


def init_git_manager(repo_root: str) -> GitManager:
    """Initialize and cache a :class:`GitManager` instance."""

    global _global_manager
    manager = GitManager(repo_root)
    manager.ensure_repo()
    _global_manager = manager
    return manager


def get_git_manager() -> GitManager:
    """Return a cached git manager, initializing it when needed."""

    global _global_manager
    if _global_manager is None:
        _global_manager = init_git_manager(os.getcwd())
    return _global_manager


# Backwards compatibility function
def git_autocommit(
    paths: Iterable[str],
    *,
    actor: str = "AIC",
    reason: str = "",
    tag: str = "",
    timestamp: Optional[datetime] = None,
) -> None:
    """Stage and commit modified files with standardized metadata (backwards compatibility)."""
    manager = get_git_manager()
    existing_paths = [path for path in paths if os.path.exists(path)]
    if not existing_paths:
        return

    manager.add(existing_paths)

    ts = timestamp or datetime.now()
    tag_prefix = f"[{tag}] " if tag else ""
    reason_suffix = f" - {reason}" if reason else ""
    message = f"{tag_prefix}{actor} auto-commit @ {ts.isoformat(timespec='seconds')}{reason_suffix}"
    manager.commit(message, identity=GitIdentity(name=actor, email="ai@local"))
