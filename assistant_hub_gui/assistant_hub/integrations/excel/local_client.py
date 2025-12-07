"""Local Excel helpers using pandas/openpyxl."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def load_sheet(path: str, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name)


def save_sheet(path: str, sheet_name: str, df: pd.DataFrame) -> None:
    dest = Path(path)
    mode = "a" if dest.exists() else "w"
    with pd.ExcelWriter(dest, engine="openpyxl", mode=mode, if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
