from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from assistant_hub import db as hub_db
from config.config import get_api_config


def _float_env(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


MIN_COST_USD = _float_env("OSDASH_SESSION_COST_MIN_USD", 0.05)
MAX_COST_USD = _float_env("OSDASH_SESSION_COST_MAX_USD", 2.50)
SEED_META_KEY = "api_session_costs.seed"
REPORT_RELATIVE_PATH = Path("reports") / "api_session_costs_report.md"


@dataclass(frozen=True)
class ProviderSpec:
    key_attr: str
    label: str
    model_env: Optional[str] = None
    default_attr: Optional[str] = None


PROVIDER_SPECS: Dict[str, ProviderSpec] = {
    "openai": ProviderSpec(
        key_attr="openai_api_key",
        label="OpenAI",
        model_env="OPENAI_MODELS",
        default_attr="openai_model",
    ),
    "anthropic": ProviderSpec(
        key_attr="anthropic_api_key",
        label="Anthropic",
        model_env="ANTHROPIC_MODELS",
        default_attr="anthropic_model",
    ),
    "google": ProviderSpec(
        key_attr="google_api_key",
        label="Google Gemini",
        model_env="GOOGLE_MODELS",
        default_attr="google_model",
    ),
    "xai": ProviderSpec(
        key_attr="xai_api_key",
        label="xAI",
        model_env="XAI_MODELS",
        default_attr="xai_model",
    ),
    "cohere": ProviderSpec(
        key_attr="cohere_api_key",
        label="Cohere",
        model_env="COHERE_MODELS",
    ),
    "deepseek": ProviderSpec(
        key_attr="deepseek_api_key",
        label="DeepSeek",
        model_env="DEEPSEEK_MODELS",
    ),
    "groq": ProviderSpec(
        key_attr="groq_api_key",
        label="Groq",
        model_env="GROQ_MODELS",
        default_attr="groq_model",
    ),
    "perplexity": ProviderSpec(
        key_attr="perplexity_api_key",
        label="Perplexity",
        model_env="PERPLEXITY_MODELS",
    ),
    "mistral": ProviderSpec(
        key_attr="mistral_api_key",
        label="Mistral",
        model_env="MISTRAL_MODELS",
    ),
    "together": ProviderSpec(
        key_attr="together_api_key",
        label="Together AI",
        model_env="TOGETHER_MODELS",
    ),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _unique_list(values: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for value in values:
        if not value:
            continue
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _parse_model_env(env_key: Optional[str]) -> List[str]:
    if not env_key:
        return []
    raw = os.getenv(env_key)
    if not raw:
        return []
    return _unique_list(raw.split(","))


def _default_versions(spec: ProviderSpec, config) -> List[str]:
    if spec.default_attr:
        value = getattr(config, spec.default_attr, None)
        if value:
            return [str(value)]
    return ["default"]


def _get_enabled_providers(config) -> Dict[str, ProviderSpec]:
    enabled: Dict[str, ProviderSpec] = {}
    for provider, spec in PROVIDER_SPECS.items():
        if getattr(config, spec.key_attr, None):
            enabled[provider] = spec
    return enabled


def _get_provider_versions(spec: ProviderSpec, config) -> List[str]:
    versions = _parse_model_env(spec.model_env)
    if versions:
        return versions
    return _default_versions(spec, config)


def _ensure_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS api_session_costs (
            provider TEXT NOT NULL,
            version TEXT NOT NULL,
            cost_per_session_usd REAL NOT NULL,
            credits_remaining REAL NOT NULL DEFAULT 0,
            remaining_minutes INTEGER NOT NULL DEFAULT 0,
            seeded_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (provider, version)
        )
        """
    )
    conn.commit()


def _get_seed(conn) -> int:
    raw = hub_db.get_meta(conn, SEED_META_KEY)
    if raw:
        try:
            return int(raw)
        except ValueError:
            pass
    seed = secrets.randbits(32)
    hub_db.set_meta(conn, SEED_META_KEY, str(seed))
    return seed


def _seeded_cost(seed: int, provider: str, version: str) -> float:
    token = f"{seed}:{provider}:{version}".encode("utf-8")
    digest = hashlib.sha256(token).digest()
    value = int.from_bytes(digest[:4], "big") / 0xFFFFFFFF
    cost = MIN_COST_USD + (MAX_COST_USD - MIN_COST_USD) * value
    return round(cost, 4)


def _seed_missing_rows(conn, versions_map: Dict[str, List[str]], seed: int) -> None:
    if not versions_map:
        return
    existing = {
        (row["provider"], row["version"])
        for row in conn.execute(
            "SELECT provider, version FROM api_session_costs"
        ).fetchall()
    }
    now = _now_iso()
    inserted = False
    for provider, versions in versions_map.items():
        for version in versions:
            key = (provider, version)
            if key in existing:
                continue
            cost = _seeded_cost(seed, provider, version)
            conn.execute(
                """
                INSERT INTO api_session_costs (
                    provider,
                    version,
                    cost_per_session_usd,
                    credits_remaining,
                    remaining_minutes,
                    seeded_at,
                    updated_at
                ) VALUES (?, ?, ?, 0, 0, ?, ?)
                """,
                (provider, version, cost, now, now),
            )
            inserted = True
    if inserted:
        conn.commit()


def _write_failure_report(
    reason: str,
    versions_map: Dict[str, List[str]],
    generated_at: Optional[str] = None,
) -> str:
    repo_root = Path(__file__).resolve().parents[1]
    report_path = repo_root / REPORT_RELATIVE_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = generated_at or _now_iso()
    lines = [
        "# API Session Cost Report (Fallback)",
        "",
        f"Generated: {timestamp}",
        f"Reason: {reason}",
        "",
        "Providers checked:",
    ]
    if versions_map:
        for provider, versions in sorted(versions_map.items()):
            versions_text = ", ".join(versions) if versions else "default"
            lines.append(f"- {provider}: {versions_text}")
    else:
        lines.append("- none")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(report_path)


def build_session_costs_snapshot(conn) -> Dict[str, object]:
    _ensure_table(conn)
    config = get_api_config()
    enabled = _get_enabled_providers(config)
    generated_at = _now_iso()
    credits_remaining = 0
    credits_status = "zero"

    versions_map: Dict[str, List[str]] = {
        provider: _get_provider_versions(spec, config)
        for provider, spec in enabled.items()
    }

    if not enabled:
        report_path = _write_failure_report(
            "No API keys configured.",
            versions_map,
            generated_at,
        )
        return {
            "items": [],
            "providers": [],
            "credits_remaining": credits_remaining,
            "credits_status": credits_status,
            "generated_at": generated_at,
            "report_path": report_path,
            "error": "No API keys configured.",
        }

    seed = _get_seed(conn)
    _seed_missing_rows(conn, versions_map, seed)

    allowed = {(provider, version) for provider, versions in versions_map.items() for version in versions}
    if not allowed:
        report_path = _write_failure_report(
            "No API versions discovered for the configured keys.",
            versions_map,
            generated_at,
        )
        return {
            "items": [],
            "providers": sorted(enabled.keys()),
            "credits_remaining": credits_remaining,
            "credits_status": credits_status,
            "generated_at": generated_at,
            "report_path": report_path,
            "error": "No API versions discovered.",
        }

    placeholders = ",".join("?" for _ in enabled)
    rows = conn.execute(
        f"SELECT * FROM api_session_costs WHERE provider IN ({placeholders})",
        list(enabled.keys()),
    ).fetchall()

    items: List[Dict[str, object]] = []
    for row in rows:
        key = (row["provider"], row["version"])
        if key not in allowed:
            continue
        spec = enabled.get(row["provider"])
        items.append(
            {
                "provider": row["provider"],
                "provider_label": spec.label if spec else row["provider"],
                "version": row["version"],
                "cost_per_session_usd": float(row["cost_per_session_usd"]),
                "credits_remaining": float(row["credits_remaining"]),
                "remaining_minutes": int(row["remaining_minutes"]),
                "seeded_at": row["seeded_at"],
                "updated_at": row["updated_at"],
            }
        )

    if not items:
        report_path = _write_failure_report(
            "Session cost table returned no rows.",
            versions_map,
            generated_at,
        )
        return {
            "items": [],
            "providers": sorted(enabled.keys()),
            "credits_remaining": credits_remaining,
            "credits_status": credits_status,
            "generated_at": generated_at,
            "report_path": report_path,
            "error": "No session cost rows available.",
        }

    items.sort(key=lambda item: (item["provider_label"], item["version"]))

    return {
        "items": items,
        "providers": sorted(enabled.keys()),
        "credits_remaining": credits_remaining,
        "credits_status": credits_status,
        "generated_at": generated_at,
        "report_path": None,
    }


def write_failure_report(reason: str, versions_map: Optional[Dict[str, List[str]]] = None) -> str:
    return _write_failure_report(reason, versions_map or {}, _now_iso())
