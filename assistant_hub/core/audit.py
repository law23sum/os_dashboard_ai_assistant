"""Audit logging helpers to give the scaffold traceability."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from assistant_hub.versioning.git_manager import GitManager


@dataclass
class AuditEntry:
    action: str
    description: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    commit_status: Optional[dict[str, str]] = None


class AuditLogger:
    """Write append-only audit records and optionally commit outputs."""

    def __init__(self, log_path: Path, git_manager: GitManager | None = None):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.git_manager = git_manager

    def record(
        self,
        action: str,
        description: str,
        metadata: Optional[dict[str, Any]] = None,
        commit_paths: Iterable[str] | None = None,
    ) -> AuditEntry:
        entry = AuditEntry(action=action, description=description, metadata=metadata or {})
        commit_result = self._maybe_commit(action, commit_paths)
        if commit_result:
            entry.commit_status = commit_result
        self._append(entry)
        return entry

    def _append(self, entry: AuditEntry) -> None:
        with self.log_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(entry.__dict__) + "\n")

    def _maybe_commit(self, message: str, paths: Iterable[str] | None) -> Optional[dict[str, str]]:
        if not self.git_manager or paths is None:
            return None
        if not self.git_manager.is_repo:
            return {"status": "skipped", "reason": "not a git repository"}
        try:
            self.git_manager.add_and_commit(message, paths)
            return {"status": "committed"}
        except Exception as exc:  # pragma: no cover - defensive guard
            return {"status": "failed", "reason": str(exc)}
