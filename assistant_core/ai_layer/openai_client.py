"""OpenAI/ChatGPT API Client for OS Dashboard AI Assistant"""

import asyncio
from typing import Dict, Any, List, Optional
import openai
from openai import AsyncOpenAI

from config import get_api_config
from logging_config import setup_logger


class OpenAIClient:
    """OpenAI API client for ChatGPT integration"""

    def __init__(self):
        self.config = get_api_config()
        self.logger = setup_logger("OpenAIClient")
        self.client: Optional[AsyncOpenAI] = None

    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            self.client = AsyncOpenAI(
                api_key=self.config.openai_api_key,
                organization=self.config.openai_organization
            )

            # Test connection
            await self.health_check()
            self.logger.info("OpenAI client initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible"""
        try:
            # Simple test call
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            self.logger.error(f"OpenAI health check failed: {e}")
            return False

    async def chat_completion(self, message: str, system_prompt: str = None,
                            temperature: float = 0.7, max_tokens: int = 1000,
                            conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate chat completion"""
        try:
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current message
            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}")
            raise

    async def generate_embeddings(self, texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
        """Generate embeddings for text"""
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )

            return [embedding.embedding for embedding in response.data]

        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            raise

    async def analyze_image(self, image_url: str, prompt: str = "What's in this image?") -> str:
        """Analyze image using GPT-4 Vision"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            raise

    async def function_calling(self, message: str, functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use OpenAI function calling"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": message}],
                functions=functions,
                function_call="auto"
            )

            return {
                "message": response.choices[0].message.content,
                "function_call": response.choices[0].message.function_call
            }

        except Exception as e:
            self.logger.error(f"Function calling failed: {e}")
            raise

    async def create_assistant(self, name: str, instructions: str, tools: List[str] = None) -> Dict[str, Any]:
        """Create an OpenAI Assistant"""
        try:
            assistant_tools = []
            if tools:
                for tool in tools:
                    if tool == "code_interpreter":
                        assistant_tools.append({"type": "code_interpreter"})
                    elif tool == "retrieval":
                        assistant_tools.append({"type": "retrieval"})

            assistant = await self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=assistant_tools,
                model=self.config.openai_model
            )

            return {
                "id": assistant.id,
                "name": assistant.name,
                "instructions": assistant.instructions
            }

        except Exception as e:
            self.logger.error(f"Assistant creation failed: {e}")
            raise

    async def shutdown(self):
        """Shutdown OpenAI client"""
        if self.client:
            await self.client.close()
        self.logger.info("OpenAI client shutdown complete")

    # Backward compatibility methods
    def chat(self, model: str, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Send a chat completion request and return the raw response (synchronous wrapper)"""
        # For backward compatibility, create a sync client
        sync_client = openai.OpenAI(
            api_key=self.config.openai_api_key,
            organization=self.config.openai_organization
        )
        return sync_client.chat.completions.create(model=model, messages=messages, **kwargs)


def get_default_client() -> OpenAIClient:
    """Convenience for callers that need a quick client instance."""
    return OpenAIClient()


def chat(model: str, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
    """Convenience function for simple chat completions that returns just the text response.

    This is a simpler interface for cases where you just need the text response.
    """
    client = get_default_client()
    response = client.chat(model=model, messages=messages, **kwargs)
    return response.choices[0].message.content or ""
