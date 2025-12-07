"""Shared Microsoft Graph client utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .auth import request_access_token

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


@dataclass
class GraphRequestContext:
    """Context for Graph requests."""

    access_token: Optional[str] = None

    def ensure_token(self) -> str:
        if not self.access_token:
            self.access_token = request_access_token()
        return self.access_token


class GraphClient:
    """Minimal client wrapper to issue authenticated Graph requests."""

    def __init__(self, context: Optional[GraphRequestContext] = None):
        self.context = context or GraphRequestContext()

    def _headers(self, *, include_content_type: bool = True) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {self.context.ensure_token()}"}
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def get(self, relative_url: str, *, expect_json: bool = True) -> Any:
        url = GRAPH_BASE_URL + relative_url
        response = requests.get(url, headers=self._headers(), timeout=30)
        response.raise_for_status()
        return response.json() if expect_json else response.content

    def patch(self, relative_url: str, payload: Any) -> Dict[str, Any]:
        url = GRAPH_BASE_URL + relative_url
        response = requests.patch(url, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json() if response.content else {}

    def post(self, relative_url: str, payload: Any) -> Dict[str, Any]:
        url = GRAPH_BASE_URL + relative_url
        response = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def put(self, relative_url: str, payload: Any) -> Dict[str, Any]:
        url = GRAPH_BASE_URL + relative_url
        if isinstance(payload, (bytes, bytearray)):
            headers = self._headers(include_content_type=False)
            response = requests.put(url, headers=headers, data=payload, timeout=30)
        else:
            response = requests.put(url, headers=self._headers(), json=payload, timeout=30)
        response.raise_for_status()
        return response.json() if response.content else {}
