#!/usr/bin/env python3
"""Unified launcher for the shared React UI (desktop + browser)."""
from __future__ import annotations

import argparse
import sys

from assistant_hub_gui.webview_app import launch_browser, launch_desktop


def _prompt_mode() -> str:
    if not sys.stdin.isatty():
        return "browser"

    print("Select UI surface:")
    print("  1) Desktop app (pywebview shell)")
    print("  2) Web browser")
    choice = input("Mode [1/2]: ").strip() or "1"
    mapping = {"1": "desktop", "desktop": "desktop", "2": "browser", "browser": "browser"}
    return mapping.get(choice.lower(), "desktop")


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch the shared React UI")
    parser.add_argument(
        "--mode",
        choices=("desktop", "browser"),
        default=None,
        help="Desktop launches the pywebview shell, browser opens the default browser",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for the FastAPI server")
    parser.add_argument("--port", type=int, default=8800, help="Port for the FastAPI server")
    parser.add_argument(
        "--dist",
        type=str,
        default=None,
        help="Optional path to the built React assets (defaults to frontend/dist)",
    )
    args = parser.parse_args()

    mode = args.mode or _prompt_mode()
    try:
        if mode == "desktop":
            launch_desktop(args.host, args.port, args.dist)
        else:
            launch_browser(args.host, args.port, args.dist)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
