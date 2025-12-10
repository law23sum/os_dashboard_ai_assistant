"""Real-time Office integration helpers inspired by the AI Office Agent architecture docs."""
from __future__ import annotations

import logging
import threading
import time
import uuid
from collections import defaultdict
from concurrent.futures import Future
from dataclasses import dataclass, field, asdict
from enum import Enum
from queue import Queue, Empty
from typing import Any, Callable, Dict, List, Optional, Set

import requests


class MessageType(str, Enum):
    """Message operations supported by the Office agent."""

    DOCUMENT_OPENED = "document_opened"
    DOCUMENT_CHANGED = "document_changed"
    DOCUMENT_SAVED = "document_saved"

    AI_ANALYZE_REQUEST = "ai_analyze_request"
    AI_GENERATE_REQUEST = "ai_generate_request"
    AI_SUGGEST_REQUEST = "ai_suggest_request"

    AI_ANALYSIS_RESULT = "ai_analysis_result"
    AI_CONTENT_GENERATED = "ai_content_generated"
    AI_SUGGESTIONS_READY = "ai_suggestions_ready"

    LIVE_EDIT_UPDATE = "live_edit_update"
    FORMATTING_UPDATE = "formatting_update"
    STRUCTURE_UPDATE = "structure_update"

    SESSION_START = "session_start"
    SESSION_END = "session_end"
    ERROR = "error"


class ApplicationType(str, Enum):
    """Applications that participate in the collaboration mesh."""

    POWERPOINT = "powerpoint"
    WORD = "word"
    EXCEL = "excel"
    ONENOTE = "onenote"
    ADOBE_PHOTOSHOP = "adobe_photoshop"
    ADOBE_ILLUSTRATOR = "adobe_illustrator"
    WEB_DASHBOARD = "web_dashboard"


@dataclass
class AIOfficeMessage:
    """Normalized message envelope for WebSocket and AI requests."""

    type: MessageType
    source: ApplicationType
    target: ApplicationType
    payload: Dict[str, Any]
    session_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=lambda: time.time())
    document_id: Optional[str] = None

    def __post_init__(self) -> None:
        if isinstance(self.type, str):  # allow loose construction
            self.type = MessageType(self.type)
        if isinstance(self.source, str):
            self.source = ApplicationType(self.source)
        if isinstance(self.target, str):
            self.target = ApplicationType(self.target)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dict for transport."""
        result = asdict(self)
        result["type"] = self.type.value
        result["source"] = self.source.value
        result["target"] = self.target.value
        return result


@dataclass
class ClientSession:
    """Connected client metadata."""

    client_id: str
    application: ApplicationType
    user_id: Optional[str]
    document_id: Optional[str]
    capabilities: List[str] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: f"session_{uuid.uuid4().hex}")
    last_seen: float = field(default_factory=lambda: time.time())

    def touch(self) -> None:
        self.last_seen = time.time()


class AIOfficeWebSocketRouter:
    """Routes document events and proxies AI requests for Office clients."""

    def __init__(
        self,
        ai_service_url: Optional[str] = None,
        *,
        ai_service_client: Optional[Callable[[AIOfficeMessage], Dict[str, Any]]] = None,
        ai_timeout: int = 30,
    ) -> None:
        self.ai_service_url = ai_service_url.rstrip("/") if ai_service_url else None
        self._ai_service_client = ai_service_client
        self.ai_timeout = ai_timeout
        self.logger = logging.getLogger(__name__)

        self._clients: Dict[str, ClientSession] = {}
        self._document_index: Dict[str, Set[str]] = defaultdict(set)

        self._ai_queue: "Queue[Optional[Dict[str, Any]]]" = Queue()
        self._pending_jobs: Dict[str, Future] = {}
        self._queue_thread = threading.Thread(target=self._drain_ai_queue, daemon=True)
        self._stop_event = threading.Event()
        self._queue_thread.start()

    # ------------------------------------------------------------------
    # Client/session management
    # ------------------------------------------------------------------
    def register_client(
        self,
        client_id: str,
        application: ApplicationType | str,
        *,
        user_id: Optional[str] = None,
        document_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> ClientSession:
        """Register a collaborating client and update routing tables."""
        app_enum = ApplicationType(application)
        capabilities = capabilities or []

        session = ClientSession(
            client_id=client_id,
            application=app_enum,
            user_id=user_id,
            document_id=document_id,
            capabilities=capabilities,
            session_id=session_id or f"session_{uuid.uuid4().hex}",
        )
        self._clients[client_id] = session
        if document_id:
            self._document_index[document_id].add(client_id)
        self.logger.debug("Registered client %s (%s)", client_id, application)
        return session

    def unregister_client(self, client_id: str) -> None:
        session = self._clients.pop(client_id, None)
        if not session:
            return
        if session.document_id and client_id in self._document_index.get(session.document_id, set()):
            self._document_index[session.document_id].discard(client_id)
            if not self._document_index[session.document_id]:
                self._document_index.pop(session.document_id, None)
        self.logger.debug("Unregistered client %s", client_id)

    def get_client(self, client_id: str) -> Optional[ClientSession]:
        return self._clients.get(client_id)

    def list_clients(self) -> List[ClientSession]:
        return list(self._clients.values())

    def list_active_documents(self) -> Dict[str, List[str]]:
        return {doc: sorted(clients) for doc, clients in self._document_index.items()}

    # ------------------------------------------------------------------
    # Event routing helpers
    # ------------------------------------------------------------------
    def broadcast_live_edit(self, client_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare a live-edit broadcast for other collaborators."""
        client = self._clients.get(client_id)
        if not client or not client.document_id:
            return {"recipients": [], "message": None}

        client.touch()
        recipients = [cid for cid in self._document_index[client.document_id] if cid != client_id]
        message = AIOfficeMessage(
            type=MessageType.LIVE_EDIT_UPDATE,
            source=client.application,
            target=client.application,
            payload={**payload, "sourceClient": client.client_id},
            session_id=client.session_id,
            document_id=client.document_id,
        )
        return {"recipients": recipients, "message": message.to_dict()}

    def handle_document_operation(
        self,
        client_id: str,
        operation: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Route document operation to the correct AI worker or broadcast."""
        payload = payload or {}
        op_map = {
            "analyze_content": MessageType.AI_ANALYZE_REQUEST,
            "generate_content": MessageType.AI_GENERATE_REQUEST,
            "create_visualization": MessageType.AI_SUGGEST_REQUEST,
        }
        if operation in op_map:
            return self.handle_ai_request(client_id, op_map[operation], payload)
        if operation == "apply_formatting":
            result = self.broadcast_live_edit(client_id, {"changes": payload})
            result["operation"] = operation
            return result
        raise ValueError(f"Unsupported document operation: {operation}")

    def handle_ai_request(
        self,
        client_id: str,
        message_type: MessageType,
        payload: Optional[Dict[str, Any]] = None,
        *,
        target: Optional[ApplicationType | str] = None,
    ) -> Dict[str, Any]:
        """Queue an AI request for asynchronous processing."""
        payload = payload or {}
        client = self._clients.get(client_id)
        if not client:
            raise ValueError(f"Client {client_id} is not registered")

        target_app = ApplicationType(target) if target else client.application
        message = AIOfficeMessage(
            type=message_type,
            source=client.application,
            target=target_app,
            payload=payload,
            session_id=client.session_id,
            document_id=payload.get("document_id") or client.document_id,
        )
        job_id = self.submit_ai_request(message)
        estimate = self.estimate_processing_time(message_type)
        return {
            "job_id": job_id,
            "estimated_time": estimate,
            "message": message.to_dict(),
        }

    def route_message(self, message: AIOfficeMessage) -> List[str]:
        """Return a list of target client IDs for a message."""
        if message.document_id and message.document_id in self._document_index:
            return [cid for cid in self._document_index[message.document_id]]
        return [cid for cid, client in self._clients.items() if client.application == message.target]

    # ------------------------------------------------------------------
    # AI processing queue
    # ------------------------------------------------------------------
    def submit_ai_request(self, message: AIOfficeMessage) -> str:
        job_id = f"job_{uuid.uuid4().hex}"
        future: Future = Future()
        self._pending_jobs[job_id] = future
        self._ai_queue.put({"job_id": job_id, "message": message, "future": future})
        self.logger.debug("Queued AI job %s for %s", job_id, message.type.value)
        return job_id

    def get_ai_job_result(self, job_id: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        future = self._pending_jobs.get(job_id)
        if not future:
            return None
        try:
            result = future.result(timeout=timeout)
            return result
        except Exception as exc:  # pragma: no cover - Future timeout/error surfaces to caller
            self.logger.error("AI job %s failed: %s", job_id, exc)
            return {"success": False, "error": str(exc)}

    def estimate_processing_time(self, message_type: MessageType) -> float:
        estimates = {
            MessageType.AI_ANALYZE_REQUEST: 4.0,
            MessageType.AI_GENERATE_REQUEST: 6.5,
            MessageType.AI_SUGGEST_REQUEST: 3.0,
        }
        return estimates.get(message_type, 2.0)

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def shutdown(self, wait: bool = True) -> None:
        """Stop the worker thread and clean up pending jobs."""
        self._stop_event.set()
        self._ai_queue.put(None)
        if wait and self._queue_thread.is_alive():
            self._queue_thread.join(timeout=2)

    def __del__(self) -> None:  # pragma: no cover - destructor best-effort cleanup
        try:
            self.shutdown(wait=False)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _drain_ai_queue(self) -> None:
        while not self._stop_event.is_set():
            try:
                job = self._ai_queue.get(timeout=0.5)
            except Empty:
                continue
            if job is None:
                break
            future: Future = job["future"]
            message: AIOfficeMessage = job["message"]
            try:
                result = self._call_ai_service(message)
                payload = {"success": True, "result": result}
                future.set_result(payload)
            except Exception as exc:
                future.set_result({"success": False, "error": str(exc)})
            finally:
                self._pending_jobs.pop(job["job_id"], None)
                self._ai_queue.task_done()

    def _call_ai_service(self, message: AIOfficeMessage) -> Dict[str, Any]:
        if self._ai_service_client:
            return self._ai_service_client(message)
        if not self.ai_service_url:
            raise RuntimeError("AI service URL is not configured")

        endpoint = self._resolve_endpoint(message.type)
        url = f"{self.ai_service_url}/{endpoint}"
        response = requests.post(url, json=message.to_dict(), timeout=self.ai_timeout)
        response.raise_for_status()
        return response.json()

    def _resolve_endpoint(self, message_type: MessageType) -> str:
        mapping = {
            MessageType.AI_ANALYZE_REQUEST: "analyze",
            MessageType.AI_GENERATE_REQUEST: "generate",
            MessageType.AI_SUGGEST_REQUEST: "suggest",
        }
        return mapping.get(message_type, "process")


__all__ = [
    "AIOfficeWebSocketRouter",
    "AIOfficeMessage",
    "ApplicationType",
    "MessageType",
    "ClientSession",
]
