"""Lightweight fallback implementation of the ``colorlog`` package.

This module provides minimal drop-in classes used by the project's
``logging_config`` helpers without requiring the external dependency.
It mirrors the StreamHandler and ColoredFormatter interfaces expected
by the rest of the codebase while deferring to Python's built-in
``logging`` module for behavior.
"""

from __future__ import annotations

import logging
from typing import Any, Dict


class StreamHandler(logging.StreamHandler):
    """Simple alias for :class:`logging.StreamHandler`.

    The real ``colorlog`` package exposes a custom subclass. For our
    purposes the standard handler is sufficient because formatting is
    handled by :class:`ColoredFormatter` below.
    """

    pass


class ColoredFormatter(logging.Formatter):
    """Basic formatter that accepts ``log_colors`` argument.

    The real implementation applies ANSI colors based on the provided
    mapping. This lightweight version stores the mapping for API
    compatibility but otherwise delegates to ``logging.Formatter``.
    """

    def __init__(self, fmt: str, *, datefmt: str | None = None, log_colors: Dict[str, str] | None = None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.log_colors = log_colors or {}

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        """Format the specified record.

        Color codes are ignored, but the method preserves compatibility
        with the ``colorlog`` API so callers can rely on the same
        signature and behavior shape.
        """

        return super().format(record)


__all__ = ["StreamHandler", "ColoredFormatter"]
