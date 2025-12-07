"""API connectors for the OS Dashboard AI Assistant."""

from typing import Any, Dict, Optional
import logging

from .base import IntegrationAPIGateway
from .microsoft_graph import MicrosoftGraphConnector, ResourceRef
from .universal_connector import (
    AuthenticationException,
    BaseConnector,
    ConnectorCapability,
    ConnectorConfig,
    ConnectorManager,
    ConnectorRegistry,
    ContentBlock,
    ContentBlockType,
    MicrosoftGraphConnector,
    GitConnector,
    OfficeFileConnector,
    OpenAIConnector,
    ConnectorException,
    ConnectorHealthMonitor,
    OperationResult,
    Section,
    OperationStatus,
    RateLimitException,
    ResourceNotFoundException,
    UnsupportedOperationException,
)
from .git import GitConnector
from .pdf import PDFConnector

logger = logging.getLogger(__name__)

__version__ = "1.1.0"
__all__ = [
    "AuthenticationException",
    "BaseConnector",
    "ConnectorCapability",
    "ConnectorConfig",
    "ConnectorException",
    "ConnectorHealthMonitor",
    "IntegrationAPIGateway",
    "OperationResult",
    "MicrosoftGraphConnector",
    "OfficeFileConnector",
    "PDFConnector",
    "OpenAIConnector",
    "MicrosoftGraphConnector",
    "OfficeFileConnector",
    "OpenAIConnector",
    "OperationResult",
    "PDFConnector",
    "ResourceRef",
    "Section",
    "OperationResult",
    "OperationStatus",
    "RateLimitException",
    "ResourceNotFoundException",
    "UnsupportedOperationException",
    "get_connector",
    "list_available_connectors",
    "register_connector",
]

# Global connector registry
_connector_registry: Dict[str, Any] = {}


def get_connector(name: str) -> Optional[Any]:
    """Get a connector instance by name."""
    return _connector_registry.get(name)


def list_available_connectors() -> Dict[str, Any]:
    """List all available connectors."""
    return _connector_registry.copy()


def register_connector(name: str, connector_class: Any) -> None:
    """Register a connector class."""
    _connector_registry[name] = connector_class
    logger.info(f"Registered connector: {name}")
