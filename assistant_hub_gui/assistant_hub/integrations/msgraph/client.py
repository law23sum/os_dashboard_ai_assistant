"""Generic Microsoft Graph client."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import requests


class GraphClient:
    """Small helper around the Microsoft Graph REST API."""

    def __init__(self, token_provider: Callable[[], str], *, base_url: str = "https://graph.microsoft.com/v1.0") -> None:
        self.token_provider = token_provider
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token_provider()}"}

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        response = requests.get(self.base_url + path, headers=self._headers(), timeout=30, **kwargs)
        response.raise_for_status()
        return response

    def post(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any) -> requests.Response:
        response = requests.post(self.base_url + path, headers=self._headers(), json=json, timeout=30, **kwargs)
        response.raise_for_status()
        return response

    def patch(self, path: str, json: Optional[Any] = None, **kwargs: Any) -> requests.Response:
        response = requests.patch(self.base_url + path, headers=self._headers(), json=json, timeout=30, **kwargs)
        response.raise_for_status()
        return response

    def put(self, path: str, json: Optional[Any] = None, **kwargs: Any) -> requests.Response:
        response = requests.put(self.base_url + path, headers=self._headers(), json=json, timeout=30, **kwargs)
        response.raise_for_status()
        return response
