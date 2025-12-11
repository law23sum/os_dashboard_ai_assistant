"""Shared theme tokens for Tkinter, FastAPI, and React."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Tuple

THEME_FILE = (
    Path(__file__).resolve().parents[1] / "frontend" / "src" / "theme" / "tokens.json"
)
DEFAULT_THEME = "dark"


def _load_theme_catalog() -> Dict[str, Dict[str, Any]]:
    if not THEME_FILE.exists():
        raise FileNotFoundError(
            f"Theme catalog not found at {THEME_FILE}. "
            "Ensure the frontend assets are checked out."
        )
    with THEME_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def theme_catalog() -> Dict[str, Dict[str, Any]]:
    """Load and cache the full theme catalog."""
    return _load_theme_catalog()


def list_available_themes() -> Tuple[str, ...]:
    """Return the available theme names."""
    return tuple(theme_catalog().keys())


def _default_theme_name() -> str:
    catalog = theme_catalog()
    if DEFAULT_THEME in catalog:
        return DEFAULT_THEME
    if "plain" in catalog:
        return "plain"
    return next(iter(catalog.keys()))


def get_theme_definition(name: str | None = None) -> Tuple[str, Dict[str, Any]]:
    """Return the canonical theme definition (name + token map)."""
    catalog = theme_catalog()
    key = (name or "").strip().lower()
    if key in catalog:
        return key, catalog[key]
    default_name = _default_theme_name()
    return default_name, catalog[default_name]


def get_color_tokens(name: str | None = None) -> Dict[str, str]:
    """Return flattened color tokens for convenient consumption."""
    _, definition = get_theme_definition(name)
    tokens = {
        key: value
        for key, value in definition.get("tokens", {}).items()
        if isinstance(value, str)
    }
    return tokens


def get_gradients(name: str | None = None) -> Dict[str, str]:
    """Return gradient definitions for the requested theme."""
    _, definition = get_theme_definition(name)
    gradients = definition.get("gradients", {}) or {}
    return {key: value for key, value in gradients.items() if isinstance(value, str)}
