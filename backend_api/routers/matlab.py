"""Placeholder routes for MATLAB integrations."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def matlab_status() -> dict[str, str]:
    return {"status": "not_implemented"}
