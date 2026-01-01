"""Centralized exception hierarchy for OS Dashboard AI Assistant.

This module provides a comprehensive exception hierarchy that improves
error handling, debugging, and user experience throughout the application.
"""

from __future__ import annotations

from typing import Any, Optional


class OSDashBaseException(Exception):
    """Base exception for all OS Dashboard exceptions.
    
    Provides consistent error handling with context and error codes.
    """
    
    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize exception with message and optional context.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            context: Optional dictionary with additional context
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause
    
    def __str__(self) -> str:
        """Return formatted error message with context."""
        parts = [self.message]
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        return " | ".join(parts)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class ConfigurationError(OSDashBaseException):
    """Raised when configuration is invalid or missing."""
    pass


class DatabaseError(OSDashBaseException):
    """Raised when database operations fail."""
    pass


class ProjectDiscoveryError(OSDashBaseException):
    """Raised when project discovery fails."""
    pass


class MonitorError(OSDashBaseException):
    """Raised when project monitoring fails."""
    pass


class OrchestratorError(OSDashBaseException):
    """Raised when orchestrator operations fail."""
    pass


class APIError(OSDashBaseException):
    """Raised when API operations fail."""
    pass


class IntegrationError(OSDashBaseException):
    """Raised when third-party integrations fail."""
    pass


class AuthenticationError(OSDashBaseException):
    """Raised when authentication fails."""
    pass


class ValidationError(OSDashBaseException):
    """Raised when data validation fails."""
    pass


class ResourceNotFoundError(OSDashBaseException):
    """Raised when a requested resource is not found."""
    pass


class TimeoutError(OSDashBaseException):
    """Raised when an operation times out."""
    pass


class NetworkError(OSDashBaseException):
    """Raised when network operations fail."""
    pass


class FileSystemError(OSDashBaseException):
    """Raised when file system operations fail."""
    pass


class ProcessError(OSDashBaseException):
    """Raised when subprocess operations fail."""
    pass


