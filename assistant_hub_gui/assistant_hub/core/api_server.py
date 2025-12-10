"""Lightweight HTTP API server exposing dashboard data for third-party tools."""
from __future__ import annotations

import json
import sqlite3
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any, Callable, Dict, List, Tuple

from ..logging_config import get_logger
from ..sync_scheduler import create_default_scheduler
from ..integrations import IntegrationAPIGateway


def _open_db(db_path: Path) -> sqlite3.Connection:
    """Open a read/write SQLite connection for the API handler."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _fetch_rows(
    db_path: Path, query: str, params: Tuple[Any, ...] = ()
) -> List[Dict[str, Any]]:
    with _open_db(db_path) as conn:
        cur = conn.execute(query, params)
        return [_row_to_dict(row) for row in cur.fetchall()]


def _get_agent_runs(db_path: Path, limit: int = 20) -> List[Dict[str, Any]]:
    return _fetch_rows(
        db_path,
        "SELECT agent, action_type, input_context, output_summary, related_files, "
        "git_commit_hash, created_at FROM agent_runs ORDER BY datetime(created_at) DESC LIMIT ?",
        (limit,),
    )


def _get_projects(db_path: Path) -> List[Dict[str, Any]]:
    return _fetch_rows(
        db_path, "SELECT name, description, status, priority FROM projects"
    )


def _get_tasks(db_path: Path, limit: int = 100) -> List[Dict[str, Any]]:
    return _fetch_rows(
        db_path,
        "SELECT id, title, project, status, priority, due_date, notes, owner, created_at, time_logged, "
        "time_estimated FROM tasks ORDER BY datetime(created_at) DESC LIMIT ?",
        (limit,),
    )


def _get_integration_api(db_path: Path) -> IntegrationAPIGateway:
    conn = _open_db(db_path)
    scheduler = create_default_scheduler(conn)
    return IntegrationAPIGateway(conn, scheduler=scheduler)


class _ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class _DashboardAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, db_path: Path, *args, **kwargs):
        self.db_path = db_path
        self.logger = get_logger("DashboardAPI")
        super().__init__(*args, **kwargs)

    # Disable noisy default logging
    def log_message(
        self, fmt: str, *args: Any
    ) -> None:  # pragma: no cover - debug only
        self.logger.debug(fmt, *args)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802 - signature from BaseHTTPRequestHandler
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 - signature from BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        params = urllib.parse.parse_qs(parsed.query)

        try:
            if path == "/" or path == "/health":
                self._handle_health()
            elif path == "/projects":
                self._handle_projects()
            elif path == "/tasks":
                self._handle_tasks(params)
            elif path == "/agent-runs" or path == "/activity":
                self._handle_agent_runs(params)
            elif path == "/integrations":
                self._handle_integrations(params)
            else:
                self._send_json({"error": "Not Found", "path": path}, status=404)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.exception("API error for %s", path)
            self._send_json({"error": str(exc)}, status=500)

    def _handle_health(self) -> None:
        payload = {"status": "ok", "message": "Dashboard API ready"}
        self._send_json(payload)

    def _handle_projects(self) -> None:
        projects = _get_projects(self.db_path)
        self._send_json({"projects": projects})

    def _handle_tasks(self, params: Dict[str, List[str]]) -> None:
        limit = int(params.get("limit", ["100"])[0])
        tasks = _get_tasks(self.db_path, limit=limit)
        self._send_json({"tasks": tasks, "limit": limit})

    def _handle_agent_runs(self, params: Dict[str, List[str]]) -> None:
        limit = int(params.get("limit", ["20"])[0])
        runs = _get_agent_runs(self.db_path, limit=limit)
        self._send_json({"agent_runs": runs, "limit": limit})

    def _handle_integrations(self, params: Dict[str, List[str]]) -> None:
        target = params.get("target", ["all"])[0]
        action = params.get("action", ["status"])[0]
        options_raw = params.get("options", [None])[0]
        options = None

        if options_raw:
            try:
                options = json.loads(options_raw)
            except json.JSONDecodeError:
                options = None

        gateway = _get_integration_api(self.db_path)
        result = gateway.call_action(target, action=action, options=options)
        self._send_json({"target": target, "action": action, "result": result})


def _handler_factory(db_path: Path) -> Callable:
    def handler(*args, **kwargs):
        _DashboardAPIHandler(db_path, *args, **kwargs)

    return handler


def start_api_server(
    db_path: Path, host: str = "127.0.0.1", port: int = 8070
) -> _ThreadedHTTPServer:
    """Start the threaded API server in a background thread.

    Args:
        db_path: Path to the SQLite database used by the dashboard.
        host: Host/interface to bind the HTTP server to.
        port: Port number for the API server.

    Returns:
        The running HTTP server instance.
    """

    db_path = Path(db_path)
    handler_class = _handler_factory(db_path)
    server = _ThreadedHTTPServer((host, port), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    logger = get_logger("DashboardAPI")
    logger.info(
        "Dashboard API server started on http://%s:%s", host, server.server_address[1]
    )
    return server
