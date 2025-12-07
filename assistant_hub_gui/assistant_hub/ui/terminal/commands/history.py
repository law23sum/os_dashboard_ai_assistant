"""History CLI commands - shows git commit history and agent runs."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

from ....config import DATA_DIR
from ....versioning import get_git_manager


def handle_history_command(args, conn: sqlite3.Connection) -> int:
    """Handle History CLI commands."""
    manager = get_git_manager()
    repo_root = Path(manager.repo_root)

    # Build git log command
    cmd = ["git", "log", "--oneline", f"--max-count={args.limit}"]

    if args.agent:
        # Filter by author (agent name)
        cmd.extend(["--author", args.agent])

    if args.tag:
        # Filter by commit message containing tag
        cmd.extend(["--grep", f"[{args.tag}]"])

    try:
        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0 and result.stdout:
            print("Recent actions:")
            print(result.stdout)
        else:
            print("No history found.")
        return 0
    except Exception as e:
        print(f"Error reading history: {e}", file=sys.stderr)
        return 1



