"""Runtime diagnostics endpoint for capturing client-side failures."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

router = APIRouter()

_LOG_ENV_VAR = "OSDASH_RUNTIME_LOG"
_DEFAULT_LOG_PATH = Path("logs") / "runtime_diagnostics.log"


class RuntimeDiagnostic(BaseModel):
    source: str = Field(..., description="Component or page that triggered the report")
    message: str = Field(..., description="Human-readable summary")
    stack: Optional[str] = Field(None, description="Captured stack trace when available")
    severity: str = Field("error", description="error|warning|info")
    context: Dict[str, Any] | None = Field(
        default=None,
        description="Additional diagnostic information (browser metadata, etc.)",
    )


def _resolve_log_path() -> Path:
    override = os.environ.get(_LOG_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    return _DEFAULT_LOG_PATH


def _append_event(payload: Dict[str, Any]) -> None:
    log_path = _resolve_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)
        handle.write("\n")


@router.post(
    "/runtime/diagnostics",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Record a runtime diagnostic event",
)
async def record_runtime_diagnostic(event: RuntimeDiagnostic) -> Dict[str, str]:
    payload = event.model_dump()
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    _append_event(payload)
    return {"status": "accepted"}


@router.get(
    "/runtime/diagnostics/ping",
    status_code=status.HTTP_204_NO_CONTENT,
    include_in_schema=False,
)
async def runtime_ping() -> Response:
    """Simple liveness endpoint for smoke tests."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)
