"""Lightweight local substitute for the requests library.

This module provides a minimal subset of the requests API needed by the
project's tests, without requiring external dependencies or network
installation steps. It supports basic GET and POST HTTP requests and
response helpers.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


class HTTPError(Exception):
    """Simple HTTP error mirroring requests.HTTPError behavior."""

    def __init__(self, response: "Response"):
        super().__init__(f"HTTP {response.status_code}")
        self.response = response


class Response:
    """Minimal response object returned by get/post helpers."""

    def __init__(self, status_code: int, content: bytes, headers: Dict[str, str]):
        self.status_code = status_code
        self.content = content
        self.headers = headers
        try:
            self.text = content.decode("utf-8")
        except Exception:
            self.text = content.decode(errors="ignore")

    def json(self) -> Any:
        return json.loads(self.text or "{}")

    def raise_for_status(self):
        if 400 <= self.status_code:
            raise HTTPError(self)


def _make_request(method: str, url: str, *, data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> Response:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            status_code = resp.getcode()
            resp_headers = dict(resp.headers)
    except urllib.error.HTTPError as e:
        content = e.read()
        status_code = e.code
        resp_headers = dict(e.headers)
    return Response(status_code, content, resp_headers)


def get(url: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None, **kwargs: Any) -> Response:
    query = urllib.parse.urlencode(params or {})
    full_url = f"{url}?{query}" if query else url
    return _make_request("GET", full_url, timeout=timeout)


def post(url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None, **kwargs: Any) -> Response:
    headers = kwargs.get("headers", {})
    payload: Optional[bytes] = None

    if json is not None:
        payload = json.dumps(json).encode("utf-8")
        headers = {**headers, "Content-Type": "application/json"}
    elif data is not None:
        payload = urllib.parse.urlencode(data).encode("utf-8")
        headers = {**headers, "Content-Type": "application/x-www-form-urlencoded"}

    return _make_request("POST", url, data=payload, headers=headers, timeout=timeout)


__all__ = ["get", "post", "Response", "HTTPError"]
