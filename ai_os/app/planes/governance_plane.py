"""Governance plane primitives.

The governance plane evaluates policies, risk, and compliance constraints
around actions proposed by the control plane and data-plane operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol, Tuple


class PolicyEngine(Protocol):
    """Protocol for policy/governance engines."""

    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        ...


@dataclass
class GovernancePlane:
    """Thin façade over a policy engine."""

    engine: PolicyEngine

    def check_action(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        return self.engine.evaluate(action)
