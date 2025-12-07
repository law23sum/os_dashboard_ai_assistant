"""API connectors for the OS Dashboard AI Assistant."""

from typing import Any, Dict, Optional
import logging

from .base import IntegrationAPIGateway
from .universal_connector import (
    AppleNotesConnector,
    BaseConnector,
    CIRDocument,
    ConnectorCapability,
    ConnectorConfig,
    ConnectorManager,
    ConnectorRegistry,
    ContentBlock,
    ContentBlockType,
    GitConnector,
    MicrosoftGraphConnector,
    OfficeFileConnector,
    OpenAIConnector,
    OperationResult,
    PDFConnector,
    Section,
)

logger = logging.getLogger(__name__)

__version__ = "1.1.0"
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
    "IntegrationAPIGateway",
    "ConnectorCapability",
    "ConnectorConfig",
    "OperationResult",
    "ConnectorManager",
    "ConnectorRegistry",
    "MicrosoftGraphConnector",
    "OfficeFileConnector",
    "PDFConnector",
    "GitConnector",
    "OpenAIConnector",
    "get_connector",
    "list_available_connectors",
]

from .base import IntegrationAPIGateway
from .universal_connector import (
    ConnectorCapability,
    ConnectorConfig,
    ConnectorManager,
    ConnectorRegistry,
    GitConnector,
    MicrosoftGraphConnector,
    OfficeFileConnector,
    OpenAIConnector,
    OperationResult,
    PDFConnector,
)

# Global connector registry
_connector_registry: Dict[str, Any] = {}


def get_connector(name: str) -> Optional[Any]:
    """Get a connector instance by name."""

    return _connector_registry.get(name)


def list_available_connectors() -> Dict[str, Any]:
    """List all available connectors."""

    return _connector_registry.copy()


def register_connector(name: str, connector_class: Any):
    """Register a connector class."""

    _connector_registry[name] = connector_class
    logger.info(f"Registered connector: {name}")
