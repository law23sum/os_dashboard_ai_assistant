"""Redaction utilities for audit payloads."""

from __future__ import annotations

import re
from typing import Any


REDACTED = "[REDACTED]"
SENSITIVE_KEYS = {
    "authorization",
    "auth",
    "token",
    "api_key",
    "apikey",
    "password",
    "secret",
    "private_key",
    "secret_key",
    "session",
    "cookie",
}

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"(?i)bearer\s+[a-z0-9\-_\.=]+"),
    re.compile(r"sk-[a-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"(?i)(api_key|apikey|token|password|secret)\s*[:=]\s*\S+"),
]


def _should_redact_key(key: str) -> bool:
    lowered = key.lower()
    if lowered in SENSITIVE_KEYS:
        return True
    return any(fragment in lowered for fragment in SENSITIVE_KEYS)


def _should_redact_value(value: str) -> bool:
    return any(pattern.search(value) for pattern in SENSITIVE_VALUE_PATTERNS)


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        redacted = {}
        for key, value in payload.items():
            if _should_redact_key(str(key)):
                redacted[key] = REDACTED
            else:
                redacted[key] = redact_payload(value)
        return redacted
    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]
    if isinstance(payload, str):
        return REDACTED if _should_redact_value(payload) else payload
    return payload
