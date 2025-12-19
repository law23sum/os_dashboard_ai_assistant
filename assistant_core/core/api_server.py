"""Compatibility wrapper to launch the FastAPI app used by the dashboard."""

from __future__ import annotations

import argparse
import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import uvicorn

from assistant_hub.api.server import create_app
from assistant_hub.config import DB_PATH


def _wait_for_port(host: str, port: int, timeout: float = 15.0) -> None:
    """Block until the TCP port is reachable or the timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            try:
                sock.connect((host, port))
                return
            except OSError:
                time.sleep(0.2)
    raise RuntimeError(f"Server did not start on {host}:{port} within {timeout}s")


@dataclass
class APIServerHandle:
    """Small facade that mirrors the legacy HTTPServer surface."""

    server: uvicorn.Server
    thread: threading.Thread
    server_address: tuple[str, int]

    def shutdown(self) -> None:
        """Request shutdown and wait briefly for the thread to finish."""
        self.server.should_exit = True
        if self.thread.is_alive():
            self.thread.join(timeout=2.0)


def start_api_server(
    db_path: Optional[Path | str] = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8070,
    frontend_dist: Optional[Path | str] = None,
) -> APIServerHandle:
    """Start the FastAPI server in a background thread."""
    db_location = Path(db_path) if db_path is not None else DB_PATH
    frontend_path = Path(frontend_dist) if frontend_dist is not None else None

    app = create_app(db_path=db_location, frontend_dist=frontend_path)
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True, name="dashboard-api")
    thread.start()
    _wait_for_port(host, port)
    return APIServerHandle(server=server, thread=thread, server_address=(host, port))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assistant Hub API server")
    parser.add_argument("--host", default="127.0.0.1", help="Host/interface to bind")
    parser.add_argument("--port", type=int, default=8070, help="Port to listen on")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help="Optional path to the SQLite database file",
    )
    parser.add_argument(
        "--frontend-dist",
        type=Path,
        default=None,
        help="Optional path to a built React/Vite frontend bundle",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    handle = start_api_server(
        db_path=args.db_path,
        host=args.host,
        port=args.port,
        frontend_dist=args.frontend_dist,
    )
    try:
        if handle.thread.is_alive():
            handle.thread.join()
    except KeyboardInterrupt:
        handle.shutdown()


if __name__ == "__main__":
    main()
