"""
FastAPI backend for AI OS.
Provides REST API endpoints to replace the Tkinter GUI frontend.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import importlib
import json
import logging
import sys
import os
import time
import traceback
import asyncio
from uuid import uuid4
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
REPO_ROOT = parent_dir
SPEC_SHEET_PATH = REPO_ROOT / "Technical Spec Sheet (Version 6 Latest Version).pdf"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and ensure demo users exist on startup."""
    audit_runner = None
    audit_emitter = None
    audit_session_correlation = None
    audit_session_started = None
    try:
        from backend_api.db import db_session
        from backend_api.routers.auth import _ensure_demo_users

        with db_session() as db:
            db.execute("SELECT 1").fetchone()

        try:
            await _ensure_demo_users()
        except Exception as exc:
            logging.warning("Could not ensure demo users on startup (non-fatal): %s", exc)

        try:
            from assistant_core.audit_maintenance import AuditMaintenanceRunner

            audit_runner = AuditMaintenanceRunner()
            await audit_runner.start()
            app.state.audit_maintenance = audit_runner
        except Exception as exc:
            logging.warning("Audit maintenance startup skipped: %s", exc)

        try:
            from assistant_hub.audit.sdk import get_default_emitter, new_correlation_id
            from assistant_hub.config import (
                ATTACHMENTS_DIR,
                DATA_DIR,
                DB_PATH,
                FILE_CACHE_DIR,
                INTEGRATIONS_DIR,
            )

            audit_emitter = get_default_emitter(agent_id="os_dashboard")
            audit_session_correlation = new_correlation_id()
            audit_session_started = datetime.now(timezone.utc)
            app.state.audit_session_correlation = audit_session_correlation
            app.state.audit_session_started = audit_session_started
            audit_emitter.emit(
                event_type="SESSION_START",
                message="Backend session started",
                payload={
                    "policy_snapshot": {
                        "data_dir": str(DATA_DIR),
                        "db_path": str(DB_PATH),
                        "attachments_dir": str(ATTACHMENTS_DIR),
                        "integrations_dir": str(INTEGRATIONS_DIR),
                        "file_cache_dir": str(FILE_CACHE_DIR),
                        "runtime_scope": os.getenv("OSDASH_RUNTIME_SCOPE", "host"),
                        "network_access": os.getenv("NETWORK_ACCESS", "unknown"),
                    },
                    "started_at": audit_session_started.isoformat(),
                },
                correlation_id=audit_session_correlation,
            )
        except Exception:
            audit_emitter = None

        logging.info("Database initialized")
    except Exception as exc:
        logging.error("Startup initialization failed: %s", exc, exc_info=True)

    try:
        yield
    finally:
        if audit_emitter:
            try:
                ended_at = datetime.now(timezone.utc)
                duration_ms = None
                if audit_session_started:
                    duration_ms = int((ended_at - audit_session_started).total_seconds() * 1000)
                audit_emitter.emit(
                    event_type="SESSION_END",
                    message="Backend session ended",
                    payload={
                        "ended_at": ended_at.isoformat(),
                        "duration_ms": duration_ms,
                    },
                    correlation_id=audit_session_correlation,
                )
            except Exception:
                pass
        if audit_runner:
            await audit_runner.stop()


app = FastAPI(
    title="AI OS API",
    description="REST API for AI OS",
    version="0.1.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware - more restrictive for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000", 
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:5176", "http://127.0.0.1:5176",
        "http://0.0.0.0:5173", "http://0.0.0.0:5174",
        "http://0.0.0.0:5175",
        "http://0.0.0.0:5176",
        # Electron file:// origin is often serialized as `null`
        "null",
        "https://localhost:3000", "https://127.0.0.1:3000",
        "https://localhost:5173", "https://127.0.0.1:5173",
        "https://localhost:5174", "https://127.0.0.1:5174",
        "https://localhost:5175", "https://127.0.0.1:5175",
        "https://localhost:5176", "https://127.0.0.1:5176",
        "https://0.0.0.0:5173", "https://0.0.0.0:5174",
        "https://0.0.0.0:5175",
        "https://0.0.0.0:5176",
        "https://0.0.0.0:8000", "https://localhost:8000", "https://127.0.0.1:8000"
    ],
    # Allow any localhost/loopback port and private network IPs for dev/preview builds.
    # This includes: localhost, 127.0.0.1, 0.0.0.0, 192.168.x.x, 10.x.x.x, 172.16-31.x.x
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods instead of "*"
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-OSD-Actor",
        "X-OSD-Cohort",
        "X-OSD-Release",
        "X-OSD-Flags",
    ],  # Explicit headers instead of "*"
    expose_headers=["Content-Type", "X-Total-Count"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# ---------------------------------------------------------------------------
# Request tracing + unified event log
# ---------------------------------------------------------------------------
def _extract_release_context(request: Request) -> dict:
    release_channel = (
        request.headers.get("x-osd-release")
        or os.getenv("OSD_RELEASE_CHANNEL")
        or os.getenv("RELEASE_CHANNEL")
    )
    cohort = request.headers.get("x-osd-cohort")
    flags = request.headers.get("x-osd-flags")
    context: dict[str, str] = {}
    if release_channel:
        context["release_channel"] = release_channel
    if cohort:
        context["cohort"] = cohort
    if flags:
        context["feature_flags"] = flags
    return context


def _merge_metadata(base: dict, extra: dict) -> dict:
    if not extra:
        return base
    merged = dict(base)
    merged.update(extra)
    return merged


# ---------------------------------------------------------------------------
# Request tracing + unified event log
# ---------------------------------------------------------------------------
try:
    from backend_api.deps import get_optional_user  # type: ignore
    from backend_api.routers.logs import record_event  # type: ignore
    from backend_api.db import db_session  # type: ignore
    from backend_api.ai_updates import ErrorSignal, queue_ai_update  # type: ignore

    @app.middleware("http")
    async def _trace_requests(request: Request, call_next):
        started = time.time()
        request_id = request.headers.get("x-correlation-id") or request.headers.get("x-request-id") or uuid4().hex
        request.state.correlation_id = request_id
        release_context = _extract_release_context(request)
        request.state.release_context = release_context
        user = None
        try:
            user = get_optional_user(request)  # type: ignore[arg-type]
        except Exception:
            user = None
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = int((time.time() - started) * 1000)
            try:
                with db_session() as db:
                    record_event(
                        db=db,
                        source="http",
                        level="error",
                        message=f"{request.method} {request.url.path} -> 500 ({duration_ms}ms)",
                        user_id=getattr(user, "id", None),
                        metadata=_merge_metadata(
                            {
                                "request_id": request_id,
                                "method": request.method,
                                "path": request.url.path,
                                "status_code": 500,
                                "duration_ms": duration_ms,
                                "error": str(exc),
                            },
                            release_context,
                        ),
                    )
            except Exception:
                pass
            try:
                stack = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                payload = ErrorSignal(
                    origin="backend",
                    source=request.url.path,
                    message=str(exc),
                    stack=stack,
                    severity="error",
                    metadata={
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        **release_context,
                    },
                )
                asyncio.create_task(asyncio.to_thread(queue_ai_update, payload))
            except Exception:
                pass
            raise

        duration_ms = int((time.time() - started) * 1000)
        response.headers["x-correlation-id"] = request_id
        try:
            with db_session() as db:
                record_event(
                    db=db,
                    source="http",
                    level="info",
                    message=f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                    user_id=getattr(user, "id", None),
                    metadata=_merge_metadata(
                        {
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": duration_ms,
                        },
                        release_context,
                    ),
                )
        except Exception:
            pass
        return response
except Exception:
    # If imports fail during early bootstrap, skip tracing.
    pass

try:
    from backend_api.domain.classification import sanitize_payload  # type: ignore
except Exception:  # pragma: no cover - fallback if domain layer missing
    def sanitize_payload(payload, user=None):
        return payload


@app.middleware("http")
async def _sanitize_sensitive_fields(request: Request, call_next):
    response = await call_next(request)
    if getattr(response, "media_type", None) != "application/json":
        return response
    body = getattr(response, "body", None)
    if not body:
        return response
    try:
        data = json.loads(body)
    except Exception:
        return response
    try:
        from backend_api.deps import get_optional_user  # type: ignore
        from backend_api.dal.context import get_data_context  # type: ignore
        user = get_optional_user(request)
        ctx = get_data_context(request, user)
    except Exception:
        user = None
        ctx = None
    sanitized = sanitize_payload(data, user=user, ctx=ctx)
    return JSONResponse(content=sanitized, status_code=response.status_code, headers=dict(response.headers))


_PMS_DEPRECATION_SUNSET = "2026-06-30"
_DEPRECATION_LOGGER = logging.getLogger("backend_api.deprecations")


@app.middleware("http")
async def _warn_pms_deprecation(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/pms"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = _PMS_DEPRECATION_SUNSET
        response.headers["Link"] = '</api/ipm>; rel="successor-version"'
        response.headers["Warning"] = '299 - "Deprecated API: use /api/ipm"'
        _DEPRECATION_LOGGER.warning("Deprecated PMS endpoint used: %s %s", request.method, request.url.path)
    return response


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "correlation_id", None)
    headers = {"x-correlation-id": request_id} if request_id else None
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
        headers=headers,
    )

# API Routes
_ROUTER_ALLOWLIST_RAW = os.environ.get("OSDASH_ROUTER_ALLOWLIST", "").strip()
_ROUTER_ALLOWLIST = (
    {name.strip() for name in _ROUTER_ALLOWLIST_RAW.split(",") if name.strip()}
    if _ROUTER_ALLOWLIST_RAW
    else None
)
_SKIP_OPTIONAL_ROUTERS = os.environ.get("OSDASH_SKIP_OPTIONAL_ROUTERS", "").strip().lower() in {
    "1",
    "true",
    "yes",
}
_ROUTER_LOGGER = logging.getLogger(__name__)


def _load_router(name: str):
    if _ROUTER_ALLOWLIST is not None and name not in _ROUTER_ALLOWLIST:
        return None
    try:
        return importlib.import_module(f"backend_api.routers.{name}")
    except Exception as exc:
        if _ROUTER_ALLOWLIST is not None or _SKIP_OPTIONAL_ROUTERS:
            _ROUTER_LOGGER.warning("Skipping router %s: %s", name, exc)
            return None
        raise


def _include_router(module, *, prefix: Optional[str], tags: List[str]) -> None:
    if module is None:
        return
    router = getattr(module, "router", None)
    if router is None:
        return
    kwargs: Dict[str, object] = {"tags": tags}
    if prefix:
        kwargs["prefix"] = prefix
    app.include_router(router, **kwargs)


_ROUTER_SPECS: List[Tuple[str, Optional[str], List[str]]] = [
    ("tasks", "/api/tasks", ["tasks"]),
    ("projects", "/api/projects", ["projects"]),
    ("chat", "/api/chat", ["chat"]),
    ("admin", "/api", ["admin"]),
    ("agent_journal", "/api", ["agent_journal"]),
    ("event_hub", "/api", ["event_hub"]),
    ("files", "/api", ["files"]),
    ("dashboard", "/api/dashboard", ["dashboard"]),
    ("documents", "/api/documents", ["documents"]),
    ("templates", "/api/templates", ["templates"]),
    ("integrations", "/api/integrations", ["integrations"]),
    ("settings", "/api/settings", ["settings"]),
    ("policy", "/api/policy", ["policy"]),
    ("exports", "/api/exports", ["exports"]),
    ("document_operations", "/api/operations", ["document_operations"]),
    ("analytics", "/api/analytics", ["analytics"]),
    ("tooling_integrations", "/api/ai-tooling", ["ai-tooling"]),
    ("tooling_patterns", "/api/ai-tooling", ["ai-tooling"]),
    ("codex_review", "/api", ["codex"]),
    ("writer", "/api/writer", ["writer"]),
    ("research", "/api/research", ["research"]),
    ("constants", "/api/constants", ["constants"]),
    ("matlab", "/api/matlab", ["matlab"]),
    ("knowledge", "/api/knowledge", ["knowledge"]),
    ("intelligence", "/api/intelligence", ["intelligence"]),
    ("reasoning", "/api/reasoning", ["reasoning"]),
    ("api_connectors", "/api/api-connectors", ["api_connectors"]),
    ("api_session_costs", "/api/api-session-costs", ["api_session_costs"]),
    ("math_sim", "/api/math-sim", ["math_sim"]),
    ("ai_systems", "/api/ai", ["ai_systems"]),
    ("ipm", "/api/ipm", ["ipm"]),
    ("pms", "/api/pms", ["pms"]),
    ("capsules", "/api/ai", ["capsules"]),
    ("coach", "/api/ai", ["coach"]),
    ("terminal", "/api/terminal", ["terminal"]),
    ("autofix", "/api/autofix", ["autofix"]),
    ("intents", "/api", ["intents"]),
    ("audit", "/api/audit", ["audit"]),
    ("search", "/api/search", ["search"]),
    ("computer_vision", "/api/computer-vision", ["computer_vision"]),
    ("neural_architecture", "/api/neural-architecture", ["neural_architecture"]),
    ("security_threat", "/api/security", ["security"]),
    ("network_monitoring", "/api/network", ["network"]),
    ("edge_computing", "/api/edge-computing", ["edge_computing"]),
    ("workflow_orchestration", "/api/workflows", ["workflows"]),
    ("platform", "/api", ["platform"]),
    ("git", "/api", ["git"]),
    ("personas", "/api/personas", ["personas"]),
    ("office", "/api/office", ["office"]),
    ("runtime_diagnostics", "/api", ["runtime"]),
    ("workspace", "/api", ["workspace"]),
    ("orchestrator", None, ["orchestrator"]),
    ("workspace_health", "/api", ["workspace_health"]),
    ("auth", "/api/auth", ["authentication"]),
    ("admin", "/api/admin", ["admin"]),
    ("logs", "/api", ["logs"]),
    ("ai_enhanced", "/api", ["ai_enhanced"]),
    ("version_control", "/api/versions", ["version_control"]),
    ("unified_logging", "/api/logs", ["logging"]),
    ("document_viewer", "/api/viewer", ["document_viewer"]),
    ("ai_integration", "/api/ai-integration", ["ai_integration"]),
    ("data_management", "/api/data", ["data_management"]),
    ("project_orchestrator", "/api", ["project_orchestrator"]),
    ("responses_api", "/api/responses", ["responses_api"]),
]

_ROUTER_MODULES: Dict[str, object] = {}
for name, prefix, tags in _ROUTER_SPECS:
    module = _load_router(name)
    _ROUTER_MODULES[name] = module
    _include_router(module, prefix=prefix, tags=tags)

platform = _ROUTER_MODULES.get("platform")
document_operations = _ROUTER_MODULES.get("document_operations")

# Legacy compatibility routes without the /api prefix.
@app.get("/system", include_in_schema=False)
async def legacy_system_status():
    if platform is None:
        raise HTTPException(status_code=503, detail="Platform router unavailable")
    return await platform.system_status()


@app.get("/planes/status", include_in_schema=False)
async def legacy_planes_status():
    if platform is None:
        raise HTTPException(status_code=503, detail="Platform router unavailable")
    return await platform.planes_status()


@app.get("/billing/usage", include_in_schema=False)
async def legacy_billing_usage(limit: int = 20):
    if platform is None:
        raise HTTPException(status_code=503, detail="Platform router unavailable")
    return await platform.billing_usage(limit=limit)


@app.get("/operations", include_in_schema=False)
async def legacy_operations(
    limit: int = 50,
    status: Optional[str] = None,
    integration_type: Optional[str] = None,
):
    if document_operations is None:
        raise HTTPException(status_code=503, detail="Document operations router unavailable")
    return await document_operations.list_document_operations(
        limit=limit, status=status, integration_type=integration_type
    )

# Mount static files
docs_dir = REPO_ROOT / "docs"
if docs_dir.exists():
    app.mount("/docs", StaticFiles(directory=str(docs_dir), html=True), name="docs")

ui_dir = REPO_ROOT / "ui"
if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

cyberchef_dir = REPO_ROOT / "CyberChef_v10.19.4"
if cyberchef_dir.exists():
    app.mount("/tools/cyberchef", StaticFiles(directory=str(cyberchef_dir), html=True), name="cyberchef")

# Serve built frontend (Vite) at /app for desktop/packaged runs
frontend_dist = REPO_ROOT / "frontend" / "dist"
if frontend_dist.exists():
    # html=True serves index.html for /app and directory requests
    app.mount("/app", StaticFiles(directory=str(frontend_dist), html=True), name="app")
    # Redirect root to the SPA when available to avoid a blank page
    @app.get("/", include_in_schema=False)
    async def _root_redirect():
        return RedirectResponse(url="/app/")

@app.get("/api/health")
async def health_check():
    """Health check endpoint with database connectivity check."""
    try:
        from backend_api.db import db_session
        # Test database connectivity
        with db_session() as db:
            db.execute("SELECT 1").fetchone()
        return {
            "status": "ok",
            "message": "AI OS API is running",
            "database": "connected"
        }
    except Exception as e:
        import logging
        logging.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "degraded",
            "message": "AI OS API is running but database is unavailable",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/api/docs/technical-spec-sheet")
async def get_technical_spec_sheet():
    """Serve the canonical Technical Spec Sheet PDF."""
    if not SPEC_SHEET_PATH.exists():
        raise HTTPException(status_code=404, detail="Technical Spec Sheet not found")
    return FileResponse(
        SPEC_SHEET_PATH,
        media_type="application/pdf",
        filename=SPEC_SHEET_PATH.name,
    )

def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port."""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

if __name__ == "__main__":
    import uvicorn
    
    # Find an available port
    default_port = 8000
    port = find_available_port(default_port)
    
    if port != default_port:
        print(f"⚠️  Port {default_port} is in use. Using port {port} instead.")
    else:
        print(f"✅ Starting server on port {port}")
    
    # SSL certificate paths
    cert_dir = REPO_ROOT / "certs"
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Check if certificates exist, otherwise fall back to HTTP
    if cert_file.exists() and key_file.exists():
        print(f"🔒 Starting with SSL on https://0.0.0.0:{port}")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            ssl_keyfile=str(key_file),
            ssl_certfile=str(cert_file)
        )
    else:
        print("Warning: SSL certificates not found. Running in HTTP mode.")
        print(f"Expected certificates at: {cert_file} and {key_file}")
        print(f"🌐 Starting server on http://0.0.0.0:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
