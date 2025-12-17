"""Compatibility shim re-exporting the canonical Assistant Hub database helpers.

This module previously contained a fork of the Tkinter database layer. To avoid
divergent schemas across the desktop and web surfaces, we now defer entirely to
``assistant_hub_gui.assistant_hub.db`` so every caller—legacy or new—shares the
same models, helpers, and SQLite file.
"""

from __future__ import annotations

from assistant_hub_gui.assistant_hub import db as _canonical  # noqa: F401
from assistant_hub_gui.assistant_hub.db import *  # type: ignore F401,F403

__all__ = (
    _canonical.__all__
    if hasattr(_canonical, "__all__")
    else [name for name in globals() if not name.startswith("_")]
)

