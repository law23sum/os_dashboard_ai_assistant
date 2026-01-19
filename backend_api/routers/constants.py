"""Placeholder routes for the constants catalog."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def constants_status() -> dict[str, str]:
    return {"status": "not_implemented"}
