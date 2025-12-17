"""CLI command handlers."""

from .onenote import handle_onenote_command
from .excel import handle_excel_command
from .word import handle_word_command
from .projects import handle_projects_command
from .history import handle_history_command
from .chat import handle_chat_command
from .workspace import (
    handle_scan_command,
    handle_test_command,
    handle_run_command,
    handle_doctor_command,
)

__all__ = [
    "handle_onenote_command",
    "handle_excel_command",
    "handle_word_command",
    "handle_projects_command",
    "handle_history_command",
    "handle_chat_command",
    "handle_scan_command",
    "handle_test_command",
    "handle_run_command",
    "handle_doctor_command",
]
