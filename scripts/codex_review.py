#!/usr/bin/env python3
"""Run a structured Codex review against a git diff."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from assistant_hub.config import DB_PATH
from assistant_hub_gui.assistant_hub.db import load_openai_api_key

CODEX_REVIEW_PATH = REPO_ROOT / "assistant_core" / "codex_review.py"
_spec = importlib.util.spec_from_file_location("assistant_core.codex_review", CODEX_REVIEW_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load codex_review from {CODEX_REVIEW_PATH}")
codex_review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(codex_review)


def _load_api_key_from_db() -> Optional[str]:
    db_path = Path(DB_PATH)
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    with closing(conn):
        try:
            return load_openai_api_key(conn)
        except Exception:
            return None


def _resolve_output_dir(path_str: Optional[str]) -> Path:
    if path_str:
        return Path(path_str)
    return REPO_ROOT / "tmp" / "codex_review"


def _ensure_output_dir(output_dir: Path) -> Path:
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    except PermissionError:
        fallback = Path(tempfile.mkdtemp(prefix="codex_review_"))
        return fallback


def _build_env() -> Dict[str, str]:
    env = os.environ.copy()
    if not env.get("OPENAI_API_KEY"):
        api_key = _load_api_key_from_db()
        if api_key:
            env["OPENAI_API_KEY"] = api_key
    return env


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a structured Codex review.")
    parser.add_argument("--base", default=None, help="Base git ref (default: HEAD~1).")
    parser.add_argument("--head", default=None, help="Head git ref (default: HEAD).")
    parser.add_argument(
        "--uncommitted",
        action="store_true",
        help="Review uncommitted (staged + unstaged) changes.",
    )
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        default=None,
        help="Limit review to specific paths (repeatable).",
    )
    parser.add_argument(
        "--include-files",
        action="store_true",
        help="Include file contents for changed files in the prompt.",
    )
    parser.add_argument(
        "--max-diff-bytes",
        type=int,
        default=200_000,
        help="Max diff size to include in prompt.",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=20_000,
        help="Max bytes per file to include when --include-files is set.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=20,
        help="Max files to include when --include-files is set.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Codex execution timeout in seconds.",
    )
    parser.add_argument(
        "--config",
        action="append",
        dest="config_overrides",
        default=[],
        help="Codex config override (repeatable): key=value",
    )
    parser.add_argument(
        "--approval-policy",
        default="never",
        help="Codex approval policy override (default: never).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for prompt/schema/results.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write prompt/schema and exit without running Codex.",
    )

    args = parser.parse_args()

    bundle = codex_review.prepare_review_bundle(
        REPO_ROOT,
        base=args.base,
        head=args.head,
        uncommitted=args.uncommitted,
        paths=args.paths,
        include_files=args.include_files,
        max_diff_bytes=args.max_diff_bytes,
        max_file_bytes=args.max_file_bytes,
        max_files=args.max_files,
    )

    output_dir = _ensure_output_dir(_resolve_output_dir(args.output_dir))

    if args.dry_run:
        assets = codex_review.write_review_assets(bundle, output_dir)
        payload = {
            "dry_run": True,
            "prompt_path": str(assets["prompt_path"]),
            "schema_path": str(assets["schema_path"]),
            "meta_path": str(assets["meta_path"]),
        }
        print(json.dumps(payload, indent=2))
        return 0

    env = _build_env()
    if not env.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set and was not found in the DB.")
        return 1

    result = codex_review.run_codex_review(
        bundle,
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        timeout_seconds=args.timeout,
        config_overrides=args.config_overrides,
        env=env,
        approval_policy=args.approval_policy,
    )

    summary = {
        "returncode": result.get("returncode"),
        "timed_out": result.get("timed_out"),
        "output_path": result.get("output_path"),
        "review": result.get("review"),
    }
    print(json.dumps(summary, indent=2))
    return 0 if result.get("returncode") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
