"""Change grouping and diff payload builder."""
from __future__ import annotations

from typing import Any, Dict

from ai_os.app.cir import CIRDocument


class ChangeEngine:
    def build_write_payload(
        self, before: CIRDocument, after: CIRDocument
    ) -> Dict[str, Any]:
        return {
            "before_title": before.root.title,
            "after_title": after.root.title,
            "before_len": len(before.root.text or ""),
            "after_len": len(after.root.text or ""),
        }
