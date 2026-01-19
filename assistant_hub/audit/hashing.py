"""Canonical serialization and hashing helpers for audit events."""

from __future__ import annotations

import dataclasses
import json
from hashlib import sha256
from typing import Any, Dict


def _to_primitive(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _to_primitive(dataclasses.asdict(value))
    if hasattr(value, "model_dump"):
        return _to_primitive(value.model_dump())
    if hasattr(value, "dict"):
        return _to_primitive(value.dict())
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_primitive(item) for item in value]
    return value


def canonical_json(payload: Dict[str, Any]) -> str:
    primitive = _to_primitive(payload)
    return json.dumps(primitive, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_event_hash(payload: Dict[str, Any]) -> str:
    encoded = canonical_json(payload).encode("utf-8")
    return sha256(encoded).hexdigest()


def event_hash_payload(event_dict: Dict[str, Any]) -> Dict[str, Any]:
    hash_payload = dict(event_dict)
    hash_payload.pop("event_hash", None)
    hash_payload.pop("prev_event_hash", None)
    return hash_payload
