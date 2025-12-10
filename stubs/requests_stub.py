"""Minimal stub of the ``requests`` API used in tests or offline runs.

The real project depends on the official ``requests`` package, but this stub
remains available under ``stubs.requests_stub`` for scenarios where network
access is unavailable. Import explicitly when needed:

    from stubs.requests_stub import post, Response, Session
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Response:
  status_code: int = 200
  _payload: Dict[str, Any] | None = None

  def json(self) -> Dict[str, Any]:
    return self._payload or {}

  def raise_for_status(self) -> None:
    return None


def post(*args: Any, **kwargs: Any) -> Response:
  token = kwargs.get("data", {}).get("client_secret", "dummy")
  return Response(status_code=200, _payload={"access_token": f"stub-{token}"})


class Session:
  """Tiny drop-in replacement supporting ``post`` only."""

  def post(self, *args: Any, **kwargs: Any) -> Response:
    return post(*args, **kwargs)


__all__ = ["post", "Response", "Session"]
