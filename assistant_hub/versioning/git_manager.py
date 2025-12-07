"""Git utilities for automated commits."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable, Optional


class GitManager:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path.cwd()

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=self.repo_root, check=True, capture_output=True, text=True)

    def init_repo(self) -> None:
        self.run("init")

    def add_and_commit(self, message: str, paths: Optional[Iterable[str]] = None) -> None:
        target_paths = list(paths) if paths else ["."]
        self.run("add", *target_paths)
        self.run("commit", "-m", message)
