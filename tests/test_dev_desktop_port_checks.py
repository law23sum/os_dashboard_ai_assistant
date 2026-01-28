from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_dev_desktop_utils_node_suite() -> None:
    """Run the Node-based desktop utility tests to guard the port scanner."""
    result = subprocess.run(
        ["node", "--test", "frontend/scripts/__tests__/dev-desktop-utils.test.mjs"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        raise AssertionError(
            "Node desktop utility tests failed:\n"
            f"STDOUT:\n{stdout or '<empty>'}\n\nSTDERR:\n{stderr or '<empty>'}"
        )
