"""Minimal FastAPI entrypoint showcasing the architecture skeleton."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
import random
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ai_os.app.cir import CIRDocument, CIRNode
from ai_os.app.connectors.notes import NotesConnector
from ai_os.app.connectors.word import WordConnector
from ai_os.app.connectors.pdf import PDFConnector
from ai_os.app.orchestration.daemons import RegulationIngestDaemon
from ai_os.app.orchestration.events import EventBus
from ai_os.app.orchestration.runner import Orchestrator
from ai_os.app.search.index import InMemoryVectorIndex
from ai_os.app.governance.audit import AuditLog, OperationRecord
from ai_os.app.governance.change_engine import ChangeEngine
from ai_os.app.system_monitor import get_system_stats
from ai_os.app.ai_proxy import ask_ai
from ai_os.app.planes import DataPlane, ControlPlane, GovernancePlane
from ai_os.app.domain import Project, Task, Workspace
from ai_os.app.billing import BillingEngine, UsageRecord
from ai_os.app.observability import ObservabilityService
from assistant_core.failure_registry import get_failure_registry
from assistant_hub.command_catalog import (
    SPEC_SHEET_COMMANDS,
    BACKEND_CLI_COMMANDS,
)
from assistant_hub_gui.assistant_hub.terminal import run_bash_command


@dataclass
class DaemonProfile:
    """Runtime metadata exposed to the React dashboard."""

    name: str
    description: str
    enabled: bool = True
    scopes: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    risk_level: str = "medium"
    success_rate: float = 0.0
    last_run: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["last_run"] = (
            self.last_run.isoformat() if self.last_run else None
        )
        return payload


class DummyStorage:
    """Simple storage adapter for demonstrating connector wiring."""

    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}

    def list(self, folder=None):
        return list(self.data.values())

    def meta(self, resource_id):
        return self.data.get(resource_id, {})

    def get(self, resource_id):
        return self.data[resource_id]

    def upsert(
        self, resource_id, title: str, text: str = "", table=None, metadata=None
    ):
        if resource_id == "new":
            resource_id = str(len(self.data) + 1)
        self.data[resource_id] = {
            "id": resource_id,
            "title": title,
            "text": text,
            "table": table,
            "metadata": metadata or {},
        }
        return self.data[resource_id]

    def search(self, query, limit: int = 10):
        matches = []
        for record in self.data.values():
            haystack = f"{record.get('title', '')} {record.get('text', '')}".lower()
            if query.lower() in haystack:
                matches.append(record)
        return matches[:limit]


REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"
DOCS_DIR = REPO_ROOT / "docs"
TERMINAL_WORKSPACES = [
    ".",
    "assistant_hub_gui",
    "assistant_hub",
    "backend_api",
    "frontend",
    "ai_os",
    "ui",
]
TERMINAL_TEMPLATE_COMMANDS = [
    {
        "label": "Workspace status",
        "command": "ls -la",
        "description": "Inspect contents of the selected workspace.",
    },
    {
        "label": "Backend health",
        "command": "uvicorn ai_os.app.main:app --reload",
        "description": "Start the FastAPI server in reload mode.",
    },
    {
        "label": "Frontend dev server",
        "command": "cd frontend && npm run dev",
        "description": "Launch the Vite dev server for the React client.",
    },
]


app = FastAPI(title="AI OS Dashboard Skeleton")
if FRONTEND_DIST.exists():
    app.mount(
        "/app",
        StaticFiles(directory=FRONTEND_DIST, html=True),
        name="webapp",
    )

    @app.get("/", response_class=HTMLResponse)
    def serve_frontend_root():
        index_path = FRONTEND_DIST / "index.html"
        return index_path.read_text(encoding="utf-8")

if DOCS_DIR.exists():
    app.mount(
        "/docs",
        StaticFiles(directory=DOCS_DIR, html=True),
        name="docs",
    )

bus = EventBus()
orch = Orchestrator(bus)
index = InMemoryVectorIndex()
audit = AuditLog()
change_engine = ChangeEngine()
observability = ObservabilityService()


@app.get("/health")
def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "healthy", "service": "os-dashboard-ai-assistant"}


class SimpleDataBackend:
    def __init__(self):
        self.store: Dict[str, Dict[str, Any]] = {}

    def put(self, collection: str, key: str, value: Dict[str, Any]) -> None:
        self.store.setdefault(collection, {})[key] = value

    def get(self, collection: str, key: str) -> Dict[str, Any] | None:
        return self.store.get(collection, {}).get(key)

    def query(self, collection: str, **filters: Any):
        for item in self.store.get(collection, {}).values():
            if all(item.get(k) == v for k, v in filters.items()):
                yield item


class EchoExecutor:
    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        observability.emit_event("control_step", {"step": step})
        return {"status": "ok", "step": step}


class AllowAllPolicy:
    def evaluate(self, context: Dict[str, Any]):
        return True, "allowed"


data_plane = DataPlane(backend=SimpleDataBackend())
control_plane = ControlPlane(executor=EchoExecutor())
governance_plane = GovernancePlane(engine=AllowAllPolicy())

notes_storage = DummyStorage()
word_storage = DummyStorage()
pdf_storage = DummyStorage()

notes = NotesConnector(notes_storage)
word = WordConnector(word_storage)
pdf = PDFConnector(pdf_storage)
failure_registry = get_failure_registry()

reg_daemon = RegulationIngestDaemon(
    pdf_connector=pdf, word_connector=word, index=index, audit=audit
)
orch.register_daemon("pdf.added.regulations", reg_daemon)

daemon_registry: Dict[str, DaemonProfile] = {
    "regulation_ingest": DaemonProfile(
        name="regulation_ingest",
        description="Watches regulation PDFs and drafts policy updates.",
        scopes=["governance", "compliance"],
        triggers=["pdf.added.regulations"],
        risk_level="medium",
        success_rate=0.94,
        last_run=datetime.utcnow(),
    ),
    "workspace_sync": DaemonProfile(
        name="workspace_sync",
        description="Keeps notes, briefs, and Word deliverables aligned.",
        scopes=["notes", "documents"],
        triggers=["notes.updated", "word.updated"],
        risk_level="low",
        success_rate=0.88,
        enabled=True,
    ),
    "ops_guardian": DaemonProfile(
        name="ops_guardian",
        description="Scans audit signals for drift and escalates anomalies.",
        scopes=["audit", "observability"],
        triggers=["audit.recorded", "signals.spike"],
        risk_level="high",
        success_rate=0.91,
        enabled=False,
    ),
}


sample_projects: List[Project] = [
    Project(
        id="proj-ops",
        name="Operations Uplift",
        owner_id="user-chris",
        tasks=[
            Task(id="task-sync", title="Wire FastAPI billing endpoint", state="todo", priority=2),
            Task(id="task-ui", title="Surface billing cards", state="in_progress", priority=3),
        ],
        workspaces=[Workspace(id="ws-control", name="Control Plane Studio")],
    ),
    Project(
        id="proj-ai",
        name="AI Ops Enhancements",
        owner_id="user-chris",
        tasks=[
            Task(id="task-audit", title="Expand audit diffs", state="done", priority=1),
            Task(id="task-daemon", title="Expose daemon toggles", state="blocked", priority=2),
        ],
    ),
]

workspace_snapshot: Dict[str, Any] = {
    "status_message": "Workspace stable. Experiments are refreshing every 30 minutes.",
    "simulation_config": {
        "type": "monte_carlo",
        "model": "financial_risk",
        "iterations": 1000,
        "confidence": 0.95,
        "parameters": [
            {"name": "volatility", "min": "0.10", "max": "0.30"},
            {"name": "recovery_rate", "min": "0.20", "max": "0.50"},
        ],
    },
    "metrics": {
        "mean": 128.4,
        "std": 14.2,
        "min": 78.0,
        "max": 182.5,
        "confidence_interval": [118.1, 136.7],
    },
    "analytics": {
        "series": [112, 118, 121, 119, 125, 127, 134, 132, 129, 131],
        "bounds": [90, 150],
    },
    "experiments": [
        {
            "id": "exp-risk-ops",
            "name": "Credit stress test",
            "status": "running",
            "progress": 54,
            "total": 100,
            "eta": "12m",
            "description": "Evaluating high-volatility scenarios against portfolio X.",
            "simulation_type": "monte_carlo",
        },
        {
            "id": "exp-liquidity",
            "name": "Liquidity depletion trial",
            "status": "completed",
            "progress": 100,
            "total": 100,
            "eta": "0m",
            "description": "Measured liquidity runway under combined outages.",
            "simulation_type": "agent_based",
        },
    ],
    "models": [
        {
            "id": "financial_risk",
            "name": "Financial Risk Model",
            "status": "stable",
            "accuracy": 0.92,
            "description": "Monte Carlo VaR approximator",
            "last_updated": datetime.utcnow().isoformat(),
        },
        {
            "id": "ops_resilience",
            "name": "Ops Resilience",
            "status": "training",
            "accuracy": 0.81,
            "description": "Predicts MTTR across infra stacks",
            "last_updated": datetime.utcnow().isoformat(),
        },
    ],
    "reports": [
        {
            "title": "Risk posture summary",
            "summary": "Exposure steady. Top drivers: credit spread widening, FX swings.",
            "generated": datetime.utcnow().isoformat(),
        }
    ],
    "knowledge_graph": {
        "nodes": [
            {"label": "Risk", "x": 0.1, "y": 0.2},
            {"label": "Liquidity", "x": 0.4, "y": 0.8},
            {"label": "Markets", "x": 0.7, "y": 0.3},
        ],
        "edges": [[0, 1], [1, 2]],
    },
    "last_design": {
        "id": "design-baseline",
        "type": "parameter_sweep",
        "variables": ["volatility", "recovery_rate"],
    },
    "updated_at": datetime.utcnow().isoformat(),
}


def _collect_tasks() -> List[Task]:
    tasks: List[Task] = []
    for project in sample_projects:
        tasks.extend(project.tasks)
    return tasks


def _calc_percent(used: Optional[float], total: Optional[float]) -> float:
    try:
        if not total:
            return 0.0
        return max(0.0, min(100.0, (float(used or 0) / float(total)) * 100.0))
    except Exception:
        return 0.0


def _touch_workspace() -> None:
    workspace_snapshot["updated_at"] = datetime.utcnow().isoformat()

usage_records: List[UsageRecord] = [
    UsageRecord(
        id="usage-1",
        subject="model:gpt-4",
        category="model_call",
        quantity=1200,
        unit="tokens",
        ts=datetime.utcnow(),
    ),
    UsageRecord(
        id="usage-2",
        subject="daemon:regulation_ingest",
        category="workflow_step",
        quantity=15,
        unit="runs",
        ts=datetime.utcnow(),
    ),
]

billing_engine = BillingEngine(price_table={"model_call": 0.000002, "workflow_step": 0.05})


_demo_seeded = False


def _record_operation(
    *,
    actor: str,
    intent: str,
    triggered_by: str,
    touches: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    diffs: Optional[List[Dict[str, Any]]] = None,
) -> OperationRecord:
    record = audit.start(
        actor=actor,
        intent=intent,
        triggered_by=triggered_by,
        metadata=metadata or {},
    )
    for touch in touches or []:
        audit.add_touch(
            record.id,
            system=touch["system"],
            resource_id=touch["resource_id"],
            action=touch.get("action", "observe"),
        )
    for diff in diffs or []:
        audit.add_diff(record.id, diff)
    audit.finish(record.id)

    if actor.startswith("daemon:"):
        daemon_name = actor.split(":", 1)[1]
        profile = daemon_registry.get(daemon_name)
        if profile:
            profile.last_run = record.finished_at or datetime.utcnow()
    return record


def _seed_demo_content() -> None:
    global _demo_seeded
    if _demo_seeded:
        return

    seed_refs: Dict[str, List[str]] = {}
    samples = [
        {
            "connector": notes,
            "actor": "persona:aria",
            "title": "Privacy Addendum Tracker",
            "text": "Compile outstanding privacy addendums across EU/US rollouts and flag mismatches.",
        },
        {
            "connector": notes,
            "actor": "persona:sora",
            "title": "Driver Playbook Outline",
            "text": "Outline driver-aware orchestrator touch-points with citations to audit history.",
        },
        {
            "connector": pdf,
            "actor": "daemon:regulation_ingest",
            "title": "EU Digital Privacy Safeguards 2024",
            "text": "Section 14 notes: consent windows, retention curves, audit notifications.",
        },
        {
            "connector": word,
            "actor": "persona:aic",
            "title": "Driver-Aware Orchestrator Brief",
            "text": "Summarize telemetry, daemon posture, and audit hooks for executive briefing.",
        },
    ]

    for sample in samples:
        connector = sample["connector"]
        cir = CIRDocument(
            root=CIRNode(
                type=getattr(connector, "node_type", "document"),  # type: ignore[arg-type]
                title=sample["title"],
                text=sample["text"],
            ),
            doc_type=getattr(connector, "doc_type", "generic"),
        )
        ref = connector.write("new", cir)  # type: ignore[attr-defined]
        index.upsert_document(
            cir,
            payload={
                "system": connector.system_name,  # type: ignore[attr-defined]
                "resource_id": ref.id,
                "title": sample["title"],
            },
        )
        before = CIRDocument(
            root=CIRNode(
                type=cir.root.type,
                title=cir.root.title,
                text="",
            ),
            doc_type=cir.doc_type,
        )
        _record_operation(
            actor=sample["actor"],
            intent=f"{connector.system_name}.ingest",  # type: ignore[attr-defined]
            triggered_by="seed",
            touches=[
                {
                    "system": connector.system_name,  # type: ignore[attr-defined]
                    "resource_id": ref.id,
                    "action": "write",
                }
            ],
            metadata={"resource_id": ref.id, "title": sample["title"]},
            diffs=[change_engine.build_write_payload(before, cir)],
        )
        seed_refs.setdefault(connector.system_name, []).append(ref.id)  # type: ignore[attr-defined]

    # Create extra audit noise so the activity timeline has variety.
    pdf_ref = seed_refs.get("pdf", [None])[0]
    word_ref = seed_refs.get("word", [None])[0]
    notes_ref = seed_refs.get("notes", [None])[0]

    if pdf_ref and word_ref:
        _record_operation(
            actor="daemon:regulation_ingest",
            intent="policy_sync.autorun",
            triggered_by="event",
            touches=[
                {"system": "pdf", "resource_id": pdf_ref, "action": "read"},
                {"system": "word", "resource_id": word_ref, "action": "write"},
            ],
            metadata={"delta": "privacy-addendum", "severity": "low"},
        )

    if notes_ref:
        _record_operation(
            actor="persona:aria",
            intent="notes.summarize_decisions",
            triggered_by="manual",
            touches=[{"system": "notes", "resource_id": notes_ref, "action": "read"}],
            metadata={"window": "last_7_days"},
        )

    # Seed git/filesystem search payloads so cards light up.
    git_doc = CIRDocument(
        root=CIRNode(
            type="document",
            title="git commit a1b2 – driver service refactor",
            text="Refactored driver_event loop to expose governance hooks and new audit calls.",
        ),
        doc_type="generic",
    )
    index.upsert_document(
        git_doc,
        payload={
            "system": "git",
            "resource_id": "commit-a1b2",
            "node_title": git_doc.root.title,
            "text_snippet": git_doc.root.text,
        },
    )

    fs_doc = CIRDocument(
        root=CIRNode(
            type="document",
            title="filesystem:/briefs/driver_orchestrator.md",
            text="Filesystem scan shows drift between ops briefing and current automation graph.",
        ),
        doc_type="generic",
    )
    index.upsert_document(
        fs_doc,
        payload={
            "system": "filesystem",
            "resource_id": "/briefs/driver_orchestrator.md",
            "node_title": fs_doc.root.title,
            "text_snippet": fs_doc.root.text,
        },
    )

    _demo_seeded = True


def _ensure_seed_data() -> None:
    if not _demo_seeded:
        _seed_demo_content()


def _serialize_operation(record: OperationRecord) -> Dict[str, Any]:
    return {
        "id": record.id,
        "actor": record.actor,
        "intent": record.intent,
        "triggered_by": record.triggered_by,
        "started_at": record.started_at.isoformat(),
        "finished_at": record.finished_at.isoformat()
        if record.finished_at
        else None,
        "touched": record.touched,
        "metadata": record.metadata,
    }


def _get_daemon_profile(name: str) -> DaemonProfile:
    daemon = daemon_registry.get(name)
    if not daemon:
        raise HTTPException(status_code=404, detail=f"Unknown daemon '{name}'")
    return daemon


def _resolve_terminal_cwd(raw: Optional[str]) -> Path:
    target = Path(raw or ".")
    if not target.is_absolute():
        target = REPO_ROOT / target
    try:
        target.relative_to(REPO_ROOT)
    except ValueError:
        target = REPO_ROOT
    return target if target.exists() else REPO_ROOT


def _relative_cwd(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


@app.on_event("startup")
def _bootstrap_demo_state():
    _seed_demo_content()


class ChatRequest(BaseModel):
    prompt: str


class TerminalRequest(BaseModel):
    command: str
    cwd: Optional[str] = None


class SimulationRunRequest(BaseModel):
    sim_type: str
    model_id: str
    iterations: int


class ExperimentDesignRequest(BaseModel):
    design_type: str = "parameter_sweep"
    variables: List[str] = []


@app.post("/notes")
def create_note(payload: Dict[str, Any]):
    title = payload.get("title", "Untitled Note")
    text = payload.get("text", "")
    cir = CIRDocument(
        root=CIRNode(type="note", title=title, text=text), doc_type="note"
    )
    ref = notes.write("new", cir)

    index.upsert_document(
        cir, payload={"system": notes.system_name, "resource_id": ref.id}
    )
    observability.emit_event("notes.write", {"resource_id": ref.id})
    audit_record = audit.start(
        actor="api:user", intent="create_note", triggered_by="api"
    )
    audit.add_touch(
        audit_record.id,
        system=notes.system_name,
        resource_id=ref.id,
        action="write",
    )
    before = CIRDocument(
        root=CIRNode(type="note", title=title, text=""), doc_type="note"
    )
    audit.add_diff(
        audit_record.id,
        change_engine.build_write_payload(before, cir),
    )
    audit.finish(audit_record.id)
    return {"id": ref.id, "title": ref.name, "audit_id": audit_record.id}


@app.post("/pdfs/regulations")
def add_regulation_pdf(payload: Dict[str, Any]):
    title = payload.get("title", "New Regulation")
    text = payload.get("text", "")
    cir = CIRDocument(root=CIRNode(type="pdf", title=title, text=text), doc_type="pdf")
    ref = pdf.write("new", cir)
    observability.emit_event("pdf.write", {"resource_id": ref.id})
    audit_record = audit.start(
        actor="api:user", intent="add_regulation_pdf", triggered_by="api"
    )
    audit.add_touch(
        audit_record.id,
        system=pdf.system_name,
        resource_id=ref.id,
        action="write",
    )
    before = CIRDocument(
        root=CIRNode(type="pdf", title=title, text=""), doc_type="pdf"
    )
    audit.add_diff(
        audit_record.id,
        change_engine.build_write_payload(before, cir),
    )
    audit.finish(audit_record.id)
    orch.emit("pdf.added.regulations", {"resource_id": ref.id})
    return {
        "pdf_id": ref.id,
        "status": "ingested_event_emitted",
        "audit_id": audit_record.id,
    }


@app.get("/search")
def unified_search(q: str):
    _ensure_seed_data()
    results = index.search(q, limit=10)
    return [{"score": score, **payload} for score, payload in results]


@app.get("/audit/{op_id}")
def get_audit(op_id: str):
    _ensure_seed_data()
    record = audit.get(op_id)
    return {
        "id": record.id,
        "actor": record.actor,
        "intent": record.intent,
        "triggered_by": record.triggered_by,
        "started_at": record.started_at,
        "finished_at": record.finished_at,
        "touched": record.touched,
        "diffs": record.diffs,
        "metadata": record.metadata,
    }


@app.get("/system")
def system_snapshot():
    """Expose psutil stats for the React dashboard and external clients."""

    return get_system_stats()


@app.post("/ai/ask")
def ask_ai_endpoint(payload: ChatRequest):
    """Simple passthrough to the lightweight chat proxy."""

    return ask_ai(payload.prompt)


@app.get("/terminal/commands")
def terminal_command_catalog():
    """Expose command catalog + workspace metadata for the Tools tab."""

    return {
        "spec_sheet": SPEC_SHEET_COMMANDS,
        "backend_cli": BACKEND_CLI_COMMANDS,
        "templates": TERMINAL_TEMPLATE_COMMANDS,
        "workspaces": TERMINAL_WORKSPACES,
    }


@app.post("/terminal")
def execute_terminal_command(payload: TerminalRequest):
    """Execute a shell command relative to the repository root."""

    command = (payload.command or "").strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command is required.")
    cwd_path = _resolve_terminal_cwd(payload.cwd)
    result = run_bash_command(command, cwd=str(cwd_path))
    return {
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
        "shell": result.shell_path,
        "cwd": _relative_cwd(Path(result.cwd)),
        "ok": result.ok,
    }


@app.get("/operations")
def list_operations(limit: int = 50):
    _ensure_seed_data()
    records = sorted(
        audit.records.values(), key=lambda record: record.started_at, reverse=True
    )
    return [_serialize_operation(record) for record in records[:limit]]


@app.get("/daemons")
def list_daemons():
    _ensure_seed_data()
    return [profile.to_dict() for profile in daemon_registry.values()]


@app.post("/daemons/{name}/enable")
def enable_daemon(name: str):
    _ensure_seed_data()
    daemon = _get_daemon_profile(name)
    daemon.enabled = True
    return daemon.to_dict()


@app.post("/daemons/{name}/disable")
def disable_daemon(name: str):
    _ensure_seed_data()
    daemon = _get_daemon_profile(name)
    daemon.enabled = False
    return daemon.to_dict()


@app.post("/daemons/{name}/run")
def run_daemon(name: str):
    _ensure_seed_data()
    daemon = _get_daemon_profile(name)
    if not daemon.enabled:
        raise HTTPException(status_code=400, detail="Daemon is disabled.")
    record = _record_operation(
        actor=f"daemon:{name}",
        intent=f"{name}.run",
        triggered_by="manual",
        touches=[
            {"system": name, "resource_id": name, "action": "execute"},
        ],
        metadata={"manual_trigger": True, "scopes": daemon.scopes},
    )
    daemon.last_run = record.finished_at or datetime.utcnow()
    return {"status": "queued", "operation_id": record.id}


@app.get("/projects")
def list_projects():
    return [asdict(project) for project in sample_projects]


@app.get("/billing/usage")
def billing_usage():
    total = billing_engine.estimate_cost(usage_records)
    return {
        "records": [
            {
                "id": r.id,
                "category": r.category,
                "quantity": r.quantity,
                "unit": r.unit,
                "ts": r.ts.isoformat(),
            }
            for r in usage_records
        ],
        "estimated_cost": round(total, 4),
    }


@app.get("/planes/status")
def planes_status():
    backend = data_plane.backend
    collections = list(getattr(backend, "store", {}).keys())
    return {
        "data_plane": {"collections": collections},
        "control_plane": {"middlewares": len(control_plane.middlewares)},
        "governance_plane": {
            "policy": governance_plane.engine.__class__.__name__,
        },
    }


@app.get("/failures")
def failure_dashboard():
    """Expose Section 14 failure summaries for observability tooling."""

    return {
        "summary": failure_registry.summarize_events(),
        "signals": failure_registry.summarize_signals(),
    }
