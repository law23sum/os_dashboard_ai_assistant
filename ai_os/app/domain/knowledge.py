"""Knowledge-level entities such as CIR documents and capsule references."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CIRDocument:
    """Canonical Internal Representation (CIR) document wrapper."""

    id: str
    title: str
    blocks: List[Dict]
    metadata: Dict[str, str]


@dataclass
class CapsuleRef:
    """Reference to a registered capsule in the capsule registry."""

    id: str
    name: str
    version: str
    kind: str  # template / executable / composite / infra
