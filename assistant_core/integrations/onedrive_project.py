"""Lightweight OneDrive client derived from the design-only onedrive_project reference."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

try:
    from msal import PublicClientApplication  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    PublicClientApplication = None  # type: ignore


@dataclass
class OneDriveSession:
    client_id: str
    tenant_id: str
    scopes: List[str]
    authority: str
    access_token: Optional[str] = None
    expires_at: Optional[float] = None


class OneDriveProjectClient:
    """Interactive MSAL client to list, update, and upload OneDrive files."""

    def __init__(self, client_id: str, tenant_id: str, scopes: Optional[List[str]] = None) -> None:
        scopes = scopes or ["Files.ReadWrite", "User.Read"]
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        if PublicClientApplication is None:
            raise RuntimeError(
                "msal dependency is not available. Install msal or run pip install -r requirements.txt to enable OneDrive features."
            )

        self.session = OneDriveSession(client_id=client_id, tenant_id=tenant_id, scopes=scopes, authority=authority)
        self.app = PublicClientApplication(client_id, authority=authority)

    # ------------------------------------------------------------------
    # Authentication helpers
    # ------------------------------------------------------------------
    def ensure_token(self) -> str:
        if self.session.access_token and self.session.expires_at and self.session.expires_at > time.time() - 10:
            return self.session.access_token
        result = self.app.acquire_token_interactive(scopes=self.session.scopes)
        if "access_token" not in result:
            raise RuntimeError("Authentication failed")
        self.session.access_token = result["access_token"]
        expires_in = result.get("expires_in", 3600)
        self.session.expires_at = time.time() + expires_in
        return self.session.access_token

    def _headers(self) -> Dict[str, str]:
        token = self.ensure_token()
        return {"Authorization": f"Bearer {token}"}

    # ------------------------------------------------------------------
    # API helpers
    # ------------------------------------------------------------------
    def list_root_files(self) -> List[Dict[str, str]]:
        response = requests.get("https://graph.microsoft.com/v1.0/me/drive/root/children", headers=self._headers())
        response.raise_for_status()
        return response.json().get("value", [])

    def update_file_content(self, file_id: str, content: bytes) -> Dict[str, str]:
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
        response = requests.put(url, headers=self._headers(), data=content)
        response.raise_for_status()
        return response.json()

    def poll_file_updates(self, file_id: str, polls: int = 3, delay: float = 2.0) -> List[str]:
        timestamps: List[str] = []
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
        for _ in range(polls):
            response = requests.get(url, headers=self._headers())
            response.raise_for_status()
            timestamps.append(response.json().get("lastModifiedDateTime", "unknown"))
            time.sleep(delay)
        return timestamps

    def upload_text_file(self, file_name: str, content: str) -> Dict[str, str]:
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}:/content"
        response = requests.put(url, headers=self._headers(), data=content.encode("utf-8"))
        response.raise_for_status()
        return response.json()
