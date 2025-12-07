<<<<<<< HEAD
"""Git management helpers for background versioning.

These helpers keep AI-driven modifications auditable by ensuring files are
added and committed with consistent metadata. They intentionally avoid
heavy dependencies so they can run in constrained environments.
=======
"""Git versioning utilities for automated AI changes.

This module provides a thin wrapper around git commands so that any
integration or workflow that mutates files can stage and commit those
changes with minimal boilerplate. It is intentionally simple and uses
``subprocess`` instead of heavier dependencies to keep the assistant
portable.
>>>>>>> develop
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
<<<<<<< HEAD
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from .. import config


@dataclass
class CommitMetadata:
    """Metadata used when creating commits."""

    actor: str = "AIC"
    reason: str = ""
    tag: str = ""

    def to_message(self) -> str:
        timestamp = datetime.now().isoformat(timespec="seconds")
        tag_prefix = f"[{self.tag}] " if self.tag else ""
        reason_suffix = f" - {self.reason}" if self.reason else ""
        return f"{tag_prefix}{self.actor} auto-commit @ {timestamp}{reason_suffix}"


class GitManager:
    """Lightweight wrapper around git commands.

    This class intentionally keeps the interface small. It supports
    initializing a repository, staging files, and writing commits with
    actor metadata. All commands run relative to the configured repo
    root so callers can provide absolute or relative paths.
    """

    def __init__(self, repo_root: Path | str | None = None):
        self.repo_root = Path(repo_root or config.PROJECT_ROOT).resolve()

    # --- internal helpers -------------------------------------------------
    def _run(self, args: Sequence[str], *, env: Optional[dict] = None) -> None:
        subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            check=True,
=======
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
>>>>>>> develop
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

<<<<<<< HEAD
    def _ensure_repo(self) -> None:
        if not (self.repo_root / ".git").exists():
            self._run(["init"])

    # --- public API -------------------------------------------------------
    def add(self, paths: Iterable[Path | str]) -> None:
        """Stage paths relative to the repository root."""

        normalized: List[str] = []
        for path in paths:
            abs_path = Path(path).resolve()
            if not abs_path.exists():
                continue
            normalized.append(os.path.relpath(abs_path, self.repo_root))
        if normalized:
            self._run(["add", *normalized])

    def commit(self, metadata: CommitMetadata) -> None:
        """Create a commit using the provided metadata.

        If there is nothing to commit, git returns a non-zero status which we
        intentionally ignore to keep the flow non-blocking for callers.
        """

        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": metadata.actor,
                "GIT_COMMITTER_NAME": metadata.actor,
                "GIT_AUTHOR_EMAIL": env.get("GIT_AUTHOR_EMAIL", "ai@local"),
                "GIT_COMMITTER_EMAIL": env.get("GIT_COMMITTER_EMAIL", "ai@local"),
            }
        )
        try:
            self._run(["commit", "-m", metadata.to_message()], env=env)
        except subprocess.CalledProcessError:
            # Nothing to commit; callers do not need to treat this as fatal.
            pass

    def add_and_commit(self, paths: Iterable[Path | str], metadata: CommitMetadata) -> None:
        """Stage and commit provided paths."""

        self._ensure_repo()
        self.add(paths)
        self.commit(metadata)


_default_manager: GitManager | None = None


def get_git_manager() -> GitManager:
    """Return a shared GitManager instance."""

    global _default_manager
    if _default_manager is None:
        _default_manager = GitManager()
    return _default_manager


def auto_commit(
    paths: Iterable[Path | str],
    *,
    actor: str = "AIC",
    reason: str = "",
    tag: str = "",
) -> None:
    """Convenience wrapper to stage and commit paths with metadata."""

    manager = get_git_manager()
    metadata = CommitMetadata(actor=actor, reason=reason, tag=tag)
    manager.add_and_commit(paths, metadata)
=======
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
>>>>>>> develop
