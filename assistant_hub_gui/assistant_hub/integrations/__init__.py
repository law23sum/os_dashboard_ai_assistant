"""External integrations for Assistant Hub."""

from .base import BaseIntegration, IntegrationStatus
from .excel import CloudExcelClient, LocalWorkbook, export_cloud_range_to_csv, summarize_local_workbook
from .filesystem import TRACKED_EXTENSIONS, discover_files
from .gmail import GmailIntegration
from .github import GitHubIntegration
from .google_calendar import GoogleCalendarIntegration
from .msgraph import GraphClient, GraphCredentials, load_credentials_from_env, request_access_token
from .notes import NotesIntegration
from .onenote import OneNoteClient, clean_section, mirror_page_to_disk, summarize_page
from .word import CloudWordClient, LocalDocument, draft_local_revision, upload_cloud_revision

__all__ = [
    "BaseIntegration",
    "IntegrationStatus",
    "GoogleCalendarIntegration",
    "GmailIntegration",
    "GitHubIntegration",
    "NotesIntegration",
    "GraphClient",
    "GraphCredentials",
    "load_credentials_from_env",
    "request_access_token",
    "OneNoteClient",
    "mirror_page_to_disk",
    "summarize_page",
    "clean_section",
    "CloudExcelClient",
    "LocalWorkbook",
    "export_cloud_range_to_csv",
    "summarize_local_workbook",
    "CloudWordClient",
    "LocalDocument",
    "draft_local_revision",
    "upload_cloud_revision",
    "TRACKED_EXTENSIONS",
    "discover_files",
]
