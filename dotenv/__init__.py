"""Minimal fallback implementation of the python-dotenv API.

The real python-dotenv package cannot be installed in certain offline
environments. We provide a tiny subset (load_dotenv / dotenv_values) so
modules that unconditionally import ``dotenv`` keep working when the real
package is unavailable. The implementation intentionally focuses on the
behavior used across this repository:

    from dotenv import load_dotenv
    load_dotenv()

It supports simple ``KEY=VALUE`` parsing with optional double/single quotes.
Lines starting with ``#`` are ignored. Existing environment variables are not
overwritten unless ``override=True`` is provided.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, Tuple

__all__ = ["load_dotenv", "dotenv_values"]


def _resolve_path(path: str | Path | None) -> Path:
    """Resolve the path to the .env file."""
    if path is None:
        candidate = Path.cwd() / ".env"
    else:
        candidate = Path(path)
        if candidate.is_dir():
            candidate = candidate / ".env"
    return candidate


def _parse_line(line: str) -> Tuple[str, str] | None:
    """Parse a KEY=VALUE line."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "=" not in stripped:
        return None
    key, raw_value = stripped.split("=", 1)
    key = key.strip()
    value = raw_value.strip()
    if not key:
        return None
    if value and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return key, value


def dotenv_values(path: str | Path | None = None, *, encoding: str = "utf-8") -> Dict[str, str]:
    """Return the variables defined inside the targeted .env file."""
    env_path = _resolve_path(path)
    if not env_path.exists():
        return {}
    values: Dict[str, str] = {}
    try:
        for line in env_path.read_text(encoding=encoding).splitlines():
            parsed = _parse_line(line)
            if not parsed:
                continue
            key, value = parsed
            values[key] = value
    except Exception:
        return {}
    return values


def load_dotenv(
    path: str | Path | None = None,
    *,
    override: bool = False,
    encoding: str = "utf-8",
) -> bool:
    """Populate os.environ with key/value pairs from a .env file."""
    values = dotenv_values(path, encoding=encoding)
    if not values:
        return False
    for key, value in values.items():
        if key in os.environ and not override:
            continue
        os.environ[key] = value
    return True
