"""Tool registry placeholder for the assistant."""
from __future__ import annotations

from typing import Callable, Dict


class ToolRegistry:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., str]] = {}

    def register(self, name: str, fn: Callable[..., str]) -> None:
        self.tools[name] = fn

    def invoke(self, name: str, *args, **kwargs) -> str:
        if name not in self.tools:
            raise KeyError(f"Tool {name} not registered")
        return self.tools[name](*args, **kwargs)
