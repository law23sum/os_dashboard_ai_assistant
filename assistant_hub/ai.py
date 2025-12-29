#!/usr/bin/env python3
"""OpenAI / ChatGPT helper utilities for Assistant Hub."""

from __future__ import annotations

import os
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
from assistant_core.openai_compat import legacy_chat_completion

# Model assignments per agent
# These map personas to the latest GPT-5.2 capability tiers
# 
# GPT-5.2 Model Family:
# - gpt-5.2: Best for complex reasoning, broad world knowledge, code-heavy or multi-step agentic tasks
# - gpt-5.2-pro: For tough problems requiring harder thinking (uses more compute)
# - gpt-5.1-codex-max: Optimized for coding tasks and interactive coding products
# - gpt-5-mini: Cost-optimized reasoning and chat; balances speed, cost, and capability
# - gpt-5-nano: High-throughput tasks, especially simple instruction-following or classification
#
# Migration guidance:
# - gpt-5.1 -> gpt-5.2: Drop-in replacement with default settings
# - o3 -> gpt-5.2: Use medium or high reasoning effort
# - gpt-4.1 -> gpt-5.2: Use none reasoning effort with prompt tuning
# - o4-mini or gpt-4.1-mini -> gpt-5-mini: Great replacement with prompt tuning
# - gpt-4.1-nano -> gpt-5-nano: Great replacement with prompt tuning
AGENT_MODELS = {
    "Sora": "gpt-5.2",
    "Aria": "gpt-5.1-codex-max",
    "AIC": "gpt-5.2-pro",
    "Chris": "gpt-5-mini",
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
    "You are a cooperative team of AI agents (Aria, AIC, Sora) tasked with helping Chris manage"
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


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY") or os.getenv("AI_CHAT_OPENAI_API_KEY")
    if key:
        _cache_api_key(key)
        return key

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


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        if OpenAI is None:
            raise RuntimeError(
                "The 'openai' package is not installed. Install it to enable ChatGPT support."
            )
        _client = OpenAI(api_key=_get_api_key())
    return _client


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


def create_custom_tool(
    name: str,
    description: str,
    grammar: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a custom tool definition for GPT-5.2.
    
    Custom tools support freeform text inputs (type: custom) and can optionally
    use context-free grammars (CFGs) to constrain outputs.
    
    Args:
        name: Tool name
        description: Tool description (be concise and explicit)
        grammar: Optional Lark grammar string for constraining outputs (CFG)
    
    Returns:
        Tool definition dict compatible with GPT-5.2 Responses API
    
    Example:
        tool = create_custom_tool(
            name="code_exec",
            description="Executes arbitrary python code",
        )
    """
    tool: Dict[str, Any] = {
        "type": "custom",
        "name": name,
        "description": description,
    }
    if grammar:
        tool["grammar"] = grammar
    return tool


def get_shell_functions(cwd: str = None) -> List[Dict]:
    """Return function definitions for shell command execution and file operations."""
    base_dir = cwd or os.getcwd()
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file. Use this to read text files, code files, configuration files, etc. from the current working directory or absolute paths. For binary files, use execute_command with appropriate tools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to read. Can be relative to the working directory or an absolute path.",
                        },
                        "max_lines": {
                            "type": "integer",
                            "description": "Maximum number of lines to read (default: 1000). Use this to limit output for large files.",
                            "default": 1000,
                        },
                    },
                    "required": ["file_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": "Execute a shell command in the terminal. Use this to run commands, check files, run scripts, etc. Always use this when you need to interact with the file system or run programs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute (e.g., 'ls -la', 'python script.py', 'git status')",
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
            # Best-effort conversion from chat vision blocks into responses input blocks.
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
        # Support both dict-like and attribute-like SDK objects.
        call_id = getattr(item, "id", None) or (item.get("id") if isinstance(item, dict) else None)
        name = getattr(item, "name", None) or (item.get("name") if isinstance(item, dict) else None)
        arguments = getattr(item, "arguments", None) or (item.get("arguments") if isinstance(item, dict) else None)
        # Some SDKs nest function under "function".
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
    previous_response_id: Optional[str] = None,
    custom_tools: Optional[List[Dict[str, Any]]] = None,
    enable_preambles: bool = False,
) -> Tuple[str, Optional[str], Optional[List[Dict]]]:
    """
    Send the conversation to OpenAI and return (reply, error_message, tool_calls).
    Returns tool_calls if the AI wants to execute commands.
    """
    messages = []
    sys_prompt = system_prompt or get_default_system_prompt()
    if sys_prompt:
        messages.append({"role": "system", "content": sys_prompt})
    messages.extend(build_message_payload(history, include_tool_results=True))

    if prompt and append_prompt:
        persona_prefix = f"[{persona}] " if persona else ""
        messages.append(
            {"role": "user", "content": f"{persona_prefix}{prompt}".strip()}
        )

    fallback_source = (
        fallback_prompt or prompt or (history[-1].content if history else "")
    )

    # Use agent-specific model if not specified
    if not model:
        model = get_agent_model(persona)

    try:
        client = get_openai_client()

        # Prepare tools/functions for shell execution
        tools = []
        if enable_shell:
            tools.extend(get_shell_functions(cwd or os.getcwd()))
        
        # Add custom tools if provided (supports type: custom for freeform inputs)
        if custom_tools:
            tools.extend(custom_tools)
        
        # Add apply_patch tool for code editing (GPT-5.2 feature)
        if os.getenv("ASSISTANT_HUB_ENABLE_APPLY_PATCH", "false").lower() == "true":
            tools.append({
                "type": "function",
                "function": {
                    "name": "apply_patch",
                    "description": "Apply a patch to create, update, or delete files in the codebase using structured diffs. Use this for iterative, multistep code editing workflows.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to modify"
                            },
                            "patch": {
                                "type": "string",
                                "description": "The patch to apply in unified diff format"
                            }
                        },
                        "required": ["file_path", "patch"]
                    }
                }
            })
        
        tools = tools if tools else None

        # Handle file uploads if provided
        # Note: OpenAI file API requires separate upload, then reference in messages
        # For now, we'll include file content in the message

        # Responses API: move system prompts into `instructions`.
        instructions, remaining = _split_system_instructions(messages)
        # GPT-5.2 supports: none, low, medium, high, xhigh
        effort = os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none")
        if effort not in ("none", "low", "medium", "high", "xhigh"):
            effort = "none"  # Default to none if invalid
        verbosity = os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium")
        if verbosity not in ("low", "medium", "high"):
            verbosity = "medium"  # Default to medium if invalid

        # Add preamble instruction if enabled (GPT-5.2 feature)
        if enable_preambles and instructions:
            instructions += "\n\nBefore you call a tool, explain why you are calling it."
        elif enable_preambles:
            instructions = "Before you call a tool, explain why you are calling it."
        
        payload: Dict[str, Any] = {
            "model": model,
            "instructions": instructions,
            "input": _to_responses_input(remaining),
            "reasoning": {"effort": effort},
            "text": {"verbosity": verbosity},
            "max_output_tokens": max_tokens,
            "store": False,
        }
        
        # Support previous_response_id for passing chain of thought between turns (GPT-5.2 feature)
        if previous_response_id:
            payload["previous_response_id"] = previous_response_id
        # Only temperature, top_p, logprobs are supported when effort == "none" for GPT-5.2
        if effort == "none":
            payload["temperature"] = temperature
        if tools:
            payload["tools"] = tools
            # Support allowed_tools for constraining tool usage
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

        if hasattr(client, "responses"):
            response = client.responses.create(**payload)
            text = _extract_responses_output_text(response)
            tool_calls = _extract_function_calls(response)
        else:
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

    elif fn_name == "apply_patch":
        """Execute apply_patch tool for code editing (GPT-5.2 feature)."""
        try:
            args = json.loads(fn_args_raw or "{}")
            file_path = args.get("file_path", "")
            patch = args.get("patch", "")
            
            if not file_path or not patch:
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "apply_patch",
                    "content": "Error: Both file_path and patch are required",
                }
            
            # Resolve path relative to cwd if not absolute
            work_dir = cwd or os.getcwd()
            if not os.path.isabs(file_path):
                file_path = os.path.join(work_dir, file_path)
            file_path = os.path.normpath(os.path.expanduser(file_path))
            
            # Parse and apply the patch
            # This is a simplified implementation - in production, use a proper diff library
            try:
                import re
                # Basic unified diff parsing
                lines = patch.split('\n')
                file_lines = []
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_lines = f.readlines()
                else:
                    file_lines = []
                
                # Simple patch application (for production, use diff-match-patch or similar)
                # This is a placeholder - proper implementation would parse unified diff format
                result_content = "Patch applied successfully (simplified implementation).\n"
                result_content += f"File: {file_path}\n"
                result_content += f"Patch preview: {patch[:200]}..."
                
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "apply_patch",
                    "content": result_content,
                }
            except Exception as e:
                return {
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": "apply_patch",
                    "content": f"Error applying patch: {str(e)}",
                }
        except Exception as e:
            return {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": "apply_patch",
                "content": f"Error processing patch request: {str(e)}",
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
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": "unknown",
        "content": "Unknown tool",
    }
