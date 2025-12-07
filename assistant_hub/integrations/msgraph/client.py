"""Tiny Graph client wrapper."""
from __future__ import annotations

from typing import Any, Dict

from assistant_hub.integrations.msgraph.auth import GraphAuthenticator


class GraphClient:
    def __init__(self, authenticator: GraphAuthenticator):
        self.authenticator = authenticator

    def get(self, url: str) -> Dict[str, Any]:
        token = self.authenticator.get_token()
        return {"url": url, "token": token.access_token}
