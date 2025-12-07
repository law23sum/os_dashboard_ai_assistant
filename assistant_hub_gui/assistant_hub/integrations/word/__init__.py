from __future__ import annotations

import importlib.util

if importlib.util.find_spec("docx") is None:
    raise ModuleNotFoundError(
        "The 'python-docx' package is required for Word integrations. Install it with `pip install python-docx`."
    )

from .cloud_client import CloudWordClient
from .local_client import LocalDocument, draft_local_revision, upload_cloud_revision
from .service import WordService

__all__ = [
    "CloudWordClient",
    "LocalDocument",
    "WordService",
    "draft_local_revision",
    "upload_cloud_revision",
]
