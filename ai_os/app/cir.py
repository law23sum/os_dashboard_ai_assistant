"""Canonical Internal Representation (CIR) schema for the AI OS layer.

This schema aims to be minimal-but-expressive so that connectors can map
heterogeneous sources into a shared structure that supports search,
reasoning, and controlled write-back.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
import uuid

from pydantic import BaseModel, Field


ContentType = Literal[
    "note",
    "document",
    "spreadsheet",
    "presentation",
    "pdf",
    "table",
    "section",
    "slide",
    "paragraph",
    "list",
    "image",
]


class Provenance(BaseModel):
    source_system: str
    source_id: str
    source_path: Optional[str] = None
    version_hint: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class Annotation(BaseModel):
    author: str
    kind: Literal["comment", "highlight", "redline", "suggestion"]
    text: str
    anchor: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EmbeddingRef(BaseModel):
    model: str
    vector_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CIRNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ContentType
    title: Optional[str] = None
    text: Optional[str] = None

    children: List["CIRNode"] = Field(default_factory=list)
    table: Optional[List[List[str]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    annotations: List[Annotation] = Field(default_factory=list)
    provenance: List[Provenance] = Field(default_factory=list)
    embedding: Optional[EmbeddingRef] = None

    def walk(self) -> List["CIRNode"]:
        nodes = [self]
        for child in self.children:
            nodes.extend(child.walk())
        return nodes


class CIRDocument(BaseModel):
    root: CIRNode
    doc_type: Literal[
        "note",
        "word",
        "onenote",
        "pdf",
        "ppt",
        "excel",
        "generic",
    ] = "generic"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
