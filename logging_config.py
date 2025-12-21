"""Repository-wide logging helpers.

This module bridges legacy imports (``import logging_config``) to the
canonical implementation inside ``assistant_hub_gui.assistant_hub`` so
both the Tkinter and React launchers share the same behavior.
"""

from assistant_hub_gui.assistant_hub.logging_config import (
    configure_logging,
    get_logger,
    setup_logger,
)

__all__ = ["configure_logging", "get_logger", "setup_logger"]
