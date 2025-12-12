#!/usr/bin/env python3
"""Run the Assistants API end-to-end from the command line.

This helper condenses the long-form notebook demo of the Assistants API
into a single CLI so teammates can exercise the workflow without copying
snippets manually.

Examples:
    # Basic one-off question (creates an assistant automatically)
    python scripts/assistants_demo.py \\
        --question "Solve 3x + 11 = 14" --instructions "You are a math tutor."

    # Reuse an existing assistant id and ask follow-up questions
    python scripts/assistants_demo.py --assistant-id asst_123 \\
        --question "Explain linear algebra" --question "Give me a quiz" \\
        --function-demo

The script intentionally mirrors the major sections of the cookbook style
notebook the user shared (assistant creation, threads, runs, messages, tool
calls) so it is easier to map the concepts to runnable code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise SystemExit(
        "The OpenAI SDK is required. Install it with `pip install --upgrade openai`."
    ) from exc


DEFAULT_MODEL = "gpt-4o"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assistants API CLI demo.")
    parser.add_argument(
        "--assistant-id",
        help="Reuse an existing assistant id instead of creating a new one.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OSDASH_ASSISTANT_MODEL", DEFAULT_MODEL),
        help="Model to use when creating a new assistant (default: %(default)s).",
    )
    parser.add_argument(
        "--instructions",
        default="You are a personal math tutor. Answer questions briefly.",
        help="Assistant instructions when creating a new instance.",
    )
    parser.add_argument(
        "--name",
        default="Math Tutor",
        help="Assistant name used during creation (default: %(default)s).",
    )
    parser.add_argument(
        "--question",
        action="append",
        dest="questions",
        help="User question to send to the assistant (repeat to ask follow ups).",
    )
    parser.add_argument(
        "--enable-code",
        action="store_true",
        help="Attach the Code Interpreter tool when creating the assistant.",
    )
    parser.add_argument(
        "--enable-file-search",
        action="store_true",
        help="Attach File Search tool (requires --file inputs).",
    )
    parser.add_argument(
        "--file",
        action="append",
        dest="files",
        help="File path to upload for code interpreter or file search (repeatable).",
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


def load_file_bytes(path: str) -> bytes:
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.read_bytes()


def wait_for_run(client: OpenAI, thread_id: str, run_id: str) -> Any:
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status not in {"queued", "in_progress"}:
            return run
        time.sleep(0.5)


def pretty_print_messages(messages) -> None:
    print("# Messages")
    for message in messages.data:
        role = message.role
        content_texts = []
        for block in message.content:
            if block.type == "text":
                content_texts.append(block.text.value)
        body = "\n".join(content_texts)
        print(f"{role}: {body}")
    print()


def create_or_update_assistant(
    client: OpenAI,
    *,
    assistant_id: Optional[str],
    name: str,
    instructions: str,
    model: str,
    enable_code: bool,
    enable_file_search: bool,
    files: Optional[List[str]],
    include_function: bool,
) -> Any:
    tools: List[Dict[str, Any]] = []
    tool_resources: Dict[str, Any] = {}
    uploaded_files: List[Any] = []

    if enable_code or files:
        tools.append({"type": "code_interpreter"})
        tool_resources["code_interpreter"] = {"file_ids": []}
    if enable_file_search:
        tools.append({"type": "file_search"})
        tool_resources["file_search"] = {"vector_store_ids": []}
    if include_function:
        tools.append({"type": "function", "function": DISPLAY_QUIZ_SCHEMA})

    if files:
        for raw_path in files:
            print(f"[assistants] Uploading file: {raw_path}")
            data = load_file_bytes(raw_path)
            upload = client.files.create(
                file=(Path(raw_path).name, data),
                purpose="assistants",
            )
            uploaded_files.append(upload)
            if "code_interpreter" in tool_resources:
                tool_resources.setdefault("code_interpreter", {"file_ids": []})
                tool_resources["code_interpreter"]["file_ids"].append(upload.id)

    if enable_file_search and uploaded_files:
        vector_store = client.beta.vector_stores.create(name="assistants-demo-store")
        for upload in uploaded_files:
            client.beta.vector_stores.files.create_and_poll(
                vector_store_id=vector_store.id,
                file_id=upload.id,
            )
        tool_resources.setdefault("file_search", {})["vector_store_ids"] = [
            vector_store.id
        ]

    if assistant_id:
        print(f"[assistants] Reusing assistant {assistant_id}")
        assistant = client.beta.assistants.update(
            assistant_id,
            tools=tools or None,
            tool_resources=tool_resources or None,
        )
    else:
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
            tools=tools or None,
            tool_resources=tool_resources or None,
        )
        print(f"[assistants] Created assistant {assistant.id}")
    return assistant


def submit_message(client: OpenAI, *, thread_id: str, content: str) -> Any:
    return client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )


def handle_function_calls(
    run,
    *,
    client: OpenAI,
    thread_id: str,
) -> Any:
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    outputs = []
    for call in tool_calls:
        if call.type != "function":
            continue
        fn_name = call.function.name
        fn_args = json.loads(call.function.arguments)
        if fn_name != "display_quiz":
            raise RuntimeError(f"Unsupported function call: {fn_name}")
        print("[assistants] Running display_quiz() with arguments:")
        print(json.dumps(fn_args, indent=2))
        responses = display_quiz(fn_args["title"], fn_args["questions"])
        outputs.append(
            {
                "tool_call_id": call.id,
                "output": json.dumps({"responses": responses}),
            }
        )

    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run.id,
        tool_outputs=outputs,
    )
    return wait_for_run(client, thread_id, run.id)


def run_questions(
    client: OpenAI,
    *,
    assistant,
    questions: Iterable[str],
    handle_functions: bool,
) -> None:
    thread = client.beta.threads.create()
    for question in questions:
        print(f"[assistants] User: {question}")
        submit_message(client, thread_id=thread.id, content=question)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        run = wait_for_run(client, thread.id, run.id)
        if run.status == "requires_action" and handle_functions:
            run = handle_function_calls(run, client=client, thread_id=thread.id)
        elif run.status == "requires_action":
            raise RuntimeError(
                "Run requires tool outputs but --function-demo was not enabled."
            )

        if run.status != "completed":
            raise RuntimeError(f"Run ended with status {run.status}")

        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="asc",
        )
        pretty_print_messages(messages)


# ---------------------------------------------------------------------------
# Sample function handler mirroring the notebook's quiz helper.
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
        print("[assistants] Dry run: parsed arguments ->")
        print(json.dumps(vars(args), indent=2))
        return

    client = create_client()
    assistant = create_or_update_assistant(
        client,
        assistant_id=args.assistant_id,
        name=args.name,
        instructions=args.instructions,
        model=args.model,
        enable_code=args.enable_code,
        enable_file_search=args.enable_file_search,
        files=args.files,
        include_function=args.function_demo,
    )

    questions = args.questions or [
        "I need to solve the equation 3x + 11 = 14. Can you help me?",
    ]
    run_questions(
        client,
        assistant=assistant,
        questions=questions,
        handle_functions=args.function_demo,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
