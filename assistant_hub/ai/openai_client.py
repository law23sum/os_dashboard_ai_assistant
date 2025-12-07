"""Minimal OpenAI client wrapper used by agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from assistant_hub.config import OpenAIConfig


@dataclass
class OpenAIMessage:
    role: str
    content: str


class OpenAIClient:
    def __init__(self, config: OpenAIConfig):
        self.config = config

    def chat(self, messages: List[OpenAIMessage], tools: Optional[List[Dict[str, Any]]] = None) -> str:
        # This is a scaffold: return a deterministic echo for now.
        transcript = "\n".join(f"{m.role}: {m.content}" for m in messages)
        tool_hint = f" with tools {', '.join(t['name'] for t in tools)}" if tools else ""
        return f"[simulated {self.config.model} response{tool_hint}]\n{transcript}"
