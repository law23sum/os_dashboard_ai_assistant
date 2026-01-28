"""Thin OpenAI client wrapper used across agents and tools."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from openai import OpenAI


def _split_system_instructions(messages: List[Dict[str, Any]]):
    instructions_parts: List[str] = []
    remaining: List[Dict[str, Any]] = []
    for msg in messages or []:
        if msg.get("role") == "system" and isinstance(msg.get("content"), str):
            instructions_parts.append(msg["content"])
        else:
            remaining.append(msg)
    instructions = "\n\n".join([p for p in instructions_parts if p.strip()]) or None
    return instructions, remaining


def _to_responses_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for msg in messages or []:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            converted: List[Dict[str, Any]] = []
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    converted.append({"type": "input_text", "text": block.get("text", "")})
                elif block.get("type") == "image_url":
                    image = block.get("image_url") or {}
                    url = image.get("url") if isinstance(image, dict) else None
                    if url:
                        converted.append({"type": "input_image", "image_url": url})
            items.append({"role": role, "content": converted})
            continue
        items.append({"role": role, "content": [{"type": "input_text", "text": str(content)}]})
    return items


def _extract_output_text(response: Any) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return str(response.output_text).strip()
    chunks: List[str] = []
    output = getattr(response, "output", None) or []
    for item in output:
        item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
        if item_type != "message":
            continue
        content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else None) or []
        for block in content:
            btype = getattr(block, "type", None) or (block.get("type") if isinstance(block, dict) else None)
            if btype == "output_text":
                text = getattr(block, "text", None) or (block.get("text") if isinstance(block, dict) else None) or ""
                if text:
                    chunks.append(str(text))
    return "\n".join(chunks).strip()


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
        """Legacy helper: call the Responses API and return the raw SDK response."""
        instructions, remaining = _split_system_instructions(messages)
        effort = kwargs.pop("reasoning_effort", os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none"))
        verbosity = kwargs.pop("verbosity", os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium"))
        max_tokens = kwargs.pop("max_tokens", None)
        temperature = kwargs.pop("temperature", None)

        payload: Dict[str, Any] = {
            "model": model,
            "instructions": instructions,
            "input": _to_responses_input(remaining),
            "reasoning": {"effort": effort},
            "text": {"verbosity": verbosity},
            "store": False,
        }
        if max_tokens is not None:
            payload["max_output_tokens"] = max_tokens
        if temperature is not None and effort == "none":
            payload["temperature"] = temperature
        payload.update(kwargs)
        return self._client.responses.create(**payload)


def get_default_client() -> OpenAIClient:
    """Convenience for callers that need a quick client instance."""

    return OpenAIClient()


def chat(model: str, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
    """Convenience function for simple chat completions that returns just the content.

    This is a simpler interface for cases where you just need the text response.
    """
    client = get_default_client()
    response = client.chat(model=model, messages=messages, **kwargs)
    return _extract_output_text(response) or ""
