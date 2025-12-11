"""Utilities for accessing the canonical technical specification."""

from .technical_spec import SPEC, spec_summary, TechnicalSpec
from .architecture import ARCHITECTURE_LAYERS, PLANES, architecture_summary, planes_summary
from .failure_modes import failure_summary

__all__ = [
    "SPEC",
    "spec_summary",
    "TechnicalSpec",
    "ARCHITECTURE_LAYERS",
    "PLANES",
    "architecture_summary",
    "planes_summary",
    "failure_summary",
]
