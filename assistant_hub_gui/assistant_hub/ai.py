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

# Token limits for ChatGPT API requests only (TPM limits)
# TPM limit: 30,000 tokens per minute
# Reserve 17% (5,100 tokens) for responses, use 83% (24,900 tokens) for input
# This maximizes input tokens while safely leaving room for output
MAX_INPUT_TOKENS = int(os.getenv("ASSISTANT_HUB_MAX_INPUT_TOKENS", "24900"))


def estimate_tokens(text: str) -> int:
    """
    Estimate token count from text.
    Rough approximation: ~4 characters per token for English text.
    This is conservative and ensures we stay under limits.
    """
    if not text:
        return 0
    # Add overhead for message formatting (role, formatting chars)
    return len(text) // 4 + 50


def truncate_messages_for_api(
    messages: List[Dict], max_tokens: int = MAX_INPUT_TOKENS
) -> List[Dict]:
    """
    Truncate messages payload to stay within token limit before sending to ChatGPT API.
    Always keeps system message and recent messages, removes older messages first.

    Args:
        messages: List of message dicts with 'role' and 'content'
        max_tokens: Maximum tokens allowed (default: MAX_INPUT_TOKENS)

    Returns:
        Truncated messages list that fits within token limit
    """
    if not messages:
        return messages

    # Always keep system message if present
    system_msg = None
    if messages and messages[0].get("role") == "system":
        system_msg = messages[0]
        messages_to_process = messages[1:]
    else:
        messages_to_process = messages

    # Estimate tokens for system message
    system_tokens = estimate_tokens(system_msg.get("content", "")) if system_msg else 0

    # Start with system message and work backwards from most recent
    truncated = []
    total_tokens = system_tokens

    # Process messages from newest to oldest
    for msg in reversed(messages_to_process):
        content = msg.get("content", "")
        msg_tokens = estimate_tokens(content)

        # Always keep at least the last 3 messages even if over limit
        if total_tokens + msg_tokens > max_tokens and len(truncated) >= 3:
            break

        truncated.insert(0, msg)
        total_tokens += msg_tokens

    # Add system message back if it was present
    if system_msg:
        truncated.insert(0, system_msg)

    return truncated


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
    " commands when needed. Use the execute_command function to run shell commands.\n\n"
    "IMPORTANT: Do not apologize for delays or mention delays. Do not say things like 'I apologize for the delay'"
    " or 'I'll proceed with modifications right now' or 'Thank you for your patience'. Just think and act directly."
    " Execute tasks immediately without meta-commentary about timing or process.",
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
    max_messages: int = 100,
    include_tool_results: bool = True,
) -> List[Dict]:
    """Convert stored history into OpenAI chat messages, including terminal output and tool results."""
    payload: List[Dict] = []
    recent = history[-max_messages:] if max_messages else history

    # Track the previous message to ensure tool results follow assistant messages
    prev_msg_dict = None

    for i, msg in enumerate(recent):
        role = msg.role if msg.role in CHAT_ROLES else "user"
        persona_marker = f"[{msg.persona}] " if msg.persona else ""
        raw_content = msg.content

        # Handle tool results - they must follow an assistant message with tool_calls
        # OpenAI API requires: tool messages must have tool_call_id and follow assistant messages with tool_calls
        if msg.kind == "tool_result" and include_tool_results:
            # Check if previous message in history was an assistant message
            # (We can't verify tool_calls from stored history, so we'll be conservative)
            prev_was_assistant = False
            if i > 0:
                prev_msg = recent[i - 1]
                prev_was_assistant = prev_msg.role == "assistant"

            # Try to extract tool_call_id from content if it was stored there
            tool_call_id = None
            extracted_content = None

            import json

            try:
                # Try parsing as JSON first (new format)
                parsed = json.loads(raw_content)
                if isinstance(parsed, dict) and "tool_call_id" in parsed:
                    tool_call_id = parsed["tool_call_id"]
                    extracted_content = parsed.get("content", "")
            except:
                # Not JSON, try text format like "tool_call_id: xxx\ncontent"
                if "tool_call_id" in raw_content:
                    lines = raw_content.split("\n", 1)
                    for line in lines:
                        if (
                            line.startswith("tool_call_id:")
                            or "tool_call_id" in line.lower()
                        ):
                            parts = line.split(":", 1)
                            if len(parts) > 1:
                                tool_call_id = parts[1].strip()
                                if len(lines) > 1:
                                    extracted_content = lines[1]
                                break

            # Use extracted content if available, otherwise use raw content
            final_content = (
                extracted_content if extracted_content is not None else raw_content
            )

            # Be very conservative: only create tool message if we have both conditions
            # Since we can't verify tool_calls from stored history, we'll be extra safe
            # and only create tool messages when we're in a recent sequence that makes sense
            # For now, convert all tool_result messages to assistant messages to avoid API errors
            # This is safer than risking invalid tool messages
            content_with_marker = f"{persona_marker}{raw_content}".strip()
            if tool_call_id:
                # Include tool_call_id in content for context, but use assistant role
                msg_dict = {
                    "role": "assistant",
                    "content": f"[Tool Result (ID: {tool_call_id})] {content_with_marker}",
                }
            else:
                msg_dict = {
                    "role": "assistant",
                    "content": f"[Tool Result] {content_with_marker}",
                }
        else:
            # Regular message handling
            content = f"{persona_marker}{raw_content}".strip()

            # Include terminal context in messages
            if msg.kind in ("terminal", "terminal_result"):
                content = f"[TERMINAL {msg.kind.upper()}]\n{content}"

            msg_dict = {"role": role, "content": content}

        payload.append(msg_dict)
        prev_msg_dict = msg_dict

    return payload


def get_agent_model(persona: str) -> str:
    """Get the assigned model for a persona."""
    return AGENT_MODELS.get(persona, DEFAULT_MODEL)


def get_shell_functions(cwd: str = None) -> List[Dict]:
    """Return function definitions for shell command execution."""
    return [
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
                            "description": f"Working directory for the command (default: {cwd or os.getcwd()})",
                            "default": cwd or os.getcwd(),
                        },
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_displayed_file",
                "description": "Read the content of the file currently displayed in the document preview panel. Use this when the user mentions a document they have open or displayed. Returns the full content of the displayed file.",
                "parameters": {"type": "object", "properties": {}, "required": []},
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
    max_tokens: int = 4000,  # Increased from 2000 for better responses
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

        # Truncate messages to stay within token limit before sending to ChatGPT API
        # This is the ONLY place we limit tokens - everything else stays unlimited
        messages = truncate_messages_for_api(messages, max_tokens=MAX_INPUT_TOKENS)

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


def execute_tool_call(
    tool_call, cwd: Optional[str] = None, gui_context: Optional[Dict] = None
) -> Dict:
    """
    Execute a tool call (shell command) and return the result.

    Args:
        tool_call: The tool call object from OpenAI
        cwd: Optional working directory
        gui_context: Optional context from GUI (e.g., active_file_session for read_displayed_file)
    """
    if tool_call.function.name == "read_displayed_file":
        # Handle reading displayed file - requires GUI context
        if not gui_context:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": "No GUI context available. Cannot read displayed file.",
            }

        active_session = gui_context.get("active_file_session")
        if not active_session:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": "No file is currently displayed in the document preview panel. Please open a file first using the 'Open Document' button or by having the AI open a file.",
            }

        file_path = active_session.get("path")
        file_type = active_session.get("type", "Unknown")

        if not file_path or not os.path.exists(file_path):
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": f"No valid file path available. File path: {file_path}",
            }

        # Try to read the file
        try:
            # Use the GUI's file reading method if available
            read_file_func = gui_context.get("read_file_func")
            if read_file_func:
                content = read_file_func(file_path, file_type)
            else:
                # Fallback: read file directly (basic text reading)
                if file_type == "PDF":
                    # Try pdfplumber first (more robust with corrupted PDFs)
                    content = ""
                    try:
                        import pdfplumber

                        with pdfplumber.open(file_path) as pdf:
                            for i, page in enumerate(pdf.pages):
                                try:
                                    text = page.extract_text()
                                    if text:
                                        content += f"\n--- Page {i+1} ---\n"
                                        content += text
                                        content += "\n"
                                except Exception:
                                    continue
                    except ImportError:
                        pass
                    except Exception as e:
                        error_msg = str(e).lower()
                        # If pdfplumber fails, try PyPDF2 with strict=False
                        if "eof" not in error_msg and "corrupt" not in error_msg:
                            content = f"Error reading PDF with pdfplumber: {str(e)}"

                    # Try PyPDF2 as fallback, especially for corrupted PDFs
                    if not content:
                        try:
                            import PyPDF2

                            with open(file_path, "rb") as f:
                                try:
                                    pdf_reader = PyPDF2.PdfReader(f, strict=False)
                                except Exception:
                                    f.seek(0)
                                    pdf_reader = PyPDF2.PdfReader(f)

                                for i, page in enumerate(pdf_reader.pages):
                                    try:
                                        text = page.extract_text()
                                        if text:
                                            content += f"\n--- Page {i+1} ---\n"
                                            content += text
                                            content += "\n"
                                    except Exception:
                                        continue
                        except ImportError:
                            if not content:
                                content = "PDF libraries not available. Install pdfplumber or PyPDF2 to read PDFs."
                        except Exception as e:
                            error_msg = str(e).lower()
                            if "eof marker" in error_msg:
                                content = f"PDF appears to be corrupted or incomplete (EOF marker not found). The file may be truncated or damaged."
                            elif not content:
                                content = f"Error reading PDF: {str(e)}"

                    if not content:
                        content = "Unable to extract text from PDF. The file may be corrupted, encrypted, or contain only images."
                else:
                    # For text files
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

            file_name = os.path.basename(file_path)
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": f"Content of displayed file '{file_name}' ({file_type}):\n\n{content}",
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": f"Error reading displayed file: {str(e)}\nFile path: {file_path}\nFile type: {file_type}",
            }

    if tool_call.function.name == "execute_command":
        import json

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
