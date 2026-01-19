#!/usr/bin/env python3
"""Sync legacy gui_nav.latest.json files from contracts/gui registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "contracts" / "gui" / "gui_nav.latest.json"

LEGACY_OUTPUTS = [
    REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json",
    REPO_ROOT / "frontend" / "src" / "data" / "gui_nav.latest.json",
    REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json",
]


def build_legacy(nav: Dict[str, Any]) -> Dict[str, Any]:
    legacy: Dict[str, Any] = {}
    for edition in nav.get("editions", []):
        edition_label = edition.get("label")
        if not edition_label:
            continue
        platforms_out: Dict[str, Any] = {}
        platforms = sorted(edition.get("platforms", []), key=lambda p: p.get("order", 0))
        for platform in platforms:
            platform_label = platform.get("label")
            if not platform_label:
                continue
            categories_out: Dict[str, Any] = {}
            categories = sorted(platform.get("categories", []), key=lambda c: c.get("order", 0))
            for category in categories:
                category_label = category.get("label")
                if not category_label:
                    continue
                features = sorted(category.get("features", []), key=lambda f: f.get("nav_order", 0))
                categories_out[category_label] = [
                    {"title": feature.get("label", ""), "path": feature.get("route", ""), "new": False}
                    for feature in features
                ]
            platforms_out[platform_label] = categories_out
        legacy[edition_label] = platforms_out
    return legacy


def main() -> None:
    nav = json.loads(CONTRACT_PATH.read_text())
    legacy = build_legacy(nav)
    for output in LEGACY_OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(legacy, indent=2))
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
