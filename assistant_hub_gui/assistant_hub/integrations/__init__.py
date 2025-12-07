"""External integrations for Assistant Hub."""

from .base import BaseIntegration, IntegrationStatus
from .google_calendar import GoogleCalendarIntegration
from .gmail import GmailIntegration
from .github import GitHubIntegration
from .notes import NotesIntegration
from .onenote.service import OneNoteService
from .excel.service import ExcelService
from .word.service import WordService

__all__ = [
    "BaseIntegration",
    "IntegrationStatus",
    "GoogleCalendarIntegration",
    "GmailIntegration",
    "GitHubIntegration",
    "NotesIntegration",
    "OneNoteService",
    "ExcelService",
    "WordService",
]

