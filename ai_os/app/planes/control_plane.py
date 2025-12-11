"""Control plane primitives.

The control plane is responsible for orchestrating workflows, agents, and
Daemons across drivers and capsules. It turns intent and plans into
executable steps and feeds back observability into future planning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Protocol


class StepExecutor(Protocol):
    """Protocol for executing atomic steps against the driver layer."""

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        ...


@dataclass
class ControlPlane:
    """Minimal control-plane façade."""

    executor: StepExecutor
    middlewares: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = field(default_factory=list)

    def run_plan(self, plan: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a linear plan of steps and return their results."""

        results: List[Dict[str, Any]] = []
        for step in plan:
            for middleware in self.middlewares:
                step = middleware(step)
            results.append(self.executor.execute_step(step))
        return results
