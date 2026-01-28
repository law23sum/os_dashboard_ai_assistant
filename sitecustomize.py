"""Ensure local sources are importable without setting PYTHONPATH.

When Python starts it imports ``sitecustomize`` if present on the path.
By inserting the repository ``src`` directory ahead of other entries,
the ``assistant_hub`` package can be resolved when running console
scripts like ``osdash`` directly from a checkout.
"""

import inspect
from functools import wraps
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _patch_httpx_app_param() -> None:
    """Add backward-compatible support for httpx `app` params."""
    try:
        import httpx
    except Exception:
        return

    def _wrap_client_init(client_cls: type) -> None:
        try:
            signature = inspect.signature(client_cls.__init__)
        except (TypeError, ValueError):
            return
        if "app" in signature.parameters:
            return

        original_init = client_cls.__init__

        @wraps(original_init)
        def _init(self, *args, **kwargs):
            app = kwargs.pop("app", None)
            transport = kwargs.pop("transport", None)
            if app is not None and transport is None:
                transport = httpx.ASGITransport(app=app)
            return original_init(self, *args, transport=transport, **kwargs)

        client_cls.__init__ = _init

    _wrap_client_init(httpx.Client)
    _wrap_client_init(httpx.AsyncClient)


_patch_httpx_app_param()
