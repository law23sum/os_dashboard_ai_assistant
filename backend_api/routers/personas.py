"""Persona management endpoints for dashboard parity."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from assistant_hub_gui.assistant_hub.db import (
    PERSONAS,
    PERSONA_ROLES,
    load_state,
    save_active_persona,
)
from backend_api.db import db_session


router = APIRouter()


class PersonaInfo(BaseModel):
    name: str
    role: str


class PersonasResponse(BaseModel):
    personas: List[PersonaInfo]
    active: str


class PersonaUpdate(BaseModel):
    persona: str


def _build_payload(active_persona: str) -> PersonasResponse:
    """Return the canonical payload for persona state."""

    personas = [
        PersonaInfo(name=persona, role=PERSONA_ROLES.get(persona, ""))
        for persona in PERSONAS
    ]
    return PersonasResponse(personas=personas, active=active_persona)


@router.get("/", response_model=PersonasResponse)
async def list_personas() -> PersonasResponse:
    """Return the available personas + the currently active persona."""

    with db_session() as conn:
        state = load_state(conn)
        active = state.active_persona
    return _build_payload(active)


@router.post("/", response_model=PersonasResponse)
async def set_active_persona(payload: PersonaUpdate) -> PersonasResponse:
    """Update the active persona to emulate the Tkinter combo box."""

    persona = payload.persona.strip()
    if persona not in PERSONAS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid persona. Must be one of {PERSONAS}",
        )

    with db_session() as conn:
        state = load_state(conn)
        state.active_persona = persona
        save_active_persona(conn, state)

    return _build_payload(persona)
