"""Project, workspace, and task primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TaskState(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass
class Task:
    id: str
    title: str
    state: TaskState = TaskState.TODO
    assignee_id: Optional[str] = None
    project_id: Optional[str] = None
    priority: int = 0


@dataclass
class Workspace:
    id: str
    name: str
    project_id: Optional[str] = None
    description: str = ""


@dataclass
class Project:
    id: str
    name: str
    owner_id: str
    tasks: List[Task] = field(default_factory=list)
    workspaces: List[Workspace] = field(default_factory=list)
