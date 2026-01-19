"""Capsule marketplace + blueprint APIs (Spec §8)."""
from __future__ import annotations

from datetime import datetime
import random
import uuid
from collections import deque
from typing import Deque, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class Capsule(BaseModel):
    """Marketplace capsule metadata aligned with Spec §8.1–§8.7."""

    id: str
    name: str
    description: str
    version: str = Field(default="1.0.0")
    author: str = Field(default="AI OS Team")
    category: str = Field(default="automation")
    tags: List[str] = Field(default_factory=list)
    drivers: List[str] = Field(default_factory=list)
    downloads: int = Field(default=0)
    rating: float = Field(default=4.5)
    status: Literal["available", "installed", "update_available"] = "available"
    verified: bool = True
    marketplace_sku: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class Blueprint(BaseModel):
    """Capsule blueprint packs (Spec §8.20)."""

    id: str
    name: str
    domain: str
    description: str
    capsules: List[str]
    default_drivers: List[str]
    policy_tier: Literal["internal", "external", "regulated"] = "internal"
    marketplace_sku: Optional[str] = None
    downloads: int = Field(default=0)
    rating: float = Field(default=4.3)


class CapsuleLogEntry(BaseModel):
    timestamp: str
    level: Literal["info", "warning", "error"] = "info"
    message: str
    run_id: Optional[str] = None


class CapsuleCreateRequest(BaseModel):
    name: str
    description: str
    category: str
    drivers: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    marketplace_sku: Optional[str] = None


class CapsuleRunRequest(BaseModel):
    inputs: Optional[Dict[str, str]] = None
    priority: Literal["low", "normal", "high"] = "normal"
    dry_run: bool = False


_CAPSULES: Dict[str, Capsule] = {}
_CAPSULE_LOGS: Dict[str, Deque[CapsuleLogEntry]] = {}
_BLUEPRINTS: Dict[str, Blueprint] = {}
_FEATURED: List[str] = []


def _init_demo_data() -> None:
    if _CAPSULES:
        return
    demo_capsules = [
        Capsule(
            id="shell-capsule",
            name="Shell Capsule",
            description="Execute Unix driver actions with ledger logging and Evidence Packs.",
            version="2.1.0",
            author="AI OS Team",
            category="system",
            tags=["unix", "shell", "automation"],
            drivers=["drv-unix", "drv-os"],
            downloads=4521,
            rating=4.8,
            status="installed",
            verified=True,
            marketplace_sku="CAP-SHELL",
            created_at="2024-06-15T00:00:00Z",
            updated_at="2025-12-01T00:00:00Z",
        ),
        Capsule(
            id="git-maintenance",
            name="Git Maintenance Capsule",
            description="Run Git hygiene operations, dependency scans, and Evidence Pack exports.",
            version="1.5.0",
            author="AI OS Team",
            category="code",
            tags=["git", "version-control", "hygiene"],
            drivers=["drv-software", "drv-govern"],
            downloads=3892,
            rating=4.7,
            status="installed",
            verified=True,
            marketplace_sku="CAP-GIT",
            created_at="2024-08-20T00:00:00Z",
            updated_at="2025-11-15T00:00:00Z",
        ),
        Capsule(
            id="document-blueprint",
            name="Document Blueprint Capsule",
            description="Generate meeting notes and project briefs via software drivers.",
            version="3.0.0",
            category="documents",
            tags=["documents", "automation", "word"],
            drivers=["drv-software", "drv-os"],
            downloads=2156,
            rating=4.6,
            status="available",
            marketplace_sku="CAP-DOC",
            created_at="2024-09-10T00:00:00Z",
            updated_at="2025-12-05T00:00:00Z",
        ),
        Capsule(
            id="sim-lab",
            name="Simulation Lab Capsule",
            description="Run research simulations and capture CIR outputs.",
            version="1.2.0",
            author="Research Team",
            category="research",
            tags=["simulation", "research", "analytics"],
            drivers=["drv-research", "drv-data"],
            downloads=1847,
            rating=4.5,
            status="available",
            marketplace_sku="CAP-SIM",
            created_at="2024-10-01T00:00:00Z",
            updated_at="2025-11-28T00:00:00Z",
        ),
        Capsule(
            id="env-daemon",
            name="EnvDaemon",
            description="Monitor package manifests, repair drift, and issue ledger notices.",
            version="2.0.0",
            author="Platform Team",
            category="automation",
            tags=["environment", "monitoring", "drift"],
            drivers=["drv-package", "drv-govern"],
            downloads=2341,
            rating=4.9,
            status="update_available",
            marketplace_sku="CAP-ENV",
            created_at="2024-07-01T00:00:00Z",
            updated_at="2025-12-10T00:00:00Z",
        ),
    ]
    for capsule in demo_capsules:
        _CAPSULES[capsule.id] = capsule
        _CAPSULE_LOGS[capsule.id] = deque(maxlen=50)
    _BLUEPRINTS.update(
        {
            "founder-blueprint": Blueprint(
                id="founder-blueprint",
                name="Founder Blueprint",
                domain="startup",
                description="Capsule pack for founders: doc automation, git hygiene, finance ledgers.",
                capsules=["git-maintenance", "document-blueprint", "env-daemon"],
                default_drivers=["drv-os", "drv-software", "drv-package"],
                policy_tier="internal",
                marketplace_sku="BP-FOUNDER",
                downloads=1523,
                rating=4.7,
            ),
            "lab-blueprint": Blueprint(
                id="lab-blueprint",
                name="Lab Blueprint",
                domain="research",
                description="Research capsule chain for HPC + CIR collection.",
                capsules=["sim-lab", "document-blueprint"],
                default_drivers=["drv-research", "drv-data"],
                policy_tier="regulated",
                marketplace_sku="BP-LAB",
                downloads=987,
                rating=4.6,
            ),
        }
    )
    _FEATURED.extend(["shell-capsule", "env-daemon", "sim-lab"])


_init_demo_data()


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _append_log(capsule_id: str, message: str, level: Literal["info", "warning", "error"] = "info", run_id: Optional[str] = None) -> None:
    if capsule_id not in _CAPSULE_LOGS:
        _CAPSULE_LOGS[capsule_id] = deque(maxlen=50)
    _CAPSULE_LOGS[capsule_id].appendleft(
        CapsuleLogEntry(timestamp=_timestamp(), level=level, message=message, run_id=run_id)
    )


@router.get("/capsules")
async def list_capsules(
    category: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    """Return capsule marketplace payload mirrored in Spec sheet."""

    capsules = list(_CAPSULES.values())
    if category:
        capsules = [cap for cap in capsules if cap.category == category]
    if status:
        capsules = [cap for cap in capsules if cap.status == status]
    if search:
        needle = search.lower()
        capsules = [
            cap
            for cap in capsules
            if needle in cap.name.lower()
            or needle in cap.description.lower()
            or any(needle in tag.lower() for tag in cap.tags)
        ]
    categories = sorted({cap.category for cap in _CAPSULES.values()})
    return {
        "capsules": capsules,
        "blueprints": list(_BLUEPRINTS.values()),
        "categories": categories,
        "featured": [cid for cid in _FEATURED if cid in _CAPSULES],
    }


@router.get("/capsules/categories")
async def capsule_categories() -> Dict[str, List[str]]:
    """Expose available capsule categories for filters."""

    return {"categories": sorted({cap.category for cap in _CAPSULES.values()})}


@router.get("/capsules/featured")
async def featured_capsules() -> Dict[str, List[Capsule]]:
    """Return a curated set of featured capsules."""

    items = [
        _CAPSULES[cid]
        for cid in _FEATURED
        if cid in _CAPSULES
    ]
    return {"items": items}


@router.post("/capsules", response_model=Capsule)
async def create_capsule(payload: CapsuleCreateRequest) -> Capsule:
    capsule_id = payload.name.lower().replace(" ", "-")
    if capsule_id in _CAPSULES:
        raise HTTPException(status_code=409, detail="Capsule already exists")
    capsule = Capsule(
        id=capsule_id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        drivers=payload.drivers,
        tags=payload.tags,
        version=payload.version,
        marketplace_sku=payload.marketplace_sku,
        status="available",
        verified=True,
        downloads=random.randint(300, 1200),
        rating=round(4.3 + random.random() * 0.6, 2),
    )
    _CAPSULES[capsule.id] = capsule
    _CAPSULE_LOGS[capsule.id] = deque(maxlen=50)
    return capsule


@router.get("/capsules/{capsule_id}", response_model=Capsule)
async def get_capsule(capsule_id: str) -> Capsule:
    capsule = _CAPSULES.get(capsule_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    return capsule


@router.put("/capsules/{capsule_id}", response_model=Capsule)
async def update_capsule(capsule_id: str, payload: Dict[str, Optional[str]]) -> Capsule:
    capsule = _CAPSULES.get(capsule_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    data = capsule.model_dump()
    data.update({k: v for k, v in payload.items() if v is not None})
    data["updated_at"] = _timestamp()
    updated = Capsule(**data)
    _CAPSULES[capsule_id] = updated
    return updated


@router.delete("/capsules/{capsule_id}")
async def delete_capsule(capsule_id: str) -> Dict[str, str]:
    if capsule_id in _CAPSULES:
        _CAPSULES.pop(capsule_id)
        _CAPSULE_LOGS.pop(capsule_id, None)
    return {"status": "deleted"}


@router.post("/capsules/{capsule_id}/install")
async def install_capsule(capsule_id: str) -> Dict[str, str]:
    capsule = _CAPSULES.get(capsule_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    capsule.status = "installed"
    capsule.updated_at = _timestamp()
    capsule.downloads += random.randint(10, 50)
    _append_log(capsule_id, "Capsule installed via marketplace", run_id=str(uuid.uuid4()))
    return {"status": "installed", "capsule_id": capsule_id}


@router.post("/capsules/{capsule_id}/run")
async def run_capsule(capsule_id: str, payload: Optional[CapsuleRunRequest] = None) -> Dict[str, str]:
    capsule = _CAPSULES.get(capsule_id)
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    run_id = str(uuid.uuid4())
    priority = payload.priority if payload else "normal"
    mode = "dry-run" if payload and payload.dry_run else "execution"
    _append_log(
        capsule_id,
        f"{mode.title()} queued at priority {priority}",
        run_id=run_id,
    )
    return {
        "status": "scheduled",
        "run_id": run_id,
        "capsule_id": capsule_id,
        "message": f"Capsule {capsule.name} scheduled ({mode})",
    }


@router.get("/capsules/{capsule_id}/logs")
async def capsule_logs(capsule_id: str, limit: int = 20) -> Dict[str, List[CapsuleLogEntry]]:
    if capsule_id not in _CAPSULE_LOGS:
        raise HTTPException(status_code=404, detail="Capsule not found")
    entries = list(_CAPSULE_LOGS[capsule_id])[:limit]
    return {"logs": entries}


@router.post("/capsules/blueprints/{blueprint_id}/deploy")
async def deploy_blueprint(blueprint_id: str) -> Dict[str, str]:
    """Simulate deploying a capsule blueprint pack."""

    blueprint = _BLUEPRINTS.get(blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    blueprint.downloads += random.randint(15, 45)
    _BLUEPRINTS[blueprint_id] = blueprint
    for capsule_id in blueprint.capsules:
        if capsule_id in _CAPSULES:
            _append_log(capsule_id, f"Deployment triggered via blueprint {blueprint.name}")
    return {
        "status": "scheduled",
        "blueprint_id": blueprint_id,
        "capsules": blueprint.capsules,
    }
