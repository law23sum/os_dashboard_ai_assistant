"""Chat API router."""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from datetime import datetime

from assistant_hub_gui.assistant_hub.db import (
    ChatMessage,
    db_insert_chat_message,
    db_clear_chat_history,
    PERSONAS,
    CHAT_ROLES,
)
from assistant_core.ai import generate_ai_reply
from backend_api.db import db_session
from backend_api.deps import get_current_user
from backend_api.security import AuthUser
from assistant_hub_gui.assistant_hub.config import DATA_DIR
import os

router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

class ChatMessageCreate(BaseModel):
    persona: str = "Chris"
    role: str = "user"
    kind: str = "chat"
    content: str
    attachments: Optional[List[str]] = None
    model_provider: Optional[str] = "openai"
    # GPT-5.2 features
    reasoning_effort: Optional[str] = None  # none, low, medium, high, xhigh
    verbosity: Optional[str] = None  # low, medium, high
    previous_response_id: Optional[str] = None  # For CoT passing
    enable_preambles: Optional[bool] = False  # Tool call explanations
    custom_tools: Optional[List[dict]] = None  # Custom tool definitions
    allowed_tools: Optional[List[str]] = None  # Constrain tool usage
    enable_apply_patch: Optional[bool] = False  # Enable apply_patch tool

class ChatMessageResponse(BaseModel):
    id: int
    persona: str
    role: str
    kind: str
    content: str
    created_at: str

    class Config:
        from_attributes = True

class ChatMessagePairResponse(BaseModel):
    """Response containing both user message and AI reply."""
    user_message: ChatMessageResponse
    ai_reply: ChatMessageResponse

@router.get("/", response_model=List[ChatMessageResponse])
async def get_chat_history(
    persona: Optional[str] = None,
    limit: int = 100,
    user: AuthUser = Depends(get_current_user),
):
    """Get chat history."""
    try:
        # Validate and sanitize limit parameter to prevent abuse
        safe_limit = max(1, min(limit, 1000))  # Clamp between 1 and 1000
        
        query = "SELECT id, persona, role, kind, content, created_at FROM chat_messages WHERE user_id = ?"
        params = [user.id]
        
        if persona:
            # Validate persona to prevent SQL injection (defense in depth)
            if persona not in PERSONAS:
                raise HTTPException(status_code=400, detail=f"Invalid persona. Must be one of {PERSONAS}")
            query += " AND persona = ?"
            params.append(persona)
        
        # Order by created_at ASC, id ASC for chronological order
        query += " ORDER BY created_at ASC, id ASC LIMIT ?"
        params.append(safe_limit)
        
        messages = []
        with db_session() as db:
            cursor = db.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                # sqlite3.Row objects can be accessed by column name
                messages.append(ChatMessageResponse(
                    id=row["id"],
                    persona=row["persona"],
                    role=row["role"],
                    kind=row["kind"],
                    content=row["content"],
                    created_at=row["created_at"],
                ))
        
        return messages  # Already in chronological order
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {str(e)}")

@router.post("/", status_code=201)
async def create_chat_message(message: ChatMessageCreate, user: AuthUser = Depends(get_current_user)):
    """Create a new chat message and auto-generate an AI reply.
    
    Returns both the user message and the AI reply so the frontend
    can display them immediately without refetching.
    """
    if message.persona not in PERSONAS:
        raise HTTPException(status_code=400, detail=f"Invalid persona. Must be one of {PERSONAS}")
    if message.role not in CHAT_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {CHAT_ROLES}")

    try:
        with db_session() as db:
            timestamp = datetime.now().isoformat(timespec="seconds")
            chat_msg = ChatMessage(
                id=0,
                persona=message.persona,
                role=message.role,
                kind=message.kind,
                content=message.content,
                created_at=timestamp,
            )
            msg_id = db_insert_chat_message(db, chat_msg)
            # Attach user_id to the inserted row (db helper is legacy).
            db.execute("UPDATE chat_messages SET user_id = ? WHERE id = ?", (user.id, msg_id))

            # Build ordered history (including brand new user message) for persona
            history_cursor = db.execute(
                """
                SELECT id, persona, role, kind, content, created_at
                FROM chat_messages
                WHERE persona = ? AND user_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (message.persona, user.id),
            )
            history_rows = history_cursor.fetchall()
            history: List[ChatMessage] = [
                ChatMessage(
                    id=row["id"],
                    persona=row["persona"],
                    role=row["role"],
                    kind=row["kind"],
                    content=row["content"],
                    created_at=row["created_at"],
                )
                for row in history_rows
            ]

            # Inject attachment + workspace context as a system message (kept bounded).
            system_chunks: List[str] = []
            if message.attachments:
                docs_root = Path(DATA_DIR) / "chat_documents" / user.id
                for doc_id in message.attachments[:5]:
                    meta_path = docs_root / doc_id / "metadata.json"
                    if not meta_path.exists():
                        continue
                    try:
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    except Exception:
                        continue
                    filename = meta.get("original_name") or meta.get("filename") or doc_id
                    preview_type = meta.get("preview_type") or "text"
                    file_path = docs_root / doc_id / (meta.get("filename") or "")
                    excerpt = ""
                    if preview_type == "text" and file_path.exists():
                        try:
                            excerpt = file_path.read_text(encoding="utf-8", errors="ignore")[:8000]
                        except Exception:
                            excerpt = ""
                    system_chunks.append(
                        f"[Attachment: {filename} | type={meta.get('file_type','')} category={meta.get('category','')}]\n{excerpt}".strip()
                    )

            # Lightweight workspace tree (top-level; bounded)
            workspace_root = Path(os.getenv("OSDASH_WORKSPACE_ROOT", Path(__file__).resolve().parents[2]))
            try:
                entries = sorted(workspace_root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:80]
                tree_lines = []
                for p in entries:
                    suffix = "/" if p.is_dir() else ""
                    tree_lines.append(f"- {p.name}{suffix}")
                if tree_lines:
                    system_chunks.append("[Workspace root listing]\n" + "\n".join(tree_lines))
            except Exception:
                pass

            if system_chunks:
                history.append(
                    ChatMessage(
                        id=0,
                        persona=message.persona,
                        role="system",
                        kind="tool_result",
                        content="\\n\\n".join(system_chunks),
                        created_at=datetime.now().isoformat(timespec="seconds"),
                    )
                )

            # Generate AI reply with GPT-5.2 features
            try:
                # Temporarily set environment variables for GPT-5.2 features if provided
                original_reasoning = os.getenv("ASSISTANT_HUB_REASONING_EFFORT")
                original_verbosity = os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY")
                original_apply_patch = os.getenv("ASSISTANT_HUB_ENABLE_APPLY_PATCH")
                
                if message.reasoning_effort:
                    os.environ["ASSISTANT_HUB_REASONING_EFFORT"] = message.reasoning_effort
                if message.verbosity:
                    os.environ["ASSISTANT_HUB_TEXT_VERBOSITY"] = message.verbosity
                if message.enable_apply_patch:
                    os.environ["ASSISTANT_HUB_ENABLE_APPLY_PATCH"] = "true"
                
                # Handle allowed_tools if provided
                if message.allowed_tools:
                    import json
                    os.environ["ASSISTANT_HUB_ALLOWED_TOOLS"] = json.dumps(message.allowed_tools)
                
                try:
                    reply_text, error, _ = generate_ai_reply(
                        history,
                        persona=message.persona,
                        append_prompt=False,
                        fallback_prompt=message.content,
                        model_provider=message.model_provider,
                        previous_response_id=message.previous_response_id,
                        custom_tools=message.custom_tools,
                        enable_preambles=message.enable_preambles or False,
                    )
                finally:
                    # Restore original environment variables
                    if original_reasoning is not None:
                        os.environ["ASSISTANT_HUB_REASONING_EFFORT"] = original_reasoning
                    elif "ASSISTANT_HUB_REASONING_EFFORT" in os.environ:
                        del os.environ["ASSISTANT_HUB_REASONING_EFFORT"]
                    
                    if original_verbosity is not None:
                        os.environ["ASSISTANT_HUB_TEXT_VERBOSITY"] = original_verbosity
                    elif "ASSISTANT_HUB_TEXT_VERBOSITY" in os.environ:
                        del os.environ["ASSISTANT_HUB_TEXT_VERBOSITY"]
                    
                    if original_apply_patch is not None:
                        os.environ["ASSISTANT_HUB_ENABLE_APPLY_PATCH"] = original_apply_patch
                    elif "ASSISTANT_HUB_ENABLE_APPLY_PATCH" in os.environ:
                        del os.environ["ASSISTANT_HUB_ENABLE_APPLY_PATCH"]
                    
                    if "ASSISTANT_HUB_ALLOWED_TOOLS" in os.environ:
                        del os.environ["ASSISTANT_HUB_ALLOWED_TOOLS"]
            except Exception as exc:
                reply_text = f"[offline] Unable to reach AI engine: {exc}"
                error = str(exc)

            if error:
                reply_text = f"{reply_text}\n\n[system] AI backend reported: {error}"

            # Save AI reply
            assistant_msg = ChatMessage(
                id=0,
                persona=message.persona,
                role="assistant",
                kind="chat",
                content=reply_text,
                created_at=datetime.now().isoformat(timespec="seconds"),
            )
            assistant_msg_id = db_insert_chat_message(db, assistant_msg)
            db.execute("UPDATE chat_messages SET user_id = ? WHERE id = ?", (user.id, assistant_msg_id))

            # Fetch both messages to return
            user_cursor = db.execute(
                "SELECT id, persona, role, kind, content, created_at FROM chat_messages WHERE id = ?",
                (msg_id,),
            )
            user_row = user_cursor.fetchone()
            if not user_row:
                raise HTTPException(status_code=500, detail="Failed to retrieve created user message")
            
            ai_cursor = db.execute(
                "SELECT id, persona, role, kind, content, created_at FROM chat_messages WHERE id = ?",
                (assistant_msg_id,),
            )
            ai_row = ai_cursor.fetchone()
            if not ai_row:
                raise HTTPException(status_code=500, detail="Failed to retrieve created AI reply")
            
            # Return both messages
            return {
                "user_message": ChatMessageResponse(
                    id=user_row["id"],
                    persona=user_row["persona"],
                    role=user_row["role"],
                    kind=user_row["kind"],
                    content=user_row["content"],
                    created_at=user_row["created_at"],
                ),
                "ai_reply": ChatMessageResponse(
                    id=ai_row["id"],
                    persona=ai_row["persona"],
                    role=ai_row["role"],
                    kind=ai_row["kind"],
                    content=ai_row["content"],
                    created_at=ai_row["created_at"],
                ),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create chat message: {str(e)}")

@router.delete("/", status_code=204)
async def clear_chat_history(
    persona: Optional[str] = None,
    user: AuthUser = Depends(get_current_user),
):
    """Clear chat history."""
    with db_session() as db:
        if persona:
            db.execute("DELETE FROM chat_messages WHERE user_id = ? AND persona = ?", (user.id, persona))
        else:
            db.execute("DELETE FROM chat_messages WHERE user_id = ?", (user.id,))
    return None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message and send response
            # For now, just echo back. In production, integrate with AI backend
            response = {
                "type": "message",
                "content": f"Echo: {message_data.get('content', '')}",
                "persona": message_data.get("persona", "AIC"),
                "role": "assistant",
            }
            await manager.send_personal_message(json.dumps(response), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
