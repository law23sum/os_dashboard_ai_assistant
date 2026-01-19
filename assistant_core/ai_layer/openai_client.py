"""OpenAI/ChatGPT API Client for AI OS"""

import asyncio
import os
from typing import Dict, Any, List, Optional, Tuple
import openai
from openai import AsyncOpenAI

from config import get_api_config
from config.logging_config import setup_logger


def _split_system_instructions(
    messages: List[Dict[str, Any]],
) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    if not messages:
        return None, []
    instructions_parts: List[str] = []
    remaining: List[Dict[str, Any]] = []
    for msg in messages:
        role = msg.get("role")
        if role == "system" and isinstance(msg.get("content"), str):
            instructions_parts.append(msg["content"])
        else:
            remaining.append(msg)
    instructions = "\n\n".join([p for p in instructions_parts if p.strip()]) or None
    return instructions, remaining


def _to_responses_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for msg in messages or []:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            converted_blocks: List[Dict[str, Any]] = []
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    converted_blocks.append({"type": "input_text", "text": block.get("text", "")})
                elif block.get("type") == "image_url":
                    image = block.get("image_url") or {}
                    url = image.get("url") if isinstance(image, dict) else None
                    if url:
                        converted_blocks.append({"type": "input_image", "image_url": url})
            items.append({"role": role, "content": converted_blocks})
            continue
        items.append({"role": role, "content": [{"type": "input_text", "text": str(content)}]})
    return items


def _extract_output_text(response: Any) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return str(response.output_text).strip()
    chunks: List[str] = []
    output = getattr(response, "output", None) or []
    for item in output:
        item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
        if item_type != "message":
            continue
        content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else None) or []
        for block in content:
            btype = getattr(block, "type", None) or (block.get("type") if isinstance(block, dict) else None)
            if btype == "output_text":
                text = getattr(block, "text", None) or (block.get("text") if isinstance(block, dict) else None) or ""
                if text:
                    chunks.append(str(text))
    return "\n".join(chunks).strip()


def _extract_function_calls(response: Any) -> Optional[List[Dict[str, Any]]]:
    calls: List[Dict[str, Any]] = []
    output = getattr(response, "output", None) or []
    for item in output:
        item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
        if item_type != "function_call":
            continue
        call_id = getattr(item, "id", None) or (item.get("id") if isinstance(item, dict) else None)
        name = getattr(item, "name", None) or (item.get("name") if isinstance(item, dict) else None)
        arguments = getattr(item, "arguments", None) or (item.get("arguments") if isinstance(item, dict) else None)
        if not name:
            fn = getattr(item, "function", None) or (item.get("function") if isinstance(item, dict) else None) or {}
            name = getattr(fn, "name", None) or (fn.get("name") if isinstance(fn, dict) else None)
            if not arguments:
                arguments = getattr(fn, "arguments", None) or (fn.get("arguments") if isinstance(fn, dict) else None)
        if name:
            calls.append({"id": call_id, "name": name, "arguments": arguments or "{}"})
    return calls or None


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
                organization=self.config.openai_organization,
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
            await self.client.responses.create(
                model=self.config.openai_model,
                input="Hello",
                reasoning={"effort": "none"},
                max_output_tokens=8,
                store=False,
            )
            return True
        except Exception as e:
            self.logger.error(f"OpenAI health check failed: {e}")
            return False

    async def chat_completion(
        self,
        message: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        conversation_history: List[Dict[str, str]] = None,
    ) -> str:
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

            instructions, remaining = _split_system_instructions(messages)
            # GPT-5.2 supports: none, low, medium, high, xhigh
            effort = os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none")
            if effort not in ("none", "low", "medium", "high", "xhigh"):
                effort = "none"
            verbosity = os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium")
            if verbosity not in ("low", "medium", "high"):
                verbosity = "medium"
            
            response = await self.client.responses.create(
                model=self.config.openai_model,
                instructions=instructions,
                input=_to_responses_input(remaining),
                reasoning={"effort": effort},
                text={"verbosity": verbosity},
                temperature=temperature if effort == "none" else None,
                max_output_tokens=max_tokens,
                store=False,
            )
            return _extract_output_text(response)

        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}")
            raise

    async def generate_embeddings(
        self, texts: List[str], model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """Generate embeddings for text"""
        try:
            response = await self.client.embeddings.create(model=model, input=texts)

            return [embedding.embedding for embedding in response.data]

        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            raise

    async def analyze_image(
        self, image_url: str, prompt: str = "What's in this image?"
    ) -> str:
        """Analyze image using the configured multimodal model via Responses API."""
        try:
            # GPT-5.2 supports: none, low, medium, high, xhigh
            effort = os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none")
            if effort not in ("none", "low", "medium", "high", "xhigh"):
                effort = "none"
            verbosity = os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium")
            if verbosity not in ("low", "medium", "high"):
                verbosity = "medium"
            
            response = await self.client.responses.create(
                model=self.config.openai_model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_image", "image_url": image_url},
                        ],
                    }
                ],
                reasoning={"effort": effort},
                text={"verbosity": verbosity},
                max_output_tokens=600,
                store=False,
            )
            return _extract_output_text(response)

        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            raise

    async def function_calling(
        self, message: str, functions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use OpenAI function calling (Responses API custom tools)."""
        try:
            tools = [{"type": "function", "function": fn} for fn in (functions or [])]
            # GPT-5.2 supports: none, low, medium, high, xhigh
            effort = os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none")
            if effort not in ("none", "low", "medium", "high", "xhigh"):
                effort = "none"
            verbosity = os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium")
            if verbosity not in ("low", "medium", "high"):
                verbosity = "medium"
            
            # Support allowed_tools for constraining tool usage (GPT-5.2 feature)
            tool_choice = "auto" if tools else None
            allowed_tools_env = os.getenv("ASSISTANT_HUB_ALLOWED_TOOLS")
            if allowed_tools_env and tools:
                try:
                    import json
                    allowed_tools_list = json.loads(allowed_tools_env)
                    if isinstance(allowed_tools_list, list):
                        tool_choice = {
                            "type": "allowed_tools",
                            "mode": os.getenv("ASSISTANT_HUB_TOOL_CHOICE_MODE", "auto"),
                            "tools": allowed_tools_list,
                        }
                except Exception:
                    pass
            
            response = await self.client.responses.create(
                model=self.config.openai_model,
                input=[{"role": "user", "content": [{"type": "input_text", "text": message}]}],
                tools=tools or None,
                tool_choice=tool_choice,
                reasoning={"effort": effort},
                text={"verbosity": verbosity},
                max_output_tokens=800,
                store=False,
            )

            calls = _extract_function_calls(response)
            return {
                "message": _extract_output_text(response),
                "function_call": calls[0] if calls else None,
            }

        except Exception as e:
            self.logger.error(f"Function calling failed: {e}")
            raise

    async def create_assistant(
        self, name: str, instructions: str, tools: List[str] = None
    ) -> Dict[str, Any]:
        """
        DEPRECATED: Create an OpenAI Assistant using the legacy Assistants API.
        
        The Assistants API is deprecated and will be shut down on August 26, 2026.
        Migrate to the Responses API using Prompts instead.
        
        Migration guide: https://platform.openai.com/docs/assistants/migration
        
        Key changes:
        - Assistants → Prompts (create/manage in OpenAI dashboard, reference by ID)
        - Threads → Conversations
        - Runs → Responses
        - Use client.responses.create() with prompt_id parameter instead
        
        This method is kept for backward compatibility only.
        """
        import warnings
        warnings.warn(
            "create_assistant() uses the deprecated Assistants API. "
            "Migrate to Responses API with Prompts. "
            "See: https://platform.openai.com/docs/assistants/migration",
            DeprecationWarning,
            stacklevel=2
        )
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
                model=self.config.openai_model,
            )

            return {
                "id": assistant.id,
                "name": assistant.name,
                "instructions": assistant.instructions,
            }

        except Exception as e:
            self.logger.error(f"Assistant creation failed: {e}")
            raise

    async def create_conversation(
        self, items: Optional[List[Dict[str, Any]]] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Conversation object for persistent chat state.
        
        Conversations replace Threads in the Responses API and can store items
        (messages, tool calls, outputs) for long-running context.
        
        Args:
            items: Initial conversation items (messages, tool calls, etc.)
            metadata: Optional metadata to attach to the conversation
            
        Returns:
            Conversation object with id and metadata
        """
        try:
            payload: Dict[str, Any] = {}
            if items:
                payload["items"] = items
            if metadata:
                payload["metadata"] = metadata
                
            conversation = await self.client.conversations.create(**payload)
            return {
                "id": conversation.id,
                "object": conversation.object,
                "created_at": conversation.created_at,
                "metadata": getattr(conversation, "metadata", {}),
            }
        except Exception as e:
            self.logger.error(f"Conversation creation failed: {e}")
            raise

    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Retrieve a conversation by ID."""
        try:
            conversation = await self.client.conversations.retrieve(conversation_id)
            return {
                "id": conversation.id,
                "object": conversation.object,
                "created_at": conversation.created_at,
                "metadata": getattr(conversation, "metadata", {}),
            }
        except Exception as e:
            self.logger.error(f"Conversation retrieval failed: {e}")
            raise

    async def shutdown(self):
        """Shutdown OpenAI client"""
        if self.client:
            await self.client.close()
        self.logger.info("OpenAI client shutdown complete")

    # Backward compatibility methods
    def chat(
        self, model: str, messages: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Legacy helper: call the Responses API but return the raw SDK response object."""
        # For backward compatibility, create a sync client.
        sync_client = openai.OpenAI(
            api_key=self.config.openai_api_key,
            organization=self.config.openai_organization,
        )
        instructions, remaining = _split_system_instructions(messages)
        effort = kwargs.pop("reasoning_effort", os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none"))
        verbosity = kwargs.pop("verbosity", os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium"))
        max_tokens = kwargs.pop("max_tokens", None)
        temperature = kwargs.pop("temperature", None)

        payload: Dict[str, Any] = {
            "model": model,
            "instructions": instructions,
            "input": _to_responses_input(remaining),
            "reasoning": {"effort": effort},
            "text": {"verbosity": verbosity},
            "store": False,
        }
        if max_tokens is not None:
            payload["max_output_tokens"] = max_tokens
        if temperature is not None and effort == "none":
            payload["temperature"] = temperature
        payload.update(kwargs)
        return sync_client.responses.create(**payload)


def get_default_client() -> OpenAIClient:
    """Convenience for callers that need a quick client instance."""
    return OpenAIClient()


def chat(model: str, messages: List[Dict[str, Any]], **kwargs: Any) -> str:
    """Convenience function for simple chat completions that returns just the text response.

    This is a simpler interface for cases where you just need the text response.
    """
    client = get_default_client()
    response = client.chat(model=model, messages=messages, **kwargs)
    return _extract_output_text(response) or ""
