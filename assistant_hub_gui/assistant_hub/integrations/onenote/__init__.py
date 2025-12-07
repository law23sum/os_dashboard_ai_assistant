"""OneNote integration package."""

from .client import OneNoteClient
from .service import clean_section, mirror_page_to_disk, summarize_page, OneNoteService

__all__ = [
    "OneNoteClient",
    "OneNoteService",
    "clean_section",
    "mirror_page_to_disk",
    "summarize_page",
]
