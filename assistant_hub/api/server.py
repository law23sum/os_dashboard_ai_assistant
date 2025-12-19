"""FastAPI application that exposes assistant_hub data to the React desktop client."""
from __future__ import annotations

import logging
import sqlite3
from contextlib import closing
from contextvars import ContextVar
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal, Tuple
import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Scope, Receive, Send

from ai_os.app.system_monitor import get_system_stats
from assistant_core.cognitive_framework import CognitiveFrameworkManager, DaemonStatus

from ..ai import DEFAULT_SYSTEM_PROMPT, generate_ai_reply
from ..db import (
    CHAT_ROLES,
    ChatMessage,
    PERSONAS,
    Project,
    Task,
    db_delete_project,
    db_delete_task,
    db_insert_chat_message,
    db_insert_task,
    db_update_task,
    db_upsert_project,
    init_db,
    load_state,
    load_settings,
    load_security_status,
    save_settings,
    Settings,
)
from ..integrations import IntegrationAPIGateway
from ..research_workspace import ResearchWorkspaceState
from ..demo_seed import ensure_demo_data
from assistant_hub.config import DB_PATH
from assistant_hub.writer_workspace import WriterWorkspaceState
from assistant_hub.dashboard_workspace import build_dashboard_snapshot
from assistant_hub.projects_workspace import build_project_snapshot
from assistant_hub.analytics_workspace import build_analytics_summary, build_analytics_report
from assistant_hub.integrations_workspace import IntegrationsWorkspaceState
from assistant_hub.monitoring_workspace import MonitoringWorkspaceState
from ..sync_scheduler import create_default_scheduler
from ..terminal import run_bash_command
from assistant_hub.command_catalog import command_catalog
from assistant_hub.theme import get_theme_definition, list_available_themes
from backend_api.routers import (
    api_connectors as api_connectors_router,
    ai_systems as ai_systems_router,
    audit as audit_router,
    autofix as autofix_router,
    capsules as capsules_router,
    coach as coach_router,
    computer_vision as computer_vision_router,
    edge_computing as edge_router,
    git as git_router,
    intelligence as intelligence_router,
    intents as intents_router,
    network_monitoring as network_router,
    neural_architecture as neural_architecture_router,
    office as office_router,
    personas as personas_router,
    projects as projects_router,
    reasoning as reasoning_router,
    runtime_diagnostics as runtime_router,
    search as search_router,
    security_threat as security_router,
    templates as templates_router,
    workflow_orchestration as workflows_router,
    workspace as workspace_router,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"
LEGACY_UI_DIST = REPO_ROOT / "ui" / "web" / "dist"
SPEC_SHEET_PATH = REPO_ROOT / "Technical Spec Sheet (Version 6 Latest Version).pdf"
logger = logging.getLogger(__name__)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class StripPrefixMiddleware:
    """Allow clients to access routes with an optional leading prefix (e.g., /api)."""

    def __init__(
        self,
        app: ASGIApp,
        prefix: str = "/api",
        exclusions: Tuple[str, ...] = (),
    ) -> None:
        if not prefix.startswith("/"):
            raise ValueError("Prefix must start with '/'.")
        if prefix != "/" and prefix.endswith("/"):
            prefix = prefix.rstrip("/")
        self.app = app
        self.prefix = prefix
        self.exclusions = tuple(exclusions)
        logger.info("StripPrefixMiddleware enabled for prefix '%s'", self.prefix)

    def _should_strip(self, path: str) -> bool:
        if not path.startswith(self.prefix):
            return False
        if self.exclusions:
            for excluded in self.exclusions:
                if path.startswith(excluded):
                    return False
        return path == self.prefix or path.startswith(f"{self.prefix}/")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in {"http", "websocket"}:
            path = scope.get("path") or ""
            if self._should_strip(path):
                new_scope = dict(scope)
                trimmed = path[len(self.prefix) :] or "/"
                new_scope["path"] = trimmed
                raw_path = scope.get("raw_path")
                if isinstance(raw_path, (bytes, bytearray)):
                    new_scope["raw_path"] = trimmed.encode("utf-8")
                scope = new_scope
        await self.app(scope, receive, send)


class CorrelationIdMiddleware:
    """Assign a correlation ID to every request and expose it via headers/context."""

    def __init__(self, app: ASGIApp, header_name: str = "x-correlation-id") -> None:
        self.app = app
        self.header_name = header_name.lower()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        existing = headers.get(self.header_name.encode())
        correlation_id = (
            existing.decode("utf-8") if existing else str(uuid.uuid4())
        )
        scope["correlation_id"] = correlation_id
        token = request_id_ctx.set(correlation_id)
        start = time.perf_counter()

        async def send_wrapper(message: Dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append(self.header_name, correlation_id)
                duration_ms = int((time.perf_counter() - start) * 1000)
                headers.setdefault("x-response-time-ms", str(duration_ms))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_ctx.reset(token)


def _current_correlation_id() -> str:
    cid = request_id_ctx.get()
    return cid or ""


class TaskPayload(BaseModel):
    title: str
    project: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None


class ProjectPayload(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    priority: Optional[str] = "MEDIUM"


class ChatPayload(BaseModel):
    message: str
    persona: Optional[str] = None
    system_prompt: Optional[str] = DEFAULT_SYSTEM_PROMPT


class ChatMessageRequest(BaseModel):
    persona: str = "Chris"
    role: str = "user"
    kind: str = "chat"
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    persona: str
    role: str
    kind: str
    content: str
    created_at: str


class CommandPayload(BaseModel):
    command: str
    cwd: Optional[str] = None


class SimulationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    type: str = Field(..., description="Simulation type identifier")
    model_id: str = Field(..., description="Model identifier to run")
    iterations: int = Field(ge=1, default=1000)


class ExperimentDesignRequest(BaseModel):
    type: str = Field("parameter_sweep", description="Design template name")
    variables: List[str] = Field(default_factory=list)


class SimulationRequestCompat(BaseModel):
    """Compatible request model for frontend that uses sim_type instead of type."""
    model_config = ConfigDict(protected_namespaces=())
    sim_type: str = Field(..., description="Simulation type identifier")
    model_id: str = Field(..., description="Model identifier to run")
    iterations: int = Field(ge=1, default=1000)


class ExperimentDesignRequestCompat(BaseModel):
    """Compatible request model for frontend that uses design_type instead of type."""
    design_type: str = Field("parameter_sweep", description="Design template name")
    variables: List[str] = Field(default_factory=list)


class WriterDocumentPayload(BaseModel):
    title: str
    doc_type: str = Field("Article", alias="type")
    summary: Optional[str] = None
    theme: Optional[str] = None


class WriterNarrativePayload(BaseModel):
    title: Optional[str] = "Untitled Narrative"
    doc_type: str = Field("Article", alias="type")
    genre: str = "Creative"
    theme: Optional[str] = None


class WriterSavePayload(BaseModel):
    content: str


class SettingsResponse(BaseModel):
    theme: str
    default_view: str
    show_system_status: bool
    font_scale: str
    data_preferences: Dict[str, bool]
    change_permission_mode: Optional[str] = None
    continuity_mode: Optional[str] = None
    risk_appetite: Optional[str] = None


class SettingsUpdatePayload(BaseModel):
    theme: Optional[str] = None
    default_view: Optional[str] = None
    show_system_status: Optional[bool] = None
    font_scale: Optional[str] = None
    data_preferences: Optional[Dict[str, bool]] = None
    change_permission_mode: Optional[str] = None
    continuity_mode: Optional[str] = None
    risk_appetite: Optional[str] = None


class NASRequest(BaseModel):
    action: str = Field(..., description="NAS action: start_search, resume_search, evaluate_best, export_architecture")
    search_space: str = Field("conv_nets", description="Search space type")
    fitness_metric: str = Field("accuracy", description="Fitness metric to optimize")
    population_size: int = Field(50, ge=10, le=500)
    generations: int = Field(100, ge=10, le=1000)


class SecurityRequest(BaseModel):
    action: str = Field(..., description="Security action: scan, report, update, configure")
    scan_type: str = Field("full_scan", description="Type of security scan")
    target: str = Field("all_systems", description="Scan target")


class EdgeRequest(BaseModel):
    action: str = Field(..., description="Edge action: deploy, status, configure, sync, optimize")
    node_id: Optional[str] = Field(None, description="Target node ID")
    deployment_config: Optional[Dict[str, Any]] = Field(None, description="Deployment configuration")


class WorkflowRequest(BaseModel):
    action: str = Field(..., description="Workflow action: start, stop, view, configure, create")
    workflow_id: Optional[str] = Field(None, description="Workflow identifier")
    config: Optional[Dict[str, Any]] = Field(None, description="Workflow configuration")


class ThemeResponse(BaseModel):
    name: str
    label: str
    tokens: Dict[str, str]
    gradients: Dict[str, str] = Field(default_factory=dict)
    available: List[str] = Field(default_factory=list)


class IntegrationActionPayload(BaseModel):
    action: Literal["connect", "disconnect", "test"] = Field(
        ..., description="Action to perform on the connector"
    )


def create_app(
    db_path: Path | None = None, frontend_dist: Path | None = None
) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(title="OS Dashboard API", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        StripPrefixMiddleware,
        prefix="/api",
        exclusions=("/api/docs",),
    )
    app.add_middleware(CorrelationIdMiddleware)

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException):
        cid = _current_correlation_id()
        payload = {
            "error": {
                "type": exc.__class__.__name__,
                "code": exc.status_code,
                "message": exc.detail,
            },
            "correlation_id": cid,
        }
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception):
        cid = _current_correlation_id()
        logger.exception("Unhandled exception", extra={"correlation_id": cid})
        payload = {
            "error": {
                "type": exc.__class__.__name__,
                "code": 500,
                "message": "Internal server error",
            },
            "correlation_id": cid,
        }
        return JSONResponse(status_code=500, content=payload)

    # Surface the realtime Office router so the React frontend can read metrics
    # and trigger AI actions without spinning up the separate demo server.
    app.include_router(office_router.router, prefix="/office", tags=["office"])
    # Additional routers from backend_api to keep advanced surfaces in sync across
    # the desktop (Tkinter/PyWebView) and browser clients.
    app.include_router(api_connectors_router.router, prefix="/api-connectors", tags=["api_connectors"])
    app.include_router(ai_systems_router.router, prefix="/ai", tags=["ai_systems"])
    app.include_router(audit_router.router, prefix="/audit", tags=["audit"])
    app.include_router(autofix_router.router, prefix="/autofix", tags=["autofix"])
    app.include_router(capsules_router.router, prefix="/ai", tags=["capsules"])
    app.include_router(coach_router.router, prefix="/ai", tags=["coach"])
    app.include_router(computer_vision_router.router, prefix="/computer-vision", tags=["computer_vision"])
    app.include_router(edge_router.router, prefix="/edge-computing", tags=["edge_computing"])
    app.include_router(git_router.router, tags=["git"])
    app.include_router(intelligence_router.router, prefix="/intelligence", tags=["intelligence"])
    app.include_router(intents_router.router, tags=["intents"])
    app.include_router(network_router.router, prefix="/network", tags=["network"])
    app.include_router(neural_architecture_router.router, prefix="/neural-architecture", tags=["neural_architecture"])
    app.include_router(personas_router.router, prefix="/personas", tags=["personas"])
    app.include_router(reasoning_router.router, prefix="/reasoning", tags=["reasoning"])
    app.include_router(runtime_router.router, tags=["runtime"])
    app.include_router(search_router.router, prefix="/search", tags=["search"])
    app.include_router(security_router.router, prefix="/security", tags=["security"])
    app.include_router(templates_router.router, prefix="/templates", tags=["templates"])
    app.include_router(workflows_router.router, prefix="/workflows", tags=["workflows"])
    app.include_router(workspace_router.router, tags=["workspace"])

    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        app.mount("/docs", StaticFiles(directory=docs_dir, html=True), name="docs")

    cyberchef_dir = REPO_ROOT / "CyberChef_v10.19.4"
    if cyberchef_dir.exists():
        app.mount(
            "/cyberchef", StaticFiles(directory=cyberchef_dir, html=True), name="cyberchef"
        )

    db_path = Path(db_path or DB_PATH)
    # Ensure the DB exists with all required tables
    init_conn = init_db(db_path)
    ensure_demo_data(init_conn)
    init_conn.close()

    def connect() -> sqlite3.Connection:
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _db_ready() -> bool:
        try:
            with closing(connect()) as conn:
                conn.execute("SELECT 1").fetchone()
            return True
        except Exception:
            logger.exception("Database readiness check failed")
            return False

    scheduler_conn = sqlite3.connect(str(db_path), check_same_thread=False)
    scheduler_conn.row_factory = sqlite3.Row
    scheduler = create_default_scheduler(scheduler_conn)
    gateway = IntegrationAPIGateway(scheduler_conn, scheduler=scheduler)
    research_state = ResearchWorkspaceState()
    writer_state = WriterWorkspaceState()
    integrations_state = IntegrationsWorkspaceState()
    monitoring_state = MonitoringWorkspaceState()
    framework = CognitiveFrameworkManager()

    if frontend_dist is None:
        if FRONTEND_DIST.exists():
            frontend_dist = FRONTEND_DIST
        elif LEGACY_UI_DIST.exists():
            frontend_dist = LEGACY_UI_DIST

    index_path: Optional[Path] = None
    if frontend_dist:
        dist_path = Path(frontend_dist)
        if dist_path.exists():
            candidate = dist_path / "index.html"
            if candidate.exists():
                index_path = candidate
                
                def _get_index_html() -> str:
                    """Get index.html content with base tag injected."""
                    html_content = index_path.read_text(encoding="utf-8")
                    # Inject base tag if not present to ensure relative paths work correctly
                    if "<base" not in html_content.lower():
                        # Insert base tag right after <head>
                        html_content = html_content.replace(
                            "<head>",
                            '<head>\n    <base href="/app/">',
                            1
                        )
                    return html_content

                @app.get("/", include_in_schema=False)
                async def serve_root():
                    return Response(content=_get_index_html(), media_type="text/html")

                @app.get("/app", include_in_schema=False)
                async def serve_app_redirect():
                    """Redirect /app to /app/."""
                    from fastapi.responses import RedirectResponse
                    return RedirectResponse(url="/app/", status_code=301)

                @app.get("/app/", include_in_schema=False)
                async def serve_app_index():
                    """Serve index.html with base tag for proper asset resolution."""
                    return Response(content=_get_index_html(), media_type="text/html")

                # Mount static files for assets - this must come after the route handlers
                # Mount assets directory separately to ensure they're served correctly
                assets_dir = dist_path / "assets"
                if assets_dir.exists():
                    app.mount(
                        "/app/assets",
                        StaticFiles(directory=assets_dir),
                        name="spa-assets",
                    )
                
                # Mount other static directories
                for static_dir in ["docs"]:
                    static_path = dist_path / static_dir
                    if static_path.exists():
                        app.mount(
                            f"/app/{static_dir}",
                            StaticFiles(directory=static_path),
                            name=f"spa-{static_dir}",
                        )
                
                # Mount root for SPA routing (fallback to index.html for non-asset routes)
                @app.get("/app/{full_path:path}", include_in_schema=False)
                async def serve_spa_routes(full_path: str):
                    """Serve index.html for SPA routes, but not for assets."""
                    # Don't serve index.html for asset requests (they should be handled by mounts)
                    if full_path.startswith("assets/") or full_path.startswith("docs/"):
                        raise HTTPException(status_code=404, detail="Asset not found")
                    return Response(content=_get_index_html(), media_type="text/html")

    @app.on_event("startup")
    async def _initialize_framework():
        await framework.initialize()

    def _load_state() -> Any:
        with closing(connect()) as conn:
            return load_state(conn)

    def _load_settings_state() -> Settings:
        with closing(connect()) as conn:
            return load_settings(conn)

    def _chat_row_to_response(row: sqlite3.Row) -> ChatMessageResponse:
        payload = dict(row)
        return ChatMessageResponse(**payload)

    def _fetch_chat_messages(
        persona: Optional[str],
        limit: int,
        conn: sqlite3.Connection,
    ) -> List[ChatMessageResponse]:
        query = """
            SELECT id, persona, role, kind, content, created_at
            FROM chat_messages
        """
        params: List[Any] = []
        if persona:
            query += " WHERE persona = ?"
            params.append(persona)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return list(reversed([_chat_row_to_response(row) for row in rows]))

    @app.get("/settings", response_model=SettingsResponse)
    async def get_settings():
        settings = _load_settings_state()
        return SettingsResponse(
            theme=settings.theme,
            default_view=settings.default_view,
            show_system_status=settings.show_system_status,
            font_scale=settings.font_scale,
            data_preferences=dict(settings.data_preferences),
            change_permission_mode=settings.change_permission_mode,
            continuity_mode=settings.continuity_mode,
            risk_appetite=settings.risk_appetite,
        )

    @app.get("/api/docs/technical-spec-sheet")
    async def get_technical_spec_sheet():
        if not SPEC_SHEET_PATH.exists():
            raise HTTPException(status_code=404, detail="Technical Spec Sheet not found")
        return FileResponse(
            SPEC_SHEET_PATH,
            media_type="application/pdf",
            filename=SPEC_SHEET_PATH.name,
        )

    @app.put("/settings", response_model=SettingsResponse)
    async def update_settings(payload: SettingsUpdatePayload):
        updates = payload.model_dump(exclude_unset=True)
        with closing(connect()) as conn:
            settings = load_settings(conn)
            for key, value in updates.items():
                if key == "data_preferences" and isinstance(value, dict):
                    for pref_key, pref_value in value.items():
                        settings.data_preferences[pref_key] = bool(pref_value)
                elif key == "change_permission_mode" and isinstance(value, str):
                    settings.change_permission_mode = value
                    settings.auto_overwrite = value == "auto"
                elif hasattr(settings, key):
                    setattr(settings, key, value)  # type: ignore[arg-type]
            save_settings(conn, settings)
        return SettingsResponse(
            theme=settings.theme,
            default_view=settings.default_view,
            show_system_status=settings.show_system_status,
            font_scale=settings.font_scale,
            data_preferences=dict(settings.data_preferences),
            change_permission_mode=settings.change_permission_mode,
            continuity_mode=settings.continuity_mode,
            risk_appetite=settings.risk_appetite,
        )

    @app.get("/ui/theme", response_model=ThemeResponse)
    async def get_theme(name: Optional[str] = Query(None, description="Theme name")):
        resolved_name, definition = get_theme_definition(name)
        available = list(list_available_themes())
        tokens = definition.get("tokens", {})
        gradients = definition.get("gradients", {})
        return ThemeResponse(
            name=resolved_name,
            label=definition.get("label", resolved_name.title()),
            tokens=tokens if isinstance(tokens, dict) else {},
            gradients=gradients if isinstance(gradients, dict) else {},
            available=available,
        )

    @app.get("/analytics/summary")
    async def analytics_summary():
        state = _load_state()
        return build_analytics_summary(state)

    @app.get("/analytics/report")
    async def analytics_report():
        state = _load_state()
        return {"report": build_analytics_report(state)}

    @app.get("/integrations/summary")
    async def integrations_summary():
        return integrations_state.snapshot()

    @app.post("/integrations/connectors/{connector_id}/actions")
    async def connector_action(connector_id: str, payload: IntegrationActionPayload):
        if payload.action == "test":
            result = integrations_state.test_connector(connector_id)
            if result is None:
                raise HTTPException(status_code=404, detail="Connector not found")
            return {"success": result["success"], "detail": result["detail"]}

        connect = payload.action == "connect"
        connector = integrations_state.toggle_connection(connector_id, connect)
        if connector is None:
            raise HTTPException(status_code=404, detail="Connector not found")
        status = "connected" if connector.connected else "disconnected"
        return {
            "status": status,
            "connector": connector.__dict__,
        }

    @app.get("/monitoring/summary")
    async def monitoring_summary():
        return monitoring_state.snapshot()

    @app.post("/monitoring/actions")
    async def monitoring_action(payload: Dict[str, Any]):
        action = payload.get("action", "check_health")
        metrics = payload.get("system_metrics")
        window = payload.get("monitoring_window")
        thresholds = payload.get("alert_thresholds")
        try:
            result = monitoring_state.run_action(action, metrics, window, thresholds)
            return result
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    def _fetch_agent_runs(limit: int) -> List[Dict[str, Any]]:
        with closing(connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, agent, action_type, input_context, output_summary,
                       related_files, git_commit_hash, created_at
                FROM agent_runs
                ORDER BY datetime(created_at) DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]

    def _search_documents(query: str, limit: int = 30) -> List[Dict[str, Any]]:
        pattern = f"%{query.lower()}%"
        results: List[Dict[str, Any]] = []
        with closing(connect()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT title, notes, project
                FROM tasks
                WHERE lower(title) LIKE ? OR lower(notes) LIKE ?
                ORDER BY datetime(created_at) DESC
                LIMIT ?
                """,
                (pattern, pattern, limit),
            )
            for row in cursor.fetchall():
                results.append(
                    {
                        "node_title": row["title"],
                        "text_snippet": row["notes"],
                        "system": f"task:{row['project']}",
                    }
                )

            cursor.execute(
                """
                SELECT name, description, status
                FROM projects
                WHERE lower(name) LIKE ? OR lower(description) LIKE ?
                LIMIT ?
                """,
                (pattern, pattern, limit),
            )
            for row in cursor.fetchall():
                results.append(
                    {
                        "node_title": row["name"],
                        "text_snippet": row["description"],
                        "system": f"project:{row['status']}",
                    }
                )

        return results[:limit]

    def _collect_web_pages() -> List[Dict[str, str]]:
        pages: List[Dict[str, str]] = []
        docs_root = REPO_ROOT / "docs"
        if docs_root.exists():
            for path in docs_root.rglob("*.html"):
                rel = path.relative_to(docs_root).as_posix()
                pages.append(
                    {
                        "label": rel,
                        "url": f"/docs/{rel}",
                        "kind": "html",
                    }
                )

        cyberchef_root = REPO_ROOT / "CyberChef_v10.19.4"
        if cyberchef_root.exists():
            pages.append(
                {
                    "label": "CyberChef",
                    "url": "/cyberchef/CyberChef_v10.19.4.html",
                    "kind": "app",
                }
            )
        return pages

    def _daemon_by_slug(slug: str):
        slug = slug.lower()
        for daemon in framework.daemon_runtime.daemons.values():
            if daemon.daemon_type.value == slug or daemon.id == slug:
                return daemon
        raise HTTPException(status_code=404, detail=f"Unknown daemon: {slug}")

    @app.get("/health")
    def health(request: Request):
        cid = _current_correlation_id()
        return {"status": "ok", "correlation_id": cid}

    @app.get("/ready")
    def ready(request: Request):
        cid = _current_correlation_id()
        return {
            "status": "ok" if _db_ready() else "degraded",
            "correlation_id": cid,
        }

    @app.get("/system")
    def system_status():
        return get_system_stats()

    @app.get("/planes/status")
    def plane_status():
        state = _load_state()
        collections = sorted({task.project for task in state.tasks})
        daemons = framework.daemon_runtime.get_daemon_status()
        data_plane = {
            "collections": collections,
            "task_count": len(state.tasks),
            "project_count": len(state.projects),
        }
        control_plane = {
            "daemons": len(daemons),
            "running": sum(1 for info in daemons.values() if info["status"] == DaemonStatus.RUNNING.value),
        }
        governance_plane = {
            "active_persona": state.active_persona,
            "policies": ["default_guardrails"],
        }
        return {
            "data_plane": data_plane,
            "control_plane": control_plane,
            "governance_plane": governance_plane,
        }

    @app.get("/projects")
    def list_projects():
        state = _load_state()
        return {"projects": [asdict(project) for project in state.projects]}

    @app.post("/projects")
    def add_project(payload: ProjectPayload):
        with closing(connect()) as conn:
            project = Project(
                name=payload.name,
                description=payload.description or "",
                status=payload.status or "active",
                priority=(payload.priority or "MEDIUM").upper(),
            )
            db_upsert_project(conn, project)
            return {"project": asdict(project)}

    @app.delete("/projects/{project_name}")
    def delete_project(project_name: str):
        with closing(connect()) as conn:
            db_delete_project(conn, project_name)
        return {"deleted": project_name}

    @app.get("/projects/links", response_model=List[projects_router.ProjectLinkResponse])
    async def list_project_links(
        project: Optional[str] = None, integration: Optional[str] = None
    ):
        return await projects_router.list_links(project=project, integration=integration)

    @app.get("/projects/ledger", response_model=List[projects_router.ProjectLedgerEvent])
    async def list_project_ledger(project: Optional[str] = None, limit: int = 50):
        return await projects_router.list_project_ledger(project=project, limit=limit)

    @app.get(
        "/projects/intelligence",
        response_model=List[projects_router.ProjectIntelligenceResponse],
    )
    async def list_project_intelligence():
        return await projects_router.list_project_intelligence()

    @app.get(
        "/projects/{project_name}/links",
        response_model=List[projects_router.ProjectLinkResponse],
    )
    async def get_project_links(project_name: str, integration: Optional[str] = None):
        return await projects_router.get_project_links(
            project_name=project_name, integration=integration
        )

    @app.get(
        "/projects/{project_name}/ledger",
        response_model=List[projects_router.ProjectLedgerEvent],
    )
    async def get_project_ledger(project_name: str, limit: int = 50):
        return await projects_router.get_project_ledger(project_name=project_name, limit=limit)

    @app.get(
        "/projects/{project_name}/intelligence",
        response_model=projects_router.ProjectIntelligenceResponse,
    )
    async def get_project_intelligence(project_name: str):
        return await projects_router.get_project_intelligence(project_name=project_name)

    @app.get(
        "/projects/{project_name}/insights",
        response_model=projects_router.ProjectInsightResponse,
    )
    async def get_project_insights(project_name: str):
        return await projects_router.get_project_insights(project_name=project_name)

    @app.get("/projects/{project_name}/trf", response_model=projects_router.ProjectTRFResponse)
    async def get_project_trf(project_name: str, limit: int = 10):
        return await projects_router.get_project_trf(project_name=project_name, limit=limit)

    @app.get("/tasks")
    def list_tasks(limit: int = Query(100, ge=1, le=500)):
        state = _load_state()
        return {"tasks": [asdict(task) for task in state.tasks[:limit]], "limit": limit}

    @app.post("/tasks")
    def add_task(payload: TaskPayload):
        state = _load_state()
        with closing(connect()) as conn:
            task = Task(
                id=0,
                title=payload.title,
                project=payload.project or "General",
                status=(payload.status or "TODO").upper(),
                priority=(payload.priority or "MEDIUM").upper(),
                due_date=payload.due_date or "",
                notes=payload.notes or "",
                owner=payload.owner or state.active_persona,
            )
            new_id = db_insert_task(conn, task)
            task.id = new_id
            return {"task": asdict(task)}

    @app.put("/tasks/{task_id}")
    def update_task(task_id: int, payload: TaskPayload):
        state = _load_state()
        existing = next((task for task in state.tasks if task.id == task_id), None)
        if not existing:
            raise HTTPException(status_code=404, detail="Task not found")
        for field_name, value in payload.dict(exclude_unset=True).items():
            if value is None:
                continue
            if field_name in ("status", "priority"):
                value = value.upper()
            setattr(existing, field_name, value)
        with closing(connect()) as conn:
            db_update_task(conn, existing)
        return {"task": asdict(existing)}

    @app.delete("/tasks/{task_id}")
    def delete_task(task_id: int):
        with closing(connect()) as conn:
            db_delete_task(conn, task_id)
        return {"deleted": task_id}

    @app.get("/search")
    def search(query: str = Query(..., min_length=2)):
        return {"query": query, "results": _search_documents(query)}

    @app.get("/web/pages")
    def web_pages():
        return {"pages": _collect_web_pages()}

    @app.get("/operations")
    def operations(limit: int = Query(25, ge=1, le=200)):
        return {"operations": _fetch_agent_runs(limit), "limit": limit}

    @app.get("/operations/summary")
    def operations_summary():
        """Return summary statistics for operations/agent runs."""
        operations = _fetch_agent_runs(200)
        total = len(operations)
        
        # Calculate statistics
        by_agent = {}
        by_action = {}
        recent_24h = 0
        
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=24)
        
        for op in operations:
            agent = op.get("agent", "unknown")
            action = op.get("action_type", "unknown")
            created_at = op.get("created_at", "")
            
            by_agent[agent] = by_agent.get(agent, 0) + 1
            by_action[action] = by_action.get(action, 0) + 1
            
            try:
                op_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if op_time > cutoff:
                    recent_24h += 1
            except (ValueError, AttributeError):
                pass
        
        return {
            "total": total,
            "recent_24h": recent_24h,
            "by_agent": by_agent,
            "by_action": by_action,
            "last_updated": now.isoformat() + "Z"
        }

    @app.get("/chat", response_model=List[ChatMessageResponse])
    def list_chat_messages(
        persona: Optional[str] = Query(None, description="Filter by persona"),
        limit: int = Query(100, ge=1, le=500),
    ):
        with closing(connect()) as conn:
            return _fetch_chat_messages(persona, limit, conn)

    @app.post("/chat", response_model=ChatMessageResponse, status_code=201)
    def create_chat_message(payload: ChatMessageRequest):
        if payload.persona not in PERSONAS:
            raise HTTPException(status_code=400, detail="Unknown persona")
        if payload.role not in CHAT_ROLES:
            raise HTTPException(status_code=400, detail="Invalid role")

        chat_message = ChatMessage(
            id=0,
            persona=payload.persona,
            role=payload.role,
            kind=payload.kind,
            content=payload.content,
        )
        with closing(connect()) as conn:
            new_id = db_insert_chat_message(conn, chat_message)
            cursor = conn.execute(
                """
                SELECT id, persona, role, kind, content, created_at
                FROM chat_messages
                WHERE id = ?
                """,
                (new_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=500, detail="Failed to load chat message")
            return _chat_row_to_response(row)

    @app.get("/audit/{operation_id}")
    def audit_detail(operation_id: int):
        with closing(connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, agent, action_type, input_context, output_summary,
                       related_files, git_commit_hash, created_at
                FROM agent_runs
                WHERE id = ?
                """,
                (operation_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Operation not found")
            return {"operation": dict(row)}

    @app.get("/daemons")
    def daemon_status():
        statuses = framework.daemon_runtime.get_daemon_status()
        payload = []
        for daemon_id, meta in statuses.items():
            daemon = framework.daemon_runtime.daemons.get(daemon_id)
            payload.append(
                {
                    "id": daemon_id,
                    "name": daemon.daemon_type.value if daemon else meta["type"],
                    "type": meta["type"],
                    "status": meta["status"],
                    "enabled": meta["status"] == DaemonStatus.RUNNING.value,
                    "last_execution": meta["last_execution"],
                    "execution_count": meta["execution_count"],
                    "schedule_interval": getattr(daemon.config, "schedule_interval", None) if daemon else None,
                }
            )
        return {"daemons": payload}

    @app.post("/daemons/{daemon_slug}/{action}")
    async def toggle_daemon(daemon_slug: str, action: str):
        daemon = _daemon_by_slug(daemon_slug)
        if action == "enable":
            await daemon.start()
            return {"status": "running", "daemon": daemon.daemon_type.value}
        if action == "disable":
            await daemon.stop()
            return {"status": "stopped", "daemon": daemon.daemon_type.value}
        if action == "run":
            result = await daemon.execute({"trigger": "manual"})
            return {"status": "completed", "daemon": daemon.daemon_type.value, "result": result}
        raise HTTPException(status_code=400, detail="Unsupported action")

    @app.post("/ai/ask")
    async def ai_console(payload: ChatPayload):
        persona = payload.persona or _load_state().active_persona
        if persona not in PERSONAS:
            persona = PERSONAS[0]
        with closing(connect()) as conn:
            history_state = load_state(conn)
            history = history_state.chat_messages

        user_message = ChatMessage(id=0, persona=persona, role="user", content=payload.message)
        history.append(user_message)

        reply, error, _ = generate_ai_reply(
            history,
            persona=persona,
            prompt=payload.message,
            system_prompt=payload.system_prompt or DEFAULT_SYSTEM_PROMPT,
            enable_shell=False,
        )
        if error:
            raise HTTPException(status_code=500, detail=error)

        with closing(connect()) as conn:
            db_insert_chat_message(conn, user_message)
            db_insert_chat_message(
                conn,
                ChatMessage(id=0, persona=persona, role="assistant", content=reply),
            )

        return {"response": reply, "persona": persona}

    @app.get("/terminal/commands")
    def list_commands():
        return command_catalog()

    @app.post("/terminal")
    def run_command(payload: CommandPayload):
        result = run_bash_command(payload.command, cwd=payload.cwd or ".")
        return {
            "command": payload.command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "shell": result.shell_path,
            "cwd": result.cwd,
            "ok": result.ok,
        }

    @app.get("/integrations")
    def list_integrations():
        return {"integrations": gateway.available_integrations()}

    @app.get("/billing/usage")
    def billing_usage(limit: int = Query(20, ge=1, le=100)):
        rows = _fetch_agent_runs(limit)
        estimated_cost = round(len(rows) * 0.02, 2)
        return {"estimated_cost": estimated_cost, "currency": "USD", "records": rows}

    @app.get("/research/workspace")
    def research_workspace():
        return research_state.snapshot()

    @app.get("/research/snapshot")
    def research_snapshot():
        """Alias for /research/workspace to match frontend expectations."""
        return research_state.snapshot()

    @app.post("/research/run-simulation")
    def run_simulation(request: SimulationRequest):
        experiment = research_state.start_simulation(request.type, request.model_id, request.iterations)
        return {"experiment": experiment, "workspace": research_state.snapshot()}

    @app.post("/research/run")
    def run_simulation_compat(request: SimulationRequestCompat):
        """Compatible endpoint for frontend that uses sim_type instead of type."""
        experiment = research_state.start_simulation(request.sim_type, request.model_id, request.iterations)
        return {"experiment": experiment, "workspace": research_state.snapshot()}

    @app.post("/research/design-experiment")
    def design_experiment(request: ExperimentDesignRequest):
        design = research_state.design_experiment(request.type, request.variables)
        return {"design": design, "workspace": research_state.snapshot()}

    @app.post("/research/design")
    def design_experiment_compat(request: ExperimentDesignRequestCompat):
        """Compatible endpoint for frontend that uses design_type instead of type."""
        design = research_state.design_experiment(request.design_type, request.variables)
        return {"design": design, "workspace": research_state.snapshot()}

    @app.get("/writer/snapshot")
    def writer_snapshot():
        return writer_state.snapshot()

    @app.post("/writer/documents")
    def writer_create_document(payload: WriterDocumentPayload):
        doc = writer_state.create_document(
            payload.title,
            payload.doc_type,
            summary=payload.summary,
            theme=payload.theme,
        )
        return {"document": doc, "workspace": writer_state.snapshot()}

    @app.post("/writer/documents/{document_id}/save")
    def writer_save_document(document_id: str, payload: WriterSavePayload):
        try:
            doc = writer_state.save_document(document_id, payload.content)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"document": doc, "workspace": writer_state.snapshot()}

    @app.post("/writer/narrative")
    def writer_generate_narrative(payload: WriterNarrativePayload):
        content = writer_state.generate_narrative(
            payload.doc_type,
            payload.theme or "adventure",
            payload.genre,
            payload.title or "Untitled Narrative",
        )
        return {"content": content}

    @app.post("/writer/stats/nudge")
    def writer_nudge_stats():
        delta = writer_state.simulate_activity()
        return {"delta_words": delta, "stats": writer_state.stats}

    @app.get("/dashboard/stats")
    def dashboard_stats():
        state = _load_state()
        tasks = list(getattr(state, "tasks", []) or [])
        projects = list(getattr(state, "projects", []) or [])

        tasks_by_status: Dict[str, int] = {}
        tasks_by_priority: Dict[str, int] = {}
        for task in tasks:
            tasks_by_status[task.status] = tasks_by_status.get(task.status, 0) + 1
            tasks_by_priority[task.priority] = tasks_by_priority.get(task.priority, 0) + 1

        total_projects = len(projects)
        active_projects = sum(1 for proj in projects if getattr(proj, "status", "").lower() == "active")

        system_stats = get_system_stats()
        memory = system_stats.get("memory") or {}
        disk = system_stats.get("disk") or {}
        mem_percent = memory.get("percent")
        if mem_percent is None and memory.get("total"):
            mem_percent = round((memory.get("used", 0) / max(memory.get("total", 1), 1)) * 100, 2)
        disk_percent = disk.get("percent")
        if disk_percent is None and disk.get("total"):
            disk_percent = round((disk.get("used", 0) / max(disk.get("total", 1), 1)) * 100, 2)
        with closing(connect()) as conn:
            security_status = load_security_status(conn)

        return {
            "total_tasks": len(tasks),
            "tasks_by_status": tasks_by_status,
            "tasks_by_priority": tasks_by_priority,
            "total_projects": total_projects,
            "active_projects": active_projects,
            "system_stats": {
                "cpu_percent": system_stats.get("cpu_percent", 0),
                "memory_percent": mem_percent or 0,
                "disk_percent": disk_percent or 0,
            },
            "security_status": {
                "status": security_status.status,
                "message": security_status.message,
                "updated_at": security_status.updated_at,
                "source": security_status.source,
            },
        }

    @app.get("/dashboard/summary")
    def dashboard_summary():
        state = _load_state()
        snapshot = build_dashboard_snapshot(state)
        data = snapshot.to_dict()
        data["web_pages"] = _collect_web_pages()
        return data

    @app.get("/projects/summary")
    def projects_summary():
        state = _load_state()
        snapshot = build_project_snapshot(state.projects)
        return snapshot.to_dict()

    @app.post("/intelligence/nas")
    def neural_architecture_search(request: NASRequest):
        """Neural Architecture Search endpoint."""
        # Placeholder implementation - would integrate with actual NAS system
        return {
            "status": f"NAS {request.action} initiated",
            "search_space": request.search_space,
            "fitness_metric": request.fitness_metric,
            "population_size": request.population_size,
            "generations": request.generations,
            "best_architecture": "Searching...",
            "current_generation": 0,
            "message": "Neural Architecture Search is running in background"
        }

    @app.post("/security/threats")
    def security_threat_detection(request: SecurityRequest):
        """Security Threat Detection endpoint."""
        # Placeholder implementation - would integrate with actual security system
        threats_found = 0
        risk_score = "Low"
        
        if request.scan_type == "full_scan":
            threats_found = 2
            risk_score = "Medium"
        
        return {
            "status": "🟢 Scan completed",
            "scan_type": request.scan_type,
            "target": request.target,
            "threats_found": threats_found,
            "risk_score": risk_score,
            "scanned_items": 1247,
            "duration_seconds": 3.5,
            "message": f"Security {request.action} completed successfully"
        }

    @app.post("/edge/operations")
    def edge_computing_operations(request: EdgeRequest):
        """Edge Computing & Distributed AI endpoint."""
        # Placeholder implementation - would integrate with actual edge computing system
        return {
            "status": f"Edge {request.action} completed",
            "node_id": request.node_id or "all",
            "network_status": "🌐 Network: 5/5 nodes online - Optimal performance",
            "deployment_config": request.deployment_config or {},
            "nodes_online": 5,
            "total_nodes": 5,
            "avg_latency_ms": 45,
            "throughput_gbps": 2.4,
            "efficiency_percent": 94.2,
            "message": "Edge operation completed successfully"
        }

    @app.post("/workflows/orchestrate")
    def workflow_orchestration(request: WorkflowRequest):
        """Workflow Orchestration endpoint."""
        # Placeholder implementation - would integrate with actual workflow system
        return {
            "status": f"🔄 Orchestrator: {request.action} completed",
            "workflow_id": request.workflow_id or "default",
            "config": request.config or {},
            "active_count": 3,
            "completed_today": 12,
            "success_rate": "96.7%",
            "running_workflows": [
                {"id": "1", "name": "Data Processing Pipeline", "progress": 67},
                {"id": "2", "name": "ML Model Training", "progress": 23},
                {"id": "3", "name": "Analytics Report", "progress": 89}
            ],
            "message": "Workflow operation completed successfully"
        }

    return app


def run_app(host: str = "127.0.0.1", port: int = 8071):
    """Utility to run API with uvicorn."""
    import uvicorn
    from pathlib import Path

    # Check for SSL certificates
    repo_root = Path(__file__).resolve().parents[3]
    cert_dir = repo_root / "certs"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    ssl_keyfile = None
    ssl_certfile = None
    if cert_file.exists() and key_file.exists():
        ssl_keyfile = str(key_file)
        ssl_certfile = str(cert_file)
        print(f"🔒 Starting with SSL on https://{host}:{port}")
    else:
        print(f"🌐 Starting server on http://{host}:{port}")

    uvicorn.run(
        create_app(), 
        host=host, 
        port=port, 
        log_level="info",
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )
