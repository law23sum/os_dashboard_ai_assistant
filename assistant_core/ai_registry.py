"""Shared agent model registry for discussion and routing helpers."""

from __future__ import annotations

from assistant_hub.db import (
    PERSONAL_AI_PERSONAS,
    GENERIC_AI_PERSONAS,
    CHAT_PERSONAS,
    GENERIC_AI_PROVIDERS,
)
from .ai import AGENT_MODELS, AGENT_MODEL_FALLBACKS, DEFAULT_MODEL

__all__ = [
    "AGENT_MODELS",
    "AGENT_MODEL_FALLBACKS",
    "DEFAULT_MODEL",
    "PERSONAL_AI_PERSONAS",
    "GENERIC_AI_PERSONAS",
    "CHAT_PERSONAS",
    "GENERIC_AI_PROVIDERS",
]
