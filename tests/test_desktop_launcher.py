"""Regression tests for the Electron dev launcher."""
from pathlib import Path

DEV_SCRIPT = Path("frontend/scripts/dev-desktop.js")


def test_dev_desktop_enforces_vite_port_and_preload() -> None:
    contents = DEV_SCRIPT.read_text(encoding="utf-8")
    assert "function waitForPort" in contents, "dev-desktop.js must wait for Vite before spawning Electron"
    assert "--strictPort" in contents, "Vite must crash if the dynamically chosen port is hijacked"
    assert "VITE_DEV_SERVER_URL" in contents, "Electron must point to the exact Vite origin to avoid blank screens"
