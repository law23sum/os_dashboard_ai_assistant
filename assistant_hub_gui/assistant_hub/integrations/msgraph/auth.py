"""Authentication helpers for Microsoft Graph."""
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
    scope: str = "https://graph.microsoft.com/.default"

    @property
    def token_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

    def as_form_data(self) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
            "grant_type": "client_credentials",
        }


def load_credentials_from_env() -> GraphCredentials:
    """Load Graph credentials from environment variables."""
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        raise ValueError("Missing Graph credentials. Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET.")

    return GraphCredentials(tenant_id=tenant_id or "", client_id=client_id or "", client_secret=client_secret or "")


def request_access_token(credentials: GraphCredentials) -> str:
    """Request a bearer token using the client credentials flow."""
    response = requests.post(credentials.token_url, data=credentials.as_form_data(), timeout=30)
    response.raise_for_status()
    data = response.json()
    if "access_token" not in data:
        raise RuntimeError(f"Token response missing access_token: {data}")
    return data["access_token"]
