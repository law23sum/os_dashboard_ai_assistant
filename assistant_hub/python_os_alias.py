"""Expose the ``python_os`` alias as a thin wrapper around the active interpreter."""

from __future__ import annotations

import subprocess
import sys
from typing import List


def main(argv: List[str] | None = None) -> int:
    """Execute the requested command with the current Python interpreter."""

    if argv is None:
        argv = sys.argv[1:]

    # Auto-add -f flag to compileall for better visibility
    if len(argv) >= 2 and argv[0] == "-m" and argv[1] == "compileall":
        if "-f" not in argv and "-q" not in argv:
            # Insert -f after compileall for verbose output
            argv = argv[:2] + ["-f"] + argv[2:]

    cmd = [sys.executable, *argv]

    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("python_os: underlying python interpreter not found", file=sys.stderr)
        return 127


if __name__ == "__main__":  # pragma: no cover - thin wrapper
    raise SystemExit(main())
