"""In-memory hybrid-ish vector index for the AI OS."""
from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Tuple

from ai_os.app.cir import CIRDocument, EmbeddingRef
from ai_os.app.search.embedder import Embedder


class InMemoryVectorIndex:
    def __init__(self, embedder: Optional[Embedder] = None):
        self.embedder = embedder or Embedder()
        self.vectors: Dict[str, List[float]] = {}
        self.payloads: Dict[str, Dict] = {}

    def upsert_document(self, cir: CIRDocument, payload: Dict):
        for node in cir.root.walk():
            text = node.text or ""
            if not text.strip():
                continue
            vector = self.embedder.embed(text)
            vector_id = str(uuid.uuid4())
            self.vectors[vector_id] = vector
            self.payloads[vector_id] = {
                **payload,
                "node_id": node.id,
                "node_type": node.type,
                "node_title": node.title,
                "text_snippet": text[:240],
            }
            node.embedding = EmbeddingRef(
                model=self.embedder.model_name,
                vector_id=vector_id,
            )

    def _cosine(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = (sum(x * x for x in a) ** 0.5) or 1.0
        norm_b = (sum(y * y for y in b) ** 0.5) or 1.0
        return dot / (norm_a * norm_b)

    def search(self, query: str, limit: int = 10) -> List[Tuple[float, Dict]]:
        query_vector = self.embedder.embed(query)
        scored = [
            (self._cosine(query_vector, vector), payload)
            for vector, payload in zip(self.vectors.values(), self.payloads.values())
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[:limit]
