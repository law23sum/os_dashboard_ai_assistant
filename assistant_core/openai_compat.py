"""Shared OpenAI compatibility helpers.

Provides a single fall-back path for environments where the ``openai`` package
does not expose the newer Responses API. The helper translates the Responses
payload into a classic Chat Completions request and returns the assistant text.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

try:
    from openai import APIError, AuthenticationError  # type: ignore
except Exception:  # pragma: no cover - dependency missing
    APIError = Exception  # type: ignore
    AuthenticationError = Exception  # type: ignore


def _messages_from_responses_input(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """Convert ``responses`` input blocks into Chat Completions messages."""
    messages: List[Dict[str, str]] = []
    instructions = payload.get("instructions")
    if instructions:
        messages.append({"role": "system", "content": instructions})

    for item in payload.get("input", []):
        role = item.get("role", "user")
        content_blocks = item.get("content") or []
        text_parts = [
            block.get("text", "")
            for block in content_blocks
            if isinstance(block, dict) and block.get("type") == "input_text"
        ]
        messages.append({"role": role, "content": "\n".join(text_parts)})
    return messages


def legacy_chat_completion(
    client: Any,
    payload: Dict[str, Any],
) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
    """
    Execute a legacy Chat Completions request using the data prepared for the
    Responses API. Returns (text, tool_calls) where tool_calls is always None
    because classic completions cannot trigger functions.
    """
    try:
        import openai  # type: ignore
    except Exception as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            "OpenAI client does not expose the Responses API and the legacy "
            "ChatCompletion module could not be imported. Install/upgrade the "
            "`openai` package to enable AI features."
        ) from exc

    messages = _messages_from_responses_input(payload)
    chat_kwargs = {
        "model": payload.get("model"),
        "messages": messages,
        "temperature": payload.get("temperature", 0.2),
    }
    max_tokens = payload.get("max_output_tokens", 2000)

    def _create(kwargs: Dict[str, Any]):
        chat_client = getattr(client, "chat", None)
        completions = getattr(chat_client, "completions", None) if chat_client else None
        if callable(completions):
            return completions.create(**kwargs)
        return openai.ChatCompletion.create(**kwargs)

    try:
        completion = _create({**chat_kwargs, "max_completion_tokens": max_tokens})
    except (TypeError, APIError, AuthenticationError):
        completion = _create({**chat_kwargs, "max_tokens": max_tokens})

    choice = completion.choices[0]
    message = getattr(choice, "message", None) or (choice.get("message") if isinstance(choice, dict) else {})
    content = (message or {}).get("content") or ""
    return content.strip(), None
