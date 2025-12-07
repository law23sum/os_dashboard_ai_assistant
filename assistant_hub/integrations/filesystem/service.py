"""Filesystem service stub."""
from pathlib import Path
from typing import List


def list_files(root: str) -> List[str]:
    return [str(p) for p in Path(root).glob("**/*") if p.is_file()]
