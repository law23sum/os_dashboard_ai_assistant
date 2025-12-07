from __future__ import annotations

import importlib.util

# Ensure python-docx is installed when Word integrations are used
if importlib.util.find_spec("docx") is None:
    raise ModuleNotFoundError(
        "The 'python-docx' package is required for Word integrations. Install it with `pip install python-docx`."
    )

"""Word integration package."""

from .cloud_client import CloudWordClient
from .local_client import LocalDocument
from .service import WordService, draft_local_revision, upload_cloud_revision

__all__ = [
    "CloudWordClient",
    "LocalDocument",
    "WordService",
    "draft_local_revision",
    "upload_cloud_revision",
]
