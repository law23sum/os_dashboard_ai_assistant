"""Placeholder routes for knowledge services."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def knowledge_status() -> dict[str, str]:
    return {"status": "not_implemented"}
