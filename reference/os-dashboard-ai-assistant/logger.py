"""
Logging configuration for OS Dashboard AI Assistant
"""
import logging
import colorlog
from config import get_config

def setup_logger(name: str = "dashboard_ai") -> logging.Logger:
    """Setup colored logger with proper formatting"""
    config = get_config()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler with color formatting
    handler = colorlog.StreamHandler()
    handler.setLevel(getattr(logging, config.log_level.upper()))
    
    # Create formatter
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
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Global logger instance
logger = setup_logger()