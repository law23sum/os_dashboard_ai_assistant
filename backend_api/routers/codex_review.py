"""Codex review API router."""

from __future__ import annotations

import os
import uuid
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from assistant_core.db import init_db, load_openai_api_key

# Try to import codex_review, but make it optional
try:
    import importlib
    codex_review = importlib.import_module("assistant_core.codex_review")
except (ImportError, ModuleNotFoundError):
    codex_review = None  # type: ignore

router = APIRouter()
REPO_ROOT = Path(__file__).resolve().parents[2]


class CodexReviewRequest(BaseModel):
    base: Optional[str] = Field(default=None, description="Base git ref.")
    head: Optional[str] = Field(default=None, description="Head git ref.")
    uncommitted: bool = Field(default=False, description="Include uncommitted changes.")
    paths: Optional[List[str]] = Field(default=None, description="Path filters.")
    include_files: bool = Field(
        default=False,
        description="Include file contents for changed files.",
    )
    max_diff_bytes: int = Field(default=200_000, ge=1)
    max_file_bytes: int = Field(default=20_000, ge=1)
    max_files: int = Field(default=20, ge=1)
    timeout_seconds: int = Field(default=180, ge=1)
    config_overrides: Optional[List[str]] = Field(default=None)
    approval_policy: str = Field(default="never")
    dry_run: bool = Field(default=True)


@router.post("/codex/review")
def run_codex_review(request: CodexReviewRequest) -> Dict[str, Any]:
    if codex_review is None:
        raise HTTPException(
            status_code=503,
            detail="Codex review module is not available. Please ensure assistant_core.codex_review is installed."
        )
    
    bundle = codex_review.prepare_review_bundle(
        REPO_ROOT,
        base=request.base,
        head=request.head,
        uncommitted=request.uncommitted,
        paths=request.paths,
        include_files=request.include_files,
        max_diff_bytes=request.max_diff_bytes,
        max_file_bytes=request.max_file_bytes,
        max_files=request.max_files,
    )

    output_dir = REPO_ROOT / "tmp" / "codex_review" / uuid.uuid4().hex

    if request.dry_run:
        assets = codex_review.write_review_assets(bundle, output_dir)
        return {
            "dry_run": True,
            "prompt_path": str(assets["prompt_path"]),
            "schema_path": str(assets["schema_path"]),
            "meta_path": str(assets["meta_path"]),
            "diff_truncated": bundle.diff_truncated,
            "files_included": [ctx.path for ctx in bundle.file_contexts],
        }

    env = os.environ.copy()
    if not env.get("OPENAI_API_KEY"):
        with closing(init_db()) as conn:
            api_key = load_openai_api_key(conn)
        if api_key:
            env["OPENAI_API_KEY"] = api_key

    if not env.get("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured.")

    result = codex_review.run_codex_review(
        bundle,
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        timeout_seconds=request.timeout_seconds,
        config_overrides=request.config_overrides,
        env=env,
        approval_policy=request.approval_policy,
    )

    return {
        "dry_run": False,
        "diff_truncated": bundle.diff_truncated,
        "files_included": [ctx.path for ctx in bundle.file_contexts],
        "output_path": result.get("output_path"),
        "returncode": result.get("returncode"),
        "timed_out": result.get("timed_out"),
        "review": result.get("review"),
        "stderr": result.get("stderr"),
    }
