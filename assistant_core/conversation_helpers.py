#!/usr/bin/env python3
"""
Helper functions for managing Conversations API (migration from Assistants API).

The Conversations API replaces Threads and provides better state management
for multi-turn conversations. Use these helpers to migrate from the old
Assistants API pattern.

Migration guide: https://platform.openai.com/docs/assistants/migration
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def create_conversation_from_history(
    client: OpenAI,
    messages: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a Conversation from a list of messages (migration helper).
    
    This converts ChatMessage-style messages into Conversation items format.
    
    Args:
        client: OpenAI client instance
        messages: List of messages in format [{"role": "user", "content": "..."}, ...]
        metadata: Optional metadata to attach
        
    Returns:
        Conversation object with id
    """
    if OpenAI is None:
        raise RuntimeError("OpenAI SDK not installed")
    
    items = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        # Convert to Responses API input format
        if isinstance(content, str):
            item_content = [{"type": "input_text", "text": content}]
        elif isinstance(content, list):
            item_content = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        item_content.append({"type": "input_text", "text": block.get("text", "")})
                    elif block.get("type") == "image_url":
                        img_url = block.get("image_url", {})
                        if isinstance(img_url, dict):
                            item_content.append({
                                "type": "input_image",
                                "image_url": img_url.get("url"),
                                "detail": img_url.get("detail", "auto"),
                            })
            if not item_content:
                continue
        else:
            item_content = [{"type": "input_text", "text": str(content)}]
        
        items.append({
            "role": role,
            "content": item_content,
        })
    
    payload: Dict[str, Any] = {"items": items}
    if metadata:
        payload["metadata"] = metadata
    
    conversation = client.conversations.create(**payload)
    return {
        "id": conversation.id,
        "object": conversation.object,
        "created_at": conversation.created_at,
        "metadata": getattr(conversation, "metadata", {}),
    }


def migrate_thread_to_conversation(
    client: OpenAI,
    thread_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Migrate a Thread from the old Assistants API to a Conversation.
    
    This helper fetches all messages from a thread and converts them
    into a new Conversation object.
    
    Args:
        client: OpenAI client instance
        thread_id: Thread ID from the old Assistants API
        metadata: Optional metadata to attach to the new conversation
        
    Returns:
        New Conversation object with migrated items
    """
    if OpenAI is None:
        raise RuntimeError("OpenAI SDK not installed")
    
    # Fetch all messages from the thread
    messages = []
    for page in client.beta.threads.messages.list(thread_id=thread_id, order="asc").iter_pages():
        messages.extend(page.data)
    
    # Convert messages to conversation items
    items = []
    for msg in messages:
        item = {"role": msg.role}
        item_content = []
        
        for content in msg.content:
            if content.type == "text":
                # Use input_text for user messages, output_text for assistant
                content_type = "input_text" if msg.role == "user" else "output_text"
                item_content.append({
                    "type": content_type,
                    "text": content.text.value,
                })
            elif content.type == "image_url":
                item_content.append({
                    "type": "input_image",
                    "image_url": content.image_url.url,
                    "detail": getattr(content.image_url, "detail", "auto"),
                })
        
        if item_content:
            item["content"] = item_content
            items.append(item)
    
    # Create conversation with migrated items
    payload: Dict[str, Any] = {"items": items}
    if metadata:
        payload["metadata"] = metadata
    
    conversation = client.conversations.create(**payload)
    return {
        "id": conversation.id,
        "object": conversation.object,
        "created_at": conversation.created_at,
        "metadata": getattr(conversation, "metadata", {}),
    }


def use_conversation_for_chat(
    client: OpenAI,
    conversation_id: str,
    user_message: str,
    prompt_id: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Send a message using a Conversation (simpler than managing previous_response_id).
    
    This is the recommended pattern for multi-turn conversations in the Responses API.
    Conversations store state server-side and don't expire like standalone responses.
    
    Args:
        client: OpenAI client instance
        conversation_id: Conversation ID to use
        user_message: User's message
        prompt_id: Optional prompt ID (created in dashboard)
        model: Model to use (if not specified in prompt)
        **kwargs: Additional parameters for responses.create()
        
    Returns:
        Response object
    """
    if OpenAI is None:
        raise RuntimeError("OpenAI SDK not installed")
    
    payload: Dict[str, Any] = {
        "input": [{"role": "user", "content": [{"type": "input_text", "text": user_message}]}],
        "conversation": conversation_id,
        "store": True,  # Store responses when using conversations
    }
    
    if prompt_id:
        payload["prompt"] = {"id": prompt_id}
    if model:
        payload["model"] = model
    
    payload.update(kwargs)
    
    return client.responses.create(**payload)









