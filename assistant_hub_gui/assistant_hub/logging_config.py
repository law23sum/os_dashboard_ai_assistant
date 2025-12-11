"""Logging configuration for OS Dashboard AI Assistant."""

import logging
from typing import Optional


def configure_logging(
    level: int = logging.INFO, format_string: Optional[str] = None
) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
    """
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        level=level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_logger(name: str = "assistant_hub") -> logging.Logger:
    """Compat shim that mirrors config.logging_config.setup_logger."""
    configure_logging()
    return get_logger(name)
