"""Local Excel utilities using pandas/openpyxl when available."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pd = None  # type: ignore


class LocalExcelError(RuntimeError):
    """Raised when local Excel operations cannot be performed."""


def require_pandas() -> None:
    if pd is None:
        raise LocalExcelError("pandas is required for local Excel operations. Install pandas and openpyxl.")


def load_sheet(path: str | Path, sheet_name: Optional[str] = None):
    """Load an Excel sheet into a pandas DataFrame."""

    require_pandas()
    return pd.read_excel(Path(path), sheet_name=sheet_name)


def write_sheet(path: str | Path, sheet_name: str, df) -> None:
    """Write a DataFrame back to a sheet, replacing existing content."""

    require_pandas()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
