"""Integration helpers for deployments, Office add-ins, APIs, and compatibility checks."""

from .advanced_systems import (
    DeploymentConfig,
    OfficeAddinConfig,
    HostConfig,
    RequirementSet,
    StaticSiteDeployer,
    OfficeAddinEmbedder,
    APIIntegrationManager,
    CrossPlatformCompatibilityManager,
)
from .office_realtime import (
    AIOfficeWebSocketRouter,
    AIOfficeMessage,
    ApplicationType,
    MessageType,
    ClientSession,
)
from .office_client import AIOfficeClient

__all__ = [
    "DeploymentConfig",
    "OfficeAddinConfig",
    "HostConfig",
    "RequirementSet",
    "StaticSiteDeployer",
    "OfficeAddinEmbedder",
    "APIIntegrationManager",
    "CrossPlatformCompatibilityManager",
    "AIOfficeWebSocketRouter",
    "AIOfficeMessage",
    "ApplicationType",
    "MessageType",
    "ClientSession",
    "AIOfficeClient",
]
