"""Parse and organize Markdown specifications for the Assistant Hub GUI."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Set

from .paths import DOCUMENTATION_ROOT


@dataclass
class SpecDocument:
    """Structured representation of a Markdown specification."""

    path: Path
    title: str
    sections: List[str] = field(default_factory=list)
    keywords: Set[str] = field(default_factory=set)
    summary: str = ""

    @property
    def relative_path(self) -> Path:
        try:
            return self.path.relative_to(DOCUMENTATION_ROOT)
        except ValueError:
            return self.path


class SpecRegistry:
    """Loads Markdown specifications and exposes useful aggregates."""

    def __init__(self, docs_root: Path | None = None):
        self.docs_root = docs_root or DOCUMENTATION_ROOT
        self.documents: List[SpecDocument] = self._load_documents()
        self.keyword_index: Dict[str, List[SpecDocument]] = self._build_keyword_index()

    def _load_documents(self) -> List[SpecDocument]:
        docs: List[SpecDocument] = []
        if not self.docs_root.exists():
            return docs

        for md_path in sorted(self.docs_root.rglob("*.md")):
            docs.append(self._parse_document(md_path))
        return docs

    def _parse_document(self, path: Path) -> SpecDocument:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        title = path.stem.replace('_', ' ').title()
        sections: List[str] = []
        keywords: Set[str] = set()
        summary_parts: List[str] = []

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("# "):
                title = line[2:].strip()
                keywords.update(self._tokenize(title))
            elif line.startswith("## "):
                section = line[3:].strip()
                sections.append(section)
                keywords.update(self._tokenize(section))
            elif line.startswith("- ") or line.startswith("* "):
                keywords.update(self._tokenize(line[2:]))
            elif len(summary_parts) < 5:
                summary_parts.append(line)
                keywords.update(self._tokenize(line))

        if not sections:
            sections = ["Overview"]

        summary = "\n".join(summary_parts[:5])
        return SpecDocument(path=path, title=title, sections=sections, keywords=keywords, summary=summary)

    def _tokenize(self, text: str) -> Set[str]:
        tokens = re.findall(r"[A-Za-z0-9_]+", text.lower())
        return {token for token in tokens if len(token) > 2}

    def _build_keyword_index(self) -> Dict[str, List[SpecDocument]]:
        index: Dict[str, List[SpecDocument]] = {}
        for doc in self.documents:
            for keyword in doc.keywords:
                index.setdefault(keyword, []).append(doc)
        return index

    def find_docs_for_keywords(self, keywords: Iterable[str]) -> List[SpecDocument]:
        normalized = {kw.lower() for kw in keywords}
        matches: Dict[Path, SpecDocument] = {}
        for keyword in normalized:
            for doc in self.keyword_index.get(keyword, []):
                matches[doc.path] = doc
        return list(matches.values())

    def keyword_totals(self, limit: int = 12) -> List[tuple[str, int]]:
        counter: Counter[str] = Counter()
        for doc in self.documents:
            counter.update(doc.keywords)
        return counter.most_common(limit)

    def summary_rows(self) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        for doc in self.documents:
            rows.append(
                {
                    "title": doc.title,
                    "sections": ", ".join(doc.sections[:3]),
                    "keywords": ", ".join(sorted(list(doc.keywords))[:5]),
                    "path": str(doc.relative_path),
                }
            )
        return rows

    def total_documents(self) -> int:
        return len(self.documents)

    def themes(self) -> List[str]:
        groups: Set[str] = set()
        for doc in self.documents:
            if doc.sections:
                groups.add(doc.sections[0].split(':')[0])
        return sorted(groups)
