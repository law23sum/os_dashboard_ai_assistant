#!/usr/bin/env python3
"""
Single Entry Point - OS Dashboard AI Assistant

Launch the React-based UI for web or desktop, or the legacy Tkinter interface.
Both surfaces share the same backend and writer workspace state.

Usage:
    python run.py                    # Interactive mode selection
    python run.py --mode web         # Launch web dev server
    python run.py --mode desktop     # Launch Electron desktop app
    python run.py --mode web-build   # Serve production web build
    python run.py --mode desktop-build  # Serve production in pywebview
    python run.py --legacy           # Launch legacy Tkinter GUI

Environment Variables:
    OSDASH_UI_MODE    - Pre-select mode (web, desktop, web-build, desktop-build)
    DEV_MODE          - Alternative to OSDASH_UI_MODE

Build Commands (from frontend/):
    npm run build:web              # Build for web deployment
    npm run build:desktop:linux    # Build Linux executables
    npm run build:desktop:windows  # Build Windows executables
    npm run build:desktop:mac      # Build macOS executables
    npm run build:all              # Build all targets
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from start_ui import MODE_LOOKUP, main as start_ui_main  # noqa: E402
except ImportError as e:
    print(f"Error: Could not import start_ui module: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)


BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    OS Dashboard AI Assistant                                  ║
║                    Unified Launcher v2.0                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  A single codebase for web browser AND desktop app deployment.               ║
║  Features migrated from Tkinter with modern React/TypeScript UI.             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def _launch_legacy_gui() -> int:
    """Launch the legacy Tkinter GUI for backward compatibility."""
    try:
        from assistant_hub_gui.main import main as tk_main
        tk_main()
        return 0
    except ImportError as e:
        print(f"Error: Could not launch legacy GUI: {e}")
        print("The Tkinter interface requires ttkbootstrap and other dependencies.")
        return 1


def _print_modes() -> None:
    """Print available modes."""
    print("\nAvailable modes:")
    for mode, (label, _) in MODE_LOOKUP.items():
        print(f"  {mode:15} - {label}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch the OS Dashboard React UI (web/desktop) or the legacy Tk interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Interactive mode selection
  python run.py --mode web         # Launch web browser dev server
  python run.py --mode desktop     # Launch Electron desktop app
  python run.py --legacy           # Launch legacy Tkinter GUI
  
Build targets (run from frontend/):
  npm run build:desktop:linux      # Linux (AppImage, DEB, RPM)
  npm run build:desktop:windows    # Windows (NSIS installer, Portable)
  npm run build:desktop:mac        # macOS (DMG, ZIP)
        """,
    )
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_LOOKUP.keys()),
        help="Launch React UI in a specific mode (web, desktop, web-build, desktop-build)",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Launch the legacy Tkinter interface instead of the React UI",
    )
    parser.add_argument(
        "--list-modes",
        action="store_true",
        help="List all available modes and exit",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress banner output",
    )
    args = parser.parse_args()

    # Show banner unless quiet mode
    if not args.quiet and not args.list_modes:
        print(BANNER)

    # List modes and exit
    if args.list_modes:
        _print_modes()
        return 0

    # Launch legacy Tkinter GUI
    if args.legacy:
        print("→ Launching legacy Tkinter UI")
        print("  Note: The React UI is now the canonical desktop surface.")
        print("  Use --mode desktop for the modern experience.\n")
        return _launch_legacy_gui()

    # Set mode from CLI argument
    if args.mode:
        os.environ["OSDASH_UI_MODE"] = args.mode

    return start_ui_main()


if __name__ == "__main__":
    raise SystemExit(main())
