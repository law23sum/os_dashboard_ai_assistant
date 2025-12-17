#!/usr/bin/env python3
"""Unified launcher for the shared React UI (desktop + browser)."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
_VENV_FLAG = "OSDASH_ACTIVE_VENV"
from .autofix_monitor import start_auto_fix_monitor, stop_auto_fix_monitor


def _venv_python() -> Path | None:
    """Return the repo-managed Python interpreter if it exists."""
    if os.name == "nt":
        candidate = REPO_ROOT / "venv" / "Scripts" / "python.exe"
    else:
        candidate = REPO_ROOT / "venv" / "bin" / "python"
    return candidate if candidate.exists() else None


def _venv_ready(python_path: Path) -> bool:
    """Check whether the repo venv has the required backend dependencies."""
    try:
        subprocess.check_call(
            [str(python_path), "-c", "import fastapi, pydantic"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _ensure_repo_python() -> None:
    """Re-exec into the repo's virtualenv to guarantee dependency consistency."""
    target = _venv_python()
    if not target:
        return
    if os.environ.get(_VENV_FLAG) == "1":
        return
    if not _venv_ready(target):
        print(
            "[launcher] Repo virtualenv is missing FastAPI/Pydantic. "
            "Run `venv/bin/python -m pip install -r requirements.txt` to enable the desktop shell."
        )
        return
    try:
        if Path(sys.executable).resolve() == target.resolve():
            return
    except FileNotFoundError:
        pass

    env = os.environ.copy()
    env[_VENV_FLAG] = "1"
    args = [str(target), "-m", "assistant_hub_gui.main", *sys.argv[1:]]
    print(f"[launcher] Switching to repo virtualenv interpreter at {target}")
    os.execvpe(str(target), args, env)


_ensure_repo_python()

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

    monitor = start_auto_fix_monitor()
    try:
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
    finally:
        stop_auto_fix_monitor(monitor)


if __name__ == "__main__":
    raise SystemExit(main())
