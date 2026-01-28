"""Compatibility shim for legacy imports.

All core API server functionality now lives in
``assistant_hub_gui.assistant_hub.core.api_server`` so that both the desktop
launcher and the standalone backend reuse the exact same FastAPI application.
"""

from __future__ import annotations

from assistant_hub_gui.assistant_hub.core.api_server import *  # noqa: F401,F403
