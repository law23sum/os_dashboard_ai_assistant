"""Local Excel helpers (non-Graph)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import csv


class LocalWorkbook:
    """Represents a workbook stored on disk.

    This is intentionally lightweight and does not attempt to parse XLSX files
    directly. Instead, it provides convenience helpers for storing summaries or
    extracted tables alongside the workbook path so higher layers can plug in
    richer tooling (pandas/openpyxl) later.
    """

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def describe(self) -> Dict[str, str]:
        return {
            "path": str(self.path),
            "exists": str(self.path.exists()),
        }

    def write_summary(self, instruction: str, summary: str) -> Path:
        summary_path = self.path.with_suffix(self.path.suffix + ".summary.txt")
        summary_path.write_text(f"Instruction: {instruction}\n\n{summary}\n", encoding="utf-8")
        return summary_path

    def export_table(self, sheet_name: str, rows: List[List[str]]) -> Path:
        export_path = self.path.with_suffix(f".{sheet_name}.csv")
        with export_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        return export_path
