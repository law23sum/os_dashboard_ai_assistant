"""Local Excel helpers using pandas/openpyxl."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import csv

try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None  # type: ignore


def _require_pandas() -> None:
    if pd is None:  # pragma: no cover - optional dependency
        raise ModuleNotFoundError(
            "pandas is required for Excel integrations. "
            "Install optional dependencies with `python3 -m pip install -r requirements.txt`."
        )


def load_sheet(path: str, sheet_name: str) -> pd.DataFrame:
    """Load a sheet from an Excel file using pandas."""
    _require_pandas()
    return pd.read_excel(path, sheet_name=sheet_name)


def save_sheet(path: str, sheet_name: str, df: pd.DataFrame) -> None:
    """Save a DataFrame to an Excel file."""
    _require_pandas()
    dest = Path(path)
    mode = "a" if dest.exists() else "w"
    with pd.ExcelWriter(
        dest, engine="openpyxl", mode=mode, if_sheet_exists="replace"
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


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
        summary_path.write_text(
            f"Instruction: {instruction}\n\n{summary}\n", encoding="utf-8"
        )
        return summary_path

    def export_table(self, sheet_name: str, rows: List[List[str]]) -> Path:
        export_path = self.path.with_suffix(f".{sheet_name}.csv")
        with export_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        return export_path
