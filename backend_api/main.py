"""
FastAPI backend for OS Dashboard AI Assistant.
Provides REST API endpoints to replace the Tkinter GUI frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
REPO_ROOT = parent_dir
SPEC_SHEET_PATH = REPO_ROOT / "Technical Spec Sheet (Version 6 Latest Version).pdf"

app = FastAPI(
    title="OS Dashboard AI Assistant API",
    description="REST API for OS Dashboard AI Assistant",
    version="0.1.0",
    docs_url="/swagger",
    redoc_url="/redoc",
)

# CORS middleware - more restrictive for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000", 
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://0.0.0.0:5173", "http://0.0.0.0:5174",
        # Electron file:// origin is often serialized as `null`
        "null",
        "https://localhost:3000", "https://127.0.0.1:3000",
        "https://localhost:5173", "https://127.0.0.1:5173",
        "https://localhost:5174", "https://127.0.0.1:5174",
        "https://0.0.0.0:5173", "https://0.0.0.0:5174",
        "https://0.0.0.0:8000", "https://localhost:8000", "https://127.0.0.1:8000"
    ],
    # Allow any localhost/loopback port for dev/preview builds.
    allow_origin_regex=r"^https?://(localhost|127\\.0\\.0\\.1|0\\.0\\.0\\.0)(:\\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods instead of "*"
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Explicit headers instead of "*"
    expose_headers=["Content-Type", "X-Total-Count"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# API Routes
from backend_api.routers import (
    tasks,
    projects,
    intents,
    chat,
    dashboard,
    documents,
    templates,
    integrations,
    office,
    settings,
    document_operations,
    analytics,
    writer,
    research,
    api_connectors,
    ai_systems,
    terminal,
    intelligence,
    reasoning,
    audit,
    search,
    computer_vision,
    neural_architecture,
    security_threat,
    edge_computing,
    workflow_orchestration,
    platform,
    personas,
    capsules,
    autofix,
    runtime_diagnostics,
    coach,
    git,
    network_monitoring,
    workspace,
    auth,
    admin,
    logs,
    ai_enhanced,
    version_control,
    unified_logging,
    document_viewer,
    ai_integration,
    data_management,
    project_orchestrator,
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(
    document_operations.router,
    prefix="/api/operations",
    tags=["document_operations"],
)
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(writer.router, prefix="/api/writer", tags=["writer"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(reasoning.router, prefix="/api/reasoning", tags=["reasoning"])
app.include_router(
    api_connectors.router, prefix="/api/api-connectors", tags=["api_connectors"]
)
app.include_router(ai_systems.router, prefix="/api/ai", tags=["ai_systems"])
app.include_router(capsules.router, prefix="/api/ai", tags=["capsules"])
app.include_router(coach.router, prefix="/api/ai", tags=["coach"])
app.include_router(terminal.router, prefix="/api/terminal", tags=["terminal"])
app.include_router(autofix.router, prefix="/api/autofix", tags=["autofix"])
app.include_router(intents.router, prefix="/api", tags=["intents"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(
    computer_vision.router, prefix="/api/computer-vision", tags=["computer_vision"]
)
app.include_router(
    neural_architecture.router, prefix="/api/neural-architecture", tags=["neural_architecture"]
)
app.include_router(
    security_threat.router, prefix="/api/security", tags=["security"]
)
app.include_router(
    network_monitoring.router, prefix="/api/network", tags=["network"]
)
app.include_router(
    edge_computing.router, prefix="/api/edge-computing", tags=["edge_computing"]
)
app.include_router(
    workflow_orchestration.router, prefix="/api/workflows", tags=["workflows"]
)
app.include_router(platform.router, prefix="/api", tags=["platform"])
app.include_router(git.router, prefix="/api", tags=["git"])
app.include_router(personas.router, prefix="/api/personas", tags=["personas"])
app.include_router(office.router, prefix="/api/office", tags=["office"])
app.include_router(runtime_diagnostics.router, prefix="/api", tags=["runtime"])
app.include_router(workspace.router, prefix="/api", tags=["workspace"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(logs.router, prefix="/api", tags=["logs"])
app.include_router(ai_enhanced.router, prefix="/api", tags=["ai_enhanced"])
app.include_router(version_control.router, prefix="/api/versions", tags=["version_control"])
app.include_router(unified_logging.router, prefix="/api/logs", tags=["logging"])
app.include_router(document_viewer.router, prefix="/api/viewer", tags=["document_viewer"])
app.include_router(ai_integration.router, prefix="/api/ai-integration", tags=["ai_integration"])
app.include_router(data_management.router, prefix="/api/data", tags=["data_management"])
app.include_router(project_orchestrator.router, prefix="/api", tags=["project_orchestrator"])

# Legacy compatibility routes without the /api prefix.
@app.get("/system", include_in_schema=False)
async def legacy_system_status():
    return await platform.system_status()


@app.get("/planes/status", include_in_schema=False)
async def legacy_planes_status():
    return await platform.planes_status()


@app.get("/billing/usage", include_in_schema=False)
async def legacy_billing_usage(limit: int = 20):
    return await platform.billing_usage(limit=limit)


@app.get("/operations", include_in_schema=False)
async def legacy_operations(
    limit: int = 50,
    status: Optional[str] = None,
    integration_type: Optional[str] = None,
):
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
            "message": "OS Dashboard AI Assistant API is running",
            "database": "connected"
        }
    except Exception as e:
        import logging
        logging.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "degraded",
            "message": "OS Dashboard AI Assistant API is running but database is unavailable",
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
