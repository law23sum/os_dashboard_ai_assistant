#!/usr/bin/env python3
"""
Rebuild iaManifest.complete.json from iaManifest.from_json.json and routeComponentMap.
Ensures component paths match actual page components where available.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parent.parent
FROM_JSON = REPO_ROOT / "frontend" / "src" / "data" / "iaManifest.from_json.json"
ROUTE_MAP_PATH = REPO_ROOT / "frontend" / "src" / "navigation" / "routeComponentMap.ts"
OUTPUT_JSON = REPO_ROOT / "frontend" / "src" / "data" / "iaManifest.complete.json"

DEFAULT_CATEGORY_COMPONENT = "frontend/src/components/templates/CategoryHomeTemplate.tsx"
DEFAULT_FEATURE_COMPONENT = "frontend/src/components/templates/FeaturePageTemplate.tsx"


def load_route_component_map() -> Dict[str, str]:
    route_map: Dict[str, str] = {}
    for line in ROUTE_MAP_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*\"([^\"]+)\"\s*:\s*\"([^\"]+)\"", line)
        if match:
            route_map[match.group(1)] = match.group(2)
    return route_map


def main() -> None:
    if not FROM_JSON.exists():
        raise SystemExit(f"Missing manifest: {FROM_JSON}")

    data = json.loads(FROM_JSON.read_text(encoding="utf-8"))
    platforms = data.get("platforms", [])
    route_map = load_route_component_map()

    for platform in platforms:
        for category in platform.get("categories", []):
            home_route = category.get("homeRoute")
            if home_route:
                category["homeComponentPath"] = route_map.get(home_route, DEFAULT_CATEGORY_COMPONENT)
            for feature in category.get("features", []):
                route = feature.get("route")
                if route:
                    feature["componentPath"] = route_map.get(route, DEFAULT_FEATURE_COMPONENT)

    OUTPUT_JSON.write_text(json.dumps({"platforms": platforms}, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
