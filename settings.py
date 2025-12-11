"""Global application settings and constants for OS Dashboard AI Assistant."""

import os
from pathlib import Path

# Application metadata
APP_NAME = "OS Dashboard AI Assistant"
APP_VERSION = "1.0.0"
APP_AUTHOR = "OS Dashboard Team"

# Directory paths
PROJECT_ROOT = Path(__file__).parent
ASSISTANT_CORE_DIR = PROJECT_ROOT / "assistant_core"
UI_DIR = PROJECT_ROOT / "ui"
CONFIG_DIR = PROJECT_ROOT / "config"
TESTS_DIR = PROJECT_ROOT / "tests"

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"

# Configuration file paths
CONFIG_YAML = CONFIG_DIR / "config.yaml"
CREDENTIALS_DIR = CONFIG_DIR / "credentials"

# Default settings
DEFAULT_REFRESH_INTERVAL = 300  # seconds
DEFAULT_LOG_LEVEL = "INFO"

# API rate limits (requests per minute)
API_RATE_LIMITS = {
    "openai": 100,
    "google": 1000,
    "microsoft": 1000,
}

# Supported file types
SUPPORTED_DOCUMENT_TYPES = [
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".txt", ".md", ".csv", ".json"
]

# AI model settings
DEFAULT_AI_MODEL = "gpt-4"
MAX_TOKENS_PER_REQUEST = 4000
TEMPERATURE = 0.7

# Database settings
DATABASE_TYPE = "sqlite"
DATABASE_PATH = DATA_DIR / "app.db"

# UI settings
UI_THEME = "dark"
UI_WINDOW_SIZE = (1200, 800)

# Create necessary directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, CACHE_DIR, CREDENTIALS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)
