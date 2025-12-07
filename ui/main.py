#!/usr/bin/env python3
"""UI entrypoint for OS Dashboard AI Assistant."""

import sys
import os

# Add project root to path for proper imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dashboard_app import run_ui
from config.logging_config import configure_logging

if __name__ == "__main__":
    configure_logging()
    run_ui()
