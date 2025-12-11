"""Shared helpers for project snapshots across Tk and React."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Sequence

from assistant_hub.db import Project


def _serialize(project: Project) -> Dict[str, str]:
    return {
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "priority": project.priority,
        "order_num": project.order_num,
    }


@dataclass
class ProjectWorkspaceSnapshot:
    projects: List[Dict[str, str]]
    status_counts: Dict[str, int]
    priority_counts: Dict[str, int]
    generated_at: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "projects": self.projects,
            "status_counts": self.status_counts,
            "priority_counts": self.priority_counts,
            "generated_at": self.generated_at,
        }


def build_project_snapshot(projects: Sequence[Project]) -> ProjectWorkspaceSnapshot:
    status_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {}
    serialized = []
    for project in projects:
        status_counts[project.status] = status_counts.get(project.status, 0) + 1
        priority_counts[project.priority] = priority_counts.get(project.priority, 0) + 1
        serialized.append(_serialize(project))
    return ProjectWorkspaceSnapshot(
        projects=serialized,
        status_counts=status_counts,
        priority_counts=priority_counts,
        generated_at=datetime.now().isoformat(timespec="seconds"),
    )
