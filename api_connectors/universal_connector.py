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


@dataclass
class OperationResult:
    """Standard result format for all connector operations."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
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


class BaseConnector(ABC):
    """Universal base class for all software connectors."""

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.is_connected: bool = False
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

    async def read_resource(self, resource_id: str, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")

        processor = self.processors.get(file_path.suffix)
        if not processor:
            return OperationResult(success=False, error="Unsupported file type")

        try:
            cir_document = await processor.process_file(file_path)
            return OperationResult(success=True, data=cir_document)
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def write_resource(self, resource_id: str, cir_content: Any, options: Optional[Dict[str, Any]] = None) -> OperationResult:
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
        self.ocr_engine = self._initialize_ocr()

    async def connect(self) -> OperationResult:
        self.is_connected = True
        return OperationResult(success=True, data={"status": "connected"})

    async def disconnect(self) -> OperationResult:
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        self.last_health_check = datetime.utcnow()
        return OperationResult(success=True, data={"status": "healthy"})

    async def list_resources(
        self, resource_type: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
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
            resources = [res for res in resources if all(res.get(k) == v for k, v in filters.items())]

        return OperationResult(success=True, data=resources)

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")

        stat = file_path.stat()
        return OperationResult(
            success=True,
            data={"size": stat.st_size, "modified": datetime.fromtimestamp(stat.st_mtime), "suffix": file_path.suffix},
        )

    async def read_resource(self, resource_id: str, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        if fitz is None:
            return OperationResult(success=False, error="PyMuPDF is not installed")

        file_path = self.base_path / resource_id
        if not file_path.exists():
            return OperationResult(success=False, error="File not found")

        try:
            pdf_document = fitz.open(str(file_path))
            pages: List[str] = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text = page.get_text()
                if not text.strip() and self.ocr_engine and Image is not None:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text = await self._perform_ocr(img)
                pages.append(text)
            pdf_document.close()
            return OperationResult(success=True, data={"pages": pages, "title": file_path.stem})
        except Exception as exc:  # pragma: no cover - depends on local files
            return OperationResult(success=False, error=str(exc))

    async def write_resource(self, resource_id: str, cir_content: Any, options: Optional[Dict[str, Any]] = None) -> OperationResult:
        return OperationResult(success=False, error="PDF writing not implemented")

    async def create_resource(
        self, resource_type: str, cir_content: Any, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        return OperationResult(success=False, error="Create operation not implemented")

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
        if self.ocr_engine:
            return self.ocr_engine.image_to_string(image)
        return ""

    def _initialize_ocr(self):
        try:  # pragma: no cover - optional dependency
            import pytesseract

            return pytesseract
        except Exception:
            return None


class GitConnector(BaseConnector):
    """Connector for Git repositories with version control integration."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.repo_path = Path(config.settings.get("repo_path", "."))
        self.repo: Optional[Repo] = None

    async def connect(self) -> OperationResult:
        if Repo is None:
            return OperationResult(success=False, error="GitPython is not installed")

        try:
            if self.repo_path.exists() and (self.repo_path / ".git").exists():
                self.repo = Repo(str(self.repo_path))
            else:
                self.repo = Repo.init(str(self.repo_path))
            self.is_connected = True
            return OperationResult(success=True, data={"status": "connected"})
        except Exception as exc:  # pragma: no cover - filesystem dependent
            return OperationResult(success=False, error=str(exc))

    async def disconnect(self) -> OperationResult:
        self.is_connected = False
        self.repo = None
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        exists = self.repo_path.exists() and (self.repo_path / ".git").exists()
        self.last_health_check = datetime.utcnow()
        return OperationResult(success=exists, data={"repo_exists": exists})

    async def list_resources(
        self, resource_type: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
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

        tasks = []
        for connector_id in target_connectors:
            connector = self.connectors.get(connector_id)
            if connector and connector.supports_capability(ConnectorCapability.SEARCH):
                tasks.append(self._search_connector(connector_id, connector, query))

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
