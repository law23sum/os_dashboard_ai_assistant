"""Local Excel helper stub."""
from pathlib import Path

import pandas as pd


def summarize_workbook(path: Path) -> str:
    return f"Summarized workbook at {path} with pandas {pd.__version__}"
