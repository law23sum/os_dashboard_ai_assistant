"""Simple unit tests for the Office router and local AI service."""
from assistant_core.integrations.office_realtime import (
    AIOfficeWebSocketRouter,
    ApplicationType,
    MessageType,
)
from assistant_core.intelligence.office_ai_service import OfficeAIProcessingService


def test_office_router_handles_ai_requests(tmp_path):
    service = OfficeAIProcessingService(workspace_dir=str(tmp_path))
    router = AIOfficeWebSocketRouter(ai_service_client=service.process_message)

    client = router.register_client(
        "client-1",
        ApplicationType.POWERPOINT,
        document_id="doc-123",
    )

    job_info = router.handle_ai_request(
        client.client_id,
        MessageType.AI_GENERATE_REQUEST,
        payload={"document_type": "powerpoint", "prompt": "Q4 update"},
    )

    result = router.get_ai_job_result(job_info["job_id"], timeout=5)
    assert result["success"] is True
    assert result["result"]["status"] in {"generated", "success", "simulated"}


def test_office_ai_service_analysis(tmp_path):
    service = OfficeAIProcessingService(workspace_dir=str(tmp_path))
    message = {
        "type": "ai_analyze_request",
        "source": "web_dashboard",
        "target": "word",
        "payload": {"text": "<h1>Hello</h1>"},
        "session_id": "test",
        "document_id": "doc-xyz",
    }
    response = service.process_message(message)
    assert response["status"] == "analyzed"
    assert "analysis" in response
    assert response["analysis"]["score"] <= 1.0
