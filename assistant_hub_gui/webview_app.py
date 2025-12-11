"""Hybrid launcher that serves the React UI for both desktop (pywebview) and browser."""
from __future__ import annotations

import argparse
import copy
import logging
import os
import platform
import socket
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional, Tuple

import uvicorn
from uvicorn.config import LOGGING_CONFIG as UVICORN_LOGGING_CONFIG

from assistant_hub.api.server import create_app

REPO_ROOT = Path(__file__).resolve().parents[1]
# Prefer the new shared React bundle under frontend/dist, fall back to the legacy ui/web build.
DEFAULT_DIST = REPO_ROOT / "frontend" / "dist"
LEGACY_DIST = REPO_ROOT / "ui" / "web" / "dist"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
WINDOW_TITLE = "OS Dashboard · AI Assistant"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
BACKEND_LOG = REPO_ROOT / "logs" / "backend_server.log"


def _wait_for_port(host: str, port: int, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return
            except OSError:
                time.sleep(0.2)
    raise RuntimeError(f"Server did not start on {host}:{port} within {timeout}s")


def _uvicorn_log_config() -> dict:
    """Return a copy of uvicorn's logging config that also writes to logs/backend_server.log."""
    BACKEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    config = copy.deepcopy(UVICORN_LOGGING_CONFIG)
    config["handlers"]["backend-file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "access",
        "filename": str(BACKEND_LOG),
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 3,
        "encoding": "utf-8",
    }
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        handlers = config["loggers"].get(logger_name, {}).get("handlers")
        if handlers is not None and "backend-file" not in handlers:
            handlers.append("backend-file")
    config["formatters"]["access"]["fmt"] = "%(asctime)s - %(message)s"
    return config


def _start_backend(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    frontend_dist: Optional[Path] = None,
) -> Tuple[uvicorn.Server, threading.Thread]:
    app = create_app(frontend_dist=frontend_dist)
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False,
        lifespan="on",
        log_config=_uvicorn_log_config(),
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True, name="uvicorn-react")
    thread.start()
    _wait_for_port(host, port)
    return server, thread


def _resolve_frontend(dist_path: Optional[str] = None) -> Optional[Path]:
    candidates: list[Optional[Path]] = []
    if dist_path:
        candidates.append(Path(dist_path))
    candidates.extend([DEFAULT_DIST, LEGACY_DIST])
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return None


def _preferred_gui_backend() -> Optional[str]:
    """Pick the most capable pywebview backend for the current platform."""
    if os.environ.get("PYWEBVIEW_GUI"):
        return None  # Respect explicit overrides from the environment.
    if platform.system() == "Windows":
        # EdgeChromium (WebView2) is the only Windows backend that fully supports ES modules.
        return "edgechromium"
    return None


def _run_pywebview(window_url: str, gui_backend: Optional[str] = None) -> None:
    """Create and start a pywebview window optionally forcing a GUI backend."""
    import webview  # type: ignore

    def on_loaded():
        """Callback when window is loaded."""
        print(f"[UI] Webview loaded: {window_url}")
        try:
            # Small delay to ensure page is fully loaded
            time.sleep(0.5)
            # Try to get the current URL to verify it loaded
            windows = webview.windows
            if windows:
                window = windows[0]
                # Inject a simple test to check if JS is working
                try:
                    result = window.evaluate_js("""
                        (function() {
                            console.log('Webview JS is working!');
                            var root = document.getElementById('root');
                            if (root) {
                                console.log('Root element found');
                                return 'root_found';
                            } else {
                                console.error('Root element NOT found!');
                                return 'root_not_found';
                            }
                        })();
                    """)
                    print(f"[UI] JS evaluation result: {result}")
                except Exception as js_error:
                    print(f"[UI] JS evaluation error: {js_error}")
        except Exception as e:
            print(f"[UI] Error in on_loaded callback: {e}")

    window = webview.create_window(
        WINDOW_TITLE,
        window_url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        confirm_close=True,
        on_top=False,
    )
    
    start_kwargs: dict[str, object] = {"debug": True}
    if gui_backend:
        start_kwargs["gui"] = gui_backend
    
    # Set up loaded callback if supported
    try:
        if hasattr(window, 'loaded'):
            window.loaded += on_loaded
    except Exception as e:
        print(f"[UI] Could not set loaded callback: {e}")
    
    print(f"[UI] Starting webview with debug=True, URL: {window_url}")
    webview.start(**start_kwargs)


def launch_browser(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    dist_path: Optional[str] = None,
) -> None:
    """Start backend server and open the default browser."""
    frontend = _resolve_frontend(dist_path)
    server, thread = _start_backend(host, port, frontend)
    url = f"http://{host}:{port}/app/"
    print(f"[UI] Opening browser at {url}")
    webbrowser.open(url)
    try:
        while thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[UI] Stopping backend...")
    finally:
        server.should_exit = True


def launch_desktop(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    dist_path: Optional[str] = None,
) -> None:
    """Launch the React UI inside a pywebview shell for cross-platform desktop builds."""
    frontend = _resolve_frontend(dist_path)
    if not frontend:
        raise RuntimeError(
            f"Frontend dist not found. Checked: {DEFAULT_DIST}, {LEGACY_DIST}"
        )
    print(f"[UI] Using frontend dist: {frontend}")
    
    server, thread = _start_backend(host, port, frontend)
    url = f"http://{host}:{port}/app/"
    print(f"[UI] Starting desktop shell at {url}")
    
    # Give the server a moment to fully initialize
    time.sleep(0.5)
    
    # Verify the URL is accessible
    try:
        import urllib.request
        test_url = f"http://{host}:{port}/app/"
        response = urllib.request.urlopen(test_url, timeout=2)
        if response.getcode() == 200:
            print(f"[UI] Server is ready, loading webview...")
        else:
            print(f"[UI] Warning: Server returned status {response.getcode()}")
    except Exception as e:
        print(f"[UI] Warning: Could not verify server readiness: {e}")

    gui_backend = _preferred_gui_backend()
    try:
        _run_pywebview(url, gui_backend)
    except ImportError as exc:
        raise RuntimeError(
            "pywebview is not installed. Add it to requirements.txt and pip install."
        ) from exc
    except (ValueError, RuntimeError) as exc:
        if gui_backend is None:
            raise
        print(
            "[UI] Edge WebView2 runtime is unavailable. Install Microsoft Edge WebView2 "
            "for the best desktop experience."
        )
        print(f"[UI] Falling back to default pywebview backend ({exc}).")
        _run_pywebview(url, None)
    finally:
        server.should_exit = True
        if thread.is_alive():
            thread.join(timeout=3)


def main() -> None:
    parser = argparse.ArgumentParser(description="React UI launcher")
    parser.add_argument("--desktop", action="store_true", help="Launch pywebview shell")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--dist",
        type=str,
        default=None,
        help="Path to built React assets (defaults to frontend/dist)",
    )
    args = parser.parse_args()

    if args.desktop:
        launch_desktop(args.host, args.port, args.dist)
    else:
        launch_browser(args.host, args.port, args.dist)


if __name__ == "__main__":
    main()
