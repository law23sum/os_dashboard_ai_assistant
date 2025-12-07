"""Connector protocol and shared helpers for the AI OS layer."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from ai_os.app.cir import CIRDocument, CIRNode, Provenance


@dataclass
class ResourceRef:
    id: str
    name: str
    path: Optional[str] = None
    kind: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Connector(Protocol):
    system_name: str

    def list_resources(self, folder: Optional[str] = None) -> List[ResourceRef]:
        ...

    def get_metadata(self, resource_id: str) -> Dict[str, Any]:
        ...

    def read(self, resource_id: str) -> CIRDocument:
        ...

    def write(
        self,
        resource_id: str,
        cir: CIRDocument,
        operations: Optional[Dict[str, Any]] = None,
    ) -> ResourceRef:
        ...

    def search(self, query: str, limit: int = 10) -> List[ResourceRef]:
        ...

    def diff(self, before: CIRDocument, after: CIRDocument) -> Dict[str, Any]:
        ...


class StorageBackedConnector:
    """Lightweight connector implementation backed by a storage adapter."""

    system_name: str = "generic"
    node_type: str = "document"
    doc_type: str = "generic"

    def __init__(self, storage):
        self.storage = storage

    def list_resources(self, folder: Optional[str] = None) -> List[ResourceRef]:
        items = self.storage.list(folder=folder)
        return [
            ResourceRef(
                id=item["id"],
                name=item.get("title") or item.get("name") or item["id"],
                path=item.get("path"),
                kind=self.node_type,
                metadata=item,
            )
            for item in items
        ]

    def get_metadata(self, resource_id: str) -> Dict[str, Any]:
        return self.storage.meta(resource_id)

    def read(self, resource_id: str) -> CIRDocument:
        record = self.storage.get(resource_id)
        root = CIRNode(
            type=self.node_type,  # type: ignore[arg-type]
            title=record.get("title") or record.get("name"),
            text=record.get("text", ""),
            table=record.get("table"),
            provenance=[
                Provenance(
                    source_system=self.system_name,
                    source_id=resource_id,
                    source_path=record.get("path"),
                )
            ],
            metadata=record.get("metadata", {}),
        )
        return CIRDocument(root=root, doc_type=self.doc_type)

    def write(
        self, resource_id: str, cir: CIRDocument, operations: Optional[Dict[str, Any]] = None
    ) -> ResourceRef:
        data = {
            "title": cir.root.title or "Untitled",
            "text": cir.root.text or "",
            "table": cir.root.table,
            "metadata": cir.root.metadata,
        }
        saved = self.storage.upsert(resource_id, **data)
        return ResourceRef(
            id=saved["id"],
            name=saved.get("title") or saved.get("name") or saved["id"],
            path=saved.get("path"),
            kind=self.node_type,
            metadata=saved,
        )

    def search(self, query: str, limit: int = 10) -> List[ResourceRef]:
        results = self.storage.search(query, limit=limit)
        return [
            ResourceRef(
                id=item["id"],
                name=item.get("title") or item.get("name") or item["id"],
                path=item.get("path"),
                kind=self.node_type,
                metadata=item,
            )
            for item in results
        ]

    def diff(self, before: CIRDocument, after: CIRDocument) -> Dict[str, Any]:
        return {
            "system": self.system_name,
            "before_title": before.root.title,
            "after_title": after.root.title,
            "before_text_len": len(before.root.text or ""),
            "after_text_len": len(after.root.text or ""),
        }
