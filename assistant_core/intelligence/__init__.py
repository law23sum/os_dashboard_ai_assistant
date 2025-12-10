"""Intelligence modules providing data collection and quality assurance features."""

from .data_collector import DataCollector, SyncDataCollector, DataSource
from .quality_assurance import (
    ContentValidator,
    BatchValidator,
    AccessibilityChecker,
    ValidationRule,
    ValidationResult,
)
from .office_ai_service import OfficeAIProcessingService

__all__ = [
    "DataCollector",
    "SyncDataCollector",
    "DataSource",
    "ContentValidator",
    "BatchValidator",
    "AccessibilityChecker",
    "ValidationRule",
    "ValidationResult",
    "OfficeAIProcessingService",
]
