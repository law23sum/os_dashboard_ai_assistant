"""CLI command handlers."""

from .onenote import handle_onenote_command
from .excel import handle_excel_command
from .word import handle_word_command
from .projects import handle_projects_command
from .history import handle_history_command

__all__ = [
    "handle_onenote_command",
    "handle_excel_command",
    "handle_word_command",
    "handle_projects_command",
    "handle_history_command",
]


