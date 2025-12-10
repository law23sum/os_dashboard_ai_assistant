#!/usr/bin/env python3
"""OpenAI / ChatGPT helper utilities for Assistant Hub."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from openai import APIError, AuthenticationError, OpenAI  # type: ignore
except Exception:  # pragma: no cover - handled gracefully when dependency missing.
    OpenAI = None  # type: ignore

    class APIError(Exception):
        pass

    class AuthenticationError(Exception):
        pass


from .db import ChatMessage, CHAT_ROLES, PERSONAS
from .terminal import run_bash_command

# Model assignments per agent
# Note: o1 models require special handling (no system messages, different API)
AGENT_MODELS = {
    "Sora": "gpt-4o",  # Using gpt-4o (closest to "5.1" - latest GPT-4)
    "Aria": "gpt-4o",
    "AIC": "o1-mini",  # Using o1-mini for reasoning model (latest stable o1)
    "Chris": "gpt-4o-mini",  # Default for human user
}

# Fallback models if primary model unavailable
AGENT_MODEL_FALLBACKS = {
    "AIC": "gpt-4o",  # Fallback if o1-mini unavailable
}

DEFAULT_MODEL = os.getenv("ASSISTANT_HUB_OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_SYSTEM_PROMPT = os.getenv(
    "ASSISTANT_HUB_SYSTEM_PROMPT",
    "You are a cooperative team of AI agents (Aria, AIC, Sora) tasked with helping Chris manage"
    " priorities, code, and research. Explain your thinking clearly, cite concrete next steps,"
    " and keep answers concise and actionable. You have access to a shell terminal and can execute"
    " commands when needed. You can also read files directly using the read_file function, or use"
    " execute_command to run shell commands. Files in the current working directory (browse directory)"
    " are accessible to you.",
)

_client: Optional[OpenAI] = None


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY") or os.getenv("AI_CHAT_OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "OpenAI API key missing. Set OPENAI_API_KEY or AI_CHAT_OPENAI_API_KEY in your environment."
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
) -> Tuple[str, Optional[str], Optional[List[Dict]]]:
    """
    Send the conversation to OpenAI and return (reply, error_message, tool_calls).
    Returns tool_calls if the AI wants to execute commands.
    """
    messages = []
    sys_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
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
        tools = None
        if enable_shell:
            tools = get_shell_functions(cwd or os.getcwd())

        # Handle file uploads if provided
        # Note: OpenAI file API requires separate upload, then reference in messages
        # For now, we'll include file content in the message

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)

        message = response.choices[0].message
        text = message.content or ""
        tool_calls = (
            message.tool_calls
            if hasattr(message, "tool_calls") and message.tool_calls
            else None
        )

        return text.strip(), None, tool_calls
    except (AuthenticationError, APIError, ValueError, RuntimeError) as exc:
        return _offline_reply(fallback_source or "(empty prompt)", exc), str(exc), None


def execute_tool_call(tool_call, cwd: Optional[str] = None) -> Dict:
    """Execute a tool call (shell command or file operation) and return the result."""
    import json

    if tool_call.function.name == "read_file":
        try:
            args = json.loads(tool_call.function.arguments)
            file_path = args.get("file_path", "")
            max_lines = args.get("max_lines", 1000)

            if not file_path:
                return {
                    "tool_call_id": tool_call.id,
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
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": "read_file",
                    "content": f"Error: File not found: {file_path}",
                }

            if not os.path.isfile(file_path):
                return {
                    "tool_call_id": tool_call.id,
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
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "read_file",
                        "content": f"File: {file_path}\nTotal lines: {total_lines}\n\n{content}",
                    }
            except UnicodeDecodeError:
                # Binary file - suggest using execute_command with appropriate tool
                return {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": "read_file",
                    "content": f"Error: File appears to be binary or not text-encoded: {file_path}. Use execute_command with appropriate tools (e.g., 'file', 'hexdump', 'strings') to inspect binary files.",
                }
        except Exception as e:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_file",
                "content": f"Error reading file: {str(e)}",
            }

    elif tool_call.function.name == "execute_command":
        try:
            args = json.loads(tool_call.function.arguments)
            command = args.get("command", "")
            work_dir = args.get("working_directory", cwd) or cwd or os.getcwd()

            if not command:
                return {
                    "tool_call_id": tool_call.id,
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
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "execute_command",
                "content": content,
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call.id,
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
