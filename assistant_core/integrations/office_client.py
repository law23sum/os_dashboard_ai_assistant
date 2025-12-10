"""Async client helper for connecting Python agents to the Office realtime service."""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Optional

import websockets

logger = logging.getLogger(__name__)


class AIOfficeClient:
    """Minimal async client for the websocket router."""

    def __init__(
        self,
        endpoint: str,
        *,
        application: str = "web_dashboard",
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self.endpoint = endpoint
        self.application = application
        self.document_id = document_id
        self.user_id = user_id
        self.session_id = session_id or f"client_{uuid.uuid4().hex}"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None

    async def __aenter__(self) -> "AIOfficeClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        self.websocket = await websockets.connect(self.endpoint)
        await self._send(
            {
                "type": "register",
                "application": self.application,
                "sessionId": self.session_id,
                "documentId": self.document_id,
                "userId": self.user_id,
            }
        )
        response = await self.websocket.recv()
        logger.info("Registered client: %s", response)

    async def disconnect(self) -> None:
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def send_ai_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        await self._send(
            {
                "type": "ai_request",
                "messageType": payload.get("messageType", "ai_generate_request"),
                "payload": payload,
            }
        )
        return json.loads(await self.websocket.recv())

    async def listen(self):
        async for message in self.websocket:
            yield json.loads(message)

    async def _send(self, payload: Dict[str, Any]):
        if not self.websocket:
            raise RuntimeError("Client is not connected")
        await self.websocket.send(json.dumps(payload))
