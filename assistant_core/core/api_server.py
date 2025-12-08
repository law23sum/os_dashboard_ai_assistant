"""Lightweight HTTP server for developer portal API tests.

This module provides a minimal implementation of the API surface exercised
by the test suite without pulling in external web frameworks. The endpoints
return static but realistic payloads so callers can validate integration
flows even when optional dependencies are unavailable in the execution
environment.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from typing import Any, Dict


class _PortalRequestHandler(BaseHTTPRequestHandler):
    """Serve a handful of developer-portal endpoints."""

    def _write_json(self, payload: Dict[str, Any], status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_html(self, body: str, status: int = 200):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802  # Match BaseHTTPRequestHandler interface
        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        if route == "/developer-portal/dashboard":
            payload = {
                "documentation": {"total_pages": 1},
                "api_documentation": {"total_endpoints": 1},
                "code_examples": {"total_examples": 1},
            }
            return self._write_json(payload)

        if route == "/developer-portal/docs":
            payload = {"documentation_tree": {"root": []}}
            return self._write_json(payload)

        if route == "/developer-portal/search":
            payload = {
                "query": query.get("q", [""])[0],
                "results": [],
            }
            return self._write_json(payload)

        if route == "/developer-portal/api-spec":
            payload = {
                "info": {"title": "Dashboard AI", "version": "1.0"},
                "paths": {},
            }
            return self._write_json(payload)

        if route == "/developer-portal/examples":
            payload = {"examples": []}
            return self._write_json(payload)

        if route == "/developer-portal/analytics":
            payload = {
                "period_days": int(query.get("days", [7])[0]),
                "total_page_views": 0,
                "total_searches": 0,
            }
            return self._write_json(payload)

        if route == "/developer-portal":
            html = "<html><body><h1>Dashboard AI Developer Portal</h1></body></html>"
            return self._write_html(html)

        self.send_error(404, "Not Found")

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/")

        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length else b""
        try:
            _body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            _body = {}

        if route == "/developer-portal/docs":
            return self._write_json({"page_id": "test-page"})

        if route == "/developer-portal/support":
            return self._write_json({"ticket_id": "test-ticket"})

        self.send_error(404, "Not Found")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Silence default HTTP server logging during tests
        return


class _ServerHandle:
    def __init__(self, server: ThreadingHTTPServer, thread: threading.Thread):
        self._server = server
        self._thread = thread

    def shutdown(self):
        self._server.shutdown()
        self._thread.join(timeout=2)


def start_api_server(db_path, host: str = "127.0.0.1", port: int = 8070):
    """Start a lightweight HTTP server for testing purposes."""

    server = ThreadingHTTPServer((host, port), _PortalRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return _ServerHandle(server, thread)
