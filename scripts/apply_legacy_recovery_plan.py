#!/usr/bin/env python3
"""
Apply legacy recovery plan:
- merge redirects into path_mapping.json
- add Legacy Recovery platform with restore routes into gui_nav.latest.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = REPO_ROOT / "docs" / "integration" / "legacy_recovery_plan.json"
NAV_PATH = REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json"
PATH_MAPPING_PATH = REPO_ROOT / "path_mapping.json"


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


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    if not PLAN_PATH.exists():
        raise SystemExit(f"Missing plan: {PLAN_PATH}")

    plan = load_json(PLAN_PATH)
    redirects = {
        normalize_path(src): normalize_path(dst)
        for src, dst in (plan.get("redirects") or {}).items()
        if src and dst
    }

    mapping = load_json(PATH_MAPPING_PATH) if PATH_MAPPING_PATH.exists() else {}
    conflicts = {}
    for src, dst in redirects.items():
        existing = mapping.get(src)
        if existing and existing != dst:
            conflicts[src] = {"existing": existing, "new": dst}
            continue
        mapping[src] = dst

    if redirects:
        write_json(PATH_MAPPING_PATH, mapping)

    nav = load_json(NAV_PATH)
    restore_records = plan.get("restore_records", [])
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for record in restore_records:
        route = normalize_path(record.get("route_final") or "")
        if not route:
            continue
        title = record.get("title") or "Untitled"
        category = record.get("category") or "Legacy"
        grouped[category].append({"title": title, "path": route, "new": True})

    for edition, platforms in nav.items():
        if not isinstance(platforms, dict):
            continue
        platform = platforms.setdefault("Legacy Recovery", {})
        if not isinstance(platform, dict):
            continue
        for category, features in grouped.items():
            existing = platform.setdefault(category, [])
            if not isinstance(existing, list):
                continue
            existing_paths = {item.get("path") for item in existing if isinstance(item, dict)}
            for feature in features:
                if feature["path"] not in existing_paths:
                    existing.append(feature)

    write_json(NAV_PATH, nav)

    if conflicts:
        conflict_path = REPO_ROOT / "docs" / "integration" / "legacy_recovery_redirect_conflicts.json"
        write_json(conflict_path, conflicts)
        print(f"Redirect conflicts written to {conflict_path}")

    print(f"Updated {PATH_MAPPING_PATH}")
    print(f"Updated {NAV_PATH}")


if __name__ == "__main__":
    main()
