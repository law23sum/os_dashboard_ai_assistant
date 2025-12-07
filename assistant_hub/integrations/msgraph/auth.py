"""Placeholder authentication for Microsoft Graph."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class GraphToken:
    access_token: str
    token_type: str = "Bearer"


class GraphAuthenticator:
    def __init__(self, tenant_id: Optional[str], client_id: Optional[str], client_secret: Optional[str]):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self) -> GraphToken:
        return GraphToken(access_token="fake-token")
