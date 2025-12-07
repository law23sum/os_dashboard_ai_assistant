"""Simple JSON-backed state storage."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from assistant_hub.core.models import AssistantState, Project, Task


class JSONStateStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> AssistantState:
        if not self.path.exists():
            return AssistantState()
        data = json.loads(self.path.read_text())
        projects = [Project(**p) for p in data.get("projects", [])]
        tasks = [Task(**t) for t in data.get("tasks", [])]
        return AssistantState(tasks=tasks, projects=projects)

    def save(self, state: AssistantState) -> None:
        payload: dict[str, Any] = {
            "projects": [p.__dict__ for p in state.projects],
            "tasks": [t.__dict__ for t in state.tasks],
        }
        self.path.write_text(json.dumps(payload, indent=2))
