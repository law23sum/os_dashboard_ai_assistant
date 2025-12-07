"""Git versioning helpers for automated AI-driven edits.

This module provides a thin wrapper around git commands so that any
integration that mutates files can stage and commit those changes with
consistent metadata. It intentionally avoids heavy dependencies such as
GitPython to keep the footprint small and predictable.
"""
from __future__ import annotations

import os
import subprocess
from datetime import datetime
from typing import Iterable, List, Optional


class GitManager:
    """Minimal git helper for staging and committing files."""

    def __init__(self, repo_root: str) -> None:
        self.repo_root = os.path.abspath(repo_root)

    def _run(self, args: List[str], env: Optional[dict] = None) -> None:
        subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

    def ensure_repo(self) -> None:
        """Initialize git repository when missing."""
        git_dir = os.path.join(self.repo_root, ".git")
        if not os.path.isdir(git_dir):
            self._run(["init"])

    def add(self, paths: Iterable[str]) -> None:
        """Stage the provided paths relative to repo root."""
        rel_paths = [os.path.relpath(path, self.repo_root) for path in paths]
        if rel_paths:
            self._run(["add", *rel_paths])

    def commit(self, message: str, actor: Optional[str] = None) -> None:
        """Create a commit; no-op when there is nothing to commit."""
        env = os.environ.copy()
        if actor:
            env.setdefault("GIT_AUTHOR_NAME", actor)
            env.setdefault("GIT_COMMITTER_NAME", actor)
            env.setdefault("GIT_AUTHOR_EMAIL", "ai@local")
            env.setdefault("GIT_COMMITTER_EMAIL", "ai@local")

        try:
            self._run(["commit", "-m", message], env=env)
        except subprocess.CalledProcessError:
            # Nothing to commit; ignore silently.
            return


_git_manager: Optional[GitManager] = None


def init_git_manager(repo_root: str) -> GitManager:
    """Initialize and cache the global GitManager instance."""
    global _git_manager
    manager = GitManager(repo_root)
    manager.ensure_repo()
    _git_manager = manager
    return manager


def get_git_manager() -> GitManager:
    """Return the cached GitManager, defaulting to current working directory."""
    global _git_manager
    if _git_manager is None:
        init_git_manager(os.getcwd())
    assert _git_manager is not None
    return _git_manager


def git_autocommit(
    paths: Iterable[str],
    *,
    actor: str = "AIC",
    reason: str = "",
    tag: str = "",
    timestamp: Optional[datetime] = None,
) -> None:
    """Stage and commit modified files with standardized metadata."""
    manager = get_git_manager()
    existing_paths = [path for path in paths if os.path.exists(path)]
    if not existing_paths:
        return

    manager.add(existing_paths)

    ts = timestamp or datetime.now()
    tag_prefix = f"[{tag}] " if tag else ""
    reason_suffix = f" - {reason}" if reason else ""
    message = f"{tag_prefix}{actor} auto-commit @ {ts.isoformat(timespec='seconds')}{reason_suffix}"
    manager.commit(message, actor=actor)
