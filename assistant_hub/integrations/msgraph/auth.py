"""Authentication helpers for Microsoft Graph integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import requests


@dataclass
class GraphCredentials:
    tenant_id: str
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> "GraphCredentials":
        """Load credentials from environment variables or config file."""
        # First check environment variables
        tenant_id = os.environ.get("AZURE_TENANT_ID", "")
        client_id = os.environ.get("AZURE_CLIENT_ID", "")
        client_secret = os.environ.get("AZURE_CLIENT_SECRET", "")

        # If not all credentials are in environment, try loading from config file
        if not all([tenant_id, client_id, client_secret]):
            config_file = Path.home() / ".assistant_hub" / "azure_config.txt"
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        for line in f:
                            line = line.strip()
                            if "=" in line and not line.startswith("#"):
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip()
                                # Only set if not already in environment
                                if key == "AZURE_TENANT_ID" and not tenant_id:
                                    tenant_id = value
                                elif key == "AZURE_CLIENT_ID" and not client_id:
                                    client_id = value
                                elif key == "AZURE_CLIENT_SECRET" and not client_secret:
                                    client_secret = value
                except Exception:
                    # If file read fails, continue with what we have from env
                    pass

        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
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
