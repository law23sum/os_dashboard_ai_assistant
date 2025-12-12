#!/usr/bin/env python3
"""Run regression tests and hand failures to the AI auto-fix loop."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_LOG_DIR = REPO_ROOT / "logs" / "tests"
TEST_LOG_DIR.mkdir(parents=True, exist_ok=True)

PYTHON = os.environ.get("PYTHON", sys.executable)

TEST_COMMANDS: List[Dict[str, object]] = [
    {
        "name": "office-api",
        "cmd": [PYTHON, "tests/test_office_api.py"],
        "cwd": REPO_ROOT,
        "description": "FastAPI office endpoints + AI router wiring",
    },
    {
        "name": "office-router",
        "cmd": [PYTHON, "tests/test_office_router.py"],
        "cwd": REPO_ROOT,
        "description": "In-process Office realtime router smoke tests",
    },
]


def _timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _run_command(name: str, cmd: List[str], cwd: Path) -> Tuple[int, str]:
    display = shlex.join(cmd)
    log_path = TEST_LOG_DIR / f"{name}.log"
    print(f"▶️  Running {name}: {display} (cwd={cwd})")
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env={**os.environ, "CI": os.environ.get("CI", "1")},
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{_timestamp()}] $ {display}\n")
        handle.write(proc.stdout)
        if proc.returncode != 0:
            handle.write(
                f"\n[{_timestamp()}] ERROR: {name} exited with code {proc.returncode}\n"
            )
        handle.write("\n" + "-" * 80 + "\n\n")
    if proc.returncode == 0:
        print(f"✅ {name} passed")
    else:
        print(f"❌ {name} failed (see {log_path})")
    return proc.returncode, str(log_path)


def _run_ai_autofix(log_dir: Path, attempts: int, test_cmd: str) -> int:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "ai_auto_fix.py"),
        "--logs-only",
        "--log-dir",
        str(log_dir),
        "--disable-binary-monitor",
        "--no-daemon",
        "--verify-seconds",
        "20",
        "--max-attempts",
        str(attempts),
    ]
    if test_cmd:
        cmd.extend(["--test", test_cmd])
    print(f"🤖 Launching AI auto-fix: {shlex.join(cmd)}")
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    if proc.returncode == 0:
        print("🤖 Auto-fix reported success")
    else:
        print("⚠️  Auto-fix failed. Inspect logs/tests for context.")
    return proc.returncode


def run_tests(max_attempts: int) -> int:
    for test in TEST_COMMANDS:
        name = str(test["name"])
        cmd = list(test["cmd"])  # type: ignore[arg-type]
        cwd = Path(test["cwd"])  # type: ignore[arg-type]
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            code, _ = _run_command(name, cmd, cwd)
            if code == 0:
                break
            print(f"Attempt {attempt}/{max_attempts} for {name} failed. Triggering AI auto-fix...")
            autofix_code = _run_ai_autofix(TEST_LOG_DIR, 1, shlex.join(cmd))
            if autofix_code != 0:
                print(
                    "🚨 Auto-fix could not resolve the issue. Please review the logs/tests directory "
                    "and rerun scripts/run_tests_with_autofix.py after manual intervention."
                )
                return autofix_code
        else:
            print(
                f"❌ Exhausted {max_attempts} attempts for {name}. See logs/tests/{name}.log "
                "for troubleshooting steps."
            )
            return 1
    print("🎉 All tests/builds passed.")
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run regression tests and hand failures to the AI auto-fix loop.",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=3,
        help="Maximum attempts per test before requiring manual intervention.",
    )
    args = parser.parse_args(argv)
    return run_tests(max_attempts=max(1, args.attempts))


if __name__ == "__main__":
    raise SystemExit(main())
