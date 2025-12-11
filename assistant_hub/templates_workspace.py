"""Shared template/catalog workspace for templates UI surfaces.

This layer keeps Tkinter, FastAPI, and React aligned by exposing the same
metadata for document templates (governance, toolchain alignment, sample
files) plus placeholder matrices derived from the governed template bodies.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from .document_templates import DocumentTemplateProfile, TemplateSample, document_templates

try:  # Prefer the richer governed template payloads if available.
    from assistant_hub_gui.assistant_hub.document_templates import DEFAULT_TEMPLATES
except Exception:  # pragma: no cover - Tk package may be unavailable in some envs.
    DEFAULT_TEMPLATES: Dict[str, Dict[str, str]] = {}


def _sample_to_dict(sample: TemplateSample) -> Dict[str, str]:
    return {
        "extension": sample.extension,
        "filename": sample.filename,
        "description": sample.description,
    }


def _profile_to_dict(profile: DocumentTemplateProfile) -> Dict[str, Any]:
    return {
        "name": profile.name,
        "purpose": profile.purpose,
        "governance": list(profile.governance),
        "toolchain_alignment": list(profile.toolchain_alignment),
        "daemon_support": list(profile.daemon_support),
        "sample_files": [_sample_to_dict(sample) for sample in profile.sample_files],
    }


def _extract_placeholders(template_body: str) -> List[str]:
    """Return sorted placeholder list from a template body."""
    return sorted(set(re.findall(r"{([a-zA-Z0-9_]+)}", template_body)))


class TemplatesWorkspace:
    """Container that exposes document template metadata + placeholder map."""

    def __init__(self) -> None:
        self._catalog = document_templates
        self._defaults = DEFAULT_TEMPLATES

    def document_catalog(self) -> List[Dict[str, Any]]:
        """Structured catalog shared with UI clients."""
        return [_profile_to_dict(profile) for profile in self._catalog]

    def placeholder_matrix(self) -> List[Dict[str, Any]]:
        """Summaries of governed templates + extracted placeholder tokens."""
        matrix: List[Dict[str, Any]] = []
        for template_id, payload in self._defaults.items():
            content = payload.get("content", "")
            placeholders = _extract_placeholders(content)
            matrix.append(
                {
                    "id": template_id,
                    "name": payload.get("name", template_id.replace("_", " ").title()),
                    "category": payload.get("category", "document"),
                    "placeholder_count": len(placeholders),
                    "placeholders": placeholders,
                    "preview": content[:240].strip(),
                }
            )
        matrix.sort(key=lambda entry: entry["name"])
        return matrix

    def snapshot(self) -> Dict[str, Any]:
        """Return catalog + placeholder metadata."""
        return {
            "catalog": self.document_catalog(),
            "placeholder_matrix": self.placeholder_matrix(),
        }


__all__ = ["TemplatesWorkspace"]
