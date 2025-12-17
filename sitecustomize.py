"""Ensure local sources are importable without setting PYTHONPATH.

When Python starts it imports ``sitecustomize`` if present on the path.
By inserting the repository ``src`` directory ahead of other entries,
the ``assistant_hub`` package can be resolved when running console
scripts like ``osdash`` directly from a checkout.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
