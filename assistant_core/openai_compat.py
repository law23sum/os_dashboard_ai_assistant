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
        if hasattr(completions, "create"):
            return completions.create(**kwargs)

        # If the provided client does not expose chat.completions (older helper or mock),
        # try the module-level OpenAI client helpers so we can still access the modern API.
        module_chat = getattr(openai, "chat", None)
        module_completions = getattr(module_chat, "completions", None) if module_chat else None
        module_create = getattr(module_completions, "create", None) if module_completions else None
        if callable(module_create):
            try:
                return module_create(**kwargs)
            except Exception:
                # We'll try alternate fallbacks below.
                pass

        # Fall back to constructing a fresh OpenAI client from the imported package.
        openai_client_cls = getattr(openai, "OpenAI", None)
        if openai_client_cls:
            try:
                client_kwargs = {}
                api_key = getattr(client, "api_key", None)
                if api_key:
                    client_kwargs["api_key"] = api_key
                organization = getattr(client, "organization", None)
                if organization:
                    client_kwargs["organization"] = organization
                project = getattr(client, "project", None)
                if project:
                    client_kwargs["project"] = project
                fresh_client = openai_client_cls(**client_kwargs)
                fresh_chat = getattr(fresh_client, "chat", None)
                fresh_completions = (
                    getattr(fresh_chat, "completions", None) if fresh_chat else None
                )
                if hasattr(fresh_completions, "create"):
                    return fresh_completions.create(**kwargs)
            except Exception:
                # Fall through to legacy handling if a fresh client cannot be created.
                pass

        legacy_chat = getattr(openai, "ChatCompletion", None)
        openai_version = getattr(openai, "__version__", "")
        is_legacy_version = openai_version.startswith("0.")
        if legacy_chat is not None and hasattr(legacy_chat, "create") and is_legacy_version:
            return legacy_chat.create(**kwargs)

        raise RuntimeError(
            "OpenAI client does not expose chat completions. Upgrade the integration "
            "to use `client.chat.completions.create(...)`, or install an openai "
            "package that still provides the legacy ChatCompletion API (< 1.0)."
        )

    try:
        completion = _create({**chat_kwargs, "max_completion_tokens": max_tokens})
    except (TypeError, APIError, AuthenticationError):
        completion = _create({**chat_kwargs, "max_tokens": max_tokens})

    choice = completion.choices[0]
    message = getattr(choice, "message", None) or (choice.get("message") if isinstance(choice, dict) else {})
    content = (message or {}).get("content") or ""
    return content.strip(), None
