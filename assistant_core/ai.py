#!/usr/bin/env python3
"""OpenAI / ChatGPT helper utilities for Assistant Hub."""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    from openai import APIError, AuthenticationError, OpenAI  # type: ignore
except Exception:  # pragma: no cover - handled gracefully when dependency missing.
    OpenAI = None  # type: ignore

    class APIError(Exception):
        pass

    class AuthenticationError(Exception):
        pass


from .db import (
    ChatMessage,
    CHAT_ROLES,
    PERSONAS,
    init_db,
    load_openai_api_key,
    save_openai_api_key,
)
from .terminal import run_bash_command
from .prompting.gpt5_scaffold import (
    GPT5ScaffoldOptions,
    apply_gpt5_prompting_scaffold,
)
from .openai_compat import legacy_chat_completion
from config.config import get_api_config  # Import global config

# Try to import Anthropic
try:
    from anthropic import Anthropic, APIError as AnthropicAPIError
except ImportError:
    Anthropic = None
    class AnthropicAPIError(Exception): pass

class AIAssistant:
    """AI assistant façade used by the CLI, GUI, and tests."""

    def __init__(self, app_state: Any | None = None, *, persona: Optional[str] = None):
        self.app_state = app_state
        self.persona = (
            persona
            or getattr(app_state, "active_persona", None)
            or os.getenv("ASSISTANT_DEFAULT_PERSONA", "AIC")
        )
        self.history: List[ChatMessage] = []
        self.openai_available = openai_available()

    def add_message(
        self, content: str, *, role: str = "user", kind: str = "chat"
    ) -> ChatMessage:
        message = ChatMessage(
            id=len(self.history) + 1,
            persona=self.persona,
            role=role,
            kind=kind,
            content=content,
        )
        self.history.append(message)
        return message

    def reply(self, prompt: str) -> str:
        try:
            response, error, _ = generate_ai_reply(
                self.history, self.persona, prompt=prompt
            )
            if error:
                return error
            return response
        except Exception:
            return f"[offline] {prompt}"


# Model assignments per agent
# These map each persona to the new GPT-5/5.2 capability tiers
AGENT_MODELS = {
    "Sora": "gpt-5.2",  # Complex reasoning + planning
    "Aria": "gpt-5.1-codex-max",  # Coding + content polish
    "AIC": "gpt-5.2-pro",  # Deep reasoning / agentic control
    "Chris": "gpt-5-mini",  # Cost-optimized default chat
}

# Fallback models if primary model unavailable
AGENT_MODEL_FALLBACKS = {
    "AIC": "gpt-5.2",
    "Sora": "gpt-5-mini",
    "Aria": "gpt-5-mini",
    "Chris": "gpt-5-nano",
}

DEFAULT_MODEL = os.getenv("ASSISTANT_HUB_OPENAI_MODEL", "gpt-5-mini")
DEFAULT_SYSTEM_PROMPT = os.getenv(
    "ASSISTANT_HUB_SYSTEM_PROMPT",
    "You are a cooperative team of AI agents (Aria, AIC, Sora, Data Science) tasked with helping Chris manage"
    " priorities, code, and research. Explain your thinking clearly, cite concrete next steps,"
    " and keep answers concise and actionable. You have access to a shell terminal and can execute"
    " commands when needed. You can also read files directly using the read_file function, or use"
    " execute_command to run shell commands. Files in the current working directory (browse directory)"
    " are accessible to you.",
)


def _env_flag(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in ("0", "false", "no", "off")


def get_default_system_prompt() -> str:
    """Return the default system prompt, optionally wrapped with GPT-5 scaffolding."""
    base = DEFAULT_SYSTEM_PROMPT
    if not _env_flag("ASSISTANT_HUB_GPT5_PROMPT_SCAFFOLD", True):
        return base
    eagerness = os.getenv("ASSISTANT_HUB_AGENTIC_EAGERNESS", "medium")
    return apply_gpt5_prompting_scaffold(
        base,
        options=GPT5ScaffoldOptions(
            agentic_eagerness=eagerness, tools=["read_file", "execute_command"]
        ),
    )

_client: Optional[OpenAI] = None


def _cache_api_key(key: str) -> None:
    """Persist the key in the DB for future sessions."""
    try:
        conn = init_db()
    except Exception:
        return
    try:
        existing = load_openai_api_key(conn)
        if existing != key:
            save_openai_api_key(conn, key)
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _fetch_key_from_db() -> Optional[str]:
    try:
        conn = init_db()
    except Exception:
        return None
    try:
        return load_openai_api_key(conn)
    except Exception:
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _running_under_pytest() -> bool:
    """Return True when executed inside a pytest session."""
    return "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY") or os.getenv("AI_CHAT_OPENAI_API_KEY")
    if key:
        _cache_api_key(key)
        return key

    # When tests are running, avoid pulling keys from the local DB to keep expectations deterministic.
    if _running_under_pytest():
        raise ValueError(
            "OpenAI API key missing. Set OPENAI_API_KEY or AI_CHAT_OPENAI_API_KEY in your environment."
        )

    key = _fetch_key_from_db()
    if not key:
        raise ValueError(
            "OpenAI API key missing. Set OPENAI_API_KEY or AI_CHAT_OPENAI_API_KEY in your environment, "
            "or store one in the database via assistant_hub.db.save_openai_api_key()."
        )
    return key


def openai_available() -> bool:
    """Return True if the OpenAI client can be instantiated."""
    if OpenAI is None:
        return False
    try:
        _ = _get_api_key()
    except Exception:
        return False
    return True


def get_openai_client(provider: str = "openai") -> OpenAI:
    global _client
    # We might need multiple clients for different providers, so we can't just cache one global _client 
    # if we are switching providers. For now, we'll instantiate fresh or use a dict cache if needed.
    # To keep it simple, we will return a new client for non-OpenAI providers.
    
    config = get_api_config()
    
    if provider == "openai":
        if _client is None:
            if OpenAI is None:
                raise RuntimeError("The 'openai' package is not installed.")
            _client = OpenAI(api_key=_get_api_key())
        return _client
        
    elif provider == "xai":
        if not config.xai_api_key:
            raise ValueError("xAI API key missing.")
        return OpenAI(
            api_key=config.xai_api_key,
            base_url="https://api.x.ai/v1"
        )
        
    elif provider == "deepseek":
        if not config.deepseek_api_key:
            raise ValueError("DeepSeek API key missing.")
        return OpenAI(
            api_key=config.deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
        
    elif provider == "groq":
        if not config.groq_api_key:
            raise ValueError("Groq API key missing.")
        return OpenAI(
            api_key=config.groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
    elif provider == "cohere":
        if not config.cohere_api_key:
             raise ValueError("Cohere API key missing.")
        # Cohere V2 is partially compatible but might need specific tweaks. 
        # Using native url for now if compatible, otherwise this might fail.
        return OpenAI(
            api_key=config.cohere_api_key,
            base_url="https://api.cohere.com/v2" 
        )

    # Default to OpenAI
    return get_openai_client("openai")


def get_anthropic_client() -> Anthropic:
    if Anthropic is None:
        raise RuntimeError("The 'anthropic' package is not installed.")
    
    config = get_api_config()
    if not config.anthropic_api_key:
        raise ValueError("Anthropic API key missing.")
        
    return Anthropic(api_key=config.anthropic_api_key)


def build_message_payload(
    history: List[ChatMessage],
    max_messages: int = 30,
    include_tool_results: bool = True,
) -> List[Dict]:
    """Convert stored history into OpenAI chat messages, including terminal output and tool results."""
    payload: List[Dict] = []
    recent = history[-max_messages:] if max_messages else history
    for msg in recent:
        role = msg.role if msg.role in CHAT_ROLES else "user"
        persona_marker = f"[{msg.persona}] " if msg.persona else ""
        content = f"{persona_marker}{msg.content}".strip()

        # Include terminal context in messages
        if msg.kind in ("terminal", "terminal_result"):
            content = f"[TERMINAL {msg.kind.upper()}]\n{content}"

        msg_dict = {"role": role, "content": content}

        # Handle tool results
        if msg.kind == "tool_result" and include_tool_results:
            # Tool results need tool_call_id - we'll extract from content if possible
            # For now, just include as tool role
            msg_dict["role"] = "tool"

        payload.append(msg_dict)
    return payload


def get_agent_model(persona: str) -> str:
    """Get the assigned model for a persona."""
    return AGENT_MODELS.get(persona, DEFAULT_MODEL)


def get_shell_functions(cwd: str = None) -> List[Dict]:
    """Return Responses API function tool definitions for shell + file operations."""
    base_dir = cwd or os.getcwd()
    return [
        {
            "type": "function",
            "name": "read_file",
            "description": (
                "Read the contents of a file. Use this to read text files, code files, configuration files, etc. "
                "from the current working directory or absolute paths. For binary files, use execute_command with "
                "appropriate tools."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "Path to the file to read. Can be relative to the working directory or an absolute path."
                        ),
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": (
                            "Maximum number of lines to read (default: 1000). Use this to limit output for large files."
                        ),
                        "default": 1000,
                    },
                },
                "required": ["file_path"],
            },
        },
        {
            "type": "function",
            "name": "execute_command",
            "description": (
                "Execute a shell command in the terminal. Use this to run commands, check files, run scripts, etc. "
                "Always use this when you need to interact with the file system or run programs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            "The shell command to execute (e.g., 'ls -la', 'python script.py', 'git status')"
                        ),
                    },
                    "working_directory": {
                        "type": "string",
                        "description": f"Working directory for the command (default: {base_dir})",
                        "default": base_dir,
                    },
                },
                "required": ["command"],
            },
        },
    ]


def _offline_reply(prompt: str, error: Exception) -> str:
    preview = prompt.strip().splitlines()
    preview_text = preview[0][:140] if preview else ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        "(offline fallback) "
        f"{timestamp}: Unable to reach OpenAI ({error}). "
        f"Message captured: '{preview_text}'."
    )


def _split_system_instructions(messages: List[Dict[str, Any]]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Extract system messages into a single instructions string for the Responses API."""
    if not messages:
        return None, []
    instructions_parts: List[str] = []
    remaining: List[Dict[str, Any]] = []
    for msg in messages:
        if msg.get("role") == "system" and isinstance(msg.get("content"), str):
            instructions_parts.append(msg["content"])
        else:
            remaining.append(msg)
    instructions = "\n\n".join([p for p in instructions_parts if p.strip()]) or None
    return instructions, remaining


def _to_responses_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert chat messages to Responses API input item format (text-first)."""
    items: List[Dict[str, Any]] = []
    for msg in messages or []:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            converted: List[Dict[str, Any]] = []
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    converted.append({"type": "input_text", "text": block.get("text", "")})
                elif block.get("type") == "image_url":
                    image = block.get("image_url") or {}
                    url = image.get("url") if isinstance(image, dict) else None
                    if url:
                        converted.append({"type": "input_image", "image_url": url})
            items.append({"role": role, "content": converted})
            continue
        items.append({"role": role, "content": [{"type": "input_text", "text": str(content)}]})
    return items


def _extract_responses_output_text(response: Any) -> str:
    """Best-effort extraction of assistant text from a Responses API response."""
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
    """Extract custom function calls from `response.output` (Responses API)."""
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


def generate_ai_reply(
    history: List[ChatMessage],
    persona: str,
    prompt: Optional[str] = None,
    *,
    append_prompt: bool = True,
    fallback_prompt: Optional[str] = None,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 2000,
    cwd: Optional[str] = None,
    enable_shell: bool = True,
    file_paths: Optional[List[str]] = None,
    conversation_id: Optional[str] = None,
    previous_response_id: Optional[str] = None,
    uploaded_file_ids: Optional[List[str]] = None,
    vector_store_ids: Optional[List[str]] = None,
    enable_code_interpreter: bool = False,
    enable_file_search: bool = False,
    image_urls: Optional[List[str]] = None,
    image_file_ids: Optional[List[str]] = None,
    image_detail: str = "auto",
    model_provider: str = "openai",
    # GPT-5.2 features
    custom_tools: Optional[List[Dict[str, Any]]] = None,
    enable_preambles: bool = False,
) -> Tuple[str, Optional[str], Optional[List[Dict]]]:
    """
    Send the conversation to AI Provider and return (reply, error_message, tool_calls).
    Returns tool_calls if the AI wants to execute commands.
    """
    
    # Handle Anthropic separately
    if model_provider == "anthropic":
        try:
            client = get_anthropic_client()
            # Convert history to Anthropic format
            anthropic_messages = []
            system_msg = system_prompt or get_default_system_prompt()
            
            for msg in history:
                role = "assistant" if msg.role == "assistant" else "user"
                # Anthropic doesn't support system messages in the messages list usually (they go to top level system param)
                # It also doesn't support tool results the same way yet in this simple implementation
                if msg.role != "system": 
                     anthropic_messages.append({"role": role, "content": msg.content})
            
            # Add current prompt
            if prompt and append_prompt:
                anthropic_messages.append({"role": "user", "content": prompt})

            response = client.messages.create(
                model=get_api_config().anthropic_model or "claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg,
                messages=anthropic_messages
            )
            
            return response.content[0].text, None, None
            
        except Exception as e:
             return _offline_reply(prompt or "", e), str(e), None

    # Handle Google (Simple REST fallback)
    if model_provider == "google":
        import requests
        try:
            config = get_api_config()
            if not config.google_api_key:
                raise ValueError("Google API key missing")
                
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.google_model or 'gemini-1.5-pro-latest'}:generateContent?key={config.google_api_key}"
            
            # Simple conversion
            contents = []
            for msg in history:
                 if msg.role == "user":
                     contents.append({"role": "user", "parts": [{"text": msg.content}]})
                 elif msg.role == "assistant":
                     contents.append({"role": "model", "parts": [{"text": msg.content}]})
            
            if prompt and append_prompt:
                contents.append({"role": "user", "parts": [{"text": prompt}]})
                
            response = requests.post(url, json={"contents": contents})
            if response.status_code != 200:
                raise Exception(f"Google API Error: {response.text}")
                
            data = response.json()
            text = data.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")
            return text, None, None
            
        except Exception as e:
             return _offline_reply(prompt or "", e), str(e), None

    messages = []
    sys_prompt = system_prompt or get_default_system_prompt()
    if sys_prompt:
        messages.append({"role": "system", "content": sys_prompt})
    messages.extend(build_message_payload(history, include_tool_results=True))

    if prompt and append_prompt:
        persona_prefix = f"[{persona}] " if persona else ""
        prompt_text = f"{persona_prefix}{prompt}".strip()
        
        # Handle multimodal input (text + images)
        if image_urls or image_file_ids:
            content = [{"type": "input_text", "text": prompt_text}]
            
            # Add image URLs
            if image_urls:
                for img_url in image_urls:
                    content.append({
                        "type": "input_image",
                        "image_url": {
                            "url": img_url,
                            "detail": image_detail,
                        },
                    })
            
            # Add image file IDs
            if image_file_ids:
                for file_id in image_file_ids:
                    content.append({
                        "type": "input_image",
                        "image_file": {
                            "file_id": file_id,
                            "detail": image_detail,
                        },
                    })
            
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": prompt_text})

    fallback_source = (
        fallback_prompt or prompt or (history[-1].content if history else "")
    )

    # Use agent-specific model if not specified
    if not model and model_provider == "openai":
        model = get_agent_model(persona)
    
    # Set default models for other providers if not provided
    if not model:
        config = get_api_config()
        if model_provider == "xai": model = config.xai_model or "grok-1"
        elif model_provider == "deepseek": model = "deepseek-chat"
        elif model_provider == "groq": model = config.groq_model or "llama3-70b-8192"
        elif model_provider == "cohere": model = "command-r-plus"


    # Check for Data Science Agent routing
    data_science_keywords = [
        "machine learning",
        "ml",
        "dataset",
        "model training",
        "predict",
        "classification",
        "regression",
        "clustering",
        "feature",
        "algorithm",
        "hyperparameter",
        "automl",
        "data science",
        "experiment",
        "deploy model",
        "train model",
        "accuracy",
        "precision",
        "recall",
        "f1 score",
        "cross validation",
        "feature importance",
        "data drift",
    ]

    is_data_science_query = any(
        keyword in (prompt or "").lower() for keyword in data_science_keywords
    )

    if is_data_science_query and model_provider == "openai":
        try:
            from .ai_layer.agents import DataScienceAgent

            agent = DataScienceAgent()

            # Extract context from the conversation
            context = {}
            if file_paths:
                context["file_paths"] = file_paths
            if hasattr(history, "cwd") or cwd:
                context["cwd"] = cwd or getattr(history, "cwd", None)

            response = asyncio.run(agent.process_request(prompt or "", context))
            return response, None, None
        except Exception as e:
            # If agent fails, fall back to regular OpenAI processing
            pass

    try:
        client = get_openai_client(model_provider)

        # Prepare tools/functions for shell execution
        tools = []
        # Shell tools only for OpenAI/compatible usually, unless we adapt
        if enable_shell and model_provider in ["openai", "xai", "deepseek", "groq"]:
            tools.extend(get_shell_functions(cwd or os.getcwd()))
        
        # Add custom tools if provided (GPT-5.2 feature)
        if custom_tools:
            tools.extend(custom_tools)
        
        # Add code_interpreter tool if enabled
        if enable_code_interpreter and model_provider == "openai":
            code_tool: Dict[str, Any] = {"type": "code_interpreter"}
            if uploaded_file_ids:
                code_tool["code_interpreter"] = {"file_ids": uploaded_file_ids[:20]}  # Max 20 files
            tools.append(code_tool)
        
        # Add file_search tool if enabled
        if enable_file_search and vector_store_ids and model_provider == "openai":
            tools.append({
                "type": "file_search",
                "file_search": {"vector_store_ids": vector_store_ids},
            })
        
        tools = tools if tools else None

        # Handle file uploads if provided
        # Note: OpenAI file API requires separate upload, then reference in messages
        # For now, we'll include file content in the message

        instructions, remaining = _split_system_instructions(messages)
        # GPT-5.2 supports: none, low, medium, high, xhigh
        effort = os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none")
        if effort not in ("none", "low", "medium", "high", "xhigh"):
            effort = "none"
        verbosity = os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium")
        if verbosity not in ("low", "medium", "high"):
            verbosity = "medium"
        
        # Add preamble instruction if enabled (GPT-5.2 feature)
        if enable_preambles and instructions:
            instructions += "\n\nBefore you call a tool, explain why you are calling it."
        elif enable_preambles:
            instructions = "Before you call a tool, explain why you are calling it."

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages, # Standard Chat Completions API uses 'messages', not 'input' usually. Wait, existing code used Responses API?
            # The existing code seemed to use `client.responses.create` which is likely an internal or preview API wrapper for the user.
            # But standard OpenAI python client uses `client.chat.completions.create`.
            # I need to check `client.responses`. 
            # If `client.responses` exists, it's a specific wrapper. If not, I should use `chat.completions`.
            # For other providers (DeepSeek, etc), we definitely want `chat.completions`.
        }
        
        # FIX: The existing code used `client.responses.create` with `input` and `instructions`. 
        # This looks like a specific custom wrapper or a very new/different API shape.
        # However, for broader compatibility, I should use `chat.completions.create`.
        # I will switch to `chat.completions.create` for non-OpenAI providers or if `responses` is missing.
        
        use_standard_chat = model_provider != "openai" or not hasattr(client, "responses")
        
        if use_standard_chat:
             payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
             }
             if tools:
                 payload["tools"] = tools
                 payload["tool_choice"] = "auto"
                 
             response = client.chat.completions.create(**payload)
             text = response.choices[0].message.content
             tool_calls = response.choices[0].message.tool_calls
             # Adapter for tool calls format if needed
             if tool_calls:
                 tool_calls = [
                     {"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments} 
                     for tc in tool_calls
                 ]
        else:
            # Existing OpenAI Logic (Responses API?)
            payload = {
                "model": model,
                "instructions": instructions,
                "input": _to_responses_input(remaining),
                "reasoning": {"effort": effort},
                "text": {"verbosity": verbosity},
                "max_output_tokens": max_tokens,
                "store": False,
            }
            if effort == "none":
                payload["temperature"] = temperature
            if tools:
                payload["tools"] = tools
                # Support allowed_tools for constraining tool usage (GPT-5.2 feature)
                allowed_tools_env = os.getenv("ASSISTANT_HUB_ALLOWED_TOOLS")
                if allowed_tools_env:
                    try:
                        import json
                        allowed_tools_list = json.loads(allowed_tools_env)
                        if isinstance(allowed_tools_list, list):
                            payload["tool_choice"] = {
                                "type": "allowed_tools",
                                "mode": os.getenv("ASSISTANT_HUB_TOOL_CHOICE_MODE", "auto"),
                                "tools": allowed_tools_list,
                            }
                        else:
                            payload["tool_choice"] = "auto"
                    except Exception:
                        payload["tool_choice"] = "auto"
                else:
                    payload["tool_choice"] = "auto"
            
            if conversation_id:
                payload["conversation"] = conversation_id
                payload["store"] = True
            elif previous_response_id:
                payload["previous_response_id"] = previous_response_id

            if hasattr(client, "responses"):
                response = client.responses.create(**payload)
                text = _extract_responses_output_text(response)
                tool_calls = _extract_function_calls(response)
            else:
                 # Fallback to standard chat completion if client doesn't have responses
                if isinstance(payload.get("model"), str) and payload["model"].startswith("gpt-5"):
                    payload = dict(payload)
                    payload["model"] = os.getenv("ASSISTANT_HUB_OPENAI_LEGACY_MODEL", "gpt-4o-mini")
                text, tool_calls = legacy_chat_completion(client, payload)

        return text.strip(), None, tool_calls
    except (AuthenticationError, APIError, ValueError, RuntimeError) as exc:
        return _offline_reply(fallback_source or "(empty prompt)", exc), str(exc), None


def execute_tool_call(tool_call, cwd: Optional[str] = None) -> Dict:
    """Execute a tool call (shell command or file operation) and return the result."""
    import json

    # Support both Chat Completions tool_call objects and Responses API dict payloads.
    if isinstance(tool_call, dict):
        fn_name = tool_call.get("name")
        fn_args_raw = tool_call.get("arguments", "{}")
        tool_call_id = tool_call.get("id")
    else:
        fn_name = tool_call.function.name
        fn_args_raw = tool_call.function.arguments
        tool_call_id = tool_call.id

    if fn_name == "read_file":
        try:
            args = json.loads(fn_args_raw or "{}")
            file_path = args.get("file_path", "")
            max_lines = args.get("max_lines", 1000)

            if not file_path:
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "read_file",
                    "content": "Error: No file path provided",
                }

            # Resolve path relative to cwd if not absolute
            work_dir = cwd or os.getcwd()
            if not os.path.isabs(file_path):
                file_path = os.path.join(work_dir, file_path)

            file_path = os.path.normpath(os.path.expanduser(file_path))

            if not os.path.exists(file_path):
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "read_file",
                    "content": f"Error: File not found: {file_path}",
                }

            if not os.path.isfile(file_path):
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "read_file",
                    "content": f"Error: Path is not a file: {file_path}",
                }

            # Try to read as text
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                    total_lines = len(lines)

                    if total_lines > max_lines:
                        content = "".join(lines[:max_lines])
                        content += f"\n\n[File truncated: showing first {max_lines} of {total_lines} total lines]"
                    else:
                        content = "".join(lines)

                    return {
                        "tool_call_id": tool_call_id,
                        "role": "tool",
                        "name": "read_file",
                        "content": f"File: {file_path}\nTotal lines: {total_lines}\n\n{content}",
                    }
            except UnicodeDecodeError:
                # Binary file - suggest using execute_command with appropriate tool
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "read_file",
                    "content": f"Error: File appears to be binary or not text-encoded: {file_path}. Use execute_command with appropriate tools (e.g., 'file', 'hexdump', 'strings') to inspect binary files.",
                }
        except Exception as e:
            return {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": "read_file",
                "content": f"Error reading file: {str(e)}",
            }

    elif fn_name == "execute_command":
        try:
            args = json.loads(fn_args_raw or "{}")
            command = args.get("command", "")
            work_dir = args.get("working_directory", cwd) or cwd or os.getcwd()

            if not command:
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "execute_command",
                    "content": "Error: No command provided",
                }

            result = run_bash_command(command, cwd=work_dir)

            output_parts = []
            if result.stdout:
                output_parts.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")
            if not output_parts:
                output_parts.append("(no output)")

            output_parts.append(f"\nExit code: {result.returncode}")
            content = "\n".join(output_parts)

            return {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": "execute_command",
                "content": content,
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": "execute_command",
                "content": f"Error executing command: {str(e)}",
            }

    return {
        "tool_call_id": tool_call_id,
        "role": "tool",
        "name": "unknown",
        "content": "Unknown tool",
    }
class AssistantSession:
    """Lightweight AI assistant wrapper for tests and integrations."""

    def __init__(self, persona: str = "AIC"):
        self.persona = persona
        self.history: List[ChatMessage] = []

    def add_message(self, content: str, *, role: str = "user", kind: str = "chat") -> ChatMessage:
        """Record a message in the assistant history."""
        message = ChatMessage(
            id=len(self.history) + 1,
            persona=self.persona,
            role=role,
            kind=kind,
            content=content,
        )
        self.history.append(message)
        return message

    def reply(self, prompt: str) -> str:
        """Generate a reply using the existing helper or echo fallback."""
        try:
            response, error, _ = generate_ai_reply(self.history, self.persona, prompt=prompt)
            if error:
                return error
            return response
        except Exception:
            # In constrained environments fall back to deterministic echo
            return f"[offline] {prompt}"
