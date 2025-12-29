from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_app_exposes_runtime_diagnostics_endpoint():
    from assistant_hub.api.server import create_app

    app = create_app()
    client = TestClient(app)

    payload = {
        "source": "pytest",
        "message": "hello",
        "severity": "error",
        "context": {"k": "v"},
    }
    response = client.post("/api/runtime/diagnostics", json=payload)
    assert response.status_code == 202


def test_shell_tools_are_responses_api_compatible():
    from assistant_core.ai import get_shell_functions

    tools = get_shell_functions("/tmp")
    assert tools, "expected at least one tool definition"
    for tool in tools:
        assert tool.get("type") == "function"
        # Responses API requires the tool name at the top-level, not nested under "function".
        assert tool.get("name"), "missing tool.name (Responses API requirement)"
        assert "parameters" in tool and isinstance(tool["parameters"], dict)
