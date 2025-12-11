"""Data plane primitives.

The data plane is responsible for storage, indexing, and retrieval of
CIR, project ledger events, capsule artifacts, and observability data.
Concrete implementations should subclass :class:`DataPlane` and implement
these façade methods.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Protocol


class DataBackend(Protocol):
    """Protocol for low-level data backends (DB, search, object store)."""

    def put(self, collection: str, key: str, value: Dict[str, Any]) -> None:
        ...

    def get(self, collection: str, key: str) -> Dict[str, Any] | None:
        ...

    def query(self, collection: str, **filters: Any) -> Iterable[Dict[str, Any]]:
        ...


@dataclass
class DataPlane:
    """Abstract data-plane façade used by higher-level components."""

    backend: DataBackend

    def put_document(self, key: str, doc: Dict[str, Any]) -> None:
        self.backend.put("documents", key, doc)

    def get_document(self, key: str) -> Dict[str, Any] | None:
        return self.backend.get("documents", key)

    def record_event(self, event: Dict[str, Any]) -> None:
        self.backend.put("events", event.get("id", ""), event)

    def query_events(self, **filters: Any) -> Iterable[Dict[str, Any]]:
        return self.backend.query("events", **filters)
