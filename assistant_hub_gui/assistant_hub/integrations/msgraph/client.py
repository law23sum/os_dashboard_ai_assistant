"""Shared Microsoft Graph client for OneNote, Excel, and Word."""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional
import sqlite3

import requests

from .auth import GraphAuth, GraphCredentials


class GraphClient:
    """Lightweight wrapper around Microsoft Graph REST calls."""

    base_url = "https://graph.microsoft.com/v1.0"

    def __init__(self, auth: Optional[GraphAuth] = None, token_provider: Optional[Callable[[], str]] = None, conn: Optional[sqlite3.Connection] = None, use_delegated: bool = False):
        if token_provider:
            # Backwards compatibility: create a GraphAuth wrapper
            class TokenProviderAuth:
                def get_token(self):
                    return token_provider()
            self.auth = TokenProviderAuth()
        else:
            # Pass connection to from_env so it can load from database
            # Try delegated auth if requested (useful for /me/ endpoints and personal accounts)
            credentials = GraphCredentials.from_env(conn=conn)
            self.auth = auth or GraphAuth(credentials, use_delegated=use_delegated)

    def _headers(self) -> Dict[str, str]:
        token = self.auth.get_token()
        return {"Authorization": f"Bearer {token}"}

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}{path}", headers=self._headers(), timeout=10, **kwargs)
        if response.status_code == 401:
            error_detail = response.text
            # Check if this is a /me/ endpoint that might need delegated permissions
            if "/me/" in path:
                raise requests.HTTPError(
                    f"401 Unauthorized accessing {path}\n"
                    f"This endpoint requires delegated permissions (user authentication).\n"
                    f"Run: python authenticate_azure_delegated.py to set up delegated auth.\n"
                    f"Then use GraphClient(use_delegated=True) or recreate with delegated auth.\n"
                    f"Error: {error_detail}"
                )
            else:
                raise requests.HTTPError(
                    f"401 Unauthorized accessing {path}\n"
                    f"Error: {error_detail}"
                )
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

    def put(self, path: str, json: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10, **kwargs
        )
        response.raise_for_status()
        return response.json() if response.text else {}
