#!/usr/bin/env python3
"""
Generate IA manifest from gui_nav.latest.json with strict IA rules.

Rules enforced:
- Platforms -> Categories -> Features only
- Category home route is a distinct nav role (removed from features)
- Feature routes are unique across categories
- Legacy/alias routes become redirects (not nav items)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent
NAV_PATH = REPO_ROOT / "documentation" / "gui_nav_structure" / "gui_nav.latest.json"
PATH_MAPPING = REPO_ROOT / "path_mapping.json"

TEMPLATE_FEATURE = "frontend/src/components/templates/FeaturePageTemplate.tsx"
TEMPLATE_CATEGORY = "frontend/src/components/templates/CategoryHomeTemplate.tsx"

ROUTE_OVERRIDES = {
    "/governance/policy/simulator": "frontend/src/pages/governance/policy/PolicySimulator.tsx",
}

PLATFORM_DEFS: Dict[str, Tuple[str, str]] = {
    "Mission Control": ("mission-control", "/dashboard"),
    "Workspaces": ("workspaces", "/workspaces"),
    "AI Fabric": ("ai-fabric", "/ai"),
    "Data & Knowledge": ("data-knowledge", "/data"),
    "Drivers & Integrations": ("drivers-integrations", "/drivers"),
    "Docs & Spec": ("docs-spec", "/docs"),
    "Settings & Admin": ("settings-admin", "/settings"),
    "Roadmap & Risks": ("roadmap-risks", "/roadmap"),
    "Mission & Architecture": ("mission-architecture", "/mission"),
    "Governance & Security": ("governance-security", "/governance"),
    "Observability & Evidence": ("observability-evidence", "/observability"),
    "Operations & Infrastructure": ("operations-infrastructure", "/operations"),
    "Vision & Meta-Stack": ("vision-meta-stack", "/vision"),
    "Legacy Recovery": ("legacy-recovery", "/legacy"),
}


def normalize_platform_label(label: str) -> str:
    cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", label or "").strip()
    return cleaned or label


def slugify(text: str) -> str:
    value = (text or "").lower()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "item"


def normalize_path(path: str) -> str:
    if not path:
        return ""
    if not path.startswith("/"):
        path = "/" + path
    path = re.sub(r"/+", "/", path)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path


def resolve_home_route(
    base_route: str,
    category_id: str,
    category_routes: Dict[str, str],
    feature_routes: Dict[str, str],
) -> str:
    candidate = base_route
    suffix = 0
    while True:
        existing_category = category_routes.get(candidate)
        conflict = candidate in feature_routes or (
            existing_category is not None and existing_category != category_id
        )
        if not conflict:
            break
        suffix += 1
        suffix_label = "home" if suffix == 1 else f"home-{suffix}"
        candidate = normalize_path(f"{base_route}-{suffix_label}")
    if candidate != base_route:
        print(f"[ia] Adjusted category home route for {category_id}: {base_route} -> {candidate}")
    return candidate


def score_route(path: str, platform_path: str) -> int:
    score = len(path.split("/"))
    if platform_path and path.startswith(platform_path.rstrip("/") + "/"):
        score += 100
    elif platform_path and path == platform_path:
        score += 90
    return score


def load_path_mapping(canonical_routes: set[str]) -> Dict[str, str]:
    if not PATH_MAPPING.exists():
        return {}
    with PATH_MAPPING.open("r") as handle:
        mapping = json.load(handle)
    normalized: Dict[str, str] = {}
    for raw_src, raw_dst in mapping.items():
        src = normalize_path(raw_src)
        dst = normalize_path(raw_dst)
        if src and dst and src != dst:
            src_is_canonical = src in canonical_routes
            dst_is_canonical = dst in canonical_routes
            if src_is_canonical and not dst_is_canonical:
                normalized[dst] = src
            elif dst_is_canonical and not src_is_canonical:
                normalized[src] = dst
    return normalized


def derive_actor_scope(edition_name: str) -> str:
    if "Personal" in edition_name:
        return "personal"
    if "Enterprise" in edition_name:
        return "enterprise"
    return "both"


def build_manifest(nav_data: Dict) -> Tuple[List[Dict], Dict[str, str]]:
    platforms: List[Dict] = []
    platform_index: Dict[str, Dict] = {}
    legacy_redirects: Dict[str, str] = {}

    global_feature_routes: Dict[str, str] = {}
    global_category_routes: Dict[str, str] = {}

    platform_order = 1

    for edition_name, edition_data in nav_data.items():
        actor_scope = derive_actor_scope(edition_name)
        if not isinstance(edition_data, dict):
            continue

        for raw_platform_label, categories in edition_data.items():
            platform_label = normalize_platform_label(raw_platform_label)
            platform_id, platform_path = PLATFORM_DEFS.get(
                platform_label,
                (slugify(platform_label), f"/{slugify(platform_label)}"),
            )

            platform = platform_index.get(platform_id)
            if not platform:
                platform = {
                    "id": platform_id,
                    "label": platform_label,
                    "path": platform_path,
                    "actorScope": actor_scope,
                    "order": platform_order,
                    "categories": [],
                }
                platform_index[platform_id] = platform
                platforms.append(platform)
                platform_order += 1
            else:
                if platform["actorScope"] != actor_scope:
                    platform["actorScope"] = "both"

            if not isinstance(categories, dict):
                continue

            category_index = {c["id"]: c for c in platform["categories"]}

            for category_label, feature_list in categories.items():
                if not isinstance(feature_list, list):
                    continue

                category_id = f"{platform_id}-{slugify(category_label)}"
                category = category_index.get(category_id)

                if not category:
                    category = {
                        "id": category_id,
                        "label": category_label,
                        "homeRoute": "",
                        "homeComponentPath": TEMPLATE_CATEGORY,
                        "homeBestCommit": "stable",
                        "actorScope": actor_scope,
                        "order": len(platform["categories"]) + 1,
                        "features": [],
                    }
                    platform["categories"].append(category)
                    category_index[category_id] = category
                else:
                    if category["actorScope"] != actor_scope:
                        category["actorScope"] = "both"

                raw_features = [
                    f for f in feature_list if isinstance(f, dict) and f.get("path")
                ]
                if not raw_features:
                    continue

                home_route = normalize_path(f"{platform_path}/{slugify(category_label)}")
                if not home_route or home_route == "/":
                    home_route = normalize_path(f"/{platform_id}/{slugify(category_label)}")

                home_route = resolve_home_route(
                    home_route,
                    category_id,
                    global_category_routes,
                    global_feature_routes,
                )

                category["homeRoute"] = home_route
                global_category_routes[home_route] = category_id

                label_groups: Dict[str, List[Dict]] = {}
                for item in raw_features:
                    route = normalize_path(item.get("path", ""))
                    if not route or route == home_route:
                        if route and route != home_route:
                            legacy_redirects[route] = home_route
                        continue
                    label = item.get("title", "") or "Untitled"
                    label_groups.setdefault(label, []).append(item)

                canonical_by_label: Dict[str, Dict] = {}
                for label, items in label_groups.items():
                    canonical = max(
                        items,
                        key=lambda i: score_route(normalize_path(i.get("path", "")), platform_path),
                    )
                    canonical_by_label[label] = canonical
                    for item in items:
                        if item is canonical:
                            continue
                        legacy_redirects[normalize_path(item.get("path", ""))] = normalize_path(
                            canonical.get("path", "")
                        )

                ordered_features: List[Dict] = []
                seen_feature_ids: set[str] = set()
                for item in raw_features:
                    label = item.get("title", "") or "Untitled"
                    if canonical_by_label.get(label) is not item:
                        continue

                    route = normalize_path(item.get("path", ""))
                    if route in global_feature_routes:
                        legacy_redirects[route] = global_feature_routes[route]
                        continue

                    feature_id = f"{category_id}-{slugify(label)}"
                    if feature_id in seen_feature_ids:
                        legacy_redirects[route] = global_feature_routes.get(route, route)
                        continue

                    component_path = ROUTE_OVERRIDES.get(route, TEMPLATE_FEATURE)

                    feature_obj = {
                        "id": feature_id,
                        "label": label,
                        "route": route,
                        "componentPath": component_path,
                        "bestCommit": "stable",
                        "actorScope": actor_scope,
                        "order": len(category["features"]) + 1,
                        "isNew": bool(item.get("new", False)),
                    }
                    ordered_features.append(feature_obj)
                    seen_feature_ids.add(feature_id)
                    global_feature_routes[route] = route

                category["features"].extend(ordered_features)

    return platforms, legacy_redirects


def main() -> None:
    if not NAV_PATH.exists():
        print(f"Error: {NAV_PATH} not found")
        return

    with NAV_PATH.open("r") as handle:
        nav_data = json.load(handle)

    platforms, legacy_redirects = build_manifest(nav_data)

    canonical_routes = set()
    for platform in platforms:
        canonical_routes.add(normalize_path(platform.get("path", "")))
        for category in platform.get("categories", []):
            canonical_routes.add(normalize_path(category.get("homeRoute", "")))
            for feature in category.get("features", []):
                canonical_routes.add(normalize_path(feature.get("route", "")))
    canonical_routes.discard("")

    for src, dst in load_path_mapping(canonical_routes).items():
        legacy_redirects.setdefault(src, dst)

    total_categories = sum(len(p["categories"]) for p in platforms)
    total_features = sum(len(c["features"]) for p in platforms for c in p["categories"])

    output_file = REPO_ROOT / "frontend" / "src" / "data" / "iaManifest.from_json.ts"
    output_json = REPO_ROOT / "frontend" / "src" / "data" / "iaManifest.from_json.json"
    output_public_nav = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"
    output_frontend_nav = REPO_ROOT / "frontend" / "src" / "data" / "gui_nav.latest.json"

    ts_content = f"""/**
 * Complete IA Manifest - Generated from gui_nav.latest.json
 * Single Source of Truth for all {total_categories + total_features} pages
 */

export type ActorScope = 'personal' | 'enterprise' | 'both'

export interface IAFeature {{
  id: string
  label: string
  route: string
  componentPath: string
  bestCommit: 'stable' | 'increments' | 'backup'
  actorScope: ActorScope
  order: number
  isNew?: boolean
}}

export interface IACategory {{
  id: string
  label: string
  homeRoute: string
  homeComponentPath: string
  homeBestCommit: 'stable' | 'increments' | 'backup'
  features: IAFeature[]
  actorScope: ActorScope
  order: number
}}

export interface IAPlatform {{
  id: string
  label: string
  path: string
  categories: IACategory[]
  actorScope: ActorScope
  order: number
}}

export const iaManifest: IAPlatform[] = {json.dumps(platforms, indent=2)}

export const legacyRedirects: Record<string, string> = {json.dumps(legacy_redirects, indent=2)}

const allowsActorScope = (itemScope: ActorScope | undefined, actorScope: ActorScope) => {{
  if (!itemScope) return true
  if (itemScope === 'both' || itemScope === actorScope) return true
  if (actorScope === 'enterprise' && itemScope === 'personal') return true
  return false
}}

export function getPlatforms(actorScope: ActorScope): IAPlatform[] {{
  return iaManifest.filter(p => allowsActorScope(p.actorScope, actorScope))
}}

export function getCategories(platformId: string, actorScope: ActorScope): IACategory[] {{
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  if (!allowsActorScope(platform.actorScope, actorScope)) return []
  return platform.categories.filter(c => allowsActorScope(c.actorScope, actorScope))
}}

export function getFeatures(platformId: string, categoryId: string, actorScope: ActorScope): IAFeature[] {{
  const platform = iaManifest.find(p => p.id === platformId)
  if (!platform) return []
  const category = platform.categories.find(c => c.id === categoryId)
  if (!category) return []
  if (!allowsActorScope(category.actorScope, actorScope)) return []
  return category.features.filter(f => allowsActorScope(f.actorScope, actorScope))
}}

export function findRouteContext(route: string): {{
  platform?: IAPlatform
  category?: IACategory
  feature?: IAFeature
  isCategoryHome: boolean
  isPlatformLanding: boolean
}} {{
  const normalized = route === '/' ? '/' : route.replace(/\/+$/, '')
  for (const platform of iaManifest) {{
    if (normalized === platform.path) {{
      return {{
        platform,
        isCategoryHome: false,
        isPlatformLanding: true,
      }}
    }}
  }}
  for (const platform of iaManifest) {{
    for (const category of platform.categories) {{
      if (normalized === category.homeRoute) {{
        return {{
          platform,
          category,
          isCategoryHome: true,
          isPlatformLanding: false,
        }}
      }}

      for (const feature of category.features) {{
        if (normalized === feature.route || normalized.startsWith(feature.route + '/')) {{
          return {{
            platform,
            category,
            feature,
            isCategoryHome: false,
            isPlatformLanding: false,
          }}
        }}
      }}
    }}
  }}

  return {{ isCategoryHome: false, isPlatformLanding: false }}
}}
"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(ts_content)
    output_json.write_text(
        json.dumps({"platforms": platforms, "legacyRedirects": legacy_redirects}, indent=2)
    )
    output_public_nav.write_text(json.dumps(nav_data, indent=2))
    output_frontend_nav.write_text(json.dumps(nav_data, indent=2))

    print(f"Generated manifest: {output_file}")
    print(f"Generated manifest JSON: {output_json}")
    print(f"Platforms: {len(platforms)}")
    print(f"Categories: {total_categories}")
    print(f"Features: {total_features}")
    print(f"Legacy redirects: {len(legacy_redirects)}")


if __name__ == "__main__":
    main()
