#!/usr/bin/env python3
"""Generate a hierarchical test matrix covering all current features."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_PAGES = REPO_ROOT / "frontend" / "src" / "pages"
BACKEND_ROUTERS = REPO_ROOT / "backend_api" / "routers"
OUTPUT_FILE = REPO_ROOT / "tests" / "test_suite_matrix.json"

LEVELS = [
    {
        "type": "unit",
        "description": "Component-level validation focusing on isolated logic.",
    },
    {
        "type": "integration",
        "description": "Cross-module checks covering API + UI contracts.",
    },
    {
        "type": "system",
        "description": "End-to-end validation of a single deployable surface.",
    },
    {
        "type": "system_of_systems",
        "description": "Multi-surface scenarios spanning desktop/web/backend orchestration.",
    },
]

MODES = [
    {"mode": "sanity", "description": "Happy-path verification after builds."},
    {"mode": "smoke", "description": "Critical path coverage for deployments."},
    {"mode": "functional", "description": "Detailed behavior checks per feature."},
    {"mode": "regression", "description": "Guards against known/previous issues."},
]


def _camel_to_words(value: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    text = text.replace("_", " ")
    return " ".join(word.capitalize() for word in text.split())


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return cleaned.strip("-")


def collect_frontend_features() -> List[Dict[str, str]]:
    features: List[Dict[str, str]] = []
    if not FRONTEND_PAGES.exists():
        return features
    for path in sorted(FRONTEND_PAGES.glob("*.tsx")):
        if path.name.startswith("_"):
            continue
        stem = path.stem
        label = _camel_to_words(stem)
        features.append(
            {
                "slug": _slugify(f"frontend-{stem}"),
                "name": f"{label} Page",
                "source": "frontend",
                "path": str(path.relative_to(REPO_ROOT)),
            }
        )
    return features


def collect_backend_features() -> List[Dict[str, str]]:
    features: List[Dict[str, str]] = []
    if not BACKEND_ROUTERS.exists():
        return features
    for path in sorted(BACKEND_ROUTERS.glob("*.py")):
        if path.name.startswith("__"):
            continue
        stem = path.stem
        label = stem.replace("_", " ").title()
        features.append(
            {
                "slug": _slugify(f"backend-{stem}"),
                "name": f"{label} API",
                "source": "backend",
                "path": str(path.relative_to(REPO_ROOT)),
            }
        )
    return features


def build_suite() -> Dict[str, object]:
    features = collect_frontend_features() + collect_backend_features()
    suites: List[Dict[str, object]] = []
    generated_at = datetime.now(tz=timezone.utc).isoformat()
    for feature in features:
        level_entries: List[Dict[str, object]] = []
        for level in LEVELS:
            cases: List[Dict[str, object]] = []
            for mode in MODES:
                case_id = f"{feature['slug']}-{level['type']}-{mode['mode']}"
                cases.append(
                    {
                        "id": case_id,
                        "mode": mode["mode"],
                        "objective": f"{mode['description']} for {feature['name']}.",
                        "steps": [
                            f"Exercise {feature['name']} at the {level['type']} scope.",
                            f"Verify {mode['mode']} acceptance criteria and record findings.",
                        ],
                        "expected_result": f"{feature['name']} satisfies {mode['mode']} constraints without regressions.",
                    }
                )
            level_entries.append(
                {
                    "type": level["type"],
                    "description": level["description"],
                    "cases": cases,
                }
            )
        suites.append(
            {
                "feature": feature["name"],
                "source": feature["source"],
                "path": feature["path"],
                "slug": feature["slug"],
                "levels": level_entries,
            }
        )

    return {
        "metadata": {
            "generated_at": generated_at,
            "repo_root": str(REPO_ROOT),
            "feature_count": len(features),
            "level_count": len(LEVELS),
            "mode_count": len(MODES),
        },
        "levels": LEVELS,
        "modes": MODES,
        "suites": suites,
    }


def main() -> None:
    suite = build_suite()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(suite, handle, indent=2)
        handle.write("\n")
    print(
        f"🧪 Generated test suite matrix with {suite['metadata']['feature_count']} features "
        f"→ {OUTPUT_FILE.relative_to(REPO_ROOT)}"
    )


if __name__ == "__main__":
    main()
