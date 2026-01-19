from assistant_core.tooling_patterns import build_tool_examples, heuristic_triage
from assistant_core.guardrails import GuardrailConfig, evaluate_guardrails


def test_build_tool_examples_payload():
    payload = build_tool_examples()
    assert payload["tools"]
    assert payload["examples"]
    assert "openapi_hint" in payload


def test_heuristic_triage_prioritizes_aic(monkeypatch):
    monkeypatch.setenv("AGENTS_MAX_RESPONDERS", "2")
    decision = heuristic_triage("Implement system integration with reliable execution.")
    assert decision.agents[0] == "AIC"


def test_guardrails_detects_blocked_phrase():
    config = GuardrailConfig(blocked_phrases=["api key"])
    result = evaluate_guardrails("Never share your API key in logs.", config)
    assert result.allowed is False
    assert result.violations
