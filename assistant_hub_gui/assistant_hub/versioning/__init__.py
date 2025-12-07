"""Version control helpers for tracking AI-driven changes."""

from .git_manager import GitManager, get_git_manager, git_autocommit, init_git_manager
from .git_async import enqueue_git_commit, shutdown_worker, start_git_worker

__all__ = [
    "GitManager",
    "get_git_manager",
    "git_autocommit",
    "init_git_manager",
    "enqueue_git_commit",
    "shutdown_worker",
    "start_git_worker",
]
