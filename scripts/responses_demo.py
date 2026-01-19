#!/usr/bin/env python3
"""Run the Responses API end-to-end from the command line.

This is the migrated version of assistants_demo.py, using the new Responses API
with Conversations instead of the deprecated Assistants API.

Migration guide: https://platform.openai.com/docs/assistants/migration

Key changes from Assistants API:
- Assistants → Prompts (create in dashboard, reference by ID)
- Threads → Conversations (store items server-side)
- Runs → Responses (simpler: send input, get output)
- Run steps → Items (generalized objects)

Examples:
    # Basic one-off question (uses prompt from dashboard or inline instructions)
    python scripts/responses_demo.py \\
        --question "Solve 3x + 11 = 14" --instructions "You are a math tutor."

    # Use a conversation for multi-turn chat
    python scripts/responses_demo.py \\
        --conversation-id conv_123 \\
        --question "Explain linear algebra" --question "Give me a quiz" \\
        --function-demo

    # Create a new conversation and use it
    python scripts/responses_demo.py \\
        --create-conversation \\
        --question "What are the 5 Ds of dodgeball?"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(
        "The OpenAI SDK is required. Install it with `pip install --upgrade openai`."
    ) from exc


DEFAULT_MODEL = "gpt-4o-mini"  # Use a stable model name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Responses API CLI demo (migrated from Assistants API)."
    )
    parser.add_argument(
        "--prompt-id",
        help="Prompt ID from dashboard (replaces assistant-id). Create prompts in dashboard.",
    )
    parser.add_argument(
        "--conversation-id",
        help="Reuse an existing conversation ID (replaces thread-id).",
    )
    parser.add_argument(
        "--create-conversation",
        action="store_true",
        help="Create a new conversation for this session.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OSDASH_ASSISTANT_MODEL", DEFAULT_MODEL),
        help="Model to use (default: %(default)s).",
    )
    parser.add_argument(
        "--instructions",
        default="You are a personal math tutor. Answer questions briefly.",
        help="System instructions (use prompt-id for persistent prompts).",
    )
    parser.add_argument(
        "--question",
        action="append",
        dest="questions",
        help="User question to send (repeat to ask follow ups).",
    )
    parser.add_argument(
        "--function-demo",
        action="store_true",
        help="Register the sample display_quiz() function and handle tool calls.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without executing the API (useful for CI smoke tests).",
    )
    return parser.parse_args()


def create_client() -> OpenAI:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Export it or place it in your .env file."
        )
    return OpenAI(api_key=key)


def handle_function_calls(
    response: Any,
    *,
    client: OpenAI,
) -> Any:
    """Handle function calls from a Responses API response."""
    tool_calls = []
    output = getattr(response, "output", None) or []
    
    # Extract function calls from response output
    for item in output:
        item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
        if item_type == "function_call":
            call_id = getattr(item, "id", None) or (item.get("id") if isinstance(item, dict) else None)
            fn = getattr(item, "function", None) or (item.get("function") if isinstance(item, dict) else None) or {}
            fn_name = getattr(fn, "name", None) or (fn.get("name") if isinstance(fn, dict) else None)
            fn_args = getattr(fn, "arguments", None) or (fn.get("arguments") if isinstance(fn, dict) else None)
            
            if fn_name:
                tool_calls.append({
                    "id": call_id,
                    "name": fn_name,
                    "arguments": fn_args or "{}",
                })
    
    if not tool_calls:
        return None
    
    outputs = []
    for call in tool_calls:
        fn_name = call["name"]
        fn_args = json.loads(call["arguments"] or "{}")
        
        if fn_name != "display_quiz":
            raise RuntimeError(f"Unsupported function call: {fn_name}")
        
        print("[responses] Running display_quiz() with arguments:")
        print(json.dumps(fn_args, indent=2))
        responses = display_quiz(fn_args.get("title", ""), fn_args.get("questions", []))
        
        outputs.append({
            "tool_call_id": call["id"],
            "output": json.dumps({"responses": responses}),
        })
    
    # Submit tool outputs and get new response
    # In Responses API, we create a new response with tool outputs
    return outputs


def run_questions(
    client: OpenAI,
    *,
    prompt_id: Optional[str],
    conversation_id: Optional[str],
    questions: Iterable[str],
    instructions: str,
    model: str,
    handle_functions: bool,
) -> None:
    """Run questions using Responses API with Conversations."""
    
    # Create conversation if needed
    if conversation_id is None:
        print("[responses] Creating new conversation...")
        conversation = client.conversations.create()
        conversation_id = conversation.id
        print(f"[responses] Created conversation {conversation_id}")
    else:
        print(f"[responses] Using existing conversation {conversation_id}")
    
    for question in questions:
        print(f"[responses] User: {question}")
        
        # Build payload for Responses API
        payload: Dict[str, Any] = {
            "model": model,
            "input": [{"role": "user", "content": [{"type": "input_text", "text": question}]}],
            "conversation": conversation_id,
            "store": True,  # Store responses when using conversations
        }
        
        # Use prompt_id if provided, otherwise use inline instructions
        if prompt_id:
            payload["prompt"] = {"id": prompt_id}
        else:
            payload["instructions"] = instructions
        
        # Add function tool if enabled
        if handle_functions:
            payload["tools"] = [{"type": "function", "function": DISPLAY_QUIZ_SCHEMA}]
            payload["tool_choice"] = "auto"
        
        # Create response
        response = client.responses.create(**payload)
        
        # Handle function calls if needed
        if handle_functions:
            tool_outputs = handle_function_calls(response, client=client)
            if tool_outputs:
                # Create follow-up response with tool outputs
                follow_up_payload = {
                    "model": model,
                    "conversation": conversation_id,
                    "input": [
                        {
                            "role": "tool",
                            "content": [
                                {
                                    "type": "tool_output",
                                    "tool_call_id": output["tool_call_id"],
                                    "output": output["output"],
                                }
                                for output in tool_outputs
                            ],
                        }
                    ],
                    "store": True,
                }
                if prompt_id:
                    follow_up_payload["prompt"] = {"id": prompt_id}
                else:
                    follow_up_payload["instructions"] = instructions
                
                response = client.responses.create(**follow_up_payload)
        
        # Extract and print response text
        output_text = ""
        output = getattr(response, "output", None) or []
        for item in output:
            item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
            if item_type == "message":
                content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else None) or []
                for block in content:
                    btype = getattr(block, "type", None) or (block.get("type") if isinstance(block, dict) else None)
                    if btype == "output_text":
                        text = getattr(block, "text", None) or (block.get("text") if isinstance(block, dict) else None) or ""
                        if text:
                            output_text += text + "\n"
        
        # Fallback to output_text attribute if available
        if not output_text and hasattr(response, "output_text"):
            output_text = str(response.output_text)
        
        print(f"[responses] Assistant: {output_text.strip()}")
        print()


# ---------------------------------------------------------------------------
# Sample function handler (same as assistants_demo.py)
# ---------------------------------------------------------------------------

DISPLAY_QUIZ_SCHEMA = {
    "name": "display_quiz",
    "description": (
        "Displays a quiz and returns mock responses. Replace with a real UI in production."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "question_type": {
                            "type": "string",
                            "enum": ["MULTIPLE_CHOICE", "FREE_RESPONSE"],
                        },
                        "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["question_text"],
                },
            },
        },
        "required": ["title", "questions"],
    },
}


def mock_multiple_choice_response(choices: List[str]) -> str:
    if not choices:
        return ""
    return choices[0]


def mock_free_response() -> str:
    return "I'm not sure."


def display_quiz(title: str, questions: List[Dict[str, Any]]) -> List[str]:
    print(f"\nQuiz: {title}\n")
    responses: List[str] = []
    for idx, question in enumerate(questions, start=1):
        q_text = question.get("question_text", f"Question {idx}")
        q_type = question.get("question_type", "FREE_RESPONSE")
        print(f"{idx}. {q_text}")
        if q_type == "MULTIPLE_CHOICE":
            choices = question.get("choices", [])
            for option_index, choice in enumerate(choices):
                print(f"  {option_index + 1}. {choice}")
            response = mock_multiple_choice_response(choices)
        else:
            response = mock_free_response()
        responses.append(response)
        print(f"-> Response: {response}\n")
    return responses


def main() -> None:
    args = parse_args()
    if args.dry_run:
        print("[responses] Dry run: parsed arguments ->")
        print(json.dumps(vars(args), indent=2))
        return

    client = create_client()
    
    questions = args.questions or [
        "I need to solve the equation 3x + 11 = 14. Can you help me?",
    ]
    
    run_questions(
        client,
        prompt_id=args.prompt_id,
        conversation_id=args.conversation_id,
        questions=questions,
        instructions=args.instructions,
        model=args.model,
        handle_functions=args.function_demo,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)









