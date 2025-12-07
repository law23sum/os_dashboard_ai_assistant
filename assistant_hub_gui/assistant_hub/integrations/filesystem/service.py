"""Generic filesystem helpers used by integrations."""
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
