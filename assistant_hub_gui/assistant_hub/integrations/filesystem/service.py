"""File-system integration helpers for the assistant hub."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

TRACKED_EXTENSIONS = {
    ".py",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".xlsx",
    ".csv",
    ".html",
}


def discover_files(root: Path, extensions: Iterable[str] = TRACKED_EXTENSIONS) -> List[Path]:
    """Return a list of files under root that match the provided extensions."""
    matches: List[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in extensions:
            matches.append(path)
    return matches


class FileSystemService:
    """Utility helpers for discovering and registering files."""

    def __init__(self, root: str):
        self.root = Path(root)

    def discover(self, patterns: Iterable[str]) -> List[str]:
        matches: List[str] = []
        for pattern in patterns:
            matches.extend(str(path) for path in self.root.glob(pattern))
        return matches

    def ensure_folder(self, relative_path: str) -> Path:
        folder = self.root / relative_path
        folder.mkdir(parents=True, exist_ok=True)
        return folder
