"""Event sinks for the unified event journal."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .models import Event


class EventSink:
    def write(self, event: Event) -> None:
        raise NotImplementedError


class LocalAppendOnlySink(EventSink):
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _journal_path(self, agent_id: Optional[str]) -> Path:
        safe_agent = (agent_id or "os_dashboard").strip() or "os_dashboard"
        safe_agent = "".join(c if c.isalnum() or c in "-_." else "_" for c in safe_agent)
        return self.base_dir / f"{safe_agent}.jsonl"

    def write(self, event: Event) -> None:
        path = self._journal_path(event.agent_id)
        payload = event.to_dict()
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


class HubSink(EventSink):
    def __init__(self, hub) -> None:
        self.hub = hub

    def write(self, event: Event) -> None:
        self.hub.ingest(event)


def default_journal_dir() -> Path:
    env_path = os.getenv("OSDASH_AGENT_JOURNAL_DIR") or os.getenv("ASSISTANT_HUB_AGENT_JOURNAL_DIR")
    if env_path:
        return Path(env_path).expanduser()
    from assistant_hub.config import DATA_DIR

    return Path(DATA_DIR) / "event_hub" / "journals"

