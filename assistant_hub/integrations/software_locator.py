"""Utility helpers to locate common desktop tools.

The CLI and GUI can use this module to answer "where is <tool>?" style
questions for git, Word, Excel, PDF viewers, or any other executable name
provided by the user. All lookups rely on the local PATH so they are safe to
run in sandboxed environments.
"""
from __future__ import annotations

from dataclasses import dataclass
from shutil import which
from typing import Iterable, Sequence


@dataclass
class SoftwareLocation:
    """Represents the outcome of a software lookup."""

    name: str
    search_terms: list[str]
    path: str | None

    @property
    def found(self) -> bool:
        return self.path is not None

    @property
    def tried(self) -> str:
        return ", ".join(self.search_terms)


class SoftwareLocator:
    """Locate common software executables on the current system."""

    def __init__(self) -> None:
        self.default_targets: dict[str, Sequence[str]] = {
            "git": ["git"],
            "word": ["winword", "word", "libreoffice", "soffice"],
            "excel": ["excel", "libreoffice", "soffice", "calc"],
            "pdf": ["acroread", "evince", "okular", "sumatrapdf", "zathura"],
        }

    def locate(self, name: str, aliases: Iterable[str] | None = None) -> SoftwareLocation:
        """Locate an executable by name or alias list."""

        search_terms = [name, *(aliases or [])]
        for candidate in search_terms:
            resolved = which(candidate)
            if resolved:
                return SoftwareLocation(name=name, search_terms=search_terms, path=resolved)
        return SoftwareLocation(name=name, search_terms=search_terms, path=None)

    def locate_default(self, target: str) -> SoftwareLocation:
        """Locate a known target such as git, word, excel, or pdf."""

        aliases = self.default_targets.get(target.lower(), ())
        return self.locate(target, aliases)

    def scan_defaults(self) -> list[SoftwareLocation]:
        """Locate all known default targets."""

        return [self.locate_default(name) for name in self.default_targets]
