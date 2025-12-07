"""External integrations for Assistant Hub."""

from .base import BaseIntegration, IntegrationStatus
from .excel import CloudExcelClient, LocalWorkbook, export_cloud_range_to_csv, summarize_local_workbook
from .filesystem import TRACKED_EXTENSIONS, discover_files
from .gmail import GmailIntegration
from .github import GitHubIntegration
from .apple_calendar import AppleCalendarIntegration
from .msgraph import GraphClient, GraphCredentials, load_credentials_from_env, request_access_token
from .notes import NotesIntegration
from .onenote.service import OneNoteService
from .excel.service import ExcelService
from .onenote import OneNoteClient, clean_section, mirror_page_to_disk, summarize_page
# Word integration is optional - imports will succeed but classes raise errors when instantiated if python-docx is missing
from .word import CloudWordClient, LocalDocument, WordService, draft_local_revision, upload_cloud_revision

# Integration wrapper classes for GUI
from .word_integration import WordIntegration
from .excel_integration import ExcelIntegration
from .onenote_integration import OneNoteIntegration
from .onedrive_integration import OneDriveIntegration
from .filesystem_integration import FilesystemIntegration
from .git_integration import GitIntegration
from .pdf_integration import PDFIntegration

__all__ = [
    "BaseIntegration",
    "IntegrationStatus",
    "AppleCalendarIntegration",
    "GmailIntegration",
    "GitHubIntegration",
    "NotesIntegration",
    "WordIntegration",
    "ExcelIntegration",
    "OneNoteIntegration",
    "OneDriveIntegration",
    "FilesystemIntegration",
    "GitIntegration",
    "PDFIntegration",
    "GraphClient",
    "GraphCredentials",
    "load_credentials_from_env",
    "request_access_token",
    "OneNoteService",
    "ExcelService",
    "WordService",
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
