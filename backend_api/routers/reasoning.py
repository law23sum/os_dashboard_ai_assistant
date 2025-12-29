"""Reasoning / TRF router mirrored from the Tkinter cognitive panel."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from assistant_core.cognitive_framework import (
        CognitiveFrameworkManager,
        PersonaType,
        ReasoningTrace,
    )
except ImportError:  # pragma: no cover - optional dep
    CognitiveFrameworkManager = None  # type: ignore
    PersonaType = None  # type: ignore

router = APIRouter()

_manager: Optional[CognitiveFrameworkManager] = None
_manager_lock = asyncio.Lock()


class ReasoningQuery(BaseModel):
    """Request payload for executing a TRF reasoning query."""

    query: str = Field(..., min_length=3, max_length=2000)
    persona: Optional[str] = Field(
        default="aic", pattern="^[a-zA-Z_]+$", description="Persona slug (e.g., aic, chris)"
    )


class ReasoningPersonaResponse(BaseModel):
    id: str
    type: str
    label: str
    decision_threshold: float
    interaction_style: str
    capabilities: List[str]
    active: bool


async def _get_manager() -> CognitiveFrameworkManager:
    if CognitiveFrameworkManager is None:  # pragma: no cover - optional dependency
        raise HTTPException(
            status_code=503,
            detail="Cognitive framework not available. Install assistant_core.",
        )
    global _manager  # pylint: disable=global-statement
    async with _manager_lock:
        if _manager is None:
            _manager = CognitiveFrameworkManager()
        if not _manager.initialized:
            await _manager.initialize()
    return _manager


def _serialize_trace(trace: ReasoningTrace, persona_label: Optional[str] = None) -> Dict[str, Any]:
    return {
        "id": trace.id,
        "query": trace.query,
        "persona_id": trace.persona_id,
        "persona_label": persona_label,
        "created_at": trace.created_at.isoformat(),
        "final_conclusion": trace.final_conclusion,
        "overall_confidence": trace.overall_confidence,
        "steps": [
            {
                "id": step.id,
                "operator": step.operator.value,
                "premises": step.premises,
                "conclusion": step.conclusion,
                "confidence": step.confidence,
                "evidence": step.evidence,
                "timestamp": step.timestamp.isoformat(),
            }
            for step in trace.steps
        ],
    }


def _label_for_persona(manager: CognitiveFrameworkManager, persona_id: Optional[str]) -> Optional[str]:
    if not persona_id:
        return None
    persona = manager.personas.get(persona_id)
    if not persona:
        return None
    return persona.persona_type.name


def _persona_enum(persona_slug: Optional[str]) -> PersonaType:
    if PersonaType is None:  # pragma: no cover
        raise HTTPException(status_code=503, detail="Cognitive personas unavailable")
    slug = (persona_slug or "aic").strip().lower()
    for member in PersonaType:
        if member.value == slug or member.name.lower() == slug:
            return member
    raise HTTPException(status_code=400, detail=f"Unknown persona '{persona_slug}'")


@router.get("/personas", response_model=List[ReasoningPersonaResponse])
async def list_reasoning_personas():
    """Return cognitive personas available for TRF reasoning."""
    manager = await _get_manager()
    personas: List[ReasoningPersonaResponse] = []
    for persona in manager.personas.values():
        strategy = persona.strategy
        personas.append(
            ReasoningPersonaResponse(
                id=persona.id,
                type=persona.persona_type.value,
                label=persona.persona_type.name,
                decision_threshold=strategy.decision_threshold if strategy else 0.0,
                interaction_style=strategy.interaction_style if strategy else "",
                capabilities=[cap.value for cap in (strategy.capabilities if strategy else [])],
                active=persona.active,
            )
        )
    return personas


@router.get("/history")
async def list_reasoning_history(limit: int = Query(10, ge=1, le=50)):
    """Return the most recent reasoning traces."""
    manager = await _get_manager()
    traces = list(manager.reasoning_framework.reasoning_traces.values())
    traces.sort(key=lambda trace: trace.created_at, reverse=True)
    payload: List[Dict[str, Any]] = []
    for trace in traces[:limit]:
        payload.append(_serialize_trace(trace, _label_for_persona(manager, trace.persona_id)))
    return payload


@router.post("/query")
async def run_reasoning_query(payload: ReasoningQuery):
    """Execute a TRF reasoning query similar to the Tkinter reasoning console."""
    manager = await _get_manager()
    persona_type = _persona_enum(payload.persona)
    trace = await manager.reason_about(payload.query.strip(), persona_type)
    return _serialize_trace(trace, _label_for_persona(manager, trace.persona_id))
