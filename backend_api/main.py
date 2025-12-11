"""
FastAPI backend for OS Dashboard AI Assistant.
Provides REST API endpoints to replace the Tkinter GUI frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
import os
from pathlib import Path

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
from backend_api.routers import (
    tasks,
    projects,
    chat,
    dashboard,
    templates,
    integrations,
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
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
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
app.include_router(terminal.router, prefix="/api/terminal", tags=["terminal"])
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
    edge_computing.router, prefix="/api/edge-computing", tags=["edge_computing"]
)
app.include_router(
    workflow_orchestration.router, prefix="/api/workflows", tags=["workflows"]
)
app.include_router(platform.router, prefix="/api", tags=["platform"])
app.include_router(personas.router, prefix="/api/personas", tags=["personas"])

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

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "OS Dashboard AI Assistant API is running"}


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
