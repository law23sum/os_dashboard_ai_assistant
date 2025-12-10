#!/usr/bin/env python3
"""Shared data/state helpers for the Research & Simulation workspace.

The Tkinter GUI, React client, and FastAPI layer all import this module so there is
only one canonical definition of the Research dashboard defaults (aligns with the
OS Dashboard canon §4.5/§4.6 requirements).
"""

from __future__ import annotations

import copy
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_parameters() -> List[Dict[str, str]]:
    return [
        {"name": "volatility", "min": "0.1", "max": "0.5"},
        {"name": "drift_rate", "min": "0.05", "max": "0.15"},
    ]


def _default_experiments() -> List[Dict[str, Any]]:
    return [
        {
            "id": str(uuid.uuid4()),
            "name": "Monte Carlo Risk Analysis",
            "status": "running",
            "progress": 6500,
            "total": 10000,
            "eta": "2m 15s",
            "description": "Financial portfolio risk assessment with 10,000 iterations",
            "simulation_type": "monte_carlo",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Population Dynamics Model",
            "status": "completed",
            "progress": 10000,
            "total": 10000,
            "eta": "5m 42s",
            "description": "Predator-prey ecosystem simulation over 100 years",
            "simulation_type": "agent_based",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Network Optimization",
            "status": "pending",
            "progress": 0,
            "total": 12000,
            "eta": "Queue position: 1",
            "description": "Supply chain network optimization with genetic algorithm",
            "simulation_type": "optimization",
        },
    ]


def _default_models() -> List[Dict[str, Any]]:
    return [
        {
            "id": "financial_risk",
            "name": "Financial Risk Model v2.1",
            "status": "validated",
            "accuracy": 0.87,
            "description": "Monte Carlo simulation for portfolio risk assessment",
            "last_updated": "2 days ago",
        },
        {
            "id": "population_dynamics",
            "name": "Population Dynamics v1.5",
            "status": "validated",
            "accuracy": 0.92,
            "description": "Predator-prey ecosystem modeling with environmental factors",
            "last_updated": "1 week ago",
        },
        {
            "id": "network_analysis",
            "name": "Network Analysis v3.0",
            "status": "testing",
            "accuracy": 0.78,
            "description": "Graph-based network analysis and optimization",
            "last_updated": "3 days ago",
        },
    ]


def _default_reports() -> List[Dict[str, str]]:
    return [
        {
            "title": "Monte Carlo Risk Analysis Report",
            "summary": "Comprehensive analysis of portfolio risk using Monte Carlo simulation with 10,000 iterations.",
            "generated": "Today",
        },
        {
            "title": "Population Dynamics Study",
            "summary": "Long-term ecosystem modeling results showing predator-prey relationships over 100-year simulation.",
            "generated": "Yesterday",
        },
        {
            "title": "Model Validation Summary",
            "summary": "Cross-validation results and performance metrics for all registered models in the system.",
            "generated": "2 days ago",
        },
    ]


def _default_knowledge_graph() -> Dict[str, Any]:
    return {
        "nodes": [
            {"label": "Risk Models", "x": 120, "y": 80},
            {"label": "Monte Carlo", "x": 260, "y": 160},
            {"label": "Validation", "x": 420, "y": 110},
            {"label": "Statistics", "x": 180, "y": 260},
            {"label": "Optimization", "x": 520, "y": 230},
            {"label": "Results", "x": 640, "y": 80},
        ],
        "edges": [(0, 1), (0, 2), (1, 3), (3, 4), (2, 5), (4, 5)],
    }


def default_workspace_snapshot() -> Dict[str, Any]:
    """Produce a serializable snapshot used by both Tk and React layers."""
    return {
        "status_message": "Configure and run research simulations.",
        "simulation_config": {
            "type": "monte_carlo",
            "model": "financial_risk",
            "iterations": 1000,
            "confidence": 0.95,
            "parameters": _default_parameters(),
        },
        "metrics": {
            "mean": 42.7,
            "std": 3.2,
            "min": 35.1,
            "max": 48.9,
            "confidence_interval": (40.2, 45.1),
        },
        "analytics": {
            "series": [0, 35.2, 40.1, 42.3, 42.6, 42.7],
            "bounds": [0, 38.5, 41.8, 43.1, 43.2, 43.1],
        },
        "experiments": _default_experiments(),
        "models": _default_models(),
        "reports": _default_reports(),
        "knowledge_graph": _default_knowledge_graph(),
        "last_design": None,
        "updated_at": _timestamp(),
    }


@dataclass
class ResearchWorkspaceState:
    """Mutable research workspace model for API consumers."""

    snapshot_data: Dict[str, Any] = field(default_factory=default_workspace_snapshot)

    def snapshot(self) -> Dict[str, Any]:
        """Return a deep copy that includes mildly updated progress."""
        self._advance_running_experiments()
        self.snapshot_data["updated_at"] = _timestamp()
        return copy.deepcopy(self.snapshot_data)

    def reset(self) -> None:
        self.snapshot_data = default_workspace_snapshot()

    def start_simulation(self, sim_type: str, model_id: str, iterations: int) -> Dict[str, Any]:
        iterations = max(1, iterations)
        exp = {
            "id": str(uuid.uuid4()),
            "name": f"{sim_type.replace('_', ' ').title()} Simulation",
            "status": "running",
            "progress": 0,
            "total": iterations,
            "eta": "starting…",
            "description": f"{iterations:,} iteration run for model {model_id}",
            "simulation_type": sim_type,
            "started_at": _timestamp(),
        }
        self.snapshot_data["experiments"].insert(0, exp)
        self.snapshot_data["simulation_config"]["type"] = sim_type
        self.snapshot_data["simulation_config"]["model"] = model_id
        self.snapshot_data["simulation_config"]["iterations"] = iterations
        self._nudge_metrics()
        return copy.deepcopy(exp)

    def design_experiment(self, design_type: str, variables: List[str]) -> Dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "type": design_type,
            "variables": variables,
            "created_at": _timestamp(),
            "status": "ready",
        }
        self.snapshot_data["last_design"] = record
        return copy.deepcopy(record)

    def _advance_running_experiments(self) -> None:
        for exp in self.snapshot_data["experiments"]:
            if exp["status"] != "running" or not exp["total"]:
                continue
            increment = random.randint(100, 400)
            exp["progress"] = min(exp["total"], exp["progress"] + increment)
            if exp["progress"] >= exp["total"]:
                exp["status"] = "completed"
                exp["eta"] = "completed"
            else:
                remaining = exp["total"] - exp["progress"]
                seconds = max(5, remaining // max(increment, 1))
                exp["eta"] = f"{seconds}s"

    def _nudge_metrics(self) -> None:
        metrics = self.snapshot_data["metrics"]
        mean = metrics.get("mean", 42.7)
        jitter = random.uniform(-0.3, 0.3)
        new_mean = max(0.0, mean + jitter)
        std = max(0.5, metrics.get("std", 3.2) + random.uniform(-0.2, 0.2))
        metrics["mean"] = round(new_mean, 2)
        metrics["std"] = round(std, 2)
        metrics["min"] = round(new_mean - std * 2, 2)
        metrics["max"] = round(new_mean + std * 2, 2)
        metrics["confidence_interval"] = (
            round(new_mean - std, 2),
            round(new_mean + std, 2),
        )
