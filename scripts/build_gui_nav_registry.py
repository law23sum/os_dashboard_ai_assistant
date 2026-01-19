#!/usr/bin/env python3
"""Generate contract-driven GUI nav registry from legacy nav + seed."""
from __future__ import annotations

import json
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_NAV_PATH = REPO_ROOT / "frontend" / "public" / "gui_nav.latest.json"

OUTPUT_DIR = REPO_ROOT / "contracts" / "gui"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

SEED: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]] = {
    "Personal": {
        "Core": {
            "Overview": [
                {
                    "title": "Dashboard",
                    "path": "/core/dashboard",
                },
                {
                    "title": "Master Stack",
                    "path": "/core/master-stack",
                },
                {
                    "title": "Platform Overview",
                    "path": "/dashboard",
                },
            ]
        },
        "Common": {
            "Files & Storage": [
                {
                    "title": "File Browser",
                    "path": "/common/files/browser",
                }
            ],
            "Integrations": [
                {
                    "title": "Connector Catalog",
                    "path": "/common/integrations/catalog",
                }
            ],
            "Mission Control": [
                {
                    "title": "Mission Control",
                    "path": "/mission",
                }
            ],
        },
        "Audit Official Records": {
            "Record Auditor & Logbook": [
                {
                    "title": "Evidence Packs",
                    "path": "/audit/evidence-packs",
                },
                {
                    "title": "Policy Decisions",
                    "path": "/audit/policy-decisions",
                },
            ],
            "Governance Center": [
                {
                    "title": "Governance Home",
                    "path": "/governance",
                },
                {
                    "title": "Security Posture",
                    "path": "/governance/security",
                },
            ],
        },
        "Automation": {
            "Workflows & Capsules": [
                {
                    "title": "Workflow Builder",
                    "path": "/automation/workflows/builder",
                }
            ],
            "Automation Hub": [
                {
                    "title": "Automation Home",
                    "path": "/ai",
                },
                {
                    "title": "Tooling Lab",
                    "path": "/ai/tooling-lab",
                },
            ],
        },
        "Settings": {
            "Profile & Preferences": [
                {
                    "title": "Preferences",
                    "path": "/settings/preferences",
                }
            ]
        },
        "Admin": {
            "Users & Roles": [
                {
                    "title": "RBAC/ABAC",
                    "path": "/admin/access/rbac",
                }
            ],
            "Admin Console": [
                {
                    "title": "Admin Console",
                    "path": "/admin",
                }
            ],
        },
        "Workstation": {
            "Writer Workstation": [
                {
                    "title": "Draft Editor",
                    "path": "/workstation/writer/editor",
                }
            ],
            "Dev Workstation": [
                {
                    "title": "Commands Runner",
                    "path": "/workstation/dev/commands",
                }
            ],
            "Workstation Hub": [
                {
                    "title": "Workspace Hub",
                    "path": "/workspaces",
                }
            ],
        },
        "Systems": {
            "Observability": [
                {
                    "title": "Logs & Traces",
                    "path": "/systems/observability/logs-traces",
                }
            ],
            "Drivers Hub": [
                {
                    "title": "Drivers Home",
                    "path": "/drivers",
                },
                {
                    "title": "Operations Center",
                    "path": "/operations",
                },
            ],
        },
        "Simulations": {
            "Simulation Hub": [
                {
                    "title": "Run Simulations",
                    "path": "/simulations/hub/run",
                }
            ],
            "Simulation Home": [
                {
                    "title": "Simulation Home",
                    "path": "/simulations",
                }
            ],
        },
        "Research": {
            "Projects & Experiments": [
                {
                    "title": "Registry",
                    "path": "/research/registry",
                }
            ],
            "Roadmap & Future": [
                {
                    "title": "Roadmap Hub",
                    "path": "/roadmap",
                },
                {
                    "title": "Future Capabilities",
                    "path": "/roadmap/future-capabilities",
                },
                {
                    "title": "Future Deck",
                    "path": "/future",
                },
            ],
        },
        "Encyclopedia": {
            "Topics": [
                {
                    "title": "Topic Browser",
                    "path": "/encyclopedia/topics",
                }
            ],
            "Explanations": [
                {
                    "title": "Explain a Concept",
                    "path": "/encyclopedia/explanations/explain",
                }
            ],
            "History": [
                {
                    "title": "History Timeline",
                    "path": "/encyclopedia/history/timeline",
                }
            ],
        },
        "Libraries": {
            "Capsule Library": [
                {
                    "title": "Catalog",
                    "path": "/libraries/capsules/catalog",
                }
            ],
            "Reference Artifacts": [
                {
                    "title": "Reference Hub",
                    "path": "/docs/reference",
                }
            ],
        },
        "Knowledge": {
            "Perspective": [
                {
                    "title": "World Model",
                    "path": "/knowledge/perspective/world-model",
                }
            ],
            "Insight": [
                {
                    "title": "Insight Journal",
                    "path": "/knowledge/insight/journal",
                }
            ],
            "Wisdom": [
                {
                    "title": "Principles",
                    "path": "/knowledge/wisdom/principles",
                }
            ],
            "Experience": [
                {
                    "title": "Experience Log",
                    "path": "/knowledge/experience/log",
                }
            ],
        },
    },
    "Enterprise": {
        "Core": {
            "Overview": [
                {
                    "title": "Dashboard",
                    "path": "/core/dashboard",
                }
            ]
        },
        "Admin": {
            "Tenants": [
                {
                    "title": "Tenant Registry",
                    "path": "/admin/tenants/registry",
                }
            ],
            "Billing & Usage": [
                {
                    "title": "Usage Ledger",
                    "path": "/admin/billing/usage",
                }
            ],
            "Approvals": [
                {
                    "title": "Approval Console",
                    "path": "/admin/approvals/console",
                }
            ],
        },
        "Audit Official Records": {
            "Regulator Console": [
                {
                    "title": "Regulator Evidence View",
                    "path": "/audit/regulator/console",
                }
            ]
        },
    },
    "Business/Team": {},
}

AUTO_FEATURE_LABELS = [
    "Overview",
    "Runbook",
    "Evidence",
]


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace("&", "and")
        .replace("/", " ")
        .replace("+", " ")
        .replace("'", "")
        .replace("\"", "")
        .replace("–", " ")
        .replace("—", " ")
        .replace(" ", "-")
    )


def normalize_slug(value: str) -> str:
    slug = slugify(value)
    out = []
    prev_dash = False
    for ch in slug:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        else:
            if not prev_dash:
                out.append("-")
                prev_dash = True
    result = "".join(out).strip("-")
    return result or "item"


def route_slug(route: str) -> str:
    return normalize_slug(route.strip("/").replace("/", "_"))


def ensure_unique_route(route: str, used_routes: set[str]) -> str:
    candidate = route
    counter = 1
    while candidate in used_routes:
        candidate = f"{route}-{counter}"
        counter += 1
    used_routes.add(candidate)
    return candidate


def infer_widget_kind(title: str) -> str:
    lower = title.lower()
    if "search" in lower:
        return "search_box"
    if "log" in lower or "trace" in lower:
        return "log_viewer"
    if "timeline" in lower:
        return "timeline"
    if "graph" in lower or "map" in lower or "network" in lower:
        return "graph_view"
    if "table" in lower or "list" in lower:
        return "table"
    if "diff" in lower:
        return "diff_viewer"
    if "upload" in lower or "file" in lower:
        return "file_uploader"
    return "form"


def infer_display_kind(title: str) -> str:
    lower = title.lower()
    if "audit" in lower or "logbook" in lower:
        return "audit_trail"
    if "evidence" in lower:
        return "evidence_links"
    if "policy" in lower:
        return "policy_decision_panel"
    if "status" in lower or "stream" in lower:
        return "status_stream"
    if "projection" in lower:
        return "projection_view"
    return "results_panel"


def build_feature(
    platform_key: str,
    category_key: str,
    feature: Dict[str, Any],
    nav_order: int,
) -> Dict[str, Any]:
    title = feature["title"]
    route = feature["path"]
    key = route_slug(route)
    widget_kind = infer_widget_kind(title)
    display_kind = infer_display_kind(title)
    widget_id = f"w_{key}_{widget_kind}"
    display_id = f"d_{key}_{display_kind}"
    contracts = {
        "page_contract_ref": f"urn:omniverse:page:{key}",
        "emits_events": ["feature_action_started", "feature_action_completed"],
        "subscribes_projections": [f"projection.{platform_key}.{category_key}"],
    }
    return {
        "key": key,
        "label": title,
        "route": route,
        "nav_order": nav_order,
        "contracts": contracts,
        "widgets": [{"id": widget_id, "kind": widget_kind}],
        "displays": [{"id": display_id, "kind": display_kind}],
    }


def add_seed_features(
    target: OrderedDict,
    seed_platform: Dict[str, List[Dict[str, Any]]],
) -> None:
    for category_label, seed_features in seed_platform.items():
        if category_label not in target:
            target[category_label] = []
        existing_routes = {f.get("path") for f in target[category_label] if isinstance(f, dict)}
        for seed_feature in seed_features:
            if seed_feature["path"] not in existing_routes:
                target[category_label].append({
                    "title": seed_feature["title"],
                    "path": seed_feature["path"],
                    "new": True,
                })
                existing_routes.add(seed_feature["path"])


def ensure_min_categories(
    target: OrderedDict,
    platform_key: str,
    used_routes: set[str],
) -> None:
    while len(target) < 2:
        label = "Operations" if "Operations" not in target else "Controls"
        route_base = f"/{platform_key}/{normalize_slug(label)}"
        features = []
        for idx, base_label in enumerate(AUTO_FEATURE_LABELS):
            auto_route = ensure_unique_route(f"{route_base}/{normalize_slug(base_label)}", used_routes)
            features.append({"title": base_label, "path": auto_route, "new": True})
        target[label] = features


def ensure_min_features(
    category_label: str,
    features: List[Dict[str, Any]],
    platform_key: str,
    category_key: str,
    used_routes: set[str],
) -> None:
    existing_routes = {f.get("path") for f in features if isinstance(f, dict)}
    idx = 0
    while len(features) < 3 and idx < len(AUTO_FEATURE_LABELS):
        label = AUTO_FEATURE_LABELS[idx]
        idx += 1
        auto_route = ensure_unique_route(
            f"/{platform_key}/{category_key}/{normalize_slug(label)}",
            used_routes,
        )
        if auto_route in existing_routes:
            continue
        features.append({"title": label, "path": auto_route, "new": True})
        existing_routes.add(auto_route)


def build_registry() -> Dict[str, Any]:
    legacy_nav = json.loads(LEGACY_NAV_PATH.read_text())
    editions_out: List[Dict[str, Any]] = []

    for edition_label in EDITION_LABELS:
        edition_key = EDITION_KEYS.get(edition_label, normalize_slug(edition_label))
        platforms_out: List[Dict[str, Any]] = []
        edition_nav = legacy_nav.get(edition_label, {})
        if not edition_nav and edition_label == "Business/Team":
            edition_nav = legacy_nav.get("Personal", {})

        used_routes = set()
        for platform_data in edition_nav.values():
            for feature_list in platform_data.values():
                for feature in feature_list:
                    used_routes.add(feature.get("path"))

        for order_index, platform_label in enumerate(REQUIRED_PLATFORM_ORDER, start=1):
            platform_key = normalize_slug(platform_label)
            categories = OrderedDict()
            legacy_categories = edition_nav.get(platform_label, {})
            for category_label, features in legacy_categories.items():
                categories[category_label] = list(features)

            seed_platform = SEED.get(edition_label, {}).get(platform_label, {})
            if not seed_platform and edition_label == "Business/Team":
                seed_platform = SEED.get("Personal", {}).get(platform_label, {})
            add_seed_features(categories, seed_platform)

            ensure_min_categories(categories, platform_key, used_routes)

            categories_out: List[Dict[str, Any]] = []
            for category_order, (category_label, features) in enumerate(categories.items()):
                category_key = normalize_slug(category_label)
                ensure_min_features(
                    category_label,
                    features,
                    platform_key,
                    category_key,
                    used_routes,
                )
                feature_defs = []
                for nav_order, feature in enumerate(features):
                    if not feature or not isinstance(feature, dict) or not feature.get("path"):
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

    registry = {
        "meta": {
            "version": datetime.now(timezone.utc).strftime("%Y.%m.%d"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_of_truth": "hybrid_merge",
            "platform_order": REQUIRED_PLATFORM_ORDER,
        },
        "editions": editions_out,
    }

    # Apply shared_feature_key for duplicate routes across editions/categories.
    route_counts = defaultdict(int)
    for edition in editions_out:
        for platform in edition["platforms"]:
            for category in platform["categories"]:
                for feature in category["features"]:
                    route_counts[feature["route"]] += 1

    for edition in editions_out:
        for platform in edition["platforms"]:
            for category in platform["categories"]:
                for feature in category["features"]:
                    if route_counts[feature["route"]] > 1:
                        feature["shared_feature_key"] = f"shared.{route_slug(feature['route'])}"

    return registry


def main() -> None:
    registry = build_registry()
    output_path = OUTPUT_DIR / "gui_nav.latest.json"
    output_path.write_text(json.dumps(registry, indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
