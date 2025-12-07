"""Shared Microsoft Graph client for OneNote, Excel, and Word."""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional
import sqlite3

import requests

from .auth import GraphAuth, GraphCredentials, GraphDelegatedAuth, AuthenticationError


class GraphClient:
    """Lightweight wrapper around Microsoft Graph REST calls."""

    base_url = "https://graph.microsoft.com/v1.0"

    def __init__(self, auth: Optional[GraphAuth] = None, token_provider: Optional[Callable[[], str]] = None, conn: Optional[sqlite3.Connection] = None, use_delegated: bool = False):
        """
        Initialize GraphClient.
        
        Args:
            auth: Optional GraphAuth or GraphDelegatedAuth instance
            token_provider: Optional function that returns access token
            conn: Optional database connection
            use_delegated: If True, use delegated authentication (for /me/ endpoints)
        """
        if token_provider:
            # Backwards compatibility: create a GraphAuth wrapper
            class TokenProviderAuth:
                def get_token(self):
                    return token_provider()
            self.auth = TokenProviderAuth()
        elif auth:
            self.auth = auth
        else:
            # Pass connection to from_env so it can load from database
            credentials = GraphCredentials.from_env(conn=conn)
            if use_delegated:
                self.auth = GraphDelegatedAuth(credentials, conn=conn)
            else:
                self.auth = GraphAuth(credentials)

    def _headers(self) -> Dict[str, str]:
        try:
            token = self.auth.get_token()
        except Exception as e:
            error_msg = str(e)
            # If it's a delegated auth error and we need to authenticate
            if isinstance(self.auth, GraphDelegatedAuth) and "No valid access token" in error_msg:
                raise AuthenticationError(
                    "Delegated authentication required. Please authenticate using device code flow.\n"
                    "This can be done through the GUI: Settings > Integrations > Microsoft Graph > Authenticate"
                ) from e
            raise
        return {"Authorization": f"Bearer {token}"}

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}{path}", headers=self._headers(), timeout=10, **kwargs)
        if response.status_code == 400:
            error_detail = response.text
            # Check if this is a /me/ endpoint - these require delegated permissions
            if "/me/" in path:
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error", {}).get("message", error_detail)
                except:
                    error_msg = error_detail
                raise requests.HTTPError(
                    f"400 Bad Request accessing {path}\n\n"
                    f"⚠️  The /me/ endpoints require DELEGATED permissions with user sign-in.\n"
                    f"   Client credentials (app-only authentication) cannot access user data.\n\n"
                    f"SOLUTION:\n"
                    f"   The OneNote /me/ endpoints require delegated authentication.\n"
                    f"   This means a user must sign in and grant permissions.\n\n"
                    f"   Current authentication method: Client Credentials (app-only)\n"
                    f"   Required authentication method: Delegated (user sign-in)\n\n"
                    f"   To fix this, you need to:\n"
                    f"   1. Implement delegated authentication flow (authorization code or device code)\n"
                    f"   2. Request delegated permissions: Notes.ReadWrite, User.Read\n"
                    f"   3. Have the user sign in and consent to permissions\n\n"
                    f"Error details: {error_msg}"
                )
        if response.status_code == 401:
            error_detail = response.text
            # Check if this is a /me/ endpoint
            if "/me/" in path:
                raise requests.HTTPError(
                    f"401 Unauthorized accessing {path}\n"
                    f"This endpoint requires delegated permissions with user sign-in.\n"
                    f"Client credentials (app-only) authentication is not supported for /me/ endpoints.\n"
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
        if response.status_code == 400 and "/me/" in path:
            error_detail = response.text
            try:
                error_json = response.json()
                error_msg = error_json.get("error", {}).get("message", error_detail)
            except:
                error_msg = error_detail
            raise requests.HTTPError(
                f"400 Bad Request accessing {path}\n\n"
                f"⚠️  The /me/ endpoints require DELEGATED permissions with user sign-in.\n"
                f"   Client credentials (app-only authentication) cannot access user data.\n\n"
                f"Error details: {error_msg}"
            )
        response.raise_for_status()
        return response.json() if response.text else {}

    def patch(self, path: str, json: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10, **kwargs
        )
        if response.status_code == 400 and "/me/" in path:
            error_detail = response.text
            try:
                error_json = response.json()
                error_msg = error_json.get("error", {}).get("message", error_detail)
            except:
                error_msg = error_detail
            raise requests.HTTPError(
                f"400 Bad Request accessing {path}\n\n"
                f"⚠️  The /me/ endpoints require DELEGATED permissions with user sign-in.\n"
                f"   Client credentials (app-only authentication) cannot access user data.\n\n"
                f"Error details: {error_msg}"
            )
        response.raise_for_status()
        return response.json() if response.text else {}

    def put(self, path: str, json: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}{path}", headers=self._headers(), json=json, timeout=10, **kwargs
        )
        if response.status_code == 400 and "/me/" in path:
            error_detail = response.text
            try:
                error_json = response.json()
                error_msg = error_json.get("error", {}).get("message", error_detail)
            except:
                error_msg = error_detail
            raise requests.HTTPError(
                f"400 Bad Request accessing {path}\n\n"
                f"⚠️  The /me/ endpoints require DELEGATED permissions with user sign-in.\n"
                f"   Client credentials (app-only authentication) cannot access user data.\n\n"
                f"Error details: {error_msg}"
            )
        response.raise_for_status()
        return response.json() if response.text else {}
