#!/usr/bin/env python3
"""Main entry point for OS Dashboard AI Assistant."""

import sys
import os

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

try:
    from assistant_core.ai import AIAssistant
    from assistant_core.core.state import ApplicationState
    from config.logging_config import configure_logging
    from ui.dashboard_app import run_ui
except ImportError as e:
    print(f"Import error: {e}")
    print("Falling back to basic functionality...")
    # Fallback to old structure during transition
    try:
        from assistant_hub.ai import AIAssistant
        from assistant_hub.core.state import ApplicationState
        from assistant_hub.logging_config import configure_logging
        from assistant_hub.gui import run_gui as run_ui
    except ImportError:
        print("Could not import from old structure either. Exiting.")
        sys.exit(1)

def main():
    """Initialize and run the OS Dashboard AI Assistant."""
    # Configure logging
    configure_logging()

    # Initialize application state
    app_state = ApplicationState()

    # Initialize AI assistant
    ai_assistant = AIAssistant(app_state)

    # Start the UI
    run_ui(ai_assistant, app_state)

if __name__ == "__main__":
    main()
