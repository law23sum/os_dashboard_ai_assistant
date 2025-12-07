"""Shared Microsoft Graph client for OneNote, Excel, and Word."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .auth import GraphAuth, GraphCredentials


class GraphClient:
    """Lightweight wrapper around Microsoft Graph REST calls."""

    base_url = "https://graph.microsoft.com/v1.0"

    def __init__(self, auth: Optional[GraphAuth] = None):
        self.auth = auth or GraphAuth(GraphCredentials.from_env())

    def _headers(self) -> Dict[str, str]:
        token = self.auth.get_token()
        return {"Authorization": f"Bearer {token}"}

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}{path}", headers=self._headers(), timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10, **kwargs
        )
        response.raise_for_status()
        return response.json() if response.text else {}

    def patch(self, path: str, json: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10, **kwargs
        )
        response.raise_for_status()
        return response.json() if response.text else {}
