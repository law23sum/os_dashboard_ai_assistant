"""Minimal shim of the ``requests`` API used in tests.

When the real dependency is available we load and re-export it, otherwise we
fall back to a very small stub used by a couple of local helpers.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Dict, Optional


def _import_real_requests() -> Optional[object]:
    """Attempt to load the actual ``requests`` package when installed."""

    current_file = Path(__file__).resolve()
    for entry in list(sys.path):
        if not entry:
            continue
        try:
            entry_path = Path(entry).resolve()
        except OSError:
            continue
        candidate = entry_path / "requests" / "__init__.py"
        try:
            if not candidate.is_file() or candidate.resolve() == current_file:
                continue
        except OSError:
            continue

        spec = spec_from_file_location(
            "requests",
            candidate,
            submodule_search_locations=[str(candidate.parent)],
        )
        if spec and spec.loader:
            module = module_from_spec(spec)
            sys.modules[__name__] = module
            spec.loader.exec_module(module)
            return module

    return None


_force_stub = os.environ.get("OS_DASHBOARD_REQUESTS_STUB", "").lower() in {
    "1",
    "true",
    "yes",
}

_real_requests = None if _force_stub else _import_real_requests()

<<<<<<< Updated upstream
if _real_requests is not None:
    globals().update(_real_requests.__dict__)
else:

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

    class Session:
        """Tiny drop-in replacement supporting ``post`` only."""

        def post(self, *args: Any, **kwargs: Any) -> Response:
            return post(*args, **kwargs)

    __all__ = ["post", "Response", "Session"]
=======
class Session:
    """Tiny drop-in replacement supporting ``post`` only."""

    def post(self, *args: Any, **kwargs: Any) -> Response:
        return post(*args, **kwargs)


__all__ = ["post", "Response", "Session"]
>>>>>>> Stashed changes
