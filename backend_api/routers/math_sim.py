"""Math simulation endpoints (proxy)."""

from __future__ import annotations

import os
from typing import Any

import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()

_DEFAULT_BASE_URL = "http://127.0.0.1:8010"
_DEFAULT_TIMEOUT_SECONDS = 10


def _get_base_url() -> str:
    base_url = os.getenv("MATHSIM_BASE_URL", _DEFAULT_BASE_URL).strip()
    if not base_url:
        base_url = _DEFAULT_BASE_URL
    return base_url.rstrip("/")


def _fetch_json(path: str, timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS) -> Any:
    base_url = _get_base_url()
    url = f"{base_url}{path}"
    try:
        response = requests.get(url, timeout=timeout_seconds)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Math-Sim request failed for {url}: {exc}",
        ) from exc
    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Math-Sim response was not JSON for {url}.",
        ) from exc


@router.get("/")
def math_sim_status():
    """Return a minimal status payload for the proxy."""
    return {
        "status": "ok",
        "message": "Math-Sim proxy online.",
        "base_url": _get_base_url(),
        "endpoints": ["/health", "/summary"],
    }


@router.get("/health")
def math_sim_health():
    """Return reachability and upstream status payload."""
    base_url = _get_base_url()
    try:
        upstream = _fetch_json("/", timeout_seconds=3)
        return {
            "status": "ok",
            "reachable": True,
            "base_url": base_url,
            "upstream": upstream,
        }
    except HTTPException as exc:
        return {
            "status": "degraded",
            "reachable": False,
            "base_url": base_url,
            "error": exc.detail,
        }


@router.get("/summary")
def math_sim_summary():
    """Proxy the Math-Sim domain summary."""
    return _fetch_json("/api/summary")
