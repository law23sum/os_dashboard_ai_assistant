#!/usr/bin/env python3
"""Focus Resource Manager.

Purpose:
    Light helper that boosts CPU priority for actively-used IDEs
    and relaxes background-heavy apps so they yield memory/CPU.

What it does:
    - Detect frontmost macOS app via AppleScript
    - Maintain a timestamp ledger (~/OS_Dashboard_AI_Assistant/logs/focus_state.json)
      tracking when each monitored app was last focused
    - Raise scheduling priority (lower nice value) for prioritized apps
      and lower priority for deprioritized apps

Limitations:
    - Cannot force memory reallocation; relies on OS VM
    - Requires psutil (`python3 -m pip install --user psutil`)
    - User must run it periodically (cron/launchd) or with --loop
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import psutil

OPS_ROOT = Path.home() / "OS_Dashboard_AI_Assistant"
LOG_DIR = OPS_ROOT / "logs"
STATE_FILE = LOG_DIR / "focus_state.json"

PRIORITY_APPS = [
    "PyCharm",
    "IntelliJ IDEA",
    "Code",
    "Visual Studio Code",
    "Xcode",
    "DataGrip",
]

DEPRIORITIZE_APPS = [
    "Safari",
    "Google Chrome",
    "Firefox",
    "Spotify",
    "Slack",
    "Discord",
]

PRIORITY_NICE = 0
BACKGROUND_NICE = 10


def frontmost_app() -> str | None:
    script = 'tell application "System Events" to get name of first process whose frontmost is true'
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None
    return result.stdout.strip() or None


def iter_processes() -> Iterable[psutil.Process]:
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        yield proc


def _pgrep(name: str) -> List[int]:
    try:
        result = subprocess.run(
            ["pgrep", "-x", name],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode not in (0, 1):
            return []
        pids = [int(line) for line in result.stdout.splitlines() if line.strip().isdigit()]
        return pids
    except FileNotFoundError:
        return []


def set_priority(proc: psutil.Process, nice_value: int) -> bool:
    try:
        proc.nice(nice_value)
        return True
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return False


def boost_apps(app_names: List[str], nice_value: int) -> List[str]:
    adjusted = []
    lower_names = {name.lower() for name in app_names}
    try:
        for proc in iter_processes():
            name = (proc.info.get("name") or "").lower()
            if not name:
                continue
            if any(app in name for app in lower_names):
                if set_priority(proc, nice_value):
                    adjusted.append(proc.info.get("name", str(proc.pid)))
    except (psutil.AccessDenied, PermissionError):
        # Fallback: use pgrep per app
        for app in app_names:
            for pid in _pgrep(app):
                try:
                    proc = psutil.Process(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                if set_priority(proc, nice_value):
                    adjusted.append(f"{proc.name()}({pid})")
    return adjusted


def load_state() -> Dict[str, str]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(state: Dict[str, str]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def update_state(active_app: str | None) -> None:
    state = load_state()
    if active_app:
        state[active_app] = datetime.utcnow().isoformat() + "Z"
    save_state(state)


def run_once(verbose: bool = False) -> str:
    active = frontmost_app()
    update_state(active)
    boosted = []
    deprioritized = []
    if active:
        boosted = boost_apps([active], PRIORITY_NICE)
    if DEPRIORITIZE_APPS:
        deprioritized = boost_apps(DEPRIORITIZE_APPS, BACKGROUND_NICE)
    summary = (
        f"FocusManager active='{active}' boosted={len(boosted)} deprioritized={len(deprioritized)}"
    )
    if verbose:
        print(summary)
    return summary


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Adjust process priorities based on active app.")
    parser.add_argument("--loop", action="store_true", help="Run continuously (5s interval).")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between iterations in loop mode.")
    parser.add_argument("--verbose", action="store_true", help="Print adjustments each iteration.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.loop:
        try:
            while True:
                run_once(verbose=args.verbose)
                time.sleep(max(1, args.interval))
        except KeyboardInterrupt:
            return 0
    else:
        run_once(verbose=True or args.verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
