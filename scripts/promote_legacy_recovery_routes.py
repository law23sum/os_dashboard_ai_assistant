#!/usr/bin/env python3
"""
Promote Legacy Recovery routes into core platforms based on route prefixes.
Keeps /legacy/* routes under Legacy Recovery.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
NAV_PATH = REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json"
REPORT_PATH = REPO_ROOT / "docs" / "integration" / "legacy_recovery_promotion.json"

PREFIX_MAP: List[Tuple[str, str]] = [
    ("/ai-fabric", "AI Fabric"),
    ("/ai", "AI Fabric"),
    ("/data", "Data & Knowledge"),
    ("/drivers", "Drivers & Integrations"),
    ("/docs", "Docs & Spec"),
    ("/governance", "Governance & Security"),
    ("/observability-evidence", "Observability & Evidence"),
    ("/observability", "Observability & Evidence"),
    ("/operations-infrastructure", "Operations & Infrastructure"),
    ("/operations", "Operations & Infrastructure"),
    ("/roadmap", "Roadmap & Risks"),
    ("/settings", "Settings & Admin"),
    ("/mission-architecture", "Mission & Architecture"),
    ("/mission", "Mission & Architecture"),
    ("/vision", "Vision & Meta-Stack"),
    ("/workspaces", "Workspaces"),
    ("/dashboard", "Mission Control"),
    ("/mission-control", "Mission Control"),
]


def normalize_path(path: str) -> str:
    if not path:
        return ""
    if not path.startswith("/"):
        path = "/" + path
    while "//" in path:
        path = path.replace("//", "/")
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path


def titleize(value: str) -> str:
    value = value.replace("_", "-")
    value = re.sub(r"-+", "-", value).strip("-")
    parts = [part.capitalize() for part in value.split("-") if part]
    return " ".join(parts) or "Legacy"


def resolve_platform(route: str) -> Optional[str]:
    for prefix, platform in PREFIX_MAP:
        if route.startswith(prefix + "/") or route == prefix:
            return platform
    return None


def infer_category(route: str) -> str:
    parts = route.strip("/").split("/")
    if len(parts) < 2:
        return "Legacy"
    return titleize(parts[1])


def main() -> None:
    if not NAV_PATH.exists():
        raise SystemExit(f"Missing nav JSON: {NAV_PATH}")

    nav = json.loads(NAV_PATH.read_text(encoding="utf-8"))
    report = {"moved": [], "skipped": []}

    for edition, platforms in nav.items():
        if not isinstance(platforms, dict):
            continue
        legacy = platforms.get("Legacy Recovery")
        if not isinstance(legacy, dict):
            continue

        retained: Dict[str, List[Dict]] = {}

        for category_label, features in legacy.items():
            if not isinstance(features, list):
                continue
            remaining = []
            for feature in features:
                if not isinstance(feature, dict):
                    continue
                route = normalize_path(feature.get("path", ""))
                if not route or route.startswith("/legacy/"):
                    remaining.append(feature)
                    continue

                target_platform = resolve_platform(route)
                if not target_platform:
                    remaining.append(feature)
                    report["skipped"].append({
                        "edition": edition,
                        "route": route,
                        "reason": "no platform match",
                    })
                    continue

                target_categories = platforms.setdefault(target_platform, {})
                if not isinstance(target_categories, dict):
                    remaining.append(feature)
                    report["skipped"].append({
                        "edition": edition,
                        "route": route,
                        "reason": "target platform not a dict",
                    })
                    continue

                target_category = infer_category(route)
                target_features = target_categories.setdefault(target_category, [])
                if not isinstance(target_features, list):
                    remaining.append(feature)
                    report["skipped"].append({
                        "edition": edition,
                        "route": route,
                        "reason": "target category not a list",
                    })
                    continue

                if not any(isinstance(item, dict) and normalize_path(item.get("path", "")) == route for item in target_features):
                    target_features.append(feature)
                report["moved"].append({
                    "edition": edition,
                    "route": route,
                    "from": category_label,
                    "to_platform": target_platform,
                    "to_category": target_category,
                })

            if remaining:
                retained[category_label] = remaining

        platforms["Legacy Recovery"] = retained

    NAV_PATH.write_text(json.dumps(nav, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Updated {NAV_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
