#!/usr/bin/env python3
"""Compatibility shim for launching the legacy assistant GUI.

The canonical way to start the application is:

    python -m assistant_hub_gui.main

This wrapper simply forwards to that module so scripts that still call
``python run.py`` continue to work while we consolidate on a single entry point.
"""

from __future__ import annotations

from assistant_hub_gui.main import main as _launch_main


def main() -> int:
    print(
        "`python run.py` is deprecated; use `python -m assistant_hub_gui.main` instead."
    )
    _launch_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
