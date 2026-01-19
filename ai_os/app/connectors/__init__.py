"""Connectors for the AI OS Console skeleton."""
from ai_os.app.connectors.base import Connector, ResourceRef, StorageBackedConnector
from ai_os.app.connectors.notes import NotesConnector
from ai_os.app.connectors.word import WordConnector
from ai_os.app.connectors.excel import ExcelConnector
from ai_os.app.connectors.onenote import OneNoteConnector
from ai_os.app.connectors.pdf import PDFConnector
from ai_os.app.connectors.powerpoint import PowerPointConnector
from ai_os.app.connectors.git import GitConnector
from ai_os.app.connectors.filesystem import FilesystemConnector

__all__ = [
    "Connector",
    "ResourceRef",
    "StorageBackedConnector",
    "NotesConnector",
    "WordConnector",
    "ExcelConnector",
    "OneNoteConnector",
    "PDFConnector",
    "PowerPointConnector",
    "GitConnector",
    "FilesystemConnector",
]
