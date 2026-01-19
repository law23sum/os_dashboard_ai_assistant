#!/usr/bin/env python3
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "agent_exports" / "ui"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_FEATURE = "frontend/src/components/templates/FeaturePageTemplate.tsx"
TEMPLATE_CATEGORY = "frontend/src/components/templates/CategoryHomeTemplate.tsx"
TEMPLATE_PLATFORM = "frontend/src/components/templates/PlatformLandingTemplate.tsx"
ROUTE_SCAFFOLD = "frontend/src/pages/RouteScaffold.tsx"

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

NAV_SOURCES = [
    ("frontend/src/App.tsx", "Top-level routing (public/protected + dynamic routes)."),
    ("frontend/src/navigation/NavRouteRenderer.tsx", "IA route resolution + lazy loading + template fallbacks."),
    ("frontend/src/navigation/routeComponentMap.ts", "Canonical route → component map for IA rendering."),
    ("frontend/src/navigation/iaContext.tsx", "Route → platform/category/feature context."),
    ("frontend/src/navigation/iaGuardrails.ts", "IA route validation/duplicate checks."),
    ("frontend/src/navigation/context.tsx", "Breadcrumb + active nav derivation."),
    ("frontend/src/components/Layout.tsx", "Platform tabs, category dropdowns, feature sidebar, legacy redirects."),
    ("frontend/src/components/PlatformFeatureSidebar.tsx", "Feature sidebar rendering."),
    ("frontend/src/components/NavigationTree.tsx", "Tree-network nav UI (uses navigationStructure)."),
    ("frontend/src/components/TreeNetworkNavigation.tsx", "Tree-network nav UI (uses navigationStructure)."),
    ("frontend/src/data/gui_nav.latest.json", "Edition-scoped nav source of truth (frontend data)."),
    ("frontend/public/gui_nav.latest.json", "Public nav JSON used by UI builds."),
    ("documentation/gui_nav_structure/gui_nav.latest.json", "Documentation nav reference."),
    ("frontend/src/data/iaManifest.from_json.json", "Generated IA manifest + legacy redirects (JSON)."),
    ("frontend/src/data/iaManifest.from_json.ts", "Generated IA manifest + legacy redirects (TS)."),
    ("frontend/src/data/iaManifest.ts", "Canonical manifest re-export."),
    ("frontend/src/data/navigationStructure.ts", "Tree-network nav data."),
    ("frontend/src/lib/navigationStructure.ts", "Helpers for navigationStructure."),
    ("frontend/src/data/platformFeatures.ts", "Sidebar feature list by route prefix."),
    ("frontend/src/components/templates/FeaturePageTemplate.tsx", "Feature page template fallback."),
    ("frontend/src/components/templates/CategoryHomeTemplate.tsx", "Category home template fallback."),
    ("frontend/src/components/templates/PlatformLandingTemplate.tsx", "Platform landing template fallback."),
    ("frontend/src/pages/RouteScaffold.tsx", "Generic route scaffold."),
    ("frontend/src/config/navigation.ts", "Legacy nav config (unused)."),
    ("frontend/src/data/navigationManifest.ts", "Spec-driven nav manifest (unused)."),
    ("frontend/src/data/iaCanonical.ts", "Legacy canonical routing helper (unused)."),
    ("frontend/src/components/LegacyRedirector.tsx", "Legacy redirect helper (unused)."),
]


def git_info() -> Dict[str, str]:
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT).decode().strip()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
    except Exception:
        branch = "unknown"
        commit = "unknown"
    return {"branch": branch, "commit": commit}


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def strip_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def extract_json_block(text: str, marker: str) -> Optional[str]:
    idx = text.find(marker)
    if idx == -1:
        return None
    eq = text.find("=", idx)
    if eq == -1:
        return None
    brace = text.find("{", eq)
    bracket = text.find("[", eq)
    if brace == -1 and bracket == -1:
        return None
    if brace == -1:
        start = bracket
        open_char = "["
        close_char = "]"
    elif bracket == -1:
        start = brace
        open_char = "{"
        close_char = "}"
    else:
        start = min(brace, bracket)
        open_char = text[start]
        close_char = "]" if open_char == "[" else "}"
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def load_route_component_map(path: Path) -> Dict[str, str]:
    text = path.read_text()
    block = extract_json_block(text, "export const routeComponentMap")
    if not block:
        return {}
    return json.loads(strip_trailing_commas(block))


def resolve_import_path(rel_path: str) -> str:
    base = rel_path
    if rel_path.startswith("./"):
        base = str((REPO_ROOT / "frontend" / "src" / rel_path[2:]).resolve())
    elif rel_path.startswith("../"):
        base = str((REPO_ROOT / "frontend" / "src" / rel_path).resolve())
    else:
        base = str((REPO_ROOT / rel_path).resolve())
    base_path = Path(base)
    if base_path.suffix:
        return str(base_path.relative_to(REPO_ROOT))
    for ext in (".tsx", ".ts", ".jsx", ".js"):
        candidate = base_path.with_suffix(ext)
        if candidate.exists():
            return str(candidate.relative_to(REPO_ROOT))
    return str(base_path.relative_to(REPO_ROOT))


def parse_app_routes(app_path: Path) -> Dict[str, str]:
    text = app_path.read_text()
    import_re = re.compile(r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]")
    route_re = re.compile(r"<Route\s+path=\"([^\"]+)\"\s+element=\{<([^\s>/]+)")
    imports: Dict[str, str] = {}
    for match in import_re.finditer(text):
        imports[match.group(1)] = match.group(2)
    routes: Dict[str, str] = {}
    for match in route_re.finditer(text):
        route = match.group(1)
        component = match.group(2)
        rel_path = imports.get(component)
        if rel_path:
            routes[route] = resolve_import_path(rel_path)
    return routes


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(errors="ignore")


def normalize_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.strip().lower()).strip("-")


def has_params_execute_results(text: str, component_path: str) -> bool:
    if component_path == TEMPLATE_FEATURE:
        return True
    if "FeaturePageTemplate" in text:
        return True
    tokens = ["Parameters", "Execute", "Results"]
    return all(token in text for token in tokens)


def placeholder_reason(text: str, component_path: str) -> Optional[str]:
    if component_path == TEMPLATE_FEATURE:
        return "FeaturePageTemplate"
    if component_path == TEMPLATE_CATEGORY:
        return "CategoryHomeTemplate"
    if component_path == TEMPLATE_PLATFORM:
        return "PlatformLandingTemplate"
    if component_path == ROUTE_SCAFFOLD:
        return "RouteScaffold"
    if "FeaturePageTemplate" in text:
        return "FeaturePageTemplate|wrapper"
    if "CategoryHomeTemplate" in text:
        return "CategoryHomeTemplate|wrapper"
    if "PlatformLandingTemplate" in text:
        return "PlatformLandingTemplate|wrapper"
    if "RouteScaffold" in text:
        return "RouteScaffold"
    if re.search(r"return\s+null", text):
        return "empty return"
    if re.search(r"return\s*<></>", text) or re.search(r"return\s*\(\s*<></>\s*\)", text):
        return "empty return"
    return None


def analyze_component(component_path: Optional[str]) -> Tuple[bool, Optional[str], bool]:
    if not component_path:
        return True, "missing component", False
    if component_path.startswith("redirect:"):
        return True, "redirect", False
    file_path = REPO_ROOT / component_path
    if not file_path.exists():
        return True, "missing file", False
    text = read_text(file_path)
    reason = placeholder_reason(text, component_path)
    return bool(reason), reason, has_params_execute_results(text, component_path)


def build_route_context(platforms: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    route_context: Dict[str, Dict[str, Any]] = {}
    for platform in platforms:
        route_context[platform["path"]] = {
            "platform": platform,
            "category": None,
            "feature": None,
            "is_platform": True,
            "is_category_home": False,
            "is_feature": False,
        }
        for category in platform.get("categories", []):
            route_context[category["homeRoute"]] = {
                "platform": platform,
                "category": category,
                "feature": None,
                "is_platform": False,
                "is_category_home": True,
                "is_feature": False,
            }
            for feature in category.get("features", []):
                route_context[feature["route"]] = {
                    "platform": platform,
                    "category": category,
                    "feature": feature,
                    "is_platform": False,
                    "is_category_home": False,
                    "is_feature": True,
                }
    return route_context


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2))


def write_md(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n")


def main() -> None:
    repo = git_info()
    manifest_path = REPO_ROOT / "frontend" / "src" / "data" / "iaManifest.from_json.json"
    manifest = load_json(manifest_path)
    platforms: List[Dict[str, Any]] = manifest.get("platforms", [])
    legacy_redirects: Dict[str, str] = manifest.get("legacyRedirects", {})

    route_component_map = load_route_component_map(REPO_ROOT / "frontend" / "src" / "navigation" / "routeComponentMap.ts")
    app_routes = parse_app_routes(REPO_ROOT / "frontend" / "src" / "App.tsx")

    route_context = build_route_context(platforms)

    routes: List[Dict[str, Any]] = []
    empty_pages: List[Dict[str, Any]] = []

    # Platform landing routes
    for platform in platforms:
        route = platform["path"]
        component = route_component_map.get(route) or TEMPLATE_PLATFORM
        is_placeholder, reason, has_frame = analyze_component(component)
        routes.append({
            "route": route,
            "kind": "ui",
            "page_component_path": component,
            "is_redirect": False,
            "redirect_target": None,
            "is_placeholder_page": is_placeholder,
            "placeholder_reason": reason,
            "has_parameters_execute_results_frame": has_frame,
            "platform_guess": platform.get("label"),
            "category_guess": None,
            "feature_guess": None,
        })
        if is_placeholder:
            empty_pages.append({"route": route, "component": component, "reason": reason})

    # Category home routes
    for platform in platforms:
        for category in platform.get("categories", []):
            route = category["homeRoute"]
            component = route_component_map.get(route) or category.get("homeComponentPath") or TEMPLATE_CATEGORY
            is_placeholder, reason, has_frame = analyze_component(component)
            routes.append({
                "route": route,
                "kind": "ui",
                "page_component_path": component,
                "is_redirect": False,
                "redirect_target": None,
                "is_placeholder_page": is_placeholder,
                "placeholder_reason": reason,
                "has_parameters_execute_results_frame": has_frame,
                "platform_guess": platform.get("label"),
                "category_guess": category.get("label"),
                "feature_guess": None,
            })
            if is_placeholder:
                empty_pages.append({"route": route, "component": component, "reason": reason})

    # Feature routes
    for platform in platforms:
        for category in platform.get("categories", []):
            for feature in category.get("features", []):
                route = feature["route"]
                component = route_component_map.get(route) or feature.get("componentPath") or TEMPLATE_FEATURE
                is_placeholder, reason, has_frame = analyze_component(component)
                routes.append({
                    "route": route,
                    "kind": "ui",
                    "page_component_path": component,
                    "is_redirect": False,
                    "redirect_target": None,
                    "is_placeholder_page": is_placeholder,
                    "placeholder_reason": reason,
                    "has_parameters_execute_results_frame": has_frame,
                    "platform_guess": platform.get("label"),
                    "category_guess": category.get("label"),
                    "feature_guess": feature.get("label"),
                })
                if is_placeholder:
                    empty_pages.append({"route": route, "component": component, "reason": reason})

    # Legacy redirects
    for source, target in legacy_redirects.items():
        routes.append({
            "route": source,
            "kind": "ui",
            "page_component_path": f"redirect:{target}",
            "is_redirect": True,
            "redirect_target": target,
            "is_placeholder_page": False,
            "placeholder_reason": None,
            "has_parameters_execute_results_frame": False,
            "platform_guess": None,
            "category_guess": None,
            "feature_guess": None,
        })

    # App routes
    for route, component in app_routes.items():
        # Skip wildcard here; NavRouteRenderer handles IA routes already listed
        if route == "*":
            continue
        ctx = route_context.get(route, {})
        is_placeholder, reason, has_frame = analyze_component(component)
        routes.append({
            "route": route,
            "kind": "ui",
            "page_component_path": component,
            "is_redirect": False,
            "redirect_target": None,
            "is_placeholder_page": is_placeholder,
            "placeholder_reason": reason,
            "has_parameters_execute_results_frame": has_frame,
            "platform_guess": ctx.get("platform", {}).get("label") if ctx.get("platform") else None,
            "category_guess": ctx.get("category", {}).get("label") if ctx.get("category") else None,
            "feature_guess": ctx.get("feature", {}).get("label") if ctx.get("feature") else None,
        })
        if is_placeholder:
            empty_pages.append({"route": route, "component": component, "reason": reason})

    # Deduplicate routes by route key (prefer non-redirects)
    route_by_path: Dict[str, Dict[str, Any]] = {}
    for entry in routes:
        existing = route_by_path.get(entry["route"])
        if not existing:
            route_by_path[entry["route"]] = entry
        else:
            if existing.get("is_redirect") and not entry.get("is_redirect"):
                route_by_path[entry["route"]] = entry
    routes = sorted(route_by_path.values(), key=lambda x: x["route"])

    # Page catalogs
    feature_pages = []
    category_pages = []
    platform_pages = []
    other_pages = []

    for entry in routes:
        route = entry["route"]
        ctx = route_context.get(route)
        renderer = "NavRouteRenderer" if ctx else "App"
        page_entry = {
            "route": route,
            "component_path": entry["page_component_path"],
            "renderer": renderer,
            "is_placeholder_page": entry["is_placeholder_page"],
            "placeholder_reason": entry["placeholder_reason"],
            "has_parameters_execute_results_frame": entry["has_parameters_execute_results_frame"],
        }
        if ctx and ctx.get("is_feature"):
            feature_pages.append(page_entry)
        elif ctx and ctx.get("is_category_home"):
            category_pages.append(page_entry)
        elif ctx and ctx.get("is_platform"):
            platform_pages.append(page_entry)
        else:
            other_pages.append(page_entry)

    # Platform catalog
    platform_catalog = []
    for platform in platforms:
        platform_catalog.append({
            "label": platform.get("label"),
            "id": platform.get("id"),
            "path": platform.get("path"),
            "order": platform.get("order"),
            "where_defined": str(manifest_path.relative_to(REPO_ROOT)),
        })

    # Category catalog
    category_catalog = []
    for platform in platforms:
        for category in platform.get("categories", []):
            category_catalog.append({
                "platform_label": platform.get("label"),
                "platform_id": platform.get("id"),
                "category_label": category.get("label"),
                "category_id": category.get("id"),
                "homeRoute": category.get("homeRoute"),
                "component": category.get("homeComponentPath"),
                "order": category.get("order"),
                "where_defined": str(manifest_path.relative_to(REPO_ROOT)),
            })

    # Feature catalog
    feature_catalog = []
    for platform in platforms:
        for category in platform.get("categories", []):
            for feature in category.get("features", []):
                component = route_component_map.get(feature["route"]) or feature.get("componentPath")
                file_text = read_text(REPO_ROOT / component) if component else ""
                is_placeholder, reason, has_frame = analyze_component(component)
                widgets = []
                if "FeaturePageTemplate" in file_text or component == TEMPLATE_FEATURE:
                    widgets = ["Parameters", "Execute", "Results"]
                feature_catalog.append({
                    "platform": platform.get("label"),
                    "category": category.get("label"),
                    "feature_label": feature.get("label"),
                    "feature_id": feature.get("id"),
                    "route": feature.get("route"),
                    "component_path": component,
                    "shared_feature_key": normalize_label(feature.get("label", "")),
                    "placeholder_reason": reason,
                    "has_parameters_execute_results_frame": has_frame,
                    "widgets_displays": widgets,
                })

    # Duplicates
    by_component: Dict[str, List[Dict[str, str]]] = {}
    by_label: Dict[str, List[Dict[str, str]]] = {}
    for feature in feature_catalog:
        component = feature.get("component_path") or ""
        by_component.setdefault(component, []).append({
            "route": feature.get("route"),
            "label": feature.get("feature_label"),
            "platform": feature.get("platform"),
            "category": feature.get("category"),
        })
        label_key = normalize_label(feature.get("feature_label", ""))
        by_label.setdefault(label_key, []).append({
            "route": feature.get("route"),
            "label": feature.get("feature_label"),
            "platform": feature.get("platform"),
            "category": feature.get("category"),
        })

    def build_dup_groups(groups: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        dup_list = []
        for key, entries in groups.items():
            if len(entries) < 2:
                continue
            routes = sorted({e["route"] for e in entries})
            dup_list.append({
                "key": key,
                "occurrences": entries,
                "routes_identical": len(routes) == 1,
                "recommended_shared_feature_key": normalize_label(entries[0]["label"]),
                "recommended_canonical_route": routes[0] if routes else None,
            })
        return sorted(dup_list, key=lambda x: x["key"])

    duplicates = {
        "by_component_path": build_dup_groups(by_component),
        "by_label": build_dup_groups(by_label),
    }

    # Empty pages markdown
    empty_pages_lines = ["# Empty/Placeholder Pages", ""]
    for entry in sorted(empty_pages, key=lambda x: x["route"]):
        empty_pages_lines.append(f"- route: {entry['route']}")
        empty_pages_lines.append(f"  component: {entry['component']}")
        empty_pages_lines.append(f"  reason: {entry['reason']}")
    empty_pages_md = "\n".join(empty_pages_lines)

    # Redirects
    redirect_entries = []
    for source, target in legacy_redirects.items():
        redirect_entries.append({
            "from": source,
            "to": target,
            "defined_in": "frontend/src/data/iaManifest.from_json.json",
            "applied_in": "frontend/src/components/Layout.tsx",
        })

    # NAV_SOURCES
    nav_lines = ["# Navigation + Routing Sources", ""]
    for path, desc in NAV_SOURCES:
        nav_lines.append(f"- `{path}`: {desc}")

    # Outputs
    write_md(OUT_DIR / "NAV_SOURCES.md", "\n".join(nav_lines))
    write_json(OUT_DIR / "ROUTE_MAP.json", {"repo": repo, "routes": routes})
    write_json(OUT_DIR / "PAGE_CATALOG.json", {
        "feature_pages": feature_pages,
        "category_home_pages": category_pages,
        "platform_landing_pages": platform_pages,
        "other_pages": other_pages,
    })
    write_json(OUT_DIR / "PLATFORM_CATALOG.json", platform_catalog)
    write_json(OUT_DIR / "CATEGORY_CATALOG.json", category_catalog)
    write_json(OUT_DIR / "FEATURE_CATALOG.json", feature_catalog)
    write_json(OUT_DIR / "DUPLICATES.json", duplicates)
    write_md(OUT_DIR / "EMPTY_PAGES.md", empty_pages_md)
    write_json(OUT_DIR / "REDIRECTS.json", redirect_entries)


if __name__ == "__main__":
    main()
