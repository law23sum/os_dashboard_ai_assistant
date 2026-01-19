"""API routers package."""

from __future__ import annotations

import importlib
import os
from types import SimpleNamespace
from typing import Any

__all__ = [
    "agent_journal",
    "ai_systems",
    "automation_status",
    "analytics",
    "api_connectors",
    "api_session_costs",
    "codex_review",
    "coach",
    "constants",
    "tooling_integrations",
    "tooling_patterns",
    "audit",
    "chat",
    "dashboard",
    "documents",
    "document_operations",
    "exports",
    "event_hub",
    "git",
    "integrations",
    "intelligence",
    "ipm",
    "math_sim",
    "matlab",
    "knowledge",
    "network_monitoring",
    "office",
    "policy",
    "reasoning",
    "pms",
    "projects",
    "research",
    "runtime_diagnostics",
    "search",
    "platform",
    "templates",
    "settings",
    "tasks",
    "terminal",
    "workspace",
    "workspace_health",
    "writer",
]

_ALLOWLIST_RAW = os.environ.get("OSDASH_ROUTER_ALLOWLIST", "").strip()
_ALLOWLIST = (
    {name.strip() for name in _ALLOWLIST_RAW.split(",") if name.strip()}
    if _ALLOWLIST_RAW
    else None
)
_SKIP_OPTIONAL = os.environ.get("OSDASH_SKIP_OPTIONAL_ROUTERS", "").strip().lower() in {
    "1",
    "true",
    "yes",
}
_STUBS: dict[str, Any] = {}


def _stub_router(name: str) -> Any:
    existing = _STUBS.get(name)
    if existing is not None:
        return existing
    from fastapi import APIRouter

    stub = SimpleNamespace(router=APIRouter())
    _STUBS[name] = stub
    return stub


def __getattr__(name: str) -> Any:
    if name in __all__:
        if _ALLOWLIST is not None and name not in _ALLOWLIST:
            return _stub_router(name)
        try:
            return importlib.import_module(f"{__name__}.{name}")
        except ModuleNotFoundError as exc:
            if exc.name == f"{__name__}.{name}":
                return _stub_router(name)
            if _SKIP_OPTIONAL:
                return _stub_router(name)
            raise
        except Exception:
            if _SKIP_OPTIONAL:
                return _stub_router(name)
            raise
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
