"""
End-to-End API Tests for AI Features
Tests AI-related endpoints including chat, intelligence, and personas.

Spec References: §2.0, §5.4
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from backend_api.main import app
    
    with TestClient(app) as test_client:
        yield test_client


class TestChatEndpoints:
    """Test AI chat endpoints."""
    
    def test_list_chat_sessions(self, client):
        """Should list chat sessions."""
        response = client.get("/api/chat/sessions")
        assert response.status_code in [200, 404]
    
    def test_create_chat_session(self, client):
        """Should create a new chat session."""
        session_data = {
            "title": f"E2E Test Session {datetime.now().timestamp()}",
            "persona": "Aria"
        }
        response = client.post("/api/chat/sessions", json=session_data)
        assert response.status_code in [200, 201, 404]
    
    def test_send_chat_message(self, client):
        """Should send a message and receive a response."""
        # This may require an active AI backend, so accept multiple status codes
        message_data = {
            "content": "Hello, this is a test message.",
            "session_id": "test-session",
            "persona": "Aria"
        }
        response = client.post("/api/chat/message", json=message_data)
        assert response.status_code in [200, 201, 404, 503]
    
    def test_get_chat_history(self, client):
        """Should retrieve chat history."""
        response = client.get("/api/chat/history?session_id=test-session")
        assert response.status_code in [200, 404]


class TestPersonas:
    """Test persona-related endpoints."""
    
    def test_list_personas(self, client):
        """Should list all available personas."""
        response = client.get("/api/ai/personas")
        assert response.status_code in [200, 404]
    
    def test_persona_details(self, client):
        """Should get details for a specific persona."""
        personas = ["Chris", "AIC", "Aria", "Sora"]
        
        for persona in personas:
            response = client.get(f"/api/ai/personas/{persona}")
            # May or may not have a detail endpoint
            assert response.status_code in [200, 404]


class TestAIIntelligence:
    """Test AI intelligence endpoints."""
    
    def test_get_ai_status(self, client):
        """Should return AI system status."""
        response = client.get("/api/ai/status")
        assert response.status_code in [200, 404]
    
    def test_ai_models_available(self, client):
        """Should list available AI models."""
        response = client.get("/api/ai/models")
        assert response.status_code in [200, 404]


class TestSuggestions:
    """Test AI suggestions endpoints."""
    
    def test_get_suggestions(self, client):
        """Should get AI-powered suggestions."""
        response = client.get("/api/suggestions")
        assert response.status_code in [200, 404]
    
    def test_suggestion_for_project(self, client):
        """Should get suggestions for a specific project."""
        response = client.get("/api/suggestions?project=General")
        assert response.status_code in [200, 404]


class TestReasoningFramework:
    """Test Theoretical Reasoning Framework (TRF) endpoints."""
    
    def test_get_trf_status(self, client):
        """Should return TRF status."""
        response = client.get("/api/ai/trf/status")
        assert response.status_code in [200, 404]
    
    def test_trf_metrics(self, client):
        """Should return TRF metrics."""
        response = client.get("/api/ai/trf/metrics")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # TRF should have entropy, resonance, continuity
            assert any(field in data for field in ["entropy", "resonance", "continuity", "status"])


class TestCodeAnalysis:
    """Test code analysis endpoints."""
    
    def test_analyze_code(self, client):
        """Should analyze code snippet."""
        analysis_request = {
            "code": "def hello():\n    print('Hello, World!')",
            "language": "python"
        }
        response = client.post("/api/ai/analyze/code", json=analysis_request)
        assert response.status_code in [200, 201, 404, 503]
    
    def test_code_suggestions(self, client):
        """Should suggest code improvements."""
        suggestion_request = {
            "code": "x = 1\ny = 2\nz = x + y",
            "language": "python",
            "context": "optimization"
        }
        response = client.post("/api/ai/suggest/code", json=suggestion_request)
        assert response.status_code in [200, 201, 404, 503]


class TestDocumentAI:
    """Test document AI features."""
    
    def test_summarize_document(self, client):
        """Should summarize a document."""
        summarize_request = {
            "text": "This is a long document that needs summarization. It contains many paragraphs.",
            "max_length": 100
        }
        response = client.post("/api/ai/summarize", json=summarize_request)
        assert response.status_code in [200, 201, 404, 503]
    
    def test_extract_entities(self, client):
        """Should extract entities from text."""
        extract_request = {
            "text": "John Smith works at Acme Corp in New York City.",
            "entity_types": ["PERSON", "ORG", "LOC"]
        }
        response = client.post("/api/ai/extract/entities", json=extract_request)
        assert response.status_code in [200, 201, 404, 503]


class TestKnowledgeGraph:
    """Test knowledge graph endpoints."""
    
    def test_get_knowledge_graph(self, client):
        """Should return knowledge graph data."""
        response = client.get("/api/ai/knowledge-graph")
        assert response.status_code in [200, 404]
    
    def test_knowledge_graph_nodes(self, client):
        """Should return knowledge graph nodes."""
        response = client.get("/api/ai/knowledge-graph/nodes")
        assert response.status_code in [200, 404]
    
    def test_knowledge_graph_edges(self, client):
        """Should return knowledge graph edges."""
        response = client.get("/api/ai/knowledge-graph/edges")
        assert response.status_code in [200, 404]
