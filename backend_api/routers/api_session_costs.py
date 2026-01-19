"""API session cost router."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from assistant_hub.api_session_costs import build_session_costs_snapshot, write_failure_report
from backend_api.db import db_session

router = APIRouter()


class ApiSessionCostItem(BaseModel):
    provider: str
    provider_label: str
    version: str
    cost_per_session_usd: float
    credits_remaining: float
    remaining_minutes: int
    seeded_at: str
    updated_at: str


class ApiSessionCostResponse(BaseModel):
    items: List[ApiSessionCostItem]
    providers: List[str]
    credits_remaining: float
    credits_status: str
    generated_at: str
    report_path: Optional[str] = None
    error: Optional[str] = None


@router.get("/", response_model=ApiSessionCostResponse)
async def list_api_session_costs():
    """Return the API session cost snapshot for configured providers."""
    try:
        with db_session() as db:
            snapshot = build_session_costs_snapshot(db)
        return snapshot
    except Exception as exc:
        report_path = write_failure_report(f"API session cost request failed: {exc}")
        return ApiSessionCostResponse(
            items=[],
            providers=[],
            credits_remaining=0,
            credits_status="zero",
            generated_at=datetime.now(timezone.utc).isoformat(),
            report_path=report_path,
            error="Failed to build API session costs.",
        )
