#!/usr/bin/env python3
"""Single entry point for launching the OS Dashboard UI (React web or desktop)."""

from __future__ import annotations

import argparse
import os
import socket
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from assistant_hub_gui.autofix_monitor import (
    start_auto_fix_monitor,
    stop_auto_fix_monitor,
)

REPO_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = REPO_ROOT / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
DEFAULT_API_HOST = "0.0.0.0"  # Bind to all interfaces to allow network access
DEFAULT_API_PORT = 8000
DEFAULT_MODE = "web"
PREFLIGHT_SCRIPT = REPO_ROOT / "scripts" / "run_tests_with_autofix.py"
TEST_MATRIX_SCRIPT = REPO_ROOT / "scripts" / "generate_test_matrix.py"

def _build_uvicorn_cmd() -> list[str]:
    """Build uvicorn command with SSL support if certificates are available."""
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "assistant_hub.api.server:create_app",
        "--factory",
        "--reload",
        "--host",
        DEFAULT_API_HOST,
        "--port",
        str(DEFAULT_API_PORT),
    ]
    # Check for SSL certificates
    cert_dir = REPO_ROOT / "certs"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    if cert_file.exists() and key_file.exists():
        cmd.extend(["--ssl-keyfile", str(key_file)])
        cmd.extend(["--ssl-certfile", str(cert_file)])
        print(f"🔒 SSL certificates found. Starting with HTTPS on https://{DEFAULT_API_HOST}:{DEFAULT_API_PORT}")
    return cmd

UVICORN_CMD = _build_uvicorn_cmd()

ModeRunner = Callable[[], Optional[int]]
ModeDefinition = Tuple[str, str, ModeRunner]


class BackendDependencyError(RuntimeError):
    """Raised when the FastAPI backend cannot start due to missing deps."""


def _refresh_test_matrix() -> None:
    """Regenerate the cross-feature test matrix when source files change."""
    if not TEST_MATRIX_SCRIPT.exists():
        return
    print("📋 Updating test suite matrix...")
    subprocess.check_call([sys.executable, str(TEST_MATRIX_SCRIPT)], cwd=REPO_ROOT)


def _run_preflight_tests() -> None:
    """Execute regression tests before launching any UI surface."""
    skip = os.environ.get("OSDASH_SKIP_PREFLIGHT_TESTS", "").strip().lower()
    if skip in {"1", "true", "yes"}:
        print("🧪 Preflight tests skipped via OSDASH_SKIP_PREFLIGHT_TESTS.")
        return
    _refresh_test_matrix()
    if not PREFLIGHT_SCRIPT.exists():
        return
    print("🧪 Running preflight tests (scripts/run_tests_with_autofix.py)...")
    result = subprocess.call([sys.executable, str(PREFLIGHT_SCRIPT)], cwd=REPO_ROOT)
    if result != 0:
        raise SystemExit(
            "Preflight tests did not pass. Review logs/tests for context before relaunching."
        )


def _launch_master_orchestrator() -> Optional[subprocess.Popen]:
    """Launch the master AI orchestrator in the background."""
    orchestrator_enabled = os.environ.get("OSDASH_ENABLE_ORCHESTRATOR", "").strip().lower()
    if orchestrator_enabled not in {"1", "true", "yes"}:
        return None
    
    orchestrator_script = REPO_ROOT / "os_dashboard_ai_assistant.py"
    if not orchestrator_script.exists():
        return None
    
    print("🤖 Launching Master AI Orchestrator...")
    try:
        process = subprocess.Popen(
            [sys.executable, str(orchestrator_script), "--root", str(REPO_ROOT.parent)],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print(f"  ✓ Master Orchestrator launched (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"  ⚠️  Failed to launch orchestrator: {e}")
        return None


def _import_webview_app():
    """Import the optional pywebview wrapper lazily so dev mode works w/out deps."""
    try:
        from assistant_hub_gui import webview_app  # type: ignore
    except ImportError as exc:  # pragma: no cover - only hit when deps missing
        raise RuntimeError(
            "The desktop/browser preview launcher requires `uvicorn` and FastAPI "
            "dependencies. Run `pip install -r requirements.txt` to enable "
            "start_ui.py --mode web-build/desktop-build."
        ) from exc
    return webview_app


def _ensure_npm() -> str:
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError("npm is not available on PATH. Install Node.js 18+.")
    return npm


def _is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.connect((host, port))
            return True
        except OSError:
            return False


def _wait_for_port(host: str, port: int, timeout: float = 25.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _is_port_open(host, port):
            return
        time.sleep(0.2)
    raise TimeoutError(
        f"Timed out waiting {timeout:.0f}s for {host}:{port} to become available."
    )


def _start_backend() -> Optional[subprocess.Popen]:
    """Spawn the FastAPI server that serves the shared React bundle."""
    if _is_port_open(DEFAULT_API_HOST, DEFAULT_API_PORT):
        print(
            f"ℹ️  API already running on {DEFAULT_API_HOST}:{DEFAULT_API_PORT}. Reusing existing server."
        )
        return None

    try:
        import uvicorn  # noqa: F401  # Local import to detect missing dependency.
    except ImportError as exc:
        raise BackendDependencyError(
            "Python package `uvicorn` is not installed. "
            "Install backend requirements (pip install -r requirements.txt) "
            "or run `npm run dev:web` to preview the UI without APIs."
        ) from exc

    env = os.environ.copy()
    # Rebuild command to ensure SSL settings are current
    cmd = _build_uvicorn_cmd()
    process = subprocess.Popen(cmd, cwd=REPO_ROOT, env=env)
    try:
        _wait_for_port(DEFAULT_API_HOST, DEFAULT_API_PORT)
    except TimeoutError as exc:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        raise RuntimeError(
            f"FastAPI server failed to start: {exc}. Check for stale uvicorn processes."
        )
    return process


def _run_frontend(cmd: list[str], cwd: Path, *, offline: bool = False) -> int:
    env = os.environ.copy()
    env.setdefault("OSDASH_API_HOST", DEFAULT_API_HOST)
    env.setdefault("OSDASH_API_PORT", str(DEFAULT_API_PORT))
    if offline:
        env["OSDASH_API_OFFLINE"] = "1"
    return subprocess.call(cmd, cwd=cwd, env=env)


def _run_with_backend(cmd: list[str], cwd: Path) -> int:
    try:
        backend = _start_backend()
    except BackendDependencyError as exc:
        print(f"⚠️  {exc}")
        print("➡️  Launching frontend without the API. Data will use cached/demo values.")
        return _run_frontend(cmd, cwd, offline=True)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1
    try:
        return _run_frontend(cmd, cwd)
    finally:
        if backend is not None:
            backend.terminate()
            try:
                backend.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend.kill()


def run_react_web_dev() -> int:
    """Run Vite dev server (web browser) + FastAPI backend."""
    npm = _ensure_npm()
    cmd = [npm, "run", "dev:web"]
    return _run_with_backend(cmd, FRONTEND_DIR)


def run_react_desktop_dev() -> int:
    """Run Electron dev shell (desktop app) + FastAPI backend."""
    npm = _ensure_npm()
    cmd = [npm, "run", "dev:desktop"]
    return _run_with_backend(cmd, FRONTEND_DIR)


def run_web_build() -> int:
    """Serve the production React build for browser previews."""
    if not FRONTEND_DIST.exists():
        print("⚠️  frontend/dist not found. Run `cd frontend && npm run build` first.")
        return 1
    webview_app = _import_webview_app()
    webview_app.launch_browser(
        host="127.0.0.1", port=8800, dist_path=str(FRONTEND_DIST)
    )
    return 0


def run_desktop_build() -> int:
    """Serve the production React build in a desktop shell."""
    if not FRONTEND_DIST.exists():
        print("⚠️  frontend/dist not found. Run `cd frontend && npm run build` first.")
        return 1
    webview_app = _import_webview_app()
    webview_app.launch_desktop(
        host="127.0.0.1", port=8800, dist_path=str(FRONTEND_DIST)
    )
    return 0


def run_legacy_tkinter() -> int:
    """Run the legacy Tkinter interface."""
    print("Starting legacy Tkinter interface...")
    # Ensure root is in path
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    
    try:
        from assistant_hub_gui.assistant_hub.gui import run_gui
        run_gui()
        return 0
    except ImportError:
        # Fallback if the package structure is different
        try:
            sys.path.insert(0, str(REPO_ROOT / "assistant_hub_gui"))
            from assistant_hub.gui import run_gui
            run_gui()
            return 0
        except Exception as e:
            print(f"Error running legacy GUI: {e}")
            return 1
    except Exception as e:
        print(f"Error running legacy GUI: {e}")
        return 1


MODE_DEFINITIONS: Tuple[ModeDefinition, ...] = (
    ("web", "React · Web Dev (FastAPI + Vite)", run_react_web_dev),
    ("desktop", "React · Desktop Dev (FastAPI + Electron)", run_react_desktop_dev),
    ("web-build", "Serve built React in browser", run_web_build),
    ("desktop-build", "Serve built React in desktop shell", run_desktop_build),
)
MODE_LOOKUP: Dict[str, Tuple[str, ModeRunner]] = {
    name: (label, fn) for name, label, fn in MODE_DEFINITIONS
}
MODE_ALIASES = {
    "browser": "web",
    "web-dev": "web",
    "react-web": "web",
    "desktop-dev": "desktop",
    "electron": "desktop",
    "desktop-app": "desktop",
    "browser-build": "web-build",
    "desktop-build": "desktop-build",
    "pywebview": "desktop-build",
}
for idx, (name, _, _) in enumerate(MODE_DEFINITIONS, start=1):
    MODE_ALIASES[str(idx)] = name


def _normalize_mode(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    key = value.strip().lower()
    if not key:
        return None
    if key in MODE_LOOKUP:
        return key
    if key in MODE_ALIASES:
        return MODE_ALIASES[key]
    simplified = key.rstrip(").: ")
    if simplified in MODE_LOOKUP:
        return simplified
    if simplified in MODE_ALIASES:
        return MODE_ALIASES[simplified]
    digits = "".join(ch for ch in key if ch.isdigit())
    if digits:
        alias = MODE_ALIASES.get(digits)
        if alias:
            return alias
    return None


def _prompt_mode() -> str:
    """Prompt user to select desktop or web mode in dev local mode."""
    if not sys.stdin.isatty():
        return DEFAULT_MODE

    print("\n" + "=" * 70)
    print("  🚀 OS Dashboard AI Assistant — Unified Launcher")
    print("=" * 70)
    print("\n📋 Available Launch Modes:\n")
    max_choice = len(MODE_DEFINITIONS)
    for idx, (name, label, _) in enumerate(MODE_DEFINITIONS, start=1):
        default_marker = " ⭐ (default)" if name == DEFAULT_MODE else ""
        icon = "🌐" if "Web" in label else "🖥️" if "Desktop" in label else "📦"
        print(f"  {icon} {idx}) {label}{default_marker}")
    print("\n" + "-" * 70)
    print("💡 Tip: Set OSDASH_UI_MODE or DEV_MODE env var to skip this prompt")
    print("-" * 70)
    choice = input(f"\n👉 Enter your choice (1-{max_choice} or press Enter for default): ").strip()
    normalized = _normalize_mode(choice)
    if normalized:
        return normalized
    if not choice:
        print(f"✅ Using default mode: {DEFAULT_MODE}")
        return DEFAULT_MODE
    print(f"⚠️  Invalid selection, defaulting to {DEFAULT_MODE} mode.")
    return DEFAULT_MODE


def _resolve_mode(cli_mode: Optional[str]) -> str:
    for candidate in (
        cli_mode,
        os.environ.get("OSDASH_UI_MODE"),
        os.environ.get("DEV_MODE"),
    ):
        normalized = _normalize_mode(candidate)
        if normalized:
            return normalized
    return _prompt_mode()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="🚀 Unified launcher for the React web + desktop surfaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_ui.py                    # Interactive mode selection
  python start_ui.py --mode web         # Launch web dev server
  python start_ui.py --mode desktop     # Launch desktop app
  DEV_MODE=web python start_ui.py       # Use environment variable
  
Master Orchestrator:
  OSDASH_ENABLE_ORCHESTRATOR=1 python start_ui.py    # Enable master orchestrator
  
For more information, see README.md and DEPLOYMENT.md
        """
    )
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_LOOKUP.keys()),
        help="Run without prompting (web, desktop, web-build, desktop-build)",
    )
    parser.add_argument(
        "--enable-orchestrator",
        action="store_true",
        help="Enable the master AI orchestrator for multi-project management",
    )
    args = parser.parse_args()

    _run_preflight_tests()
    
    # Launch master orchestrator if enabled
    orchestrator_process = None
    if args.enable_orchestrator:
        os.environ["OSDASH_ENABLE_ORCHESTRATOR"] = "1"
    orchestrator_process = _launch_master_orchestrator()
    
    monitor = start_auto_fix_monitor()
    try:
        mode = _resolve_mode(args.mode)
        label, runner = MODE_LOOKUP[mode]
        print(f"\n🚀 Launching {label} ({mode})...")
        # Check if SSL is enabled
        cert_dir = REPO_ROOT / "certs"
        cert_file = cert_dir / "cert.pem"
        key_file = cert_dir / "key.pem"
        protocol = "https" if cert_file.exists() and key_file.exists() else "http"
        print(f"📍 API Server: {protocol}://{DEFAULT_API_HOST}:{DEFAULT_API_PORT}")
        if mode in ["web", "web-build"]:
            print(
                "🌐 Web Interface: http://localhost:5173"
                if mode == "web"
                else "🌐 Serving from: frontend/dist/"
            )
        if orchestrator_process:
            print(f"🤖 Master Orchestrator: Running (PID: {orchestrator_process.pid})")
        print()
        result = runner()
        return int(result or 0)
    finally:
        stop_auto_fix_monitor(monitor)
        if orchestrator_process:
            print("\n🛑 Stopping Master Orchestrator...")
            try:
                orchestrator_process.terminate()
                orchestrator_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                orchestrator_process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
