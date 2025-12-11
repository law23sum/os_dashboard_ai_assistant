#!/usr/bin/env python3
"""Deprecated shim that proxies to start_ui.py.

Historically this script offered a separate launcher for the React dev server.
To reduce duplication we now expose a single entry point in `start_ui.py`.
"""

from start_ui import main as start_main


def main() -> int:
    print("scripts/run_ui_dev.py is deprecated — redirecting to ./start_ui.py\n")
    return start_main()


if __name__ == "__main__":
    raise SystemExit(main())
