"""Intelligence micro-services router (monitoring, personalization, collaboration)."""

from __future__ import annotations

import json
import random
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator, ConfigDict

router = APIRouter()


class IntelligenceBase(BaseModel):
    """Disable protected namespace so fields like model_type are allowed."""

    model_config = ConfigDict(protected_namespaces=())


class MonitoringRequest(IntelligenceBase):
    action: str = Field(default="check_health", pattern="^[a-z_]+$")
    system_metrics: Dict[str, float]
    monitoring_window: int = Field(ge=1, le=24 * 14)
    alert_thresholds: Dict[str, float]

    @validator("system_metrics", pre=True)
    def _parse_metrics(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as exc:  # pragma: no cover - validation
                raise ValueError(f"Invalid JSON for system_metrics: {exc}") from exc
        return value

    @validator("alert_thresholds", pre=True)
    def _parse_thresholds(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as exc:
                raise ValueError(f"Invalid JSON for alert_thresholds: {exc}") from exc
        return value


class PersonalizationRequest(IntelligenceBase):
    recommendation_type: str = Field(
        default="content_based", pattern="^[a-z_]+$"
    )
    user_preferences: Optional[str] = ""
    context_data: Optional[str] = ""
    max_recommendations: int = Field(default=10, ge=1, le=100)


class CollaborationRequest(IntelligenceBase):
    action: str = Field(default="analyze_team", pattern="^[a-z_]+$")
    team_size: int = Field(default=5, ge=1, le=200)
    communication_patterns: Optional[str] = ""
    project_complexity: str = Field(
        default="medium", pattern="^(low|medium|high|very_high)$"
    )


@router.post("/monitoring")
async def run_monitoring(payload: MonitoringRequest) -> Dict[str, Any]:
    """Simulate intelligent monitoring / anomaly detection."""
    metrics = payload.system_metrics
    thresholds = payload.alert_thresholds
    alerts: List[Dict[str, Any]] = []

    for key, value in metrics.items():
        threshold = thresholds.get(key, 100)
        if value >= threshold:
            alerts.append(
                {
                    "metric": key,
                    "value": value,
                    "threshold": threshold,
                    "severity": random.choice(["warning", "critical"]),
                    "recommendation": f"Scale resources or throttle workload affecting {key}.",
                }
            )

    status = "healthy" if not alerts else ("degraded" if len(alerts) < 2 else "critical")

    return {
        "action": payload.action,
        "status": status,
        "window_hours": payload.monitoring_window,
        "metrics_sampled": len(metrics),
        "alerts": alerts,
        "next_check_eta_minutes": max(5, payload.monitoring_window // 2),
    }


@router.post("/personalization")
async def run_personalization(payload: PersonalizationRequest) -> Dict[str, Any]:
    """Simulate personalization engine output."""
    topics = [pref.strip() for pref in (payload.user_preferences or "").split(",") if pref.strip()]
    if not topics:
        topics = ["productivity", "automation", "insights"]

    recommendations = []
    for idx in range(min(payload.max_recommendations, 5)):
        topic = topics[idx % len(topics)]
        recommendations.append(
            {
                "rank": idx + 1,
                "title": f"{topic.title()} Strategy #{idx + 1}",
                "confidence": round(random.uniform(0.72, 0.97), 2),
                "reason": f"Matches historical preference for {topic}",
                "cta": random.choice(["Summarize", "Schedule review", "Create task"]),
            }
        )

    return {
        "type": payload.recommendation_type,
        "count": len(recommendations),
        "context_applied": bool(payload.context_data),
        "recommendations": recommendations,
    }


class MLOpsRequest(IntelligenceBase):
    action: str = Field(default="train_model", pattern="^[a-z_]+$")
    model_type: str = Field(default="classification")
    dataset_path: Optional[str] = ""
    hyperparameters: Dict[str, Any]

    @validator("hyperparameters", pre=True)
    def _parse_hparams(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as exc:
                raise ValueError(f"Invalid JSON for hyperparameters: {exc}") from exc
        return value


@router.post("/collaboration")
async def run_collaboration(payload: CollaborationRequest) -> Dict[str, Any]:
    """Simulate collaboration intelligence analysis."""
    team_load = random.randint(60, 95)
    health = "stable"
    if payload.team_size > 20 or payload.project_complexity in ("high", "very_high"):
        health = random.choice(["watch", "at_risk"])

    return {
        "action": payload.action,
        "team_size": payload.team_size,
        "complexity": payload.project_complexity,
        "collaboration_health": health,
        "insights": [
            "Standups exceed 25 minutes; consider asynchronous updates.",
            "Decision latency is trending upward due to stakeholder approvals.",
            "Knowledge base usage increased 18% week over week.",
        ],
        "recommendations": [
            {"title": "Automate status rollups", "impact": "High"},
            {"title": "Enable auto-routing for reviews", "impact": "Medium"},
        ],
        "next_review_days": random.randint(3, 7),
    }


@router.post("/mlops")
async def run_mlops(payload: MLOpsRequest) -> Dict[str, Any]:
    """Simulate MLOps pipeline operations."""
    action = payload.action
    steps = ["data_ingest", "feature_engineering", "training", "evaluation", "deployment"]
    timeline = [
        {"step": step.replace("_", " ").title(), "duration_minutes": random.randint(4, 20)}
        for step in steps
    ]
    status = "completed" if action != "deploy_model" else random.choice(["completed", "pending"])

    return {
        "action": action,
        "model_type": payload.model_type,
        "status": status,
        "dataset": payload.dataset_path or "n/a",
        "hyperparameters": payload.hyperparameters,
        "metrics": {
            "accuracy": round(random.uniform(0.78, 0.95), 3),
            "loss": round(random.uniform(0.12, 0.35), 3),
            "throughput_samples_s": random.randint(120, 420),
        },
        "timeline": timeline,
    }
