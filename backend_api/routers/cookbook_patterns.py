"""
Cookbook patterns router.

Exposes tool examples, structured triage, file search, and guardrails.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from assistant_core.cookbook_patterns import (
    build_tool_examples,
    file_search_response,
    heuristic_triage,
    structured_triage,
)
from assistant_core.guardrails import GuardrailConfig, evaluate_guardrails

router = APIRouter()


class ToolExamplesResponse(BaseModel):
    tools: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    openapi_hint: str


class TriageRequest(BaseModel):
    prompt: str = Field(..., description="User prompt to route.")
    mode: str = Field("auto", description="Routing mode: auto, heuristic, or llm.")
    max_agents: Optional[int] = Field(None, description="Limit number of agents returned.")
    model: Optional[str] = Field(None, description="Override model for LLM triage.")


class TriageResponse(BaseModel):
    agents: List[str]
    rationale: str
    confidence: float
    mode: str


class GuardrailsRequest(BaseModel):
    response_text: str = Field(..., description="Response text to validate.")
    blocked_phrases: Optional[List[str]] = Field(None, description="Override blocked phrases list.")
    max_response_chars: Optional[int] = Field(None, description="Maximum allowed characters.")
    require_safe_language: bool = Field(True, description="Enable basic safety checks.")


class GuardrailsResponse(BaseModel):
    allowed: bool
    score: float
    violations: List[Dict[str, str]]
    notes: List[str]


class FileSearchRequest(BaseModel):
    query: str = Field(..., description="Search query.")
    vector_store_ids: List[str] = Field(..., description="Vector store IDs for file_search.")
    max_num_results: Optional[int] = Field(None, description="Max chunks to return.")
    ranking_options: Optional[Dict[str, Any]] = Field(None, description="Ranking options for file_search.")
    model: Optional[str] = Field(None, description="Model override.")


class FileSearchResponse(BaseModel):
    response: str
    results: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]


@router.get("/tool-examples", response_model=ToolExamplesResponse)
async def get_tool_examples():
    """Return cookbook-inspired tool definitions and example prompts."""
    payload = build_tool_examples()
    return ToolExamplesResponse(**payload)


@router.post("/triage", response_model=TriageResponse)
async def triage_prompt(request: TriageRequest):
    """Route a prompt to the appropriate agent(s)."""
    max_agents = request.max_agents
    if max_agents is None:
        max_env = os.getenv("AGENTS_MAX_RESPONDERS")
        if max_env and max_env.isdigit():
            max_agents = int(max_env)

    mode = request.mode.lower().strip()
    if mode == "auto":
        mode = os.getenv("ASSISTANT_HUB_ROUTING_MODE", "heuristic").lower().strip()

    if mode == "llm":
        try:
            decision = await structured_triage(
                request.prompt,
                max_agents=max_agents,
                model=request.model,
            )
            return TriageResponse(
                agents=decision.agents,
                rationale=decision.rationale,
                confidence=decision.confidence,
                mode="llm",
            )
        except Exception:
            decision = heuristic_triage(request.prompt, max_agents=max_agents)
            return TriageResponse(
                agents=decision.agents,
                rationale=decision.rationale,
                confidence=decision.confidence,
                mode="heuristic",
            )

    decision = heuristic_triage(request.prompt, max_agents=max_agents)
    return TriageResponse(
        agents=decision.agents,
        rationale=decision.rationale,
        confidence=decision.confidence,
        mode="heuristic",
    )


@router.post("/guardrails", response_model=GuardrailsResponse)
async def guardrails_check(request: GuardrailsRequest):
    """Validate response text against lightweight guardrails."""
    config = GuardrailConfig(
        blocked_phrases=request.blocked_phrases or GuardrailConfig().blocked_phrases,
        max_response_chars=request.max_response_chars,
        require_safe_language=request.require_safe_language,
    )
    result = evaluate_guardrails(request.response_text, config)
    return GuardrailsResponse(
        allowed=result.allowed,
        score=result.score,
        violations=[{"rule": v.rule, "detail": v.detail} for v in result.violations],
        notes=result.notes,
    )


@router.post("/file-search", response_model=FileSearchResponse)
async def file_search(request: FileSearchRequest):
    """Run a file_search tool call against a vector store."""
    try:
        payload = await file_search_response(
            request.query,
            vector_store_ids=request.vector_store_ids,
            max_num_results=request.max_num_results,
            ranking_options=request.ranking_options,
            model=request.model,
        )
        return FileSearchResponse(**payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"File search failed: {exc}")
