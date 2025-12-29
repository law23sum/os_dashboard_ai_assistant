"""Intent Processor API bridging personas to driver plans (Spec §1.7, §8)."""
from __future__ import annotations

from datetime import datetime
import random
import uuid
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()

IntentStatus = Literal["planning", "executing", "completed", "failed"]
IntentPriority = Literal["low", "normal", "high", "critical"]


class IntentRecord(BaseModel):
    id: str
    query: str
    persona: str
    status: IntentStatus
    priority: IntentPriority
    created_at: str
    steps_total: int
    steps_completed: int
    final_result: Optional[str] = None


class IntentCreateRequest(BaseModel):
    query: str
    priority: IntentPriority = "normal"
    context: Optional[Dict[str, str]] = None
    persona: str = Field(default="aic", description="Persona executing the intent")


_INTENTS: Dict[str, IntentRecord] = {}


def _iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _advance_intents() -> None:
    for intent in _INTENTS.values():
        if intent.status in {"completed", "failed"}:
            continue
        if intent.status == "planning":
            if intent.steps_total == 0:
                intent.steps_total = random.randint(3, 6)
            # promote to executing quickly once planning has steps
            intent.status = "executing"
        if intent.status == "executing":
            if intent.steps_completed < intent.steps_total:
                intent.steps_completed += 1
            if intent.steps_completed >= intent.steps_total:
                intent.status = "completed"
                intent.final_result = "Plan executed via driver fabric"


def _seed_demo_intents() -> None:
    if _INTENTS:
        return
    samples = [
        IntentRecord(
            id="int-1",
            query="Analyze project health and generate risk report",
            persona="aic",
            status="completed",
            priority="high",
            created_at=_iso(),
            steps_total=4,
            steps_completed=4,
            final_result="Report generated with 3 risk factors",
        ),
        IntentRecord(
            id="int-2",
            query="Sync all Microsoft Graph documents to local storage",
            persona="aria",
            status="executing",
            priority="normal",
            created_at=_iso(),
            steps_total=6,
            steps_completed=3,
        ),
        IntentRecord(
            id="int-3",
            query="Run security scan on backend API endpoints",
            persona="sora",
            status="planning",
            priority="critical",
            created_at=_iso(),
            steps_total=0,
            steps_completed=0,
        ),
    ]
    for record in samples:
        _INTENTS[record.id] = record


_seed_demo_intents()


@router.get("/intents", response_model=List[IntentRecord])
async def list_intents(limit: int = Query(default=20, ge=1, le=100)) -> List[IntentRecord]:
    """Return the most recent intents after advancing progress."""

    _advance_intents()
    intents = sorted(_INTENTS.values(), key=lambda rec: rec.created_at, reverse=True)
    return intents[:limit]


@router.post("/intents", response_model=IntentRecord)
async def create_intent(payload: IntentCreateRequest) -> IntentRecord:
    intent_id = f"int-{uuid.uuid4().hex[:8]}"
    record = IntentRecord(
        id=intent_id,
        query=payload.query.strip(),
        persona=payload.persona,
        status="planning",
        priority=payload.priority,
        created_at=_iso(),
        steps_total=0,
        steps_completed=0,
    )
    _INTENTS[intent_id] = record
    # prime at least one step so the UI shows progress soon
    _advance_intents()
    return record


@router.get("/intents/{intent_id}", response_model=IntentRecord)
async def get_intent(intent_id: str) -> IntentRecord:
    intent = _INTENTS.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return intent


@router.post("/intents/{intent_id}/cancel", response_model=IntentRecord)
async def cancel_intent(intent_id: str) -> IntentRecord:
    intent = _INTENTS.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    intent.status = "failed"
    intent.final_result = "Cancelled by operator"
    return intent
