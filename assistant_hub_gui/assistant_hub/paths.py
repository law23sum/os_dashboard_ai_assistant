"""Centralized filesystem paths for the Assistant Hub GUI."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTATION_ROOT = REPO_ROOT / "documentation"


def get_documentation_path(relative_path: str) -> Path:
    """Resolve files inside the documentation directory with graceful fallbacks."""

    target = DOCUMENTATION_ROOT / relative_path
    if target.exists():
        return target
    fallback = DOCUMENTATION_ROOT / Path(relative_path).name
    return fallback if fallback.exists() else DOCUMENTATION_ROOT
