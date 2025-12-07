"""Lightweight domain models for projects and tasks."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Task:
    title: str
    project: str = "default"
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: Optional[str] = None
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Project:
    name: str
    description: str = ""


@dataclass
class AssistantState:
    tasks: List[Task] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)

    def find_project(self, name: str) -> Optional[Project]:
        return next((p for p in self.projects if p.name == name), None)
