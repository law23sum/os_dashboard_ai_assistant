"""Thin OpenAI client wrapper used across agents and tools."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from openai import OpenAI


class OpenAIClient:
    """Shared OpenAI client configured from environment variables."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self._client = OpenAI(api_key=self.api_key)

    def chat(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Send a chat completion request and return the raw response."""

        return self._client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )


def get_default_client() -> OpenAIClient:
    """Convenience for callers that need a quick client instance."""

    return OpenAIClient()


def chat(model: str, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
    """Convenience function for simple chat completions that returns just the content.

    This is a simpler interface for cases where you just need the text response.
    """
    client = get_default_client()
    response = client.chat(model=model, messages=messages, **kwargs)
    return response.choices[0].message.content or ""
