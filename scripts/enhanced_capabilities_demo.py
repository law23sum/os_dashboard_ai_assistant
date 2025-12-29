#!/usr/bin/env python3
"""Demonstrate enhanced capabilities from Assistants API deep dive.

This script showcases:
- File upload and management
- Code interpreter with file attachments
- File search with vector stores
- Image handling with detail levels
- Message annotations processing
- Context window management

All features work with Responses API (migrated from Assistants API).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError as exc:
    raise SystemExit(
        "The OpenAI SDK is required. Install it with `pip install --upgrade openai`."
    ) from exc

# Import our enhanced capabilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from assistant_core.file_tools import (
    FileManager,
    VectorStoreManager,
    ImageHandler,
    ToolResourceBuilder,
    MessageAnnotationHandler,
    ContextManager,
    create_data_visualization_assistant,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enhanced capabilities demo (Responses API)"
    )
    parser.add_argument(
        "--demo",
        choices=[
            "file_upload",
            "code_interpreter",
            "file_search",
            "image_analysis",
            "data_viz",
            "all",
        ],
        default="all",
        help="Which demo to run",
    )
    parser.add_argument(
        "--file",
        action="append",
        dest="files",
        help="File path(s) to upload",
    )
    parser.add_argument(
        "--image",
        action="append",
        dest="images",
        help="Image URL or path to analyze",
    )
    parser.add_argument(
        "--image-detail",
        choices=["low", "high", "auto"],
        default="auto",
        help="Image detail level (low=512px/85 tokens, high=detailed crops)",
    )
    parser.add_argument(
        "--question",
        default="What can you tell me about this?",
        help="Question to ask about the uploaded content",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        help="Model to use",
    )
    return parser.parse_args()


def demo_file_upload(client: OpenAI, files: List[str]) -> None:
    """Demonstrate file upload and management."""
    print("\n=== File Upload Demo ===\n")
    
    file_mgr = FileManager(client)
    
    uploaded_files = []
    for file_path in files:
        print(f"Uploading: {file_path}")
        try:
            file_info = file_mgr.upload_file(file_path, purpose="assistants")
            uploaded_files.append(file_info)
            print(f"  ✓ Uploaded: {file_info['filename']} (ID: {file_info['id']})")
            print(f"    Size: {file_info['bytes']} bytes")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    return uploaded_files


def demo_code_interpreter(
    client: OpenAI, files: List[str], question: str, model: str
) -> None:
    """Demonstrate code interpreter with file attachments."""
    print("\n=== Code Interpreter Demo ===\n")
    
    file_mgr = FileManager(client)
    tool_builder = ToolResourceBuilder()
    
    # Upload files
    file_ids = []
    for file_path in files:
        file_info = file_mgr.upload_file(file_path, purpose="assistants")
        file_ids.append(file_info["id"])
        print(f"Uploaded: {file_info['filename']} (ID: {file_info['id']})")
    
    # Build tools with code interpreter
    tools = tool_builder.build_tools_config(
        enable_code_interpreter=True,
        code_interpreter_file_ids=file_ids,
    )
    
    # Create conversation
    conversation = client.conversations.create(
        items=[{
            "role": "user",
            "content": [{"type": "input_text", "text": question}],
        }],
    )
    
    print(f"\nCreated conversation: {conversation.id}")
    print(f"Asking: {question}\n")
    
    # Create response with code interpreter
    response = client.responses.create(
        model=model,
        conversation=conversation.id,
        input=[{
            "role": "user",
            "content": [{"type": "input_text", "text": question}],
        }],
        tools=tools,
        store=True,
    )
    
    # Extract and display response
    output_text = ""
    for item in response.output:
        if hasattr(item, "type") and item.type == "message":
            for block in getattr(item, "content", []):
                if hasattr(block, "type") and block.type == "output_text":
                    output_text += getattr(block, "text", "") + "\n"
    
    if hasattr(response, "output_text"):
        output_text = str(response.output_text)
    
    print("Response:")
    print(output_text.strip())


def demo_file_search(
    client: OpenAI, files: List[str], question: str, model: str
) -> None:
    """Demonstrate file search with vector stores."""
    print("\n=== File Search Demo ===\n")
    
    file_mgr = FileManager(client)
    vector_mgr = VectorStoreManager(client)
    
    # Upload files
    file_ids = []
    for file_path in files:
        file_info = file_mgr.upload_file(file_path, purpose="assistants")
        file_ids.append(file_info["id"])
        print(f"Uploaded: {file_info['filename']} (ID: {file_info['id']})")
    
    # Create vector store
    print("\nCreating vector store...")
    vector_store = vector_mgr.create_vector_store(
        name="demo-knowledge-base",
        file_ids=file_ids,
    )
    print(f"Created vector store: {vector_store['id']}")
    
    # Build tools with file search
    tools = ToolResourceBuilder.build_tools_config(
        enable_file_search=True,
        file_search_vector_store_ids=[vector_store["id"]],
    )
    
    # Create conversation and ask question
    conversation = client.conversations.create()
    
    response = client.responses.create(
        model=model,
        conversation=conversation.id,
        input=[{
            "role": "user",
            "content": [{"type": "input_text", "text": question}],
        }],
        tools=tools,
        store=True,
    )
    
    # Extract response
    output_text = ""
    for item in response.output:
        if hasattr(item, "type") and item.type == "message":
            for block in getattr(item, "content", []):
                if hasattr(block, "type") and block.type == "output_text":
                    output_text += getattr(block, "text", "") + "\n"
    
    print("\nResponse:")
    print(output_text.strip())


def demo_image_analysis(
    client: OpenAI, images: List[str], question: str, detail: str, model: str
) -> None:
    """Demonstrate image analysis with detail levels."""
    print("\n=== Image Analysis Demo ===\n")
    print(f"Image detail level: {detail}")
    print(f"  - low: 512x512, ~85 tokens, faster")
    print(f"  - high: Detailed crops, more tokens")
    print(f"  - auto: Model decides\n")
    
    img_handler = ImageHandler()
    
    # Prepare image content
    image_blocks = []
    for img in images:
        if img.startswith("http://") or img.startswith("https://"):
            # External URL
            image_blocks.append(
                img_handler.create_image_content(image_url=img, detail=detail)
            )
            print(f"Using image URL: {img}")
        else:
            # Local file - upload first
            file_mgr = FileManager(client)
            file_info = file_mgr.upload_file(img, purpose="vision")
            image_blocks.append(
                img_handler.create_image_content(file_id=file_info["id"], detail=detail)
            )
            print(f"Uploaded image: {img} (ID: {file_info['id']})")
    
    # Create multimodal message
    message = img_handler.create_multimodal_message(question, image_blocks)
    
    # Create conversation and response
    conversation = client.conversations.create()
    
    response = client.responses.create(
        model=model,
        conversation=conversation.id,
        input=[message],
        store=True,
    )
    
    # Extract response
    output_text = ""
    if hasattr(response, "output_text"):
        output_text = str(response.output_text)
    else:
        for item in response.output:
            if hasattr(item, "type") and item.type == "message":
                for block in getattr(item, "content", []):
                    if hasattr(block, "type") and block.type == "output_text":
                        output_text += getattr(block, "text", "") + "\n"
    
    print("\nResponse:")
    print(output_text.strip())


def demo_data_visualization(client: OpenAI, csv_file: str, model: str) -> None:
    """Demonstrate data visualization with code interpreter."""
    print("\n=== Data Visualization Demo ===\n")
    
    setup = create_data_visualization_assistant(client, csv_file, model)
    
    print(f"Conversation ID: {setup['conversation_id']}")
    print(f"File ID: {setup['file_id']}")
    print(f"Tools: {json.dumps(setup['tools'], indent=2)}\n")
    
    # Create response
    response = client.responses.create(
        model=model,
        conversation=setup["conversation_id"],
        instructions=setup["instructions"],
        tools=setup["tools"],
        input=[{
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": "Create 3 data visualizations based on the trends in this file.",
            }],
        }],
        store=True,
    )
    
    # Extract response
    output_text = ""
    if hasattr(response, "output_text"):
        output_text = str(response.output_text)
    else:
        for item in response.output:
            if hasattr(item, "type") and item.type == "message":
                for block in getattr(item, "content", []):
                    if hasattr(block, "type") and block.type == "output_text":
                        output_text += getattr(block, "text", "") + "\n"
    
    print("Response:")
    print(output_text.strip())


def main() -> None:
    args = parse_args()
    
    # Create client
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=key)
    
    if args.demo == "file_upload" or args.demo == "all":
        if not args.files:
            print("Error: --file required for file_upload demo")
            return
        demo_file_upload(client, args.files)
    
    if args.demo == "code_interpreter" or args.demo == "all":
        if not args.files:
            print("Error: --file required for code_interpreter demo")
            return
        demo_code_interpreter(client, args.files, args.question, args.model)
    
    if args.demo == "file_search" or args.demo == "all":
        if not args.files:
            print("Error: --file required for file_search demo")
            return
        demo_file_search(client, args.files, args.question, args.model)
    
    if args.demo == "image_analysis" or args.demo == "all":
        if not args.images:
            print("Error: --image required for image_analysis demo")
            return
        demo_image_analysis(
            client, args.images, args.question, args.image_detail, args.model
        )
    
    if args.demo == "data_viz" or args.demo == "all":
        if not args.files or len(args.files) != 1:
            print("Error: --file (single CSV) required for data_viz demo")
            return
        demo_data_visualization(client, args.files[0], args.model)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)


