"""Cookbook-inspired patterns for tools, structured outputs, and file search."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .ai import get_openai_client
from .ai_layer.openai_client import OpenAIClient, _extract_output_text
from .file_tools import ToolResourceBuilder, ResponseInspector
from agents_ai import route_prompt_to_agent


PRIORITY_ORDER = ("AIC", "Sora", "Aria")


@dataclass
class ToolExample:
    """Simple tool definition with a paired example."""

    name: str
    description: str
    parameters: Dict[str, Any]
    example_prompt: str

    def to_function_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class TriageDecision(BaseModel):
    """Structured routing decision for multi-agent triage."""

    agents: List[str] = Field(..., min_items=1, max_items=3)
    rationale: str
    confidence: float = Field(..., ge=0.0, le=1.0)


def _prioritize_agents(agents: List[str]) -> List[str]:
    ordered: List[str] = []
    for name in PRIORITY_ORDER:
        if name in agents and name not in ordered:
            ordered.append(name)
    for name in agents:
        if name not in ordered:
            ordered.append(name)
    return ordered


def _limit_agents(agents: List[str], max_agents: Optional[int]) -> List[str]:
    if max_agents is None or max_agents <= 0:
        return agents
    return agents[:max_agents]


def build_tool_examples() -> Dict[str, Any]:
    """Return cookbook-inspired tool definitions with examples."""

    examples = [
        ToolExample(
            name="fetch_system_status",
            description="Get health and availability metrics for a system or plane.",
            parameters={
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "description": "Scope of the status query (e.g., control, data, runtime).",
                    },
                    "detail_level": {
                        "type": "string",
                        "enum": ["summary", "full"],
                        "description": "Level of detail to return.",
                    },
                },
                "required": ["scope"],
            },
            example_prompt="Check the control plane health with a full report.",
        ),
        ToolExample(
            name="create_task",
            description="Create a new task in the project tracker.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short task title."},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority.",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "ISO date for the due date.",
                    },
                },
                "required": ["title"],
            },
            example_prompt="Create a high priority task to validate the new agent routing.",
        ),
        ToolExample(
            name="search_documents",
            description="Search indexed documents for a query string.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "description": "Max results to return.",
                    },
                },
                "required": ["query"],
            },
            example_prompt="Find references to streaming in the architecture docs.",
        ),
    ]

    return {
        "tools": [example.to_function_tool() for example in examples],
        "examples": [
            {
                "prompt": example.example_prompt,
                "tool_name": example.name,
            }
            for example in examples
        ],
        "openapi_hint": (
            "Use OpenAPI schemas to chain related tool calls (e.g., "
            "resolve dependencies before execution)."
        ),
    }


def _coerce_json(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    if not text:
        return None, "empty response"
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1]), None
            except json.JSONDecodeError as exc:
                return None, str(exc)
        return None, "no json object found"


async def structured_triage(
    prompt: str,
    *,
    max_agents: Optional[int] = None,
    model: Optional[str] = None,
) -> TriageDecision:
    """Use Responses API structured outputs to pick routing agents."""

    instructions = (
        "You are a routing assistant for multi-agent roles.\n"
        "Pick the best agent(s) for the user prompt using these roles:\n"
        "- AIC: execution, systems integration, architecture, applied science.\n"
        "- Sora: formal structure, proofs, evidence, modeling, governance.\n"
        "- Aria: meaning, value, philosophy, theology, canon.\n"
        "Order agents by priority AIC, then Sora, then Aria when multiple apply.\n"
        "Avoid redundancy: prefer one agent unless multiple domains are clearly required.\n"
        "Return JSON that matches the provided schema."
    )

    schema = {
        "name": "triage_decision",
        "schema": TriageDecision.model_json_schema(),
    }

    client = OpenAIClient()
    await client.initialize()
    response_text = ""

    try:
        response = await client.client.responses.create(
            model=model or client.config.openai_model,
            instructions=instructions,
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            response_format={"type": "json_schema", "json_schema": schema},
            max_output_tokens=400,
            store=False,
        )
        response_text = _extract_output_text(response)
    except Exception:
        response = await client.client.responses.create(
            model=model or client.config.openai_model,
            instructions=instructions,
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            max_output_tokens=400,
            store=False,
        )
        response_text = _extract_output_text(response)

    data, error = _coerce_json(response_text)
    if not data:
        raise ValueError(f"Unable to parse structured output: {error or 'unknown error'}")

    decision = TriageDecision.model_validate(data)
    decision.agents = _limit_agents(_prioritize_agents(decision.agents), max_agents)
    return decision


def heuristic_triage(prompt: str, max_agents: Optional[int] = None) -> TriageDecision:
    """Keyword-based routing as a fallback or lightweight option."""

    agents = route_prompt_to_agent(prompt, {"AIC": None, "Aria": None, "Sora": None})
    ordered = _limit_agents(_prioritize_agents(agents), max_agents)
    return TriageDecision(
        agents=ordered,
        rationale="Keyword routing fallback.",
        confidence=0.4 if agents else 0.2,
    )


async def file_search_response(
    query: str,
    *,
    vector_store_ids: List[str],
    max_num_results: Optional[int] = None,
    ranking_options: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a file_search tool call and return formatted results."""

    if not vector_store_ids:
        raise ValueError("vector_store_ids is required for file search")

    client = OpenAIClient()
    await client.initialize()

    tool_config = ToolResourceBuilder.build_file_search_resources(
        vector_store_ids=vector_store_ids,
        max_num_results=max_num_results,
        ranking_options=ranking_options,
    )
    if not tool_config:
        raise ValueError("Failed to build file_search tool configuration")

    response = await client.client.responses.create(
        model=model or client.config.openai_model,
        input=[{"role": "user", "content": [{"type": "input_text", "text": query}]}],
        tools=[tool_config],
        max_output_tokens=500,
        store=False,
    )

    response_text = _extract_output_text(response)
    inspector = ResponseInspector(get_openai_client())
    results = inspector.extract_file_search_results(response)

    return {
        "response": response_text,
        "results": results,
        "tool_calls": inspector.inspect_response_tool_calls(response),
    }
