"""Tests for AI assistant functionality."""

import unittest
import os
from unittest.mock import patch, MagicMock
from assistant_core.ai import (
    AIAssistant, openai_available, get_openai_client, get_agent_model,
    build_message_payload, _get_api_key, AGENT_MODELS, DEFAULT_MODEL
)
from assistant_core.core.state import ApplicationState


class TestAIAssistant(unittest.TestCase):
    """Test cases for AIAssistant class."""

    def test_initialization(self):
        """Test AIAssistant initialization with app state."""
        app_state = ApplicationState()
        ai_assistant = AIAssistant(app_state)

        assert ai_assistant.app_state == app_state
        assert hasattr(ai_assistant, 'openai_available')
        assert isinstance(ai_assistant.openai_available, bool)

    @patch('assistant_core.ai.OpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_openai_available_with_key(self, mock_openai):
        """Test openai_available returns True when OpenAI is available and key exists."""
        result = openai_available()
        assert result is True

    @patch('assistant_core.ai.OpenAI', None)
    def test_openai_available_without_openai(self):
        """Test openai_available returns False when OpenAI is not installed."""
        result = openai_available()
        assert result is False

    @patch('assistant_core.ai._fetch_key_from_db', return_value=None)
    @patch.dict(os.environ, {}, clear=True)
    def test_openai_available_without_key(self, mock_fetch):
        """Test openai_available returns False when API key is missing."""
        result = openai_available()
        assert result is False

    @patch('assistant_core.ai.OpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_get_openai_client(self, mock_openai_class):
        """Test get_openai_client creates and returns OpenAI client."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        client = get_openai_client()

        assert client == mock_client
        mock_openai_class.assert_called_once_with(api_key='test-key')

    @patch('assistant_core.ai.OpenAI', None)
    @patch('assistant_core.ai._client', None)
    def test_get_openai_client_no_openai(self):
        """Test get_openai_client raises error when OpenAI not installed."""
        with self.assertRaises(RuntimeError) as context:
            get_openai_client()
        self.assertIn("The 'openai' package is not installed", str(context.exception))

    @patch('assistant_core.ai._fetch_key_from_db', return_value=None)
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_missing(self, mock_fetch):
        """Test _get_api_key raises error when no API key is set."""
        with self.assertRaises(ValueError) as context:
            _get_api_key()
        self.assertIn("OpenAI API key missing", str(context.exception))

    @patch.dict(os.environ, {'OPENAI_API_KEY': '', 'AI_CHAT_OPENAI_API_KEY': 'test-key'})
    def test_get_api_key_alternate_env_var(self):
        """Test _get_api_key uses alternate environment variable."""
        key = _get_api_key()
        assert key == 'test-key'

    def test_get_agent_model(self):
        """Test get_agent_model returns correct model for persona."""
        assert get_agent_model("Sora") == "gpt-5.2"
        assert get_agent_model("Aria") == "gpt-5.1-codex-max"
        assert get_agent_model("AIC") == "gpt-5.2-pro"
        assert get_agent_model("Chris") == "gpt-5-mini"
        assert get_agent_model("Unknown") == DEFAULT_MODEL

    def test_build_message_payload(self):
        """Test build_message_payload converts chat messages to OpenAI format."""
        from assistant_core.db import ChatMessage

        # Create mock messages
        messages = [
            ChatMessage(id=1, role="user", content="Hello", persona="Chris", kind="chat"),
            ChatMessage(id=2, role="assistant", content="Hi there!", persona="Aria", kind="chat"),
        ]

        payload = build_message_payload(messages)

        assert len(payload) == 2
        assert payload[0]["role"] == "user"
        assert "[Chris] Hello" in payload[0]["content"]
        assert payload[1]["role"] == "assistant"
        assert "[Aria] Hi there!" in payload[1]["content"]

    def test_build_message_payload_with_terminal(self):
        """Test build_message_payload handles terminal messages."""
        from assistant_core.db import ChatMessage

        messages = [
            ChatMessage(id=1, role="user", content="ls -la", persona="Chris", kind="terminal"),
        ]

        payload = build_message_payload(messages)

        assert len(payload) == 1
        assert "[TERMINAL TERMINAL]" in payload[0]["content"]

    def test_build_message_payload_tool_results(self):
        """Test build_message_payload handles tool result messages."""
        from assistant_core.db import ChatMessage

        messages = [
            ChatMessage(id=1, role="tool", content="Command output", persona=None, kind="tool_result"),
        ]

        payload = build_message_payload(messages)

        assert len(payload) == 1
        assert payload[0]["role"] == "tool"

    def test_build_message_payload_max_messages(self):
        """Test build_message_payload respects max_messages limit."""
        from assistant_core.db import ChatMessage

        messages = [
            ChatMessage(id=i, role="user", content=f"Message {i}", persona=None, kind="chat")
            for i in range(10)
        ]

        payload = build_message_payload(messages, max_messages=5)

        assert len(payload) == 5
        assert "Message 5" in payload[0]["content"]  # Should start from message 5
