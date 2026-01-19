#!/usr/bin/env python3
"""
Normalize legacy recovery home pages to use RouteScaffold so they include full IA sections.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = REPO_ROOT / "incomplete_pages_report.json"


def component_name_from_path(path: Path) -> str:
    base = path.stem
    cleaned = re.sub(r"[^A-Za-z0-9_]", "", base)
    if not cleaned:
        return "LegacyHomePage"
    if cleaned[0].isdigit():
        cleaned = f"Legacy{cleaned}"
    return cleaned


def main() -> None:
    if not REPORT_PATH.exists():
        raise SystemExit(f"Missing report: {REPORT_PATH}")

    data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    targets = [entry for entry in data if entry.get("route", "").startswith("/legacy/")]

    for entry in targets:
        path_str = entry.get("path")
        route = entry.get("route")
        if not path_str or not route:
            continue
        path = REPO_ROOT / path_str
        if not path.exists():
            continue
        component_name = component_name_from_path(path)
        content = "\n".join([
            "import RouteScaffold from '@/pages/RouteScaffold'",
            "",
            "/**",
            f" * {component_name}",
            f" * Route: {route}",
            " */",
            f"export default function {component_name}() {{",
            "  return <RouteScaffold />",
            "}",
            "",
        ])
        path.write_text(content, encoding="utf-8")

    print(f"Normalized {len(targets)} legacy home pages")


if __name__ == "__main__":
    main()
