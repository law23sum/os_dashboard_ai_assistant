#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


DEFAULT_PATTERNS = ("TODO: investigate",)
DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "htmlcov",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    "audit_data",
}
DEFAULT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".ts",
    ".tsx",
    ".js",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
}


@dataclass(frozen=True)
class InvestigateItem:
    path: str
    line: int
    text: str


def _should_skip(path: Path, excludes: set[str]) -> bool:
    return any(part in excludes for part in path.parts)


def _iter_files(root: Path, extensions: set[str], excludes: set[str]) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excludes]
        base = Path(dirpath)
        if _should_skip(base, excludes):
            continue
        for filename in filenames:
            path = base / filename
            if _should_skip(path, excludes):
                continue
            if path.suffix.lower() not in extensions:
                continue
            yield path


def collect_items(
    root: Path,
    patterns: Sequence[str],
    extensions: set[str],
    excludes: set[str],
) -> List[InvestigateItem]:
    items: List[InvestigateItem] = []
    for path in _iter_files(root, extensions, excludes):
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for idx, line in enumerate(handle, start=1):
                    if any(pattern in line for pattern in patterns):
                        items.append(
                            InvestigateItem(
                                path=str(path.relative_to(root)),
                                line=idx,
                                text=line.strip(),
                            )
                        )
        except OSError:
            continue
    return items


def render_markdown(root: Path, patterns: Sequence[str], items: Sequence[InvestigateItem]) -> str:
    lines = [
        "# Investigate Report",
        "",
        f"Root: `{root}`",
        f"Patterns: {', '.join(patterns)}",
        f"Total: {len(items)}",
        "",
    ]
    if not items:
        lines.append("No investigate TODOs found.")
        return "\n".join(lines)
    lines.append("## Items")
    for item in items:
        lines.append(f"- `{item.path}:{item.line}` {item.text}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect TODO: investigate markers.")
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument(
        "--pattern",
        action="append",
        dest="patterns",
        help="Pattern to match (repeatable).",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Write report to this path instead of stdout.",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    patterns = args.patterns or list(DEFAULT_PATTERNS)
    items = collect_items(root, patterns, DEFAULT_EXTENSIONS, set(DEFAULT_EXCLUDES))
    report = render_markdown(root, patterns, items)
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
