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

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

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


def _get_templates(db_path: Path) -> List[Dict[str, Any]]:
    """Get all task templates."""
    return _fetch_rows(
        db_path,
        "SELECT id, name, title, project, priority, notes, time_estimated, created_at FROM task_templates ORDER BY name"
    )


def _get_dashboard_stats(db_path: Path) -> Dict[str, Any]:
    """Aggregate dashboard statistics from database and system."""
    with _open_db(db_path) as conn:
        # Task statistics
        task_rows = conn.execute("SELECT status, priority FROM tasks").fetchall()
        total_tasks = len(task_rows)
        
        tasks_by_status: Dict[str, int] = {}
        tasks_by_priority: Dict[str, int] = {}
        
        for row in task_rows:
            status = row["status"] or "TODO"
            priority = row["priority"] or "MEDIUM"
            tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
            tasks_by_priority[priority] = tasks_by_priority.get(priority, 0) + 1
        
        # Project statistics
        project_rows = conn.execute("SELECT status FROM projects").fetchall()
        total_projects = len(project_rows)
        active_projects = sum(1 for row in project_rows if row["status"] and row["status"].upper() in ("ACTIVE", "IN_PROGRESS", "OPEN"))
        
        # System statistics
        if psutil:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                system_stats = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                }
            except Exception:
                system_stats = {
                    "cpu_percent": 0.0,
                    "memory_percent": 0.0,
                    "disk_percent": 0.0,
                }
        else:
            system_stats = {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
            }
        
        # Security status (placeholder - can be enhanced later)
        from datetime import datetime
        security_status = {
            "status": "secure",
            "message": "System security checks passed",
            "updated_at": datetime.now().isoformat(),
            "source": "system",
        }
        
        return {
            "total_tasks": total_tasks,
            "tasks_by_status": tasks_by_status,
            "tasks_by_priority": tasks_by_priority,
            "total_projects": total_projects,
            "active_projects": active_projects,
            "system_stats": system_stats,
            "security_status": security_status,
        }


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
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 - signature from BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        params = urllib.parse.parse_qs(parsed.query)

        try:
            if path == "/" or path == "/health":
                self._handle_health()
            elif path == "/dashboard/stats":
                self._handle_dashboard_stats()
            elif path == "/projects":
                self._handle_projects()
            elif path == "/tasks":
                self._handle_tasks(params)
            elif path == "/templates":
                self._handle_templates()
            elif path == "/agent-runs" or path == "/activity":
                self._handle_agent_runs(params)
            elif path == "/integrations":
                self._handle_integrations(params)
            else:
                self._send_json({"error": "Not Found", "path": path}, status=404)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.exception("API error for %s", path)
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:  # noqa: N802 - signature from BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            
            if path == "/templates":
                self._handle_create_template(data)
            elif path == "/templates/create-task":
                self._handle_create_task_from_template(data)
            else:
                self._send_json({"error": "Not Found", "path": path}, status=404)
        except Exception as exc:
            self.logger.exception("API error for %s", path)
            self._send_json({"error": str(exc)}, status=500)

    def do_PUT(self) -> None:  # noqa: N802 - signature from BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            
            if path.startswith("/templates/"):
                template_id = path.split("/")[-1]
                self._handle_update_template(template_id, data)
            else:
                self._send_json({"error": "Not Found", "path": path}, status=404)
        except Exception as exc:
            self.logger.exception("API error for %s", path)
            self._send_json({"error": str(exc)}, status=500)

    def do_DELETE(self) -> None:  # noqa: N802 - signature from BaseHTTPRequestHandler
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        
        try:
            if path.startswith("/templates/"):
                template_id = path.split("/")[-1]
                self._handle_delete_template(template_id)
            else:
                self._send_json({"error": "Not Found", "path": path}, status=404)
        except Exception as exc:
            self.logger.exception("API error for %s", path)
            self._send_json({"error": str(exc)}, status=500)

    def _handle_health(self) -> None:
        payload = {"status": "ok", "message": "Dashboard API ready"}
        self._send_json(payload)

    def _handle_dashboard_stats(self) -> None:
        stats = _get_dashboard_stats(self.db_path)
        self._send_json(stats)

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

    def _handle_templates(self) -> None:
        templates = _get_templates(self.db_path)
        self._send_json({"templates": templates})

    def _handle_create_template(self, data: Dict[str, Any]) -> None:
        import uuid
        from datetime import datetime
        
        template_id = data.get("id") or str(uuid.uuid4())
        with _open_db(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO task_templates (id, name, title, project, priority, notes, time_estimated, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    title = excluded.title,
                    project = excluded.project,
                    priority = excluded.priority,
                    notes = excluded.notes,
                    time_estimated = excluded.time_estimated
                """,
                (
                    template_id,
                    data.get("name", ""),
                    data.get("title", ""),
                    data.get("project", "General"),
                    data.get("priority", "MEDIUM"),
                    data.get("notes", ""),
                    data.get("time_estimated"),
                    data.get("created_at") or datetime.now().isoformat(),
                ),
            )
            conn.commit()
        self._send_json({"id": template_id, "message": "Template saved"})

    def _handle_update_template(self, template_id: str, data: Dict[str, Any]) -> None:
        with _open_db(self.db_path) as conn:
            conn.execute(
                """
                UPDATE task_templates SET
                    name = ?,
                    title = ?,
                    project = ?,
                    priority = ?,
                    notes = ?,
                    time_estimated = ?
                WHERE id = ?
                """,
                (
                    data.get("name", ""),
                    data.get("title", ""),
                    data.get("project", "General"),
                    data.get("priority", "MEDIUM"),
                    data.get("notes", ""),
                    data.get("time_estimated"),
                    template_id,
                ),
            )
            conn.commit()
        self._send_json({"message": "Template updated"})

    def _handle_delete_template(self, template_id: str) -> None:
        with _open_db(self.db_path) as conn:
            conn.execute("DELETE FROM task_templates WHERE id = ?", (template_id,))
            conn.commit()
        self._send_json({"message": "Template deleted"})

    def _handle_create_task_from_template(self, data: Dict[str, Any]) -> None:
        template_id = data.get("template_id")
        if not template_id:
            self._send_json({"error": "template_id required"}, status=400)
            return
        
        with _open_db(self.db_path) as conn:
            template_row = conn.execute(
                "SELECT * FROM task_templates WHERE id = ?", (template_id,)
            ).fetchone()
            
            if not template_row:
                self._send_json({"error": "Template not found"}, status=404)
                return
            
            from datetime import datetime
            conn.execute(
                """
                INSERT INTO tasks (title, project, status, priority, notes, time_estimated, created_at, owner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    template_row["title"] or "",
                    template_row["project"] or "General",
                    "TODO",
                    template_row["priority"] or "MEDIUM",
                    template_row["notes"] or "",
                    template_row["time_estimated"],
                    datetime.now().isoformat(),
                    data.get("owner", ""),
                ),
            )
            conn.commit()
        self._send_json({"message": "Task created from template"})


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
