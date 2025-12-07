"""Authentication helpers for Microsoft Graph integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

import requests


@dataclass
class GraphCredentials:
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


class GraphAuth:
    """Acquire tokens for Microsoft Graph APIs using client credentials."""

    scope: str = "https://graph.microsoft.com/.default"

    def __init__(self, credentials: GraphCredentials):
        self.credentials = credentials

    def get_token(self) -> str:
        token_url = f"https://login.microsoftonline.com/{self.credentials.tenant_id}/oauth2/v2.0/token"
        response = requests.post(
            token_url,
            data={
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scope": self.scope,
                "grant_type": "client_credentials",
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["access_token"]


# Backwards compatibility functions
def load_credentials_from_env() -> GraphCredentials:
    """Load Graph credentials from environment variables (backwards compatibility)."""
    return GraphCredentials.from_env()


def request_access_token(credentials: GraphCredentials) -> str:
    """Request a bearer token using the client credentials flow (backwards compatibility)."""
    auth = GraphAuth(credentials)
    return auth.get_token()
