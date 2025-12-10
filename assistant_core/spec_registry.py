"""Spec registry utilities for mapping code to the canonical design spec."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

_SECTION_PATTERN = re.compile(
    r"^\s*((?:\d+|[a-z])(?:\.(?:\d+|[a-z]))*)(?:\.)?\s+(.*\S)", re.IGNORECASE
)


def _normalize_identifier(identifier: str) -> str:
    normalized = identifier.strip()
    if not normalized:
        raise ValueError("Spec identifier cannot be empty")
    return normalized.rstrip(".")


@dataclass(frozen=True)
class SpecSection:
    """Represents a single entry from the canon Table of Contents."""

    identifier: str
    title: str
    depth: int
    raw: str


@dataclass(frozen=True)
class FeatureRegistration:
    """Record describing how a feature maps to spec sections."""

    name: str
    sections: Tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


class SpecRegistry:
    """Parses the canon spec and exposes lookup / registration helpers."""

    def __init__(self, spec_path: Path) -> None:
        self.spec_path = spec_path
        self._sections = self._parse_spec_file(spec_path)
        self._registrations: Dict[str, FeatureRegistration] = {}

    @staticmethod
    def _parse_spec_file(path: Path) -> Dict[str, SpecSection]:
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {path}")

        sections: Dict[str, SpecSection] = {}
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                match = _SECTION_PATTERN.match(raw_line)
                if not match:
                    continue
                identifier = _normalize_identifier(match.group(1))
                title = match.group(2).strip()
                depth = identifier.count(".") + 1
                sections[identifier] = SpecSection(
                    identifier=identifier,
                    title=title,
                    depth=depth,
                    raw=raw_line.rstrip("\n"),
                )
        return sections

    def has_section(self, identifier: str) -> bool:
        return self._normalize(identifier) in self._sections

    def get_section(self, identifier: str) -> SpecSection:
        normalized = self._normalize(identifier)
        try:
            return self._sections[normalized]
        except KeyError as exc:
            raise KeyError(f"Unknown spec section '{identifier}'") from exc

    def search(self, text: str) -> List[SpecSection]:
        """Return sections whose titles contain the provided text."""

        query = text.lower().strip()
        if not query:
            return []
        return [
            section
            for section in self._sections.values()
            if query in section.title.lower()
        ]

    def require_sections(
        self, identifiers: Iterable[str], feature: Optional[str] = None
    ) -> Tuple[str, ...]:
        normalized = tuple(self._normalize(identifier) for identifier in identifiers)
        missing = [identifier for identifier in normalized if identifier not in self._sections]
        if missing:
            feature_hint = f" for feature '{feature}'" if feature else ""
            raise KeyError(f"Unknown spec section(s){feature_hint}: {', '.join(missing)}")
        return normalized

    def register_feature(
        self,
        name: str,
        sections: Iterable[str],
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> FeatureRegistration:
        normalized = self.require_sections(sections, feature=name)
        registration = FeatureRegistration(
            name=name,
            sections=normalized,
            metadata=dict(metadata or {}),
        )
        self._registrations[name] = registration
        return registration

    def list_sections(self) -> List[SpecSection]:
        return list(self._sections.values())

    def list_registrations(self) -> List[FeatureRegistration]:
        return list(self._registrations.values())

    @staticmethod
    def _normalize(identifier: str) -> str:
        return _normalize_identifier(identifier)


_DEFAULT_SPEC_PATH = Path(__file__).resolve().parents[1] / "OS DashboardAIAssistantTOC.txt"
_DEFAULT_REGISTRY: Optional[SpecRegistry] = None


def get_default_registry(spec_path: Optional[Path] = None) -> SpecRegistry:
    """Return a cached registry for the canonical spec."""

    global _DEFAULT_REGISTRY
    target_path = spec_path or _DEFAULT_SPEC_PATH
    if _DEFAULT_REGISTRY is None or _DEFAULT_REGISTRY.spec_path != target_path:
        _DEFAULT_REGISTRY = SpecRegistry(target_path)
    return _DEFAULT_REGISTRY


__all__ = [
    "FeatureRegistration",
    "SpecRegistry",
    "SpecSection",
    "get_default_registry",
]
