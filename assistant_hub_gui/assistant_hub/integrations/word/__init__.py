"""Word integration package."""

from .cloud_client import CloudWordClient
from .local_client import LocalDocument
from .service import draft_local_revision, upload_cloud_revision

__all__ = [
    "CloudWordClient",
    "LocalDocument",
    "draft_local_revision",
    "upload_cloud_revision",
]
