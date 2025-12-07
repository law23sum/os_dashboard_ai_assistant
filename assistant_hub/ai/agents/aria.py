from assistant_hub.ai.openai_client import OpenAIClient, OpenAIMessage
from assistant_hub.ai.prompts import SYSTEM_PROMPT


class AriaAgent:
    name = "aria"

    def __init__(self, client: OpenAIClient):
        self.client = client

    def handle(self, message: str) -> str:
        return self.client.chat([
            OpenAIMessage(role="system", content=SYSTEM_PROMPT),
            OpenAIMessage(role="user", content=f"Aria: {message}"),
        ])
