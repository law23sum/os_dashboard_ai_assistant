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
    " commands when needed. Use the execute_command function to run shell commands.",
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
            raise RuntimeError("The 'openai' package is not installed. Install it to enable ChatGPT support.")
        _client = OpenAI(api_key=_get_api_key())
    return _client


def build_message_payload(history: List[ChatMessage], max_messages: int = 30, include_tool_results: bool = True) -> List[Dict]:
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
                            "description": "The shell command to execute (e.g., 'ls -la', 'python script.py', 'git status')"
                        },
                        "working_directory": {
                            "type": "string",
                            "description": f"Working directory for the command (default: {cwd or os.getcwd()})",
                            "default": cwd or os.getcwd()
                        }
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_displayed_file",
                "description": "Read the content of the file currently displayed in the document preview panel. Use this when the user mentions a document they have open or displayed. Returns the full content of the displayed file.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
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
        messages.append({"role": "user", "content": f"{persona_prefix}{prompt}".strip()})

    fallback_source = fallback_prompt or prompt or (history[-1].content if history else "")
    
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
        tool_calls = message.tool_calls if hasattr(message, 'tool_calls') and message.tool_calls else None
        
        return text.strip(), None, tool_calls
    except (AuthenticationError, APIError, ValueError, RuntimeError) as exc:
        return _offline_reply(fallback_source or "(empty prompt)", exc), str(exc), None


def execute_tool_call(tool_call, cwd: Optional[str] = None, gui_context: Optional[Dict] = None) -> Dict:
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
                "content": "No GUI context available. Cannot read displayed file."
            }
        
        active_session = gui_context.get('active_file_session')
        if not active_session:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": "No file is currently displayed in the document preview panel. Please open a file first using the 'Open Document' button or by having the AI open a file."
            }
        
        file_path = active_session.get('path')
        file_type = active_session.get('type', 'Unknown')
        
        if not file_path or not os.path.exists(file_path):
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": f"No valid file path available. File path: {file_path}"
            }
        
        # Try to read the file
        try:
            # Use the GUI's file reading method if available
            read_file_func = gui_context.get('read_file_func')
            if read_file_func:
                content = read_file_func(file_path, file_type)
            else:
                # Fallback: read file directly (basic text reading)
                if file_type == "PDF":
                    try:
                        import pdfplumber
                        content = ""
                        with pdfplumber.open(file_path) as pdf:
                            for i, page in enumerate(pdf.pages):
                                text = page.extract_text()
                                if text:
                                    content += f"\n--- Page {i+1} ---\n"
                                    content += text
                                    content += "\n"
                    except ImportError:
                        try:
                            import PyPDF2
                            content = ""
                            with open(file_path, 'rb') as f:
                                pdf_reader = PyPDF2.PdfReader(f)
                                for i, page in enumerate(pdf_reader.pages):
                                    text = page.extract_text()
                                    if text:
                                        content += f"\n--- Page {i+1} ---\n"
                                        content += text
                                        content += "\n"
                        except ImportError:
                            content = "PDF libraries not available. Install pdfplumber or PyPDF2 to read PDFs."
                    except Exception as e:
                        content = f"Error reading PDF: {str(e)}"
                else:
                    # For text files
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
            
            file_name = os.path.basename(file_path)
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": f"Content of displayed file '{file_name}' ({file_type}):\n\n{content}"
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "read_displayed_file",
                "content": f"Error reading displayed file: {str(e)}\nFile path: {file_path}\nFile type: {file_type}"
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
                    "content": "Error: No command provided"
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
                "content": content
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "execute_command",
                "content": f"Error executing command: {str(e)}"
            }
    
    return {
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": "unknown",
        "content": "Unknown tool"
    }
