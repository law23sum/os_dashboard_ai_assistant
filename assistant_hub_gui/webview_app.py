"""Hybrid launcher that serves the React UI for both desktop (pywebview) and browser."""
from __future__ import annotations

import argparse
import socket
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional, Tuple

import uvicorn

from assistant_hub.api.server import create_app

REPO_ROOT = Path(__file__).resolve().parents[1]
# Prefer the new shared React bundle under frontend/dist, fall back to the legacy ui/web build.
DEFAULT_DIST = REPO_ROOT / "frontend" / "dist"
LEGACY_DIST = REPO_ROOT / "ui" / "web" / "dist"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


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


def _start_backend(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    frontend_dist: Optional[Path] = None,
) -> Tuple[uvicorn.Server, threading.Thread]:
    app = create_app(frontend_dist=frontend_dist)
    config = uvicorn.Config(
        app, host=host, port=port, log_level="info", reload=False, lifespan="on"
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
    try:
        import webview  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "pywebview is not installed. Add it to requirements.txt and pip install."
        ) from exc

    frontend = _resolve_frontend(dist_path)
    server, thread = _start_backend(host, port, frontend)
    url = f"http://{host}:{port}/app/"
    print(f"[UI] Starting desktop shell at {url}")
    try:
        window = webview.create_window(
            "OS Dashboard · AI Assistant",
            url,
            width=1400,
            height=900,
            confirm_close=True,
        )
        webview.start()
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
