"""API routers package."""

from __future__ import annotations

import importlib
from typing import Any

__all__ = [
    "agent_journal",
    "ai_systems",
    "analytics",
    "api_connectors",
    "codex_review",
    "coach",
    "constants",
    "cookbook_integrations",
    "cookbook_patterns",
    "audit",
    "chat",
    "dashboard",
    "documents",
    "document_operations",
    "exports",
    "git",
    "integrations",
    "intelligence",
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
    "writer",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
