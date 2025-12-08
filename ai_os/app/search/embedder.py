"""Deterministic embedding stub for the AI OS search layer."""
from __future__ import annotations

import hashlib
from typing import List


class Embedder:
    """Replace with a real embedding provider in production."""

    def __init__(self, model_name: str = "text-embedding-latest"):
        self.model_name = model_name

    def embed(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [b / 255.0 for b in digest[:64]]
