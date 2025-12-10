"""Chat API router."""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path
import json

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from assistant_hub_gui.assistant_hub.db import (
    db_insert_chat_message,
    db_clear_chat_history,
    PERSONAS,
    CHAT_ROLES,
)
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

@router.get("/", response_model=List[ChatMessageResponse])
async def get_chat_history(
    persona: Optional[str] = None,
    limit: int = 100,
):
    """Get chat history."""
    query = "SELECT * FROM chat_messages WHERE 1=1"
    params = []
    
    if persona:
        query += " AND persona = ?"
        params.append(persona)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    with db_session() as db:
        cursor = db.execute(query, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
    
    messages = []
    for row in rows:
        msg_dict = dict(zip(columns, row))
        messages.append(ChatMessageResponse(**msg_dict))
    
    return list(reversed(messages))  # Return in chronological order

@router.post("/", response_model=ChatMessageResponse, status_code=201)
async def create_chat_message(message: ChatMessageCreate):
    """Create a new chat message."""
    if message.persona not in PERSONAS:
        raise HTTPException(status_code=400, detail=f"Invalid persona. Must be one of {PERSONAS}")
    if message.role not in CHAT_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {CHAT_ROLES}")
    
    with db_session() as db:
        msg_id = db_insert_chat_message(
            db,
            persona=message.persona,
            role=message.role,
            kind=message.kind,
            content=message.content,
        )

        cursor = db.execute("SELECT * FROM chat_messages WHERE id = ?", (msg_id,))
        row = cursor.fetchone()
        columns = [description[0] for description in cursor.description]
        msg_dict = dict(zip(columns, row))
    return ChatMessageResponse(**msg_dict)

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
