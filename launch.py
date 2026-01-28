#!/usr/bin/env python3
"""Deprecated shim. Use start_ui.py instead."""

from __future__ import annotations

from start_ui import main as start_ui_main


def main() -> int:
    print("launch.py is deprecated — forwarding to ./start_ui.py\n")
    return start_ui_main()


if __name__ == "__main__":
    raise SystemExit(main())
