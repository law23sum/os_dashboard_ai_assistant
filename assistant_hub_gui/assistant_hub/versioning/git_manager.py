"""Git management helpers for background versioning.

These helpers keep AI-driven modifications auditable by ensuring files are
added and committed with consistent metadata. They intentionally avoid
heavy dependencies so they can run in constrained environments.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
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
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

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
