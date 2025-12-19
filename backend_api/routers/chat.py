"""Chat API router."""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
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
):
    """Get chat history."""
    try:
        # Validate and sanitize limit parameter to prevent abuse
        safe_limit = max(1, min(limit, 1000))  # Clamp between 1 and 1000
        
        query = "SELECT id, persona, role, kind, content, created_at FROM chat_messages WHERE 1=1"
        params = []
        
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
async def create_chat_message(message: ChatMessageCreate):
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

            # Build ordered history (including brand new user message) for persona
            history_cursor = db.execute(
                """
                SELECT id, persona, role, kind, content, created_at
                FROM chat_messages
                WHERE persona = ?
                ORDER BY created_at ASC, id ASC
                """,
                (message.persona,),
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

            # Generate AI reply
            try:
                reply_text, error, _ = generate_ai_reply(
                    history,
                    persona=message.persona,
                    append_prompt=False,
                    fallback_prompt=message.content,
                )
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
):
    """Clear chat history."""
    with db_session() as db:
        db_clear_chat_history(db, persona=persona)
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
