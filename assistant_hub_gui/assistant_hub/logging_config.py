"""Logging configuration for AI OS."""

import json
import logging
import os
from typing import Optional


def _json_formatter(record: logging.LogRecord) -> str:
    payload = {
        "ts": record.created,
        "level": record.levelname,
        "logger": record.name,
        "message": record.getMessage(),
    }
    for key in ("correlation_id", "request_id"):
        if key in record.__dict__:
            payload[key] = record.__dict__[key]
    return json.dumps(payload)


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

    use_json = os.getenv("OSDASH_LOG_JSON", "false").lower() in {"1", "true", "yes"}
    handlers = []
    if use_json:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt="%(message)s"))
        handler.emit = _json_emit(handler.emit)  # type: ignore
        handlers.append(handler)
    else:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def _json_emit(orig_emit):
    def _emit(record):
        record.msg = _json_formatter(record)
        return orig_emit(record)

    return _emit


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
