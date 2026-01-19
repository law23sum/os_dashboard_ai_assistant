#!/usr/bin/env python3
"""Generate page-contracts.json from contracts/gui registry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
NAV_PATH = REPO_ROOT / "contracts" / "gui" / "gui_nav.latest.json"
OUTPUT_PATH = REPO_ROOT / "frontend" / "src" / "domain" / "page-contracts.json"


def build_contracts(nav: Dict[str, Any]) -> List[Dict[str, Any]]:
    contracts_by_route: Dict[str, Dict[str, Any]] = {}
    for edition in nav.get("editions", []):
        for platform in edition.get("platforms", []):
            platform_key = platform.get("key", "platform")
            for category in platform.get("categories", []):
                category_key = category.get("key", "category")
                for feature in category.get("features", []):
                    route = feature.get("route")
                    if not route:
                        continue
                    contract_info = feature.get("contracts", {})
                    contracts_by_route[route] = {
                        "route": route,
                        "role": "feature",
                        "entities": [platform_key, category_key],
                        "projections": contract_info.get("subscribes_projections", []),
                        "emits_events": contract_info.get("emits_events", []),
                        "params": [],
                        "configs": [],
                        "dimensions": [],
                        "compute_class": "standard",
                        "summary": feature.get("label", ""),
                    }
    return list(contracts_by_route.values())


def main() -> None:
    nav = json.loads(NAV_PATH.read_text())
    contracts = build_contracts(nav)
    OUTPUT_PATH.write_text(json.dumps(contracts, indent=2))
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
