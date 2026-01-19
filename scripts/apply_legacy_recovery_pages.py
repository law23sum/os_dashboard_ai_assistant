#!/usr/bin/env python3
"""
Restore missing page components listed in legacy_recovery_plan.json,
update routeComponentMap, and extend iaManifest.complete.json.
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = REPO_ROOT / "docs" / "integration" / "legacy_recovery_plan.json"
ROUTE_MAP_PATH = REPO_ROOT / "frontend" / "src" / "navigation" / "routeComponentMap.ts"
MANIFEST_COMPLETE_JSON = REPO_ROOT / "frontend" / "src" / "data" / "iaManifest.complete.json"


def slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = value.replace("_", "-")
    value = re.sub(r"[^A-Za-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value.lower() or "item"


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


def read_route_component_map() -> Dict[str, str]:
    route_map: Dict[str, str] = {}
    if not ROUTE_MAP_PATH.exists():
        return route_map
    for line in ROUTE_MAP_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*\"([^\"]+)\"\s*:\s*\"([^\"]+)\"", line)
        if match:
            route_map[match.group(1)] = match.group(2)
    return route_map


def write_route_component_map(route_map: Dict[str, str]) -> None:
    sorted_routes = sorted(route_map.keys())
    lines = [
        "export const routeComponentMap: Record<string, string> = {",
        *[f"  {json.dumps(route)}: {json.dumps(route_map[route])}," for route in sorted_routes],
        "}",
        "",
        "export const routeComponentRoutes = Object.keys(routeComponentMap).sort(",
        "  (a, b) => b.length - a.length,",
        ")",
        "",
    ]
    ROUTE_MAP_PATH.write_text("\n".join(lines), encoding="utf-8")


def batch_show_files(requests: List[tuple[str, str]]) -> Dict[str, Optional[str]]:
    if not requests:
        return {}
    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=REPO_ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None

    for sha, path in requests:
        proc.stdin.write(f"{sha}:{path}\n".encode("utf-8"))
    proc.stdin.close()

    contents: Dict[str, Optional[str]] = {}
    for _, path in requests:
        header = proc.stdout.readline()
        if not header:
            contents[path] = None
            continue
        header_text = header.decode("utf-8", errors="replace").strip()
        if header_text.endswith("missing"):
            contents[path] = None
            continue
        parts = header_text.split()
        if len(parts) < 3:
            contents[path] = None
            continue
        try:
            size = int(parts[2])
        except ValueError:
            contents[path] = None
            continue
        body = proc.stdout.read(size)
        proc.stdout.read(1)
        contents[path] = body.decode("utf-8", errors="replace")

    proc.stdout.close()
    proc.wait()
    return contents


def build_stub_component(title: str, route: str) -> str:
    safe_title = title.replace("\"", "\\\"")
    return "\n".join([
        "import { FeaturePageTemplate } from '@/components/templates/FeaturePageTemplate'",
        "",
        "/**",
        f" * {title}",
        f" * Route: {route}",
        " */",
        "export default function LegacyRecoveredPage() {",
        "  return (",
        "    <FeaturePageTemplate",
        f"      title=\"{safe_title}\"",
        f"      description=\"Feature page for {safe_title}.\"",
        "    />",
        "  )",
        "}",
        "",
    ])


def main() -> None:
    if not PLAN_PATH.exists():
        raise SystemExit(f"Missing plan: {PLAN_PATH}")

    plan = load_json(PLAN_PATH)
    restore_records = plan.get("restore_records", [])

    requests = []
    for record in restore_records:
        sha = record.get("commit")
        path = record.get("path")
        if sha and path:
            requests.append((sha, path))

    contents = batch_show_files(requests)

    restored_routes: Dict[str, str] = {}
    for record in restore_records:
        path = record.get("path")
        route = normalize_path(record.get("route_final") or "")
        title = record.get("title") or "Recovered Page"
        if not path or not route:
            continue
        target = REPO_ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            continue
        content = contents.get(path)
        if content is None:
            content = build_stub_component(title, route)
        target.write_text(content, encoding="utf-8")
        restored_routes[route] = path

    route_map = read_route_component_map()
    route_conflicts = {}
    for route, component_path in restored_routes.items():
        existing = route_map.get(route)
        if existing and existing != component_path:
            route_conflicts[route] = {"existing": existing, "new": component_path}
            continue
        route_map[route] = component_path

    if restored_routes:
        write_route_component_map(route_map)

    manifest = load_json(MANIFEST_COMPLETE_JSON) if MANIFEST_COMPLETE_JSON.exists() else {"platforms": []}
    platforms = manifest.setdefault("platforms", [])

    platform_id = "legacy-recovery"
    platform_label = "Legacy Recovery"
    platform_path = "/legacy"

    platform = next((p for p in platforms if p.get("id") == platform_id), None)
    if not platform:
        platform = {
            "id": platform_id,
            "label": platform_label,
            "path": platform_path,
            "actorScope": "both",
            "order": len(platforms) + 1,
            "categories": [],
        }
        platforms.append(platform)

    categories = platform.setdefault("categories", [])
    category_index = {c.get("label"): c for c in categories if isinstance(c, dict)}

    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for record in restore_records:
        route = normalize_path(record.get("route_final") or "")
        title = record.get("title") or "Recovered"
        category = record.get("category") or "Legacy"
        path = record.get("path") or ""
        if not route:
            continue
        grouped[category].append({
            "title": title,
            "route": route,
            "componentPath": path,
        })

    for category_label, features in grouped.items():
        category = category_index.get(category_label)
        if not category:
            category = {
                "id": slugify(category_label),
                "label": category_label,
                "homeRoute": f"/legacy/{slugify(category_label)}",
                "homeComponentPath": "frontend/src/components/templates/CategoryHomeTemplate.tsx",
                "homeBestCommit": "stable",
                "actorScope": "both",
                "order": len(categories) + 1,
                "features": [],
            }
            categories.append(category)
            category_index[category_label] = category
        existing_routes = {f.get("route") for f in category.get("features", []) if isinstance(f, dict)}
        order = max([f.get("order", 0) for f in category.get("features", []) if isinstance(f, dict)] + [0])
        for feature in sorted(features, key=lambda f: f["title"]):
            if feature["route"] in existing_routes:
                continue
            order += 1
            category.setdefault("features", []).append({
                "id": slugify(feature["title"]),
                "label": feature["title"],
                "route": feature["route"],
                "componentPath": feature["componentPath"],
                "bestCommit": "stable",
                "actorScope": "both",
                "order": order,
                "isNew": True,
            })

    write_json(MANIFEST_COMPLETE_JSON, manifest)

    if route_conflicts:
        conflict_path = REPO_ROOT / "docs" / "integration" / "legacy_recovery_route_conflicts.json"
        write_json(conflict_path, route_conflicts)
        print(f"Route conflicts written to {conflict_path}")

    print(f"Restored {len(restored_routes)} pages")
    print(f"Updated {ROUTE_MAP_PATH}")
    print(f"Updated {MANIFEST_COMPLETE_JSON}")

    subprocess.run(["python", str(REPO_ROOT / "scripts" / "generate_ia_manifest_ts.py")], cwd=REPO_ROOT, check=False)


if __name__ == "__main__":
    main()
