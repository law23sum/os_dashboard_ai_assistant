"""
Responses API router - Bridge between Next.js quickstart and Python backend.
Provides Responses API endpoints compatible with OpenAI Responses API format.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_core.ai import generate_ai_reply
from assistant_core.ai_layer.openai_client import OpenAIClient
from backend_api.deps import get_current_user, get_optional_user
from backend_api.security import AuthUser

router = APIRouter()


class ConversationCreate(BaseModel):
    """Create a new conversation."""
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Conversation response."""
    id: str
    metadata: Optional[Dict[str, Any]] = None


class ResponseInput(BaseModel):
    """Input for creating a response."""
    role: str
    content: List[Dict[str, Any]]


class ResponseCreate(BaseModel):
    """Create a response."""
    model: Optional[str] = None
    prompt: Optional[Dict[str, str]] = None
    instructions: Optional[str] = None
    input: List[ResponseInput]
    conversation: Optional[str] = None
    store: bool = True
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = "auto"
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    user: Optional[AuthUser] = Depends(get_optional_user),
):
    """Create a new conversation (migrated from threads)."""
    try:
        client = OpenAIClient()
        await client.initialize()
        
        # Create conversation with user metadata
        metadata = conversation.metadata or {}
        if user:
            metadata["user_id"] = user.id
        
        conv = await client.create_conversation(metadata=metadata)
        
        return ConversationResponse(
            id=conv["id"],
            metadata=conv.get("metadata", {}),
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@router.post("/responses")
async def create_response(
    response_data: ResponseCreate,
    user: Optional[AuthUser] = Depends(get_optional_user),
    request: Request = None,
):
    """Create a response using Responses API format."""
    try:
        # Convert Responses API format to internal format
        messages = []
        for item in response_data.input:
            if item.role == "user":
                # Extract text from content
                text = ""
                for content_item in item.content:
                    if content_item.get("type") == "input_text":
                        text += content_item.get("text", "")
                    elif content_item.get("type") == "output_text":
                        text += content_item.get("text", "")
                
                if text:
                    messages.append({
                        "role": "user",
                        "content": text
                    })
            elif item.role == "tool":
                # Handle tool outputs
                for content_item in item.content:
                    if content_item.get("type") == "tool_output":
                        messages.append({
                            "role": "tool",
                            "content": content_item.get("output", ""),
                            "tool_call_id": content_item.get("tool_call_id"),
                        })
        
        # Get model
        model = response_data.model or "gpt-4o"
        
        # Get instructions
        instructions = response_data.instructions
        if response_data.prompt and response_data.prompt.get("id"):
            # If prompt ID is provided, we'd need to fetch it
            # For now, use default instructions
            instructions = instructions or "You are a helpful assistant."
        
        # Prepare tools
        tools = response_data.tools or []
        enable_code_interpreter = any(t.get("type") == "code_interpreter" for t in tools)
        enable_file_search = any(t.get("type") == "file_search" for t in tools)
        
        # Extract function tools
        function_tools = [t for t in tools if t.get("type") == "function"]
        
        # Generate response
        if response_data.stream:
            # Streaming response
            async def generate_stream():
                try:
                    # For streaming, we'll use the internal generate_ai_reply
                    # and format as SSE
                    from assistant_core.ai import generate_ai_reply
                    from assistant_hub_gui.assistant_hub.db import ChatMessage
                    
                    # Convert messages to ChatMessage format
                    history = []
                    for msg in messages:
                        history.append(ChatMessage(
                            id=0,
                            persona="AIC",
                            role=msg["role"],
                            kind="chat",
                            content=msg["content"],
                            created_at="",
                        ))
                    
                    # Generate reply (non-streaming for now, but we can enhance this)
                    reply_text, error, tool_calls = generate_ai_reply(
                        history=history,
                        persona="AIC",
                        model=model,
                        temperature=response_data.temperature,
                        max_tokens=response_data.max_output_tokens or 2000,
                        enable_code_interpreter=enable_code_interpreter,
                        enable_file_search=enable_file_search,
                        conversation_id=response_data.conversation,
                    )
                    
                    # Format as SSE
                    if tool_calls:
                        for tool_call in tool_calls:
                            yield f"data: {json.dumps({'type': 'response.output_item.added', 'item': {'type': 'function_tool_call', 'id': tool_call.get('id', ''), 'name': tool_call.get('function', {}).get('name', ''), 'arguments': tool_call.get('function', {}).get('arguments', {})}})}\n\n"
                    
                    # Stream text chunks
                    words = reply_text.split()
                    for i, word in enumerate(words):
                        chunk = word + (" " if i < len(words) - 1 else "")
                        yield f"data: {json.dumps({'type': 'response.output_item.delta', 'delta': {'type': 'message.delta', 'content': [{'type': 'output_text', 'text': chunk}]}})}\n\n"
                    
                    # Completion
                    yield f"data: {json.dumps({'type': 'response.done'})}\n\n"
                except Exception as e:
                    logger.error(f"Streaming error: {e}", exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Non-streaming response
            from assistant_core.ai import generate_ai_reply
            from assistant_hub_gui.assistant_hub.db import ChatMessage
            
            # Convert messages to ChatMessage format
            history = []
            for msg in messages:
                history.append(ChatMessage(
                    id=0,
                    persona="AIC",
                    role=msg["role"],
                    kind="chat",
                    content=msg["content"],
                    created_at="",
                ))
            
            # Generate reply
            reply_text, error, tool_calls = generate_ai_reply(
                history=history,
                persona="AIC",
                model=model,
                temperature=response_data.temperature,
                max_tokens=response_data.max_output_tokens or 2000,
                enable_code_interpreter=enable_code_interpreter,
                enable_file_search=enable_file_search,
                conversation_id=response_data.conversation,
            )
            
            # Format response in Responses API format
            output_items = []
            
            # Add message output
            output_items.append({
                "type": "message",
                "role": "assistant",
                "content": [{
                    "type": "output_text",
                    "text": reply_text
                }]
            })
            
            # Add tool calls if any
            if tool_calls:
                for tool_call in tool_calls:
                    output_items.append({
                        "type": "function_tool_call",
                        "id": tool_call.get("id", ""),
                        "name": tool_call.get("function", {}).get("name", ""),
                        "arguments": tool_call.get("function", {}).get("arguments", {}),
                    })
            
            return {
                "id": f"resp_{hash(reply_text)}",
                "model": model,
                "output": output_items,
                "done": True,
            }
            
    except Exception as e:
        logger.error(f"Error creating response: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create response: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user: Optional[AuthUser] = Depends(get_optional_user),
):
    """Get conversation details."""
    try:
        client = OpenAIClient()
        await client.initialize()
        
        # Note: This would require implementing get_conversation in the client
        # For now, return a placeholder
        return {
            "id": conversation_id,
            "metadata": {},
        }
    except Exception as e:
        logger.error(f"Error getting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")


