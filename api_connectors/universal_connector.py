"""Universal connector interfaces and reference implementations.

This module defines a high-level connector contract along with
reference connectors for Microsoft Graph, Office files, PDF files,
Git repositories, and OpenAI. The implementations are written to be
safe to import even when optional third-party dependencies are not
installed; operations that require missing packages will return
informative :class:`OperationResult` errors instead of raising
exceptions.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

# Optional imports guarded to keep module importable without extras
try:  # pragma: no cover - optional dependency
    from microsoft.graph import GraphServiceClient  # type: ignore
    from azure.identity import ClientSecretCredential  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    GraphServiceClient = None
    ClientSecretCredential = None

try:  # pragma: no cover - optional dependency
    import fitz  # type: ignore
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    fitz = None
    Image = None

try:  # pragma: no cover - optional dependency
    import git  # noqa: F401
    from git import Repo  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Repo = None

try:  # pragma: no cover - optional dependency
    import openai  # noqa: F401
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    AsyncOpenAI = None


class ConnectorCapability(Enum):
    """Capabilities that connectors can support."""
"""Comprehensive connector interface and reference implementations.

This module defines a universal connector contract plus specialized
connectors for Microsoft Graph, Office files, PDF documents, Git repositories,
and OpenAI. The classes are written to match the specification provided for
connector interoperability while remaining lightweight enough to run in the
current offline development environment. Where external SDKs are optional or
unavailable, connectors return informative errors rather than failing during
import time.
"""

import asyncio
import importlib.util
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional


class ConnectorCapability(Enum):
    """Capabilities that connectors can support"""

    READ = "read"
    WRITE = "write"
    SEARCH = "search"
    WATCH = "watch"  # Real-time change notifications
    BATCH = "batch"  # Batch operations
    STREAM = "stream"  # Streaming operations
    METADATA = "metadata"  # Rich metadata extraction
    VERSIONING = "versioning"  # Version control
    COLLABORATION = "collaboration"  # Multi-user features
    ENCRYPTION = "encryption"  # Data encryption support
    WATCH = "watch"
    BATCH = "batch"
    STREAM = "stream"
    METADATA = "metadata"
    VERSIONING = "versioning"
    COLLABORATION = "collaboration"
    ENCRYPTION = "encryption"


@dataclass
class ConnectorConfig:
    """Configuration for connector instances."""

    connector_type: str
    instance_id: str
    credentials: Dict[str, Any]
    settings: Dict[str, Any]
    capabilities: List[ConnectorCapability]
    rate_limits: Dict[str, int]
    timeout_settings: Dict[str, int]
    """Configuration for connector instances"""

    connector_type: str
    instance_id: str
    credentials: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[ConnectorCapability] = field(default_factory=list)
    rate_limits: Dict[str, int] = field(default_factory=dict)
    timeout_settings: Dict[str, int] = field(default_factory=dict)


@dataclass
class OperationResult:
    """Standard result format for all connector operations."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    operation_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class _AsyncSemaphoreRateLimiter:
    """Simple rate limiter using a semaphore to throttle concurrency."""

    def __init__(self, permits: int) -> None:
        self._semaphore = asyncio.Semaphore(max(1, permits))

    async def acquire(self) -> None:
        await self._semaphore.acquire()
        # Release immediately to behave as a concurrency limiter rather than a queue
        self._semaphore.release()


class _PassthroughCircuitBreaker:
    """Minimal circuit breaker placeholder."""

    async def call(self, func, *args, **kwargs):
        return await func(*args, **kwargs)
class ContentBlockType(Enum):
    """Minimal CIR content block types used by specialized connectors"""

    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass
class ContentBlock:
    block_type: ContentBlockType
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Section:
    title: str
    content_blocks: List[ContentBlock] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CIRDocument:
    title: str
    document_type: str
    sections: List[Section] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimpleAsyncRateLimiter:
    """Small sliding-window rate limiter suitable for async connectors."""

    def __init__(self, rate_limits: Dict[str, int]):
        self.per_second = rate_limits.get("requests_per_second")
        self.per_minute = rate_limits.get("requests_per_minute", 60)
        self._timestamps: List[datetime] = []

    async def acquire(self):
        while True:
            now = datetime.utcnow()
            self._timestamps = [t for t in self._timestamps if (now - t) < timedelta(minutes=1)]

            if self.per_second:
                second_count = sum(1 for t in self._timestamps if (now - t) < timedelta(seconds=1))
                if second_count >= self.per_second:
                    await asyncio.sleep(0.05)
                    continue

            if len(self._timestamps) >= self.per_minute:
                await asyncio.sleep(0.1)
                continue

            self._timestamps.append(now)
            break


class SimpleCircuitBreaker:
    """Basic circuit breaker implementation to wrap connector calls."""

    def __init__(self, failure_threshold: int = 3, recovery_time_seconds: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_time = timedelta(seconds=recovery_time_seconds)
        self.failure_count = 0
        self.last_failure: Optional[datetime] = None

    async def call(self, operation_func, *args, **kwargs):
        if self.is_open():
            raise RuntimeError("Circuit breaker is open; operation blocked.")

        try:
            result = await operation_func(*args, **kwargs)
            self.failure_count = 0
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure = datetime.utcnow()
            raise

    def is_open(self) -> bool:
        if self.failure_count < self.failure_threshold:
            return False
        if self.last_failure and datetime.utcnow() - self.last_failure > self.recovery_time:
            self.failure_count = 0
            return False
        return True


class BaseConnector(ABC):
    """Universal base class for all software connectors."""

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.is_connected: bool = False
        self.is_connected = False
        self.last_health_check: Optional[datetime] = None
        self.rate_limiter = self._create_rate_limiter()
        self.circuit_breaker = self._create_circuit_breaker()

    # Core Interface Methods
    @abstractmethod
    async def connect(self) -> OperationResult:
        """Establish connection to the target software."""

    @abstractmethod
    async def disconnect(self) -> OperationResult:
        """Close connection and cleanup resources."""

    @abstractmethod
    async def health_check(self) -> OperationResult:
        """Check connector health and connectivity."""

    # Resource Discovery
    @abstractmethod
    async def list_resources(
        self, resource_type: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """List available resources (documents, files, etc.)."""

    @abstractmethod
    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        """Get detailed metadata for a specific resource."""

    # Content Operations
    @abstractmethod
    async def read_resource(self, resource_id: str, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        """Read content from a resource and convert to CIR."""

    @abstractmethod
    async def write_resource(
        self, resource_id: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Write CIR content to a resource."""

    @abstractmethod
    async def create_resource(
        self, resource_type: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Create new resource from CIR content."""

    @abstractmethod
    async def delete_resource(self, resource_id: str) -> OperationResult:
        """Delete a resource."""

    # Search Operations
    @abstractmethod
    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Search for content across resources."""

    # Optional Advanced Operations
    async def watch_changes(self, resource_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Watch for real-time changes (if supported)."""
        """Establish connection to the target software"""

    @abstractmethod
    async def disconnect(self) -> OperationResult:
        """Close connection and cleanup resources"""

    @abstractmethod
    async def health_check(self) -> OperationResult:
        """Check connector health and connectivity"""

    # Resource Discovery
    @abstractmethod
    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        """List available resources (documents, files, etc.)"""

    @abstractmethod
    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        """Get detailed metadata for a specific resource"""

    # Content Operations
    @abstractmethod
    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        """Read content from a resource and convert to CIR"""

    @abstractmethod
    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        """Write CIR content to a resource"""

    @abstractmethod
    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        """Create new resource from CIR content"""

    @abstractmethod
    async def delete_resource(self, resource_id: str) -> OperationResult:
        """Delete a resource"""

    # Search Operations
    @abstractmethod
    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        """Search for content across resources"""

    # Optional Advanced Operations
    async def watch_changes(self, resource_id: str = None) -> AsyncIterator[Dict[str, Any]]:
        """Watch for real-time changes (if supported)"""

        if ConnectorCapability.WATCH not in self.config.capabilities:
            raise NotImplementedError("Watch capability not supported")

        while True:
            await asyncio.sleep(30)
            yield {"type": "heartbeat", "timestamp": datetime.utcnow()}

    async def batch_operation(self, operations: List[Dict[str, Any]]) -> List[OperationResult]:
        """Execute multiple operations in batch (if supported)."""

        if ConnectorCapability.BATCH not in self.config.capabilities:
            results = []
            for op in operations:
                result = await self._execute_single_operation(op)
                results.append(result)
            return results

        return await self._execute_batch_operations(operations)

    # Utility Methods
    def supports_capability(self, capability: ConnectorCapability) -> bool:
        """Check if connector supports a specific capability."""

        return capability in self.config.capabilities

    async def _execute_with_rate_limiting(self, operation_func, *args, **kwargs):
        """Execute operation with rate limiting"""

        await self.rate_limiter.acquire()
        return await self.circuit_breaker.call(operation_func, *args, **kwargs)

    def _create_rate_limiter(self):
        limit = self.config.rate_limits.get("concurrent", 5)
        return _AsyncSemaphoreRateLimiter(limit)

    def _create_circuit_breaker(self):
        return _PassthroughCircuitBreaker()

    async def _execute_single_operation(self, operation: Dict[str, Any]) -> OperationResult:
        """Execute a single operation described by a dict."""

        operation_name = operation.get("name")
        args = operation.get("args", [])
        kwargs = operation.get("kwargs", {})
        method = getattr(self, operation_name, None)
        if not method:
            return OperationResult(success=False, error=f"Operation not supported: {operation_name}")
        return await method(*args, **kwargs)

    async def _execute_batch_operations(self, operations: List[Dict[str, Any]]) -> List[OperationResult]:
        """Placeholder batch execution to be overridden by connectors."""

        results = []
        for op in operations:
            results.append(await self._execute_single_operation(op))
        return results


class _StubProcessor:
    """Placeholder processor used when specific file processors are unavailable."""

    async def process_file(self, path: Path) -> Any:  # pragma: no cover - trivial
        raise NotImplementedError("File processor not implemented")

    async def generate_file(self, cir_content: Any, path: Path) -> None:  # pragma: no cover - trivial
        raise NotImplementedError("File processor not implemented")
        """Create rate limiter based on config"""

        return SimpleAsyncRateLimiter(self.config.rate_limits)

    def _create_circuit_breaker(self):
        """Create circuit breaker for fault tolerance"""

        failure_threshold = self.config.timeout_settings.get("failure_threshold", 3)
        recovery_time = self.config.timeout_settings.get("recovery_time_seconds", 30)
        return SimpleCircuitBreaker(failure_threshold=failure_threshold, recovery_time_seconds=recovery_time)

    async def _execute_single_operation(self, operation: Dict[str, Any]) -> OperationResult:
        name = operation.get("name")
        args = operation.get("args", [])
        kwargs = operation.get("kwargs", {})
        target = getattr(self, name, None)

        if not callable(target):
            return OperationResult(success=False, error=f"Unsupported operation: {name}")

        return await target(*args, **kwargs)

    async def _execute_batch_operations(self, operations: List[Dict[str, Any]]) -> List[OperationResult]:
        return [await self._execute_single_operation(op) for op in operations]

    def _apply_filters(self, resources: Iterable[Dict[str, Any]], filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not filters:
            return list(resources)

        filtered: List[Dict[str, Any]] = []
        for resource in resources:
            include = True
            for key, expected in filters.items():
                value = resource.get(key)
                if isinstance(expected, str) and isinstance(value, str):
                    if expected.lower() not in value.lower():
                        include = False
                        break
                elif value != expected:
                    include = False
                    break
            if include:
                filtered.append(resource)
        return filtered


class MicrosoftGraphConnector(BaseConnector):
    """Connector for Microsoft Graph API (Word, Excel, PowerPoint, OneDrive, OneNote)."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.graph_client = None
        self.supported_types = {
            "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "powerpoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "onenote": "application/onenote",
            "pdf": "application/pdf",
        }

    async def connect(self) -> OperationResult:
        if GraphServiceClient is None or ClientSecretCredential is None:
            return OperationResult(success=False, error="Microsoft Graph dependencies not installed")

        try:
            credential = ClientSecretCredential(
                tenant_id=self.config.credentials.get("tenant_id"),
                client_id=self.config.credentials.get("client_id"),
                client_secret=self.config.credentials.get("client_secret"),
            )

            self.graph_client = GraphServiceClient(credentials=credential, scopes=["https://graph.microsoft.com/.default"])
            await self.graph_client.me.get()
            self.is_connected = True
            return OperationResult(success=True, data={"status": "connected"})
        except Exception as exc:  # pragma: no cover - network dependent
            return OperationResult(success=False, error=str(exc))

    async def disconnect(self) -> OperationResult:
        self.is_connected = False
        self.graph_client = None
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        if not self.is_connected:
            return OperationResult(success=False, error="Not connected")

        try:
            await self.graph_client.me.get()
            self.last_health_check = datetime.utcnow()
            return OperationResult(success=True, data={"status": "healthy"})
        except Exception as exc:  # pragma: no cover - network dependent
            return OperationResult(success=False, error=str(exc))

    async def list_resources(
        self, resource_type: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        if not self.is_connected:
            return OperationResult(success=False, error="Not connected")

        if GraphServiceClient is None:
            return OperationResult(success=False, error="Microsoft Graph dependencies not installed")

        try:
            resources: List[Dict[str, Any]] = []
            if not resource_type or resource_type == "onedrive":
                drive_items = await self.graph_client.me.drive.root.children.get()
                for item in drive_items.value:
                    resources.append(
                        {
                            "id": item.id,
                            "name": item.name,
                            "type": "onedrive",
                            "mime_type": getattr(item.file, "mime_type", None) if getattr(item, "file", None) else None,
                            "size": getattr(item, "size", None),
                            "modified": getattr(item, "last_modified_date_time", None),
                            "path": getattr(item, "web_url", None),
                        }
                    )

            if not resource_type or resource_type == "onenote":
                notebooks = await self.graph_client.me.onenote.notebooks.get()
                for notebook in notebooks.value:
                    resources.append(
                        {
                            "id": notebook.id,
                            "name": notebook.display_name,
                            "type": "onenote_notebook",
                            "created": getattr(notebook, "created_date_time", None),
                            "modified": getattr(notebook, "last_modified_date_time", None),
                        }
                    )

            if filters:
                resources = [res for res in resources if all(res.get(k) == v for k, v in filters.items())]

            return OperationResult(success=True, data=resources)
        except Exception as exc:  # pragma: no cover - network dependent
            return OperationResult(success=False, error=str(exc))

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="Metadata retrieval not implemented")

    async def read_resource(self, resource_id: str, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        if not self.is_connected:
            return OperationResult(success=False, error="Not connected")
        return OperationResult(success=False, error="Read operation not implemented")

    async def write_resource(self, resource_id: str, cir_content: Any, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        if not self.is_connected:
            return OperationResult(success=False, error="Not connected")
        return OperationResult(success=False, error="Write operation not implemented")

    async def create_resource(
        self, resource_type: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return OperationResult(success=False, error="Create operation not implemented")

    async def delete_resource(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="Delete operation not implemented")

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        if not self.is_connected:
            return OperationResult(success=False, error="Not connected")
        return OperationResult(success=False, error="Search operation not implemented")
        if not self._dependencies_available(["microsoft.graph", "azure.identity"]):
            return OperationResult(success=False, error="Microsoft Graph dependencies not installed")

        # In an offline environment we skip actual authentication calls.
        self.is_connected = True
        return OperationResult(success=True, data={"status": "connected"})

    async def disconnect(self) -> OperationResult:
        self.graph_client = None
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        self.last_health_check = datetime.utcnow()
        if not self.is_connected:
            return OperationResult(success=False, error="Connector not connected")
        return OperationResult(success=True, data={"status": "healthy", "checked_at": self.last_health_check})

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        if not self.is_connected:
            return OperationResult(success=False, error="Connector not connected")

        # Placeholder implementation; in production this would query Graph endpoints.
        resources: List[Dict[str, Any]] = []
        return OperationResult(success=True, data=self._apply_filters(resources, filters))

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        if not self.is_connected:
            return OperationResult(success=False, error="Connector not connected")

        return OperationResult(success=True, data={"id": resource_id, "type": "graph_resource"})

    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        resource_info = await self._get_resource_info(resource_id)
        document = CIRDocument(
            title=f"Resource {resource_id}",
            document_type=resource_info.get("type", "unknown"),
            sections=[Section(title="Content", content_blocks=[ContentBlock(ContentBlockType.TEXT, "Placeholder content")])],
        )
        return OperationResult(success=True, data=document)

    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=True, data={"id": resource_id, "written": True, "title": cir_content.title})

    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        new_id = options.get("new_id") if options else f"new-{resource_type}-{datetime.utcnow().timestamp()}"
        return OperationResult(success=True, data={"id": new_id, "type": resource_type, "title": cir_content.title})

    async def delete_resource(self, resource_id: str) -> OperationResult:
        return OperationResult(success=True, data={"id": resource_id, "deleted": True})

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        results: List[Dict[str, Any]] = []
        return OperationResult(success=True, data=results)

    async def _get_resource_info(self, resource_id: str) -> Dict[str, Any]:
        # Placeholder mapping to supported types based on extension when possible.
        suffix = Path(resource_id).suffix.lower()
        if suffix == ".docx":
            resource_type = "word"
        elif suffix == ".xlsx":
            resource_type = "excel"
        elif suffix == ".pptx":
            resource_type = "powerpoint"
        elif suffix in {".one", ".onenote"}:
            resource_type = "onenote"
        else:
            resource_type = "generic"
        return {"id": resource_id, "type": resource_type}

    @staticmethod
    def _dependencies_available(modules: List[str]) -> bool:
        return all(importlib.util.find_spec(module) is not None for module in modules)


class _PlainTextProcessor:
    """Minimal processor to convert files to and from CIRDocument."""

    async def process_file(self, file_path: Path) -> CIRDocument:
        content = file_path.read_text(encoding="utf-8", errors="ignore") if file_path.exists() else ""
        section = Section(title=file_path.name, content_blocks=[ContentBlock(ContentBlockType.TEXT, content)])
        return CIRDocument(title=file_path.stem, document_type=file_path.suffix.lstrip("."), sections=[section])

    async def generate_file(self, cir_content: CIRDocument, file_path: Path) -> None:
        text_sections = []
        for section in cir_content.sections:
            text_sections.append(section.title)
            for block in section.content_blocks:
                text_sections.append(str(block.content))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("\n\n".join(text_sections), encoding="utf-8")


class OfficeFileConnector(BaseConnector):
    """Direct file format connector for Office documents (DOCX, XLSX, PPTX)."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.base_path = Path(config.settings.get("base_path", "."))
        self.processors = {
            ".docx": _StubProcessor(),
            ".xlsx": _StubProcessor(),
            ".pptx": _StubProcessor(),
        }
        processor = _PlainTextProcessor()
        self.processors = {".docx": processor, ".xlsx": processor, ".pptx": processor}

    async def connect(self) -> OperationResult:
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            test_file = self.base_path / ".test_access"
            test_file.write_text("test")
            test_file.unlink()
            self.is_connected = True
            return OperationResult(success=True, data={"status": "connected"})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def disconnect(self) -> OperationResult:
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        exists = self.base_path.exists()
        self.last_health_check = datetime.utcnow()
        return OperationResult(success=exists, data={"path_exists": exists})

    async def list_resources(
        self, resource_type: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        self.last_health_check = datetime.utcnow()
        exists = self.base_path.exists()
        return OperationResult(success=exists, data={"checked_at": self.last_health_check}, error=None if exists else "Base path missing")

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        try:
            resources: List[Dict[str, Any]] = []
            patterns = ["*.docx", "*.xlsx", "*.pptx"]
            if resource_type:
                type_patterns = {"word": ["*.docx"], "excel": ["*.xlsx"], "powerpoint": ["*.pptx"]}
                patterns = type_patterns.get(resource_type, patterns)

            for pattern in patterns:
                for file_path in self.base_path.rglob(pattern):
                    if file_path.is_file():
                        stat = file_path.stat()
                        resources.append(
                            {
                                "id": str(file_path.relative_to(self.base_path)),
                                "name": file_path.name,
                                "type": self._get_file_type(file_path.suffix),
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime),
                                "path": str(file_path),
                            }
                        )

            if filters:
                resources = [res for res in resources if all(res.get(k) == v for k, v in filters.items())]

            return OperationResult(success=True, data=resources)
            return OperationResult(success=True, data=self._apply_filters(resources, filters))
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")

        stat = file_path.stat()
        metadata = {
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "suffix": file_path.suffix,
        }
        return OperationResult(success=True, data=metadata)

    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        try:
            file_path = self.base_path / resource_id
            if not file_path.exists():
                return OperationResult(success=False, error="File not found")
            processor = self.processors.get(file_path.suffix)
            if not processor:
                return OperationResult(success=False, error="Unsupported file type")
            cir_document = await processor.process_file(file_path)
            return OperationResult(success=True, data=cir_document)
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))
    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        file_path = self.base_path / resource_id
        processor = self.processors.get(file_path.suffix)
        if not processor:
            return OperationResult(success=False, error="Unsupported file type")
        try:
            await processor.generate_file(cir_content, file_path)
            return OperationResult(success=True, data={"path": str(file_path)})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))
    async def create_resource(
        self, resource_type: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        filename = options.get("filename") if options else None
        if not filename:
            filename = f"new_document{self._default_extension(resource_type)}"

        return await self.write_resource(filename, cir_content, options)
    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        filename = options.get("filename") if options else None
        suffix_map = {"word": ".docx", "excel": ".xlsx", "powerpoint": ".pptx"}
        suffix = suffix_map.get(resource_type, ".docx")
        file_id = filename or f"{cir_content.title}{suffix}"
        return await self.write_resource(file_id, cir_content, options)

    async def delete_resource(self, resource_id: str) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")
        try:
            file_path.unlink()
            return OperationResult(success=True, data={"deleted": resource_id})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        resources = await self.list_resources(filters=filters)
        if not resources.success:
            return resources

        matches = [res for res in resources.data if query.lower() in res.get("name", "").lower()]
        return OperationResult(success=True, data=matches)

    def _get_file_type(self, suffix: str) -> str:
        return {".docx": "word", ".xlsx": "excel", ".pptx": "powerpoint"}.get(suffix.lower(), "unknown")

    def _default_extension(self, resource_type: str) -> str:
        defaults = {"word": ".docx", "excel": ".xlsx", "powerpoint": ".pptx"}
        return defaults.get(resource_type, ".docx")


class PDFConnector(BaseConnector):
    """Connector for PDF files with optional OCR support."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.base_path = Path(config.settings.get("base_path", "."))
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> OperationResult:
        self.is_connected = True
        return OperationResult(success=True, data={"status": "connected"})

    async def disconnect(self) -> OperationResult:
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        exists = self.base_path.exists()
        self.last_health_check = datetime.utcnow()
        return OperationResult(success=exists, data={"path_exists": exists, "checked_at": self.last_health_check})

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        resources: List[Dict[str, Any]] = []
        for file_path in self.base_path.rglob("*.pdf"):
            if file_path.is_file():
                stat = file_path.stat()
                resources.append(
                    {
                        "id": str(file_path.relative_to(self.base_path)),
                        "name": file_path.name,
                        "type": "pdf",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "path": str(file_path),
                    }
                )

        if filters:
            resources = self._apply_filters(resources, filters)

        return OperationResult(success=True, data=resources)

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")

        stat = file_path.stat()
        return OperationResult(
            success=True,
            data={
                "id": resource_id,
                "name": file_path.name,
                "type": "pdf",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "suffix": file_path.suffix,
            },
        )

    async def read_resource(self, resource_id: str, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")

        try:
            return OperationResult(
                success=True,
                data={"id": resource_id, "name": file_path.name, "path": str(file_path)},
            )
        except Exception as exc:  # pragma: no cover - depends on local files
            return OperationResult(success=False, error=str(exc))

    async def write_resource(
        self, resource_id: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return OperationResult(success=False, error="PDF writing not implemented")

    async def create_resource(
        self, resource_type: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return OperationResult(success=False, error="Create operation not implemented")

    async def delete_resource(self, resource_id: str) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")

        file_path.unlink()
        return OperationResult(success=True, data={"path": str(file_path)})

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        list_result = await self.list_resources(filters=filters)
        if not list_result.success:
            return list_result
        query_lower = query.lower()
        matched = [res for res in list_result.data if query_lower in res.get("name", "").lower()]
        return OperationResult(success=True, data=matched)
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")
        text_content = file_path.read_text(encoding="utf-8", errors="ignore")
        section = Section(title="Page 1", content_blocks=[ContentBlock(ContentBlockType.TEXT, text_content)])
        document = CIRDocument(title=file_path.stem, document_type="pdf", sections=[section])
        return OperationResult(success=True, data=document)

    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        file_path = self.base_path / resource_id
        text_parts: List[str] = []
        for section in cir_content.sections:
            text_parts.append(section.title)
            for block in section.content_blocks:
                text_parts.append(str(block.content))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("\n\n".join(text_parts), encoding="utf-8")
        return OperationResult(success=True, data={"path": str(file_path)})

    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        filename = options.get("filename") if options else f"{cir_content.title}.pdf"
        return await self.write_resource(filename, cir_content, options)

    async def delete_resource(self, resource_id: str) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")
        try:
            file_path.unlink()
            return OperationResult(success=True, data={"deleted": resource_id})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        resources = await self.list_resources(filters=filters)
        if not resources.success:
            return resources

        matches = [res for res in resources.data if query.lower() in res.get("name", "").lower()]
        return OperationResult(success=True, data=matches)

    async def _perform_ocr(self, image: Any) -> str:
        file_path.unlink()
        return OperationResult(success=True, data={"path": str(file_path)})

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        list_result = await self.list_resources(filters=filters)
        if not list_result.success:
            return list_result
        query_lower = query.lower()
        matched = [res for res in list_result.data if query_lower in res.get("name", "").lower()]
        return OperationResult(success=True, data=matched)

    async def _perform_ocr(self, image) -> str:
        if self.ocr_engine:
            return self.ocr_engine.image_to_string(image)
        return ""

    def _initialize_ocr(self):
        try:  # pragma: no cover - optional dependency
            import pytesseract

            return pytesseract
        except Exception:
            return None
        if importlib.util.find_spec("pytesseract"):
            import pytesseract  # type: ignore

            return pytesseract
        return None


class GitConnector(BaseConnector):
    """Connector for Git repositories using GitPython."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.repo_path = Path(config.settings.get("repo_path", "."))
        self.repo: Optional[Repo] = None

    async def connect(self) -> OperationResult:
        if Repo is None:
            return OperationResult(success=False, error="GitPython not installed")
        try:
            self.repo_path.mkdir(parents=True, exist_ok=True)
            if (self.repo_path / ".git").exists():
                self.repo = Repo(str(self.repo_path))
            else:
                self.repo = Repo.init(str(self.repo_path))
            self.is_connected = True
            return OperationResult(success=True, data={"status": "connected"})
        except Exception as exc:  # pragma: no cover - git dependent
            return OperationResult(success=False, error=str(exc))

    async def disconnect(self) -> OperationResult:
        self.repo = None
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        exists = self.repo_path.exists() and (self.repo_path / ".git").exists()
        self.last_health_check = datetime.utcnow()
        return OperationResult(success=exists, data={"repo_exists": exists, "checked_at": self.last_health_check})

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        if not self.repo:
            return OperationResult(success=False, error="Repository not connected")

        try:
            resources: List[Dict[str, Any]] = []
            for item in self.repo.index.entries:
                file_path = Path(item[0])
                full_path = self.repo_path / file_path
                if full_path.exists():
                    stat = full_path.stat()
                    commits = list(self.repo.iter_commits(paths=str(file_path), max_count=1))
                    last_commit = commits[0] if commits else None
                    resources.append(
                        {
                            "id": str(file_path),
                            "name": file_path.name,
                            "type": "git_file",
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                            "path": str(file_path),
                            "last_commit": {
                                "hash": last_commit.hexsha if last_commit else None,
                                "message": last_commit.message if last_commit else None,
                                "author": str(last_commit.author) if last_commit else None,
                                "date": last_commit.committed_datetime if last_commit else None,
                            },
                        }
                    )
            return OperationResult(success=True, data=resources)
        except Exception as exc:  # pragma: no cover - git dependent
            return OperationResult(success=False, error=str(exc))

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        if not self.repo:
            return OperationResult(success=False, error="Repository not connected")
        try:
            commits = list(self.repo.iter_commits(paths=resource_id))
            history = [
                {
                    "hash": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime,
                }
                for commit in commits
            ]
            return OperationResult(success=True, data={"history": history})
        except Exception as exc:  # pragma: no cover - git dependent
            return OperationResult(success=False, error=str(exc))

    async def read_resource(self, resource_id: str, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        file_path = self.repo_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")
        try:
            return OperationResult(success=True, data=file_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def write_resource(self, resource_id: str, cir_content: Any, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        if not self.repo:
            return OperationResult(success=False, error="Repository not connected")
        file_path = self.repo_path / resource_id
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(str(cir_content), encoding="utf-8")
            self.repo.index.add([str(file_path.relative_to(self.repo_path))])
            if options and options.get("commit_message"):
                commit = self.repo.index.commit(options["commit_message"])
                return OperationResult(success=True, data={"commit_hash": commit.hexsha})
            return OperationResult(success=True, data={"path": str(file_path)})
        except Exception as exc:  # pragma: no cover - git dependent
            return OperationResult(success=False, error=str(exc))

    async def create_resource(
        self, resource_type: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return await self.write_resource(options.get("filename", "new_file"), cir_content, options or {})

    async def disconnect(self) -> OperationResult:
        self.repo = None
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        self.last_health_check = datetime.utcnow()
        return OperationResult(success=self.repo is not None, data={"checked_at": self.last_health_check})

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        if not self.repo:
            return OperationResult(success=False, error="Repository not connected")
        resources: List[Dict[str, Any]] = []
        for item in self.repo.index.entries:
            file_path = Path(item[0])
            full_path = self.repo_path / file_path
            if full_path.exists():
                stat = full_path.stat()
                commits = list(self.repo.iter_commits(paths=str(file_path), max_count=1))
                last_commit = commits[0] if commits else None
                resources.append(
                    {
                        "id": str(file_path),
                        "name": file_path.name,
                        "type": "git_file",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "path": str(file_path),
                        "last_commit": {
                            "hash": last_commit.hexsha if last_commit else None,
                            "message": last_commit.message if last_commit else None,
                            "author": str(last_commit.author) if last_commit else None,
                            "date": last_commit.committed_datetime if last_commit else None,
                        },
                    }
                )
        return OperationResult(success=True, data=self._apply_filters(resources, filters))

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        return OperationResult(success=True, data={"id": resource_id, "type": "git_file"})

    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        file_path = self.repo_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        section = Section(title=file_path.name, content_blocks=[ContentBlock(ContentBlockType.TEXT, content)])
        document = CIRDocument(title=file_path.stem, document_type="text", sections=[section])
        return OperationResult(success=True, data=document)

    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        file_path = self.repo_path / resource_id
        content_lines: List[str] = []
        for section in cir_content.sections:
            content_lines.append(section.title)
            for block in section.content_blocks:
                content_lines.append(str(block.content))
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("\n\n".join(content_lines), encoding="utf-8")
        if self.repo:
            self.repo.index.add([str(resource_id)])
            commit_message = options.get("commit_message", f"Update {resource_id}") if options else f"Update {resource_id}"
            commit = self.repo.index.commit(commit_message)
            return OperationResult(success=True, data={"path": str(file_path), "commit_hash": commit.hexsha})
        return OperationResult(success=True, data={"path": str(file_path), "commit_hash": None})

    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        filename = options.get("filename") if options else f"{cir_content.title}.md"
        return await self.write_resource(filename, cir_content, options)

    async def delete_resource(self, resource_id: str) -> OperationResult:
        file_path = self.repo_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")
        try:
            file_path.unlink()
            if self.repo:
                self.repo.index.remove([resource_id], working_tree=True)
            return OperationResult(success=True, data={"deleted": resource_id})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        if not self.repo:
            return OperationResult(success=False, error="Repository not connected")

        matching_files: List[Dict[str, Any]] = []
        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file() and query.lower() in file_path.name.lower():
                stat = file_path.stat()
                matching_files.append(
                    {
                        "id": str(file_path.relative_to(self.repo_path)),
                        "name": file_path.name,
                        "type": "git_file",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "path": str(file_path),
                    }
                )
        return OperationResult(success=True, data=matching_files)
        file_path.unlink()
        if self.repo:
            self.repo.index.remove([str(resource_id)])
            commit_message = f"Delete {resource_id}"
            commit = self.repo.index.commit(commit_message)
            return OperationResult(success=True, data={"commit_hash": commit.hexsha})
        return OperationResult(success=True, data={"path": str(file_path)})

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        list_result = await self.list_resources(filters=filters)
        if not list_result.success:
            return list_result
        query_lower = query.lower()
        matched = [res for res in list_result.data if query_lower in res.get("name", "").lower()]
        return OperationResult(success=True, data=matched)

    async def get_version_history(self, resource_id: str) -> OperationResult:
        if not self.repo:
            return OperationResult(success=False, error="Repository not connected")
        commits = list(self.repo.iter_commits(paths=resource_id))
        history = []
        for commit in commits:
            history.append(
                {
                    "hash": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime,
                    "changes": commit.stats.files.get(resource_id, {}),
                }
            )
        return OperationResult(success=True, data=history)


class OpenAIConnector(BaseConnector):
    """Connector for OpenAI API integration."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.client: Optional[AsyncOpenAI] = None
        self.model_config = config.settings.get(
            "model_config", {"default_model": "gpt-4", "max_tokens": 4000, "temperature": 0.7}
        )

    async def connect(self) -> OperationResult:
        if AsyncOpenAI is None:
            return OperationResult(success=False, error="OpenAI client not installed")

        try:
            self.client = AsyncOpenAI(api_key=self.config.credentials.get("api_key"))
            await self.client.models.list()
            self.is_connected = True
            return OperationResult(success=True, data={"status": "connected"})
        except Exception as exc:  # pragma: no cover - network dependent
            return OperationResult(success=False, error=str(exc))

    async def disconnect(self) -> OperationResult:
        self.is_connected = False
        self.client = None
        self.client = None
        self.model_config = config.settings.get(
            "model_config",
            {"default_model": "gpt-4", "max_tokens": 4000, "temperature": 0.7},
        )

    async def connect(self) -> OperationResult:
        if not importlib.util.find_spec("openai"):
            return OperationResult(success=False, error="OpenAI SDK is not installed")
        from openai import AsyncOpenAI  # type: ignore

        self.client = AsyncOpenAI(api_key=self.config.credentials.get("api_key"))
        self.is_connected = True
        return OperationResult(success=True, data={"status": "connected"})

    async def disconnect(self) -> OperationResult:
        self.client = None
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        self.last_health_check = datetime.utcnow()
        return OperationResult(success=self.is_connected, data={"connected": self.is_connected})

    async def list_resources(
        self, resource_type: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return OperationResult(success=True, data=[])

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="Metadata retrieval not supported")

    async def read_resource(self, resource_id: str, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        return OperationResult(success=False, error="Read operation not supported")

    async def write_resource(self, resource_id: str, cir_content: Any, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        return OperationResult(success=False, error="Write operation not supported")

    async def create_resource(
        self, resource_type: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return OperationResult(success=False, error="Create operation not supported")

    async def delete_resource(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="Delete operation not supported")

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return OperationResult(success=False, error="Search operation not supported")

    async def process_document(
        self, cir_document: Any, operation: str, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        if not self.client:
            return OperationResult(success=False, error="Client not connected")

        options = options or {}
        prompt = self._create_prompt(operation, str(cir_document), options)
        try:
            response = await self.client.chat.completions.create(
                model=options.get("model", self.model_config["default_model"]),
                messages=[
                    {"role": "system", "content": "You are a helpful document processing assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=options.get("max_tokens", self.model_config["max_tokens"]),
                temperature=options.get("temperature", self.model_config["temperature"]),
            )
            result_text = response.choices[0].message.content
            return OperationResult(success=True, data=result_text)
        except Exception as exc:  # pragma: no cover - network dependent
            return OperationResult(success=False, error=str(exc))

    def _create_prompt(self, operation: str, document_text: str, options: Optional[Dict[str, Any]] = None) -> str:
        if not self.client:
            return OperationResult(success=False, error="Client not initialized")
        return OperationResult(success=True, data={"checked_at": self.last_health_check})

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=True, data=[])

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        return OperationResult(success=True, data={"id": resource_id})

    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="Read not supported for OpenAIConnector")

    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="Write not supported for OpenAIConnector")

    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="Create not supported for OpenAIConnector")

    async def delete_resource(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="Delete not supported for OpenAIConnector")

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="Search not supported for OpenAIConnector")

    async def process_document(self, cir_document: CIRDocument, operation: str, options: Dict[str, Any] = None) -> OperationResult:
        if not self.client:
            return OperationResult(success=False, error="Client not initialized")

        document_text = await self._cir_to_text(cir_document)
        prompt = await self._create_prompt(operation, document_text, options or {})

        response = await self.client.chat.completions.create(
            model=(options or {}).get("model", self.model_config["default_model"]),
            messages=[
                {"role": "system", "content": "You are a helpful document processing assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=(options or {}).get("max_tokens", self.model_config["max_tokens"]),
            temperature=(options or {}).get("temperature", self.model_config["temperature"]),
        )
        result_text = response.choices[0].message.content

        if (options or {}).get("return_cir", False):
            result_cir = await self._text_to_cir(result_text, cir_document.document_type)
            return OperationResult(success=True, data=result_cir)
        return OperationResult(success=True, data=result_text)

    async def _cir_to_text(self, cir_document: CIRDocument) -> str:
        parts: List[str] = [cir_document.title]
        for section in cir_document.sections:
            parts.append(section.title)
            for block in section.content_blocks:
                parts.append(str(block.content))
        return "\n\n".join(parts)

    async def _create_prompt(self, operation: str, document_text: str, options: Dict[str, Any] = None) -> str:
        options = options or {}
        prompts = {
            "summarize": f"Please provide a concise summary of the following document:\n\n{document_text}",
            "extract_key_points": f"Extract the key points from this document:\n\n{document_text}",
            "translate": f"Translate this document to {options.get('target_language', 'English')}:\n\n{document_text}",
            "improve_writing": f"Improve the writing quality of this document:\n\n{document_text}",
            "generate_outline": f"Create an outline based on this document:\n\n{document_text}",
        }
        return prompts.get(operation, f"Process this document for {operation}:\n\n{document_text}")


class ConnectorRegistry:
    """Registry of available connector types and their configurations."""

    def __init__(self):
        self.connector_types = {
            "microsoft_graph": MicrosoftGraphConnector,
            "office_files": OfficeFileConnector,
            "pdf": PDFConnector,
            "git": GitConnector,
            "openai": OpenAIConnector,
        }

    def get_connector_class(self, connector_type: str) -> Optional[type]:
        return self.connector_types.get(connector_type)

    def create_connector(self, connector_type: str, config: ConnectorConfig) -> BaseConnector:
        connector_class = self.get_connector_class(connector_type)
        if not connector_class:
            raise ValueError(f"Unknown connector type: {connector_type}")
        return connector_class(config)
    async def _text_to_cir(self, text: str, document_type: str) -> CIRDocument:
        section = Section(title="AI Output", content_blocks=[ContentBlock(ContentBlockType.TEXT, text)])
        return CIRDocument(title=f"Processed {document_type}", document_type=document_type, sections=[section])


class AppleNotesConnector(BaseConnector):
    """Placeholder for future Apple Notes connector."""

    async def connect(self) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def disconnect(self) -> OperationResult:
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def delete_resource(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="AppleNotesConnector not implemented")


class SystemDaemonConnector(BaseConnector):
    """Placeholder for future system daemon connector."""

    async def connect(self) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def disconnect(self) -> OperationResult:
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def delete_resource(self, resource_id: str) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        return OperationResult(success=False, error="SystemDaemonConnector not implemented")


class ConnectorManager:
    """Manages all connector instances and provides unified interface."""

    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.connector_registry = ConnectorRegistry()

    async def register_connector(self, connector_id: str, connector: BaseConnector):
        self.connectors[connector_id] = connector
        await connector.connect()

    async def get_connector(self, connector_id: str) -> Optional[BaseConnector]:
        return self.connectors.get(connector_id)

    async def execute_operation(self, connector_id: str, operation: str, *args, **kwargs) -> OperationResult:
        connector = await self.get_connector(connector_id)
        if not connector:
            return OperationResult(success=False, error="Connector not found")

        if not connector.is_connected:
            await connector.connect()

        method = getattr(connector, operation, None)
        if not method:
            return OperationResult(success=False, error="Operation not supported")

        return await method(*args, **kwargs)

    async def search_across_connectors(
        self, query: str, connector_ids: Optional[List[str]] = None
    ) -> Dict[str, OperationResult]:
        target_connectors = connector_ids or list(self.connectors.keys())
        results: Dict[str, OperationResult] = {}

        if not connector.is_connected:
            await connector.connect()
        method = getattr(connector, operation, None)
        if not method:
            return OperationResult(success=False, error="Operation not supported")
        return await method(*args, **kwargs)

    async def search_across_connectors(self, query: str, connector_ids: List[str] = None) -> Dict[str, OperationResult]:
        target_connectors = connector_ids or list(self.connectors.keys())
        results: Dict[str, OperationResult] = {}
        tasks = []
        for connector_id in target_connectors:
            connector = self.connectors.get(connector_id)
            if connector and connector.supports_capability(ConnectorCapability.SEARCH):
                tasks.append(self._search_connector(connector_id, connector, query))

        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(search_results):
            connector_id = target_connectors[i]
            if isinstance(result, Exception):
                results[connector_id] = OperationResult(success=False, error=str(result))
            else:
                results[connector_id] = result

        return results

    async def _search_connector(self, connector_id: str, connector: BaseConnector, query: str) -> OperationResult:
        try:
            return await connector.search(query)
        except Exception as exc:  # pragma: no cover - connector dependent
            return OperationResult(success=False, error=str(exc))
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))


class ConnectorRegistry:
    """Registry of available connector types and their configurations."""

    def __init__(self):
        self.connector_types = {
            "microsoft_graph": MicrosoftGraphConnector,
            "office_files": OfficeFileConnector,
            "pdf": PDFConnector,
            "git": GitConnector,
            "openai": OpenAIConnector,
            "apple_notes": AppleNotesConnector,
            "system_daemon": SystemDaemonConnector,
        }

    def get_connector_class(self, connector_type: str) -> Optional[type]:
        return self.connector_types.get(connector_type)

    def create_connector(self, connector_type: str, config: ConnectorConfig) -> BaseConnector:
        connector_class = self.get_connector_class(connector_type)
        if not connector_class:
            raise ValueError(f"Unknown connector type: {connector_type}")
        return connector_class(config)


__all__ = [
    "AppleNotesConnector",
    "BaseConnector",
    "CIRDocument",
    "ConnectorCapability",
    "ConnectorConfig",
    "ConnectorManager",
    "ConnectorRegistry",
    "ContentBlock",
    "ContentBlockType",
    "GitConnector",
    "MicrosoftGraphConnector",
    "OfficeFileConnector",
    "OpenAIConnector",
    "OperationResult",
    "PDFConnector",
    "Section",
    "SimpleAsyncRateLimiter",
    "SimpleCircuitBreaker",
    "SystemDaemonConnector",
]
