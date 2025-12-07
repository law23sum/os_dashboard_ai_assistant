"""Shared configuration helpers for the OS Dashboard assistant scaffold."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
STATE_FILE = DATA_DIR / "state.json"


@dataclass
class OpenAIConfig:
    api_key: Optional[str] = None
    model: str = "gpt-4.1"
    temperature: float = 0.2


@dataclass
class GraphConfig:
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scopes: tuple[str, ...] = ("User.Read",)


@dataclass
class AppConfig:
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    graph: GraphConfig = field(default_factory=GraphConfig)
    data_dir: Path = DATA_DIR
    state_file: Path = STATE_FILE
    extra: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Instantiate config from environment variables with safe defaults."""
        import os

        openai_cfg = OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OSDASH_MODEL", "gpt-4.1"),
            temperature=float(os.getenv("OSDASH_TEMPERATURE", 0.2)),
        )
        graph_cfg = GraphConfig(
            tenant_id=os.getenv("GRAPH_TENANT_ID"),
            client_id=os.getenv("GRAPH_CLIENT_ID"),
            client_secret=os.getenv("GRAPH_CLIENT_SECRET"),
        )
        extra = {k: v for k, v in os.environ.items() if k.startswith("OSDASH_")}
        return cls(openai=openai_cfg, graph=graph_cfg, extra=extra)
