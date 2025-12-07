#!/usr/bin/env python3
"""GUI entrypoint for OS Dashboard AI Assistant."""

import sys
import os

# Add the assistant_hub_gui directory to the path so imports work
# This allows both "from assistant_hub_gui.assistant_hub..." and "from assistant_hub..." to work
_assistant_hub_gui_dir = os.path.dirname(os.path.abspath(__file__))
if _assistant_hub_gui_dir not in sys.path:
    sys.path.insert(0, _assistant_hub_gui_dir)

# Also add parent directory for scripts that use "from assistant_hub..."
_parent_dir = os.path.dirname(_assistant_hub_gui_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from assistant_hub_gui.assistant_hub.gui import run_gui
from assistant_hub_gui.assistant_hub.logging_config import configure_logging

if __name__ == "__main__":
    configure_logging()
    run_gui()
