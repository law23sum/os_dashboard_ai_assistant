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
