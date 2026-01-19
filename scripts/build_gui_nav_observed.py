#!/usr/bin/env python3
"""Build observed GUI nav snapshot from legacy nav without seed additions."""
from __future__ import annotations

import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_NAV_PATH = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"
OUTPUT_PATH = REPO_ROOT / "contracts" / "gui" / "gui_nav.observed.json"

REQUIRED_PLATFORM_ORDER = [
    "Core",
    "Common",
    "Audit Official Records",
    "Automation",
    "Settings",
    "Admin",
    "Workstation",
    "Systems",
    "Simulations",
    "Research",
    "Encyclopedia",
    "Libraries",
    "Knowledge",
]

EDITION_LABELS = ["Personal", "Business/Team", "Enterprise"]

EDITION_KEYS = {
    "Personal": "personal",
    "Business/Team": "business_team",
    "Enterprise": "enterprise",
}


def normalize_slug(value: str) -> str:
    out = []
    prev_dash = False
    for ch in value.lower():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                out.append("-")
                prev_dash = True
    return "".join(out).strip("-") or "item"


def route_slug(route: str) -> str:
    return normalize_slug(route.strip("/").replace("/", "_"))


def infer_widget_kind(title: str) -> str:
    lower = title.lower()
    if "search" in lower:
        return "search_box"
    if "log" in lower or "trace" in lower:
        return "log_viewer"
    if "timeline" in lower:
        return "timeline"
    if "graph" in lower or "map" in lower:
        return "graph_view"
    if "table" in lower or "list" in lower:
        return "table"
    return "form"


def infer_display_kind(title: str) -> str:
    lower = title.lower()
    if "audit" in lower or "logbook" in lower:
        return "audit_trail"
    if "evidence" in lower:
        return "evidence_links"
    return "results_panel"


def build_feature(platform_key: str, category_key: str, feature: Dict[str, Any], nav_order: int) -> Dict[str, Any]:
    title = feature["title"]
    route = feature["path"]
    key = route_slug(route)
    widget_kind = infer_widget_kind(title)
    display_kind = infer_display_kind(title)
    return {
        "key": key,
        "label": title,
        "route": route,
        "nav_order": nav_order,
        "contracts": {
            "page_contract_ref": f"urn:omniverse:page:{key}",
        },
        "widgets": [{"id": f"w_{key}_{widget_kind}", "kind": widget_kind}],
        "displays": [{"id": f"d_{key}_{display_kind}", "kind": display_kind}],
    }


def build_observed() -> Dict[str, Any]:
    legacy_nav = json.loads(LEGACY_NAV_PATH.read_text())
    editions_out = []

    for edition_label in EDITION_LABELS:
        edition_key = EDITION_KEYS.get(edition_label, normalize_slug(edition_label))
        platforms_out = []
        edition_nav = legacy_nav.get(edition_label, {})
        if not edition_nav and edition_label == "Business/Team":
            edition_nav = legacy_nav.get("Personal", {})
        for order_index, platform_label in enumerate(REQUIRED_PLATFORM_ORDER, start=1):
            platform_key = normalize_slug(platform_label)
            categories_out = []
            legacy_categories = edition_nav.get(platform_label, {})
            for category_order, (category_label, features) in enumerate(legacy_categories.items()):
                category_key = normalize_slug(category_label)
                feature_defs = []
                for nav_order, feature in enumerate(features):
                    if not feature or not feature.get("path"):
                        continue
                    feature_defs.append(build_feature(platform_key, category_key, feature, nav_order))
                categories_out.append({
                    "key": f"{platform_key}_{category_key}",
                    "label": category_label,
                    "order": category_order,
                    "features": feature_defs,
                })
            platforms_out.append({
                "key": platform_key,
                "label": platform_label,
                "order": order_index,
                "categories": categories_out,
            })
        editions_out.append({
            "key": edition_key,
            "label": edition_label,
            "platforms": platforms_out,
        })

    return {
        "meta": {
            "version": datetime.now(timezone.utc).strftime("%Y.%m.%d"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_of_truth": "repo_scan",
            "platform_order": REQUIRED_PLATFORM_ORDER,
        },
        "editions": editions_out,
    }


def main() -> None:
    observed = build_observed()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(observed, indent=2))
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
