"""Edge Computing & Distributed AI router."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter()


class EdgeBase(BaseModel):
    """Ensure pydantic does not reserve the ``model_`` prefix."""

    model_config = ConfigDict(protected_namespaces=())


class EdgeNode(EdgeBase):
    """Edge computing node."""

    id: str
    location: str
    status: str
    load_percent: int
    model_count: int
    last_heartbeat: str


class AIModel(EdgeBase):
    """AI model deployed on edge."""

    id: str
    name: str
    type: str
    accuracy: float
    latency_ms: int
    deployed_at: str
    status: str


class EdgeMetrics(EdgeBase):
    """Edge computing metrics."""

    total_nodes: int
    active_nodes: int
    total_models: int
    average_latency: float
    total_requests: int
    success_rate: float


class EdgeDeployment(EdgeBase):
    """Model deployment configuration."""

    model_id: str
    target_nodes: List[str]
    strategy: str
    priority: str


class EdgeComputingStatus(EdgeBase):
    """Overall edge computing system status."""

    system_status: str
    nodes: List[EdgeNode]
    metrics: EdgeMetrics
    recent_deployments: List[Dict[str, Any]]
    available_strategies: List[str]


# Mock data
NODE_LOCATIONS = [
    "San Francisco, CA", "New York, NY", "London, UK", "Tokyo, Japan",
    "Sydney, Australia", "Berlin, Germany", "Mumbai, India", "São Paulo, Brazil"
]
DEPLOYMENT_STRATEGIES = ["Round Robin", "Load Balanced", "Geographic", "Latency Optimized"]
NODE_STATUSES = ["online", "offline", "maintenance", "degraded"]

_mock_nodes: List[EdgeNode] = []
_mock_models: List[AIModel] = []


def _generate_mock_node() -> EdgeNode:
    """Generate a mock edge node."""
    location = random.choice(NODE_LOCATIONS)
    return EdgeNode(
        id=f"edge-{location.lower().replace(', ', '-').replace(' ', '-')}-{random.randint(1, 10)}",
        location=location,
        status=random.choice(NODE_STATUSES),
        load_percent=random.randint(10, 95),
        model_count=random.randint(1, 8),
        last_heartbeat=(datetime.utcnow() - timedelta(seconds=random.randint(10, 300))).isoformat() + "Z",
    )


def _generate_mock_model() -> AIModel:
    """Generate a mock AI model."""
    model_types = ["Classification", "Detection", "NLP", "Computer Vision", "Recommendation"]
    statuses = ["active", "training", "deployed", "failed"]

    return AIModel(
        id=f"model-{random.randint(1000, 9999)}",
        name=f"Model-{random.randint(100, 999)}",
        type=random.choice(model_types),
        accuracy=round(random.uniform(0.85, 0.98), 3),
        latency_ms=random.randint(50, 500),
        deployed_at=(datetime.utcnow() - timedelta(hours=random.randint(1, 168))).isoformat() + "Z",
        status=random.choice(statuses),
    )


def _generate_mock_nodes(count: int = 8) -> List[EdgeNode]:
    """Generate multiple mock edge nodes."""
    return [_generate_mock_node() for _ in range(count)]


@router.get("/edge/status", response_model=EdgeComputingStatus)
async def get_edge_status() -> EdgeComputingStatus:
    """Get edge computing system status."""
    if not _mock_nodes:
        _mock_nodes.extend(_generate_mock_nodes())

    if not _mock_models:
        _mock_models.extend([_generate_mock_model() for _ in range(12)])

    # Calculate metrics
    active_nodes = len([n for n in _mock_nodes if n.status == "online"])
    total_models = len(_mock_models)
    avg_latency = sum(m.latency_ms for m in _mock_models) / len(_mock_models) if _mock_models else 0

    metrics = EdgeMetrics(
        total_nodes=len(_mock_nodes),
        active_nodes=active_nodes,
        total_models=total_models,
        average_latency=round(avg_latency, 1),
        total_requests=random.randint(1000, 50000),
        success_rate=round(random.uniform(0.95, 0.99), 3),
    )

    system_status = "🟢 System Operational" if active_nodes >= len(_mock_nodes) * 0.8 else "🟡 Degraded Performance"

    # Generate recent deployments
    recent_deployments = [
        {
            "model_id": m.id,
            "model_name": m.name,
            "target_nodes": random.randint(1, 4),
            "deployed_at": m.deployed_at,
            "status": m.status,
        }
        for m in random.sample(_mock_models, min(5, len(_mock_models)))
    ]

    return EdgeComputingStatus(
        system_status=system_status,
        nodes=_mock_nodes,
        metrics=metrics,
        recent_deployments=recent_deployments,
        available_strategies=DEPLOYMENT_STRATEGIES,
    )


@router.post("/edge/deploy")
async def deploy_model(payload: EdgeDeployment) -> Dict[str, Any]:
    """Deploy AI model to edge nodes."""
    target_count = len(payload.target_nodes)
    model = _generate_mock_model()
    model.name = f"Deployed-{payload.model_id}"

    # Simulate deployment to target nodes
    deployed_nodes = random.sample(_mock_nodes, min(target_count, len(_mock_nodes)))
    for node in deployed_nodes:
        node.model_count += 1

    return {
        "success": True,
        "deployment_id": f"deploy-{random.randint(1000, 9999)}",
        "model": model.dict(),
        "targeted_nodes": len(deployed_nodes),
        "strategy_used": payload.strategy,
        "estimated_completion": f"{random.randint(5, 30)} minutes",
        "message": f"Model deployed to {len(deployed_nodes)} edge nodes using {payload.strategy} strategy.",
    }


@router.post("/edge/node/manage")
async def manage_edge_node(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Manage edge node (start, stop, restart, update)."""
    action = payload.get("action", "status")
    node_id = payload.get("node_id")

    if not node_id:
        return {"success": False, "message": "Node ID required."}

    # Find node
    node = next((n for n in _mock_nodes if n.id == node_id), None)
    if not node:
        return {"success": False, "message": "Node not found."}

    actions = {
        "start": "online",
        "stop": "offline",
        "restart": "online",
        "maintenance": "maintenance",
    }

    if action in actions:
        old_status = node.status
        node.status = actions[action]
        node.last_heartbeat = datetime.utcnow().isoformat() + "Z"

        return {
            "success": True,
            "node_id": node_id,
            "action": action,
            "old_status": old_status,
            "new_status": node.status,
            "message": f"Node {node_id} {action} completed.",
        }

    return {"success": False, "message": f"Unknown action: {action}"}


@router.post("/edge/models/optimize")
async def optimize_edge_models(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize model deployment across edge nodes."""
    optimization_type = payload.get("type", "latency")
    target_improvement = payload.get("target_improvement", 0.1)

    # Simulate optimization
    before_metrics = {
        "average_latency": sum(m.latency_ms for m in _mock_models) / len(_mock_models),
        "total_requests": random.randint(8000, 45000),
        "success_rate": round(random.uniform(0.92, 0.97), 3),
    }

    improvement = random.uniform(target_improvement * 0.5, target_improvement * 1.5)
    after_metrics = {
        "average_latency": before_metrics["average_latency"] * (1 - improvement),
        "total_requests": int(before_metrics["total_requests"] * (1 + improvement * 0.1)),
        "success_rate": min(0.99, before_metrics["success_rate"] + improvement * 0.05),
    }

    return {
        "success": True,
        "optimization_type": optimization_type,
        "before_metrics": before_metrics,
        "after_metrics": {k: round(v, 2) if isinstance(v, float) else v for k, v in after_metrics.items()},
        "improvement_achieved": round(improvement * 100, 1),
        "message": f"Edge deployment optimized for {optimization_type}, achieving {round(improvement * 100, 1)}% improvement.",
    }


@router.get("/edge/models", response_model=List[AIModel])
async def get_edge_models() -> List[AIModel]:
    """Get all AI models deployed on edge."""
    if not _mock_models:
        _mock_models.extend([_generate_mock_model() for _ in range(12)])

    return _mock_models


@router.post("/edge/status/refresh")
async def refresh_edge_status() -> EdgeComputingStatus:
    """Refresh edge computing system status."""
    # Update node heartbeats and occasionally change status
    for node in _mock_nodes:
        node.last_heartbeat = datetime.utcnow().isoformat() + "Z"
        if random.random() > 0.95:  # 5% chance to change status
            node.status = random.choice(NODE_STATUSES)

    return await get_edge_status()
