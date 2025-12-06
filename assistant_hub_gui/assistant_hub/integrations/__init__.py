"""External integrations for Assistant Hub."""

from .base import BaseIntegration, IntegrationStatus
from .google_calendar import GoogleCalendarIntegration
from .gmail import GmailIntegration
from .github import GitHubIntegration
from .notes import NotesIntegration

__all__ = [
    "BaseIntegration",
    "IntegrationStatus",
    "GoogleCalendarIntegration",
    "GmailIntegration",
    "GitHubIntegration",
    "NotesIntegration",
]

