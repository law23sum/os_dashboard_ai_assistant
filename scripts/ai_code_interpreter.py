#!/usr/bin/env python3
"""
Lightweight CLI for invoking OpenAI's Code Interpreter (a.k.a. python tool)
via the Responses API.

Examples:
    python scripts/ai_code_interpreter.py "Plot sin(x) for x∈[-2π, 2π]"
    python scripts/ai_code_interpreter.py --file data/sample.csv "Summarize uploads"
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from openai import OpenAI

# Supported memory tiers per documentation.
MEMORY_CHOICES = {"1g", "4g", "16g", "64g"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenAI Code Interpreter locally.")
    parser.add_argument("prompt", help="Question or task for the python tool.")
    parser.add_argument(
        "--model",
        default=os.environ.get("OSDASH_CODE_MODEL", "gpt-5.2"),
        help="Responses model to use (default: %(default)s).",
    )
    parser.add_argument(
        "--instructions",
        default=(
            "You are a helpful data assistant. Use the python tool to explore data, "
            "generate plots, and solve math/programming problems. "
            "Explain your reasoning briefly after running code."
        ),
        help="System instructions passed to the model.",
    )
    parser.add_argument(
        "--memory",
        default="1g",
        choices=sorted(MEMORY_CHOICES),
        help="Container memory tier (default: %(default)s).",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        metavar="PATH",
        help="Input file to upload to the container (can be repeated).",
    )
    parser.add_argument(
        "--container-id",
        help="Reuse an existing container id instead of auto mode.",
    )
    parser.add_argument(
        "--dump-json",
        action="store_true",
        help="Print the raw JSON response for debugging.",
    )
    return parser.parse_args()


def upload_files(client: OpenAI, paths: Iterable[str]) -> List[str]:
    file_ids: List[str] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        with path.open("rb") as handle:
            resp = client.files.create(file=handle, purpose="assistants")
        file_ids.append(resp.id)
        print(f"[upload] {path.name} -> {resp.id}")
    return file_ids


def build_tool_config(args: argparse.Namespace, file_ids: List[str]) -> Dict[str, Any]:
    if args.container_id:
        return {"type": "code_interpreter", "container": args.container_id}

    container: Dict[str, Any] = {
        "type": "auto",
        "memory_limit": args.memory,
    }
    if file_ids:
        container["file_ids"] = file_ids

    return {
        "type": "code_interpreter",
        "container": container,
    }


def to_dict(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return item
    if hasattr(item, "model_dump"):
        try:
            return item.model_dump()
        except Exception:
            pass
    try:
        return json.loads(json.dumps(item))
    except Exception:
        return {}


def render_response(response) -> None:
    container_refs: List[Dict[str, str]] = []
    for entry in getattr(response, "output", []) or []:
        payload = to_dict(entry)
        entry_type = payload.get("type")
        if entry_type == "message":
            contents = payload.get("content", [])
            for chunk in contents:
                if chunk.get("type") == "output_text":
                    print(chunk.get("text", ""))
                for annotation in chunk.get("annotations", []) or []:
                    if annotation.get("type") == "container_file_citation":
                        container_refs.append(
                            {
                                "container_id": annotation.get("container_id", ""),
                                "file_id": annotation.get("file_id", ""),
                                "filename": annotation.get("filename", ""),
                            }
                        )
        elif entry_type == "code_interpreter_call":
            print("```python")
            logs = payload.get("code", "") or payload.get("input", "")
            if logs:
                print(logs.strip())
            print("```")
            for out in payload.get("outputs", []) or []:
                text = out.get("logs") or out.get("text")
                if text:
                    print(text.strip())

    if container_refs:
        print("\nGenerated files:")
        for ref in container_refs:
            cid = ref.get("container_id")
            fid = ref.get("file_id")
            fname = ref.get("filename") or fid
            print(f"  - {fname} (container={cid}, file_id={fid})")
        print(
            "Download files using `client.container_files.content(container_id, file_id)` "
            "or the /v1/container-files endpoints."
        )


def main() -> None:
    args = parse_args()
    client = OpenAI()
    file_ids = upload_files(client, args.file) if args.file else []
    tool = build_tool_config(args, file_ids)

    response = client.responses.create(
        model=args.model,
        instructions=args.instructions,
        input=args.prompt,
        tools=[tool],
    )

    if args.dump_json:
        print(json.dumps(response.to_dict_recursive(), indent=2))
    else:
        render_response(response)


if __name__ == "__main__":
    main()
