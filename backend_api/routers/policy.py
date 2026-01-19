"""Placeholder routes for policy management."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def policy_status() -> dict[str, str]:
    return {"status": "not_implemented"}
