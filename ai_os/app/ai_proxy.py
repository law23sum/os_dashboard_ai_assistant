"""Lightweight AI chat proxy mirroring the standalone Flask dashboard."""

from __future__ import annotations

import os
from typing import Any, Dict

try:  # Match the legacy implementation which uses requests directly
    import importlib

    _requests_mod = importlib.import_module("requests")
    if hasattr(_requests_mod, "post"):
        requests = _requests_mod  # type: ignore
    else:  # pragma: no cover - extremely unlikely
        requests = None
except Exception:  # pragma: no cover - keep API available even if requests missing
    requests = None  # type: ignore


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def ask_ai(prompt: str) -> Dict[str, Any]:
    """Send a chat request to OpenAI-compatible endpoint if configured."""

    prompt = (prompt or "").strip()
    if not prompt:
        return {"response": "Prompt is empty."}

    if not OPENAI_API_KEY or requests is None:
        return {"response": "AI service unavailable. Configure OPENAI_API_KEY."}

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - network errors
        return {"response": f"AI request failed: {exc}"}

    try:
        data = response.json()
    except ValueError:  # pragma: no cover - invalid JSON
        return {"response": "Invalid response from AI service."}

    message = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "No response")
    )
    return {"response": message, "raw": data}
