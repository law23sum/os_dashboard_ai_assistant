"""Route user intents to appropriate actions and agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Literal
import re


@dataclass
class Intent:
    """Represents a user intent for routing to agents and workflows."""
    kind: Literal["plan", "summarize", "refactor", "report", "clean", "analyze", "draft", "create_task"]
    target: Optional[str] = None  # Optional target identifier (project name, file path, etc.)
    context: Optional[str] = None  # Additional context for the intent


class Router:
    """Routes user intents to appropriate agents and workflows."""

    def __init__(self):
        self.intent_patterns: Dict[str, List[re.Pattern]] = {
            "onenote_clean": [
                re.compile(r"clean.*onenote", re.IGNORECASE),
                re.compile(r"cleanup.*note", re.IGNORECASE),
                re.compile(r"organize.*notebook", re.IGNORECASE),
            ],
            "onenote_summarize": [
                re.compile(r"summarize.*onenote", re.IGNORECASE),
                re.compile(r"summarize.*page", re.IGNORECASE),
                re.compile(r"summary.*note", re.IGNORECASE),
            ],
            "excel_analyze": [
                re.compile(r"analyze.*excel", re.IGNORECASE),
                re.compile(r"analyze.*spreadsheet", re.IGNORECASE),
                re.compile(r"summarize.*sheet", re.IGNORECASE),
            ],
            "word_draft": [
                re.compile(r"draft.*document", re.IGNORECASE),
                re.compile(r"write.*word", re.IGNORECASE),
                re.compile(r"create.*document", re.IGNORECASE),
            ],
            "project_plan": [
                re.compile(r"plan.*project", re.IGNORECASE),
                re.compile(r"create.*project", re.IGNORECASE),
                re.compile(r"roadmap", re.IGNORECASE),
            ],
            "task_create": [
                re.compile(r"create.*task", re.IGNORECASE),
                re.compile(r"add.*task", re.IGNORECASE),
                re.compile(r"new.*todo", re.IGNORECASE),
            ],
        }

        self.agent_mapping: Dict[str, str] = {
            "onenote_clean": "AIC",
            "onenote_summarize": "AIC",
            "excel_analyze": "AIC",
            "word_draft": "Aria",
            "project_plan": "Sora",
            "task_create": "Aria",
        }

    def route(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Route user input to an intent and suggest an agent."""
        user_input_lower = user_input.lower()

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern.search(user_input_lower):
                    agent = self.agent_mapping.get(intent, "AIC")
                    return {
                        "intent": intent,
                        "agent": agent,
                        "input": user_input,
                    }

        return None


def route_user_intent(user_input: str) -> Optional[Dict[str, Any]]:
    """Convenience function to route user intent."""
    router = Router()
    return router.route(user_input)


def parse_intent_from_routing(result: Optional[Dict[str, Any]]) -> Optional[Intent]:
    """Convert routing result to an Intent dataclass."""
    if not result:
        return None
    
    intent_map = {
        "project_plan": "plan",
        "onenote_summarize": "summarize",
        "onenote_clean": "clean",
        "excel_analyze": "analyze",
        "word_draft": "draft",
        "task_create": "create_task",
    }
    
    intent_kind = intent_map.get(result.get("intent", ""), "report")
    return Intent(
        kind=intent_kind,
        context=result.get("input"),
    )


def route_intent(project, intent: Intent) -> str:
    """Route an intent to the appropriate agent handler.
    
    Args:
        project: A Project instance
        intent: An Intent dataclass
        
    Returns:
        The agent's response as a string
    """
    from ..ai_layer.agents import aic, sora, aria
    from ..db import Project as DBProject
    
    # Convert db.Project to the format expected by agents if needed
    if isinstance(project, DBProject):
        # Agents expect Project with name, description, status
        project_obj = project
    else:
        project_obj = project
    
    if intent.kind == "plan":
        return sora.handle_planning(project_obj, intent)
    elif intent.kind == "report":
        return aic.handle_report(project_obj, intent)
    elif intent.kind in {"summarize", "refactor", "clean", "draft"}:
        return aria.handle_narrative(project_obj, intent)
    elif intent.kind == "analyze":
        return aic.handle_report(project_obj, intent)  # Analysis is similar to report
    elif intent.kind == "create_task":
        return sora.handle_planning(project_obj, intent)  # Task creation is planning
    else:
        return f"Unknown intent kind: {intent.kind}"

