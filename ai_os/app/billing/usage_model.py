"""Simple usage and billing model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable


@dataclass
class UsageRecord:
    """Represents a single metered usage event."""

    id: str
    subject: str  # driver/model/capsule id
    category: str  # e.g. model_call, storage, workflow_step
    quantity: float
    unit: str
    ts: datetime


@dataclass
class BillingEngine:
    """Very small billing façade."""

    price_table: Dict[str, float]

    def estimate_cost(self, records: Iterable[UsageRecord]) -> float:
        total = 0.0
        for record in records:
            total += record.quantity * self.price_table.get(record.category, 0.0)
        return total
