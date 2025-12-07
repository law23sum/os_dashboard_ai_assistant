"""OneNote integration package."""

from .client import OneNoteClient
from .service import clean_section, mirror_page_to_disk, summarize_page

__all__ = [
    "OneNoteClient",
    "clean_section",
    "mirror_page_to_disk",
    "summarize_page",
]
