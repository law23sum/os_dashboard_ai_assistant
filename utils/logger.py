"""Enhanced logging system with structured logging and context.

This module provides a comprehensive logging system with:
- Structured logging with context
- Performance tracking
- Error correlation
- Log rotation and archival
"""

from __future__ import annotations

import logging
import os
import sys
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

from utils.config_manager import get_config
from utils.exceptions import OSDashBaseException

# Context variables for request tracking
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


@dataclass
class LogContext:
    """Context information for structured logging."""
    
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    operation: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        result = {}
        if self.request_id:
            result["request_id"] = self.request_id
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.project_id:
            result["project_id"] = self.project_id
        if self.operation:
            result["operation"] = self.operation
        result.update(self.extra)
        return result


class StructuredFormatter(logging.Formatter):
    """Formatter that includes structured context in log messages."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with context."""
        # Add context from ContextVars
        if not hasattr(record, "request_id"):
            record.request_id = request_id_ctx.get("") or ""
        if not hasattr(record, "correlation_id"):
            record.correlation_id = correlation_id_ctx.get("") or ""
        
        # Format base message
        message = super().format(record)
        
        # Add extra context if present
        if hasattr(record, "log_context") and record.log_context:
            context = record.log_context.to_dict() if isinstance(record.log_context, LogContext) else record.log_context
            if context:
                context_str = " | ".join(f"{k}={v}" for k, v in context.items())
                message = f"{message} | {context_str}"
        
        return message


class ContextLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds context to log messages."""
    
    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Process log message and add context."""
        context = self.extra.get("context")
        if context:
            if isinstance(context, LogContext):
                context_dict = context.to_dict()
            else:
                context_dict = context
            
            # Add context to extra
            kwargs.setdefault("extra", {})["log_context"] = context_dict
        
        return msg, kwargs


def setup_logger(
    name: str = "osdash",
    *,
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    structured: bool = True,
) -> logging.Logger:
    """Set up a logger with proper formatting and handlers.
    
    Args:
        name: Logger name
        level: Log level (defaults to config or INFO)
        log_file: Optional log file path
        structured: Whether to use structured logging
    
    Returns:
        Configured logger instance
    """
    config = get_config()
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)
    
    # Formatter
    if structured:
        formatter = StructuredFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    elif HAS_COLORLOG:
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logger.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str, *, context: Optional[LogContext] = None) -> logging.Logger:
    """Get a logger instance with optional context.
    
    Args:
        name: Logger name (typically __name__)
        context: Optional log context
    
    Returns:
        Logger instance
    """
    logger = setup_logger(name)
    
    if context:
        return ContextLoggerAdapter(logger, {"context": context})
    
    return logger


def log_exception(
    logger: logging.Logger,
    exception: Exception,
    *,
    context: Optional[LogContext] = None,
    level: int = logging.ERROR,
) -> None:
    """Log an exception with full context.
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Optional log context
        level: Log level
    """
    if isinstance(exception, OSDashBaseException):
        log_context = LogContext(
            request_id=request_id_ctx.get(""),
            correlation_id=correlation_id_ctx.get(""),
            extra={
                "error_code": exception.error_code,
                "error_context": exception.context,
            },
        )
        if context:
            log_context.extra.update(context.extra)
            log_context.user_id = context.user_id
            log_context.project_id = context.project_id
            log_context.operation = context.operation
        
        logger.log(
            level,
            f"{exception.message}",
            extra={"log_context": log_context},
            exc_info=exception.cause or exception,
        )
    else:
        log_context = context or LogContext(
            request_id=request_id_ctx.get(""),
            correlation_id=correlation_id_ctx.get(""),
        )
        logger.log(
            level,
            f"Unhandled exception: {exception}",
            extra={"log_context": log_context},
            exc_info=exception,
        )


# Global logger instance
_logger: Optional[logging.Logger] = None


def configure_logging() -> logging.Logger:
    """Configure logging for the application."""
    global _logger
    config = get_config()
    log_file = config.paths.logs_dir / "osdash.log"
    _logger = setup_logger("osdash", log_file=log_file)
    return _logger


def get_app_logger() -> logging.Logger:
    """Get the global application logger."""
    global _logger
    if _logger is None:
        _logger = configure_logging()
    return _logger

