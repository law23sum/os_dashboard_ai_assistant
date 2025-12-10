"""FastAPI-based service that exposes the Office real-time router via WebSockets."""
from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from assistant_core.integrations.office_realtime import (
    AIOfficeMessage,
    AIOfficeWebSocketRouter,
    ApplicationType,
    MessageType,
)
from assistant_core.intelligence.office_ai_service import OfficeAIProcessingService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_app(
    *,
    ai_service_url: Optional[str] = None,
    workspace_dir: str = "./workspace",
) -> FastAPI:
    """Create a FastAPI application exposing the Office router."""

    office_ai_service = OfficeAIProcessingService(workspace_dir)
    router = AIOfficeWebSocketRouter(
        ai_service_url=ai_service_url,
        ai_service_client=office_ai_service.process_message,
    )

    app = FastAPI(title="Office AI Realtime Service", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    connected_clients: Dict[str, WebSocket] = {}

    async def _send_json(client_id: str, payload: Dict) -> None:
        websocket = connected_clients.get(client_id)
        if not websocket:
            return
        try:
            await websocket.send_json(payload)
        except RuntimeError:
            pass

    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "active_clients": len(connected_clients),
            "active_documents": router.list_active_documents(),
        }

    @app.on_event("shutdown")
    async def shutdown_event():
        router.shutdown()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        client_id = f"ws_{uuid.uuid4().hex}"
        connected_clients[client_id] = websocket
        logger.info("Client connected: %s", client_id)

        try:
            while True:
                message_data = await websocket.receive_json()
                message_type = message_data.get("type")

                if message_type == "register":
                    session = router.register_client(
                        client_id,
                        message_data.get("application", ApplicationType.WEB_DASHBOARD),
                        user_id=message_data.get("userId"),
                        document_id=message_data.get("documentId"),
                        capabilities=message_data.get("capabilities"),
                        session_id=message_data.get("sessionId"),
                    )
                    await websocket.send_json(
                        {
                            "type": "registered",
                            "clientId": session.client_id,
                            "sessionId": session.session_id,
                        }
                    )
                elif message_type == "live_edit":
                    result = router.broadcast_live_edit(
                        client_id, message_data.get("payload", {})
                    )
                    broadcast_targets = result.get("recipients", [])
                    payload = result.get("message")
                    for target in broadcast_targets:
                        await _send_json(target, payload)
                elif message_type == "ai_request":
                    job_info = router.handle_ai_request(
                        client_id,
                        MessageType(
                            message_data.get(
                                "messageType", MessageType.AI_GENERATE_REQUEST
                            )
                        ),
                        payload=message_data.get("payload", {}),
                        target=message_data.get("target"),
                    )
                    await websocket.send_json({"type": "ai_request_queued", **job_info})
                    asyncio.create_task(
                        deliver_ai_result(
                            router, job_info["job_id"], client_id, _send_json
                        )
                    )
                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Unsupported message type: {message_type}",
                        }
                    )
        except WebSocketDisconnect:
            logger.info("Client disconnected: %s", client_id)
        finally:
            router.unregister_client(client_id)
            connected_clients.pop(client_id, None)

    return app


async def deliver_ai_result(
    router: AIOfficeWebSocketRouter,
    job_id: str,
    client_id: str,
    send_json,
) -> None:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, router.get_ai_job_result, job_id, 30)
    if result is None:
        payload = {
            "type": "ai_result_timeout",
            "jobId": job_id,
            "message": "Processing timed out",
        }
    else:
        payload = {"type": "ai_result", "jobId": job_id, **result}
    await send_json(client_id, payload)


app = create_app()
