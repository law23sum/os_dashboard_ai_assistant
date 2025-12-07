"""Minimal stub of the ``requests`` API used in tests.

The project only needs a tiny subset of the interface (``post`` with
``json`` and ``raise_for_status``) to satisfy authentication helpers in
restricted environments where the real dependency may be unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Response:
    status_code: int = 200
    _payload: Dict[str, Any] = None

    def json(self) -> Dict[str, Any]:
        return self._payload or {}

    def raise_for_status(self) -> None:
        # No-op for stubbed responses
        return None


def post(*args: Any, **kwargs: Any) -> Response:
    token = kwargs.get("data", {}).get("client_secret", "dummy")
    return Response(status_code=200, _payload={"access_token": f"stub-{token}"})


__all__ = ["post", "Response"]
