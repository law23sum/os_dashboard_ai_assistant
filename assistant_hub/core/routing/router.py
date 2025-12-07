"""Route requests to specific agents."""
from __future__ import annotations

from typing import Dict, Protocol


class Agent(Protocol):
    name: str

    def handle(self, message: str) -> str:
        ...


class AgentRouter:
    def __init__(self) -> None:
        self.agents: Dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self.agents[agent.name] = agent

    def route(self, target: str, message: str) -> str:
        agent = self.agents.get(target)
        if not agent:
            return f"No agent registered for {target}."
        return agent.handle(message)
