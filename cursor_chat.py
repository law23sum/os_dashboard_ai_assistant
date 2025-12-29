#!/usr/bin/env python3
"""
Interactive terminal chat with AI agents.

This script provides an interactive chat interface where you can select
which AI agent to use and have conversations with them.

Usage:
    python cursor_chat.py
    python cursor_chat.py --agent Aria
    python cursor_chat.py --help
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import directly from the chat module to avoid package import issues
import importlib.util
chat_module_path = project_root / "ui" / "terminal" / "commands" / "chat.py"
spec = importlib.util.spec_from_file_location("chat_command", chat_module_path)
chat_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chat_module)
handle_chat_command = chat_module.handle_chat_command

import argparse


def main():
    """Main entry point for cursor chat."""
    parser = argparse.ArgumentParser(
        prog="cursor_chat",
        description="Interactive terminal chat with AI agents",
    )
    parser.add_argument(
        "--agent",
        choices=["AIC", "Aria", "Sora", "Chris"],
        help="AI agent to use (default: interactive selection)",
    )
    parser.add_argument(
        "--clear-history",
        action="store_true",
        help="Start with empty conversation history",
    )
    parser.add_argument(
        "--clear-on-switch",
        action="store_true",
        help="Clear history when switching agents",
    )
    parser.add_argument(
        "--enable-shell",
        action="store_true",
        default=True,
        help="Allow AI to execute shell commands (default: True)",
    )
    parser.add_argument(
        "--no-shell",
        dest="enable_shell",
        action="store_false",
        help="Disable shell command execution",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose error messages",
    )
    
    args = parser.parse_args()
    sys.exit(handle_chat_command(args))


if __name__ == "__main__":
    main()







