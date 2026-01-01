#!/usr/bin/env python3
"""
CLI Entry Point for OS Dashboard AI Assistant
Usage:
    python3 cli.py chat
    python3 cli.py chat --agent Aria
"""
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.terminal.cli import main
except ImportError as e:
    print(f"Error importing CLI module: {e}")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())



