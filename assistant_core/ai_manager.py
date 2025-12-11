"""AI Manager - Handles all interactions with the LLM (ChatGPT/OpenAI)."""

from typing import Dict, Any, Optional
from .ai_layer.openai_client import OpenAIClient


class AIManager:
    """Manages AI interactions and prompt handling."""

    def __init__(self):
        self.client = OpenAIClient()

    def format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with provided variables."""
        return template.format(**kwargs)

    def send_prompt(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Send a prompt to the AI service and return the response."""
        return self.client.send_request(prompt, **kwargs)

    def parse_response(self, response: Dict[str, Any]) -> str:
        """Parse the AI response into a usable format."""
        if "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]
        return ""
