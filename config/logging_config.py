"""
Logging configuration for AI OS
"""

import logging
from config import get_api_config

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False

def setup_logger(name: str = "assistant_hub") -> logging.Logger:
    """Setup colored logger with proper formatting"""
    config = get_api_config()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler with color formatting (if available)
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, config.log_level.upper()))

    # Create formatter
    if HAS_COLORLOG:
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return setup_logger(name)


# Global logger instance
logger = setup_logger()


def configure_logging():
    """Configure logging for the application."""
    global logger
    logger = setup_logger()
    return logger
