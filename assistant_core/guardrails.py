"""Lightweight guardrails for response validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GuardrailViolation:
    """Represents a single guardrail violation."""

    rule: str
    detail: str


@dataclass
class GuardrailConfig:
    """Configuration for static guardrail checks."""

    blocked_phrases: List[str] = field(
        default_factory=lambda: [
            "api key",
            "password",
            "secret",
            "private key",
            "ssh-rsa",
            "rm -rf",
            "drop database",
            "truncate table",
        ]
    )
    max_response_chars: Optional[int] = None
    require_safe_language: bool = True


@dataclass
class GuardrailResult:
    """Result of guardrail validation."""

    allowed: bool
    score: float
    violations: List[GuardrailViolation] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def evaluate_guardrails(
    response_text: str, config: Optional[GuardrailConfig] = None
) -> GuardrailResult:
    """Evaluate a response against static guardrails."""

    config = config or GuardrailConfig()
    normalized = _normalize(response_text)
    violations: List[GuardrailViolation] = []

    for phrase in config.blocked_phrases:
        phrase_norm = _normalize(phrase)
        if phrase_norm and phrase_norm in normalized:
            violations.append(
                GuardrailViolation(
                    rule="blocked_phrase",
                    detail=f"Found blocked phrase: '{phrase}'",
                )
            )

    if config.max_response_chars is not None and len(response_text) > config.max_response_chars:
        violations.append(
            GuardrailViolation(
                rule="max_response_chars",
                detail=f"Response length {len(response_text)} exceeds {config.max_response_chars}",
            )
        )

    if config.require_safe_language and response_text.strip().startswith("rm -rf"):
        violations.append(
            GuardrailViolation(
                rule="unsafe_prefix",
                detail="Response begins with a destructive shell command",
            )
        )

    score = max(0.0, 1.0 - (0.2 * len(violations)))
    allowed = len(violations) == 0

    notes = []
    if not response_text.strip():
        notes.append("Empty response text provided.")
    if not config.blocked_phrases:
        notes.append("No blocked phrases configured.")

    return GuardrailResult(allowed=allowed, score=score, violations=violations, notes=notes)
