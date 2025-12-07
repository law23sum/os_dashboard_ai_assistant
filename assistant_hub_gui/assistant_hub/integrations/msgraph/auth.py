"""Authentication helpers for Microsoft Graph.

These helpers use the client credentials flow for service integrations. They
are written as a minimal, testable layer that other integrations can share.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional

import requests

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
TOKEN_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"


@dataclass
class GraphCredentials:
    """Container for Graph credentials loaded from environment variables."""

    tenant_id: str
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> "GraphCredentials":
        return cls(
            tenant_id=os.environ.get("AZURE_TENANT_ID", ""),
            client_id=os.environ.get("AZURE_CLIENT_ID", ""),
            client_secret=os.environ.get("AZURE_CLIENT_SECRET", ""),
        )


class GraphAuthError(RuntimeError):
    """Raised when authentication fails."""


def request_access_token(credentials: Optional[GraphCredentials] = None) -> str:
    """Request an access token using the client credentials flow."""

    credentials = credentials or GraphCredentials.from_env()
    missing = [name for name, value in credentials.__dict__.items() if not value]
    if missing:
        raise GraphAuthError(f"Missing Graph credentials: {', '.join(sorted(missing))}")

    data = {
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scope": GRAPH_SCOPE,
        "grant_type": "client_credentials",
    }
    token_url = TOKEN_URL_TEMPLATE.format(tenant_id=credentials.tenant_id)
    response = requests.post(token_url, data=data, timeout=15)
    if response.status_code != 200:
        raise GraphAuthError(f"Graph token request failed: {response.status_code} {response.text}")
    payload: Dict[str, str] = response.json()
    return payload.get("access_token", "")
