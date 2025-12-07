from __future__ import annotations

"""Word integration package."""

_WORD_ERROR_MESSAGE = (
    "The 'python-docx' package is required for Word integrations. "
    "Install it with `pip install python-docx`."
)

# Try to import Word integration components, but make it optional if python-docx is not installed
try:
    from .cloud_client import CloudWordClient
    from .local_client import LocalDocument
    from .service import WordService, draft_local_revision, upload_cloud_revision
    _WORD_AVAILABLE = True
except (ModuleNotFoundError, ImportError):
    # If python-docx or any dependency is missing, create placeholder classes/functions
    _WORD_AVAILABLE = False
    
    class _WordIntegrationUnavailable:
        """Placeholder when python-docx is not installed."""
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError(_WORD_ERROR_MESSAGE)
    
    CloudWordClient = _WordIntegrationUnavailable
    LocalDocument = _WordIntegrationUnavailable
    WordService = _WordIntegrationUnavailable
    
    def draft_local_revision(*args, **kwargs):
        raise ModuleNotFoundError(_WORD_ERROR_MESSAGE)
    
    def upload_cloud_revision(*args, **kwargs):
        raise ModuleNotFoundError(_WORD_ERROR_MESSAGE)

__all__ = [
    "CloudWordClient",
    "LocalDocument",
    "WordService",
    "draft_local_revision",
    "upload_cloud_revision",
]
