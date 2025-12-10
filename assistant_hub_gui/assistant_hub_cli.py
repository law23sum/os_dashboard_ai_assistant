#!/usr/bin/env python3
"""CLI entrypoint for OS Dashboard AI Assistant."""

from assistant_hub.ui.terminal.cli import main
from assistant_hub.logging_config import configure_logging

if __name__ == "__main__":
    configure_logging()
    exit(main())
