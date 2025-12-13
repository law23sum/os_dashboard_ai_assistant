"""Tests for GPT-5 prompt scaffolding."""

import os
import unittest
from unittest.mock import patch


class TestPromptScaffold(unittest.TestCase):
    @patch.dict(
        os.environ,
        {
            "ASSISTANT_HUB_GPT5_PROMPT_SCAFFOLD": "1",
            "ASSISTANT_HUB_AGENTIC_EAGERNESS": "medium",
        },
        clear=False,
    )
    def test_scaffold_enabled_adds_marker(self):
        from assistant_core.ai import get_default_system_prompt

        prompt = get_default_system_prompt()
        assert "GPT5_PROMPT_SCAFFOLD_V1" in prompt
        assert "<tool_preambles>" in prompt

    @patch.dict(
        os.environ,
        {"ASSISTANT_HUB_GPT5_PROMPT_SCAFFOLD": "0"},
        clear=False,
    )
    def test_scaffold_disabled_does_not_add_marker(self):
        from assistant_core.ai import get_default_system_prompt, DEFAULT_SYSTEM_PROMPT

        prompt = get_default_system_prompt()
        assert prompt == DEFAULT_SYSTEM_PROMPT
        assert "GPT5_PROMPT_SCAFFOLD_V1" not in prompt

    @patch.dict(
        os.environ,
        {
            "ASSISTANT_HUB_GPT5_PROMPT_SCAFFOLD": "1",
            "ASSISTANT_HUB_AGENTIC_EAGERNESS": "low",
        },
        clear=False,
    )
    def test_low_eagerness_includes_budget_hint(self):
        from assistant_core.ai import get_default_system_prompt

        prompt = get_default_system_prompt()
        assert "max 2 tool calls" in prompt


if __name__ == "__main__":
    unittest.main()


