"""Universal Connector Interface - The foundation for all software integrations.

Provides a standardized way to interact with any software system while
maintaining flexibility for system-specific optimizations.
"""

from __future__ import annotations

import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional

from assistant_core.cir import CIRDocument


class ConnectorCapability(Enum):
    """Capabilities that connectors can support."""

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
    ANNOTATIONS = "annotations"  # Comment/annotation support
    DIFF = "diff"  # Change detection and diffing


class OperationStatus(Enum):
    """Status of connector operations."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELLED = "cancelled"


@dataclass
class ResourceRef:
    """Reference to a resource in an external system."""

    id: str
    name: str
    path: Optional[str] = None
    resource_type: Optional[str] = None
    size: Optional[int] = None
    modified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


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

    def __post_init__(self) -> None:
        if not self.rate_limits:
            self.rate_limits = {"requests_per_minute": 60}
        if not self.timeout_settings:
            self.timeout_settings = {"read_timeout": 30, "write_timeout": 60}


@dataclass
class OperationResult:
    """Standard result format for all connector operations."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    operation_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = None
    operation_id: Optional[str] = None
    timestamp: datetime = None
    status: OperationStatus = OperationStatus.SUCCESS

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}
        if self.operation_id is None:
            self.operation_id = str(uuid.uuid4())
        if not self.success:
            self.status = OperationStatus.FAILED


class RateLimiter:
    """Simple rate limiter for connector operations."""

    def __init__(self, requests_per_minute: int = 60) -> None:
        self.requests_per_minute = requests_per_minute
        self.requests: List[datetime] = []

    async def acquire(self) -> None:
        """Acquire a rate limit token."""

        now = datetime.utcnow()
        self.requests = [req_time for req_time in self.requests if (now - req_time).total_seconds() < 60]

        if len(self.requests) >= self.requests_per_minute:
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.requests.append(now)


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60) -> None:
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as exc:  # pragma: no cover - passthrough
            await self._on_failure()
            raise exc

    async def _on_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    async def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def _should_attempt_reset(self) -> bool:
        if not self.last_failure_time:
            return False
        return (datetime.utcnow() - self.last_failure_time).total_seconds() >= self.timeout


class BaseConnector(ABC):
    """Universal base class for all software connectors."""

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.system_name = config.connector_type
        self.is_connected = False
        self.last_health_check: Optional[datetime] = None
        self.rate_limiter = RateLimiter(config.rate_limits.get("requests_per_minute", 60))
        self.circuit_breaker = CircuitBreaker()
        self.operation_history: List[Dict[str, Any]] = []

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
    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        """List available resources (documents, files, etc.)."""

    @abstractmethod
    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        """Get detailed metadata for a specific resource."""

    # Content Operations
    @abstractmethod
    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        """Read content from a resource and convert to CIR."""

    @abstractmethod
    async def write_resource(self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        """Write CIR content to a resource."""

    @abstractmethod
    async def create_resource(self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None) -> OperationResult:
        """Create new resource from CIR content."""

    @abstractmethod
    async def delete_resource(self, resource_id: str) -> OperationResult:
        """Delete a resource."""

    # Search Operations
    @abstractmethod
    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        """Search for content across resources."""

    # Optional Advanced Operations
    async def watch_changes(self, resource_id: str = None) -> AsyncIterator[Dict[str, Any]]:
        """Watch for real-time changes (if supported)."""

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

    async def diff_resources(self, resource_id_1: str, resource_id_2: str) -> OperationResult:
        """Compare two resources and return differences."""

        if ConnectorCapability.DIFF not in self.config.capabilities:
            return OperationResult(
                success=False,
                error="Diff capability not supported",
                error_code="CAPABILITY_NOT_SUPPORTED",
            )

        result1 = await self.read_resource(resource_id_1)
        result2 = await self.read_resource(resource_id_2)

        if not (result1.success and result2.success):
            return OperationResult(success=False, error="Failed to read one or both resources for comparison")

        diff_data = await self._generate_diff(result1.data, result2.data)

        return OperationResult(
            success=True,
            data=diff_data,
            metadata={
                "resource_1": resource_id_1,
                "resource_2": resource_id_2,
                "diff_type": "cir_comparison",
            },
        )

    # Utility Methods
    def supports_capability(self, capability: ConnectorCapability) -> bool:
        """Check if connector supports a specific capability."""

        return capability in self.config.capabilities

    async def _execute_with_rate_limiting(self, operation_func, *args, **kwargs):
        """Execute operation with rate limiting and circuit breaker."""

        await self.rate_limiter.acquire()
        return await self.circuit_breaker.call(operation_func, *args, **kwargs)

    async def _log_operation(self, operation: str, result: OperationResult) -> None:
        """Log operation for audit and monitoring."""

        log_entry = {
            "operation": operation,
            "timestamp": datetime.utcnow(),
            "success": result.success,
            "operation_id": result.operation_id,
            "error": result.error,
            "connector": self.system_name,
        }
        self.operation_history.append(log_entry)

        if len(self.operation_history) > 100:
            self.operation_history = self.operation_history[-100:]

    async def _execute_single_operation(self, operation: Dict[str, Any]) -> OperationResult:
        """Execute a single operation from a batch."""

        op_type = operation.get("type")

        if op_type == "read":
            return await self.read_resource(operation["resource_id"], operation.get("options"))
        if op_type == "write":
            return await self.write_resource(operation["resource_id"], operation["content"], operation.get("options"))
        if op_type == "create":
            return await self.create_resource(operation["resource_type"], operation["content"], operation.get("options"))
        if op_type == "delete":
            return await self.delete_resource(operation["resource_id"])

        return OperationResult(success=False, error=f"Unknown operation type: {op_type}", error_code="INVALID_OPERATION")

    async def _execute_batch_operations(self, operations: List[Dict[str, Any]]) -> List[OperationResult]:
        """Execute batch operations - override in specific connectors."""

        results = []
        for op in operations:
            result = await self._execute_single_operation(op)
            results.append(result)
        return results

    async def _generate_diff(self, cir1: CIRDocument, cir2: CIRDocument) -> Dict[str, Any]:
        """Generate a simple diff between two CIR documents."""

        return {
            "title_changed": getattr(cir1, "title", None) != getattr(cir2, "title", None),
            "content_changed": getattr(cir1, "get_all_text", lambda: None)() != getattr(cir2, "get_all_text", lambda: None)(),
            "structure_changed": getattr(cir1, "get_structure_summary", lambda: None)()
            != getattr(cir2, "get_structure_summary", lambda: None)(),
            "metadata_changed": getattr(cir1, "metadata", None) != getattr(cir2, "metadata", None),
            "timestamp": datetime.utcnow(),
        }

    def get_operation_stats(self) -> Dict[str, Any]:
        """Get operation statistics for monitoring."""

        if not self.operation_history:
            return {"total_operations": 0}

        total = len(self.operation_history)
        successful = len([op for op in self.operation_history if op["success"]])

        return {
            "total_operations": total,
            "successful_operations": successful,
            "failed_operations": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "last_operation": self.operation_history[-1] if self.operation_history else None,
            "connector_type": self.system_name,
        }

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

class ConnectorException(Exception):
    """Base exception for connector operations."""

    def __init__(self, message: str, error_code: str = None, connector: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.connector = connector


class AuthenticationException(ConnectorException):
    """Authentication-related errors."""


class RateLimitException(ConnectorException):
    """Rate limiting errors."""


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
class ResourceNotFoundException(ConnectorException):
    """Resource not found errors."""


class UnsupportedOperationException(ConnectorException):
    """Unsupported operation errors."""


class ConnectorHealthMonitor:
    """Monitor health of connector instances."""

    def __init__(self) -> None:
        self.connector_health: Dict[str, Dict[str, Any]] = {}

    async def check_connector_health(self, connector: BaseConnector) -> Dict[str, Any]:
        """Check health of a specific connector."""

        try:
            health_result = await connector.health_check()
            stats = connector.get_operation_stats()

            health_info = {
                "connector_id": connector.config.instance_id,
                "connector_type": connector.system_name,
                "is_healthy": health_result.success,
                "last_check": datetime.utcnow(),
                "error": health_result.error,
                "stats": stats,
                "capabilities": [cap.value for cap in connector.config.capabilities],
            }

            self.connector_health[connector.config.instance_id] = health_info
            return health_info

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
        except Exception as exc:
            health_info = {
                "connector_id": connector.config.instance_id,
                "connector_type": connector.system_name,
                "is_healthy": False,
                "last_check": datetime.utcnow(),
                "error": str(exc),
                "stats": {},
                "capabilities": [],
            }

            self.connector_health[connector.config.instance_id] = health_info
            return health_info

    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health status of all connectors."""

        if not self.connector_health:
            return {"status": "no_connectors", "healthy_count": 0, "total_count": 0}

        healthy_count = len([h for h in self.connector_health.values() if h["is_healthy"]])
        total_count = len(self.connector_health)

        return {
            "status": "healthy" if healthy_count == total_count else "degraded",
            "healthy_count": healthy_count,
            "total_count": total_count,
            "health_percentage": (healthy_count / total_count) * 100 if total_count > 0 else 0,
            "connectors": self.connector_health,
        }
