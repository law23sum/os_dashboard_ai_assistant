"""AI integration that sees whole directory, analyzes uploaded files, and provides instructions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend_api.routers.auth import get_current_user
from backend_api.routers.documents import _load_metadata, _list_chat_documents
from assistant_hub_gui.assistant_hub.config import DATA_DIR, ensure_data_directories

ensure_data_directories()
CHAT_DOCUMENTS_DIR = DATA_DIR / "chat_documents"
CHAT_DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()


class DirectoryAnalysis(BaseModel):
    path: str
    total_files: int
    total_directories: int
    file_types: Dict[str, int]
    total_size_bytes: int
    structure: List[Dict[str, Any]]


class FileAnalysis(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
    analysis: Dict[str, Any]
    suggested_actions: List[Dict[str, Any]]


class AIInstruction(BaseModel):
    instruction_id: str
    title: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    confidence: float


def analyze_directory(directory_path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
    """Recursively analyze directory structure."""
    if current_depth >= max_depth:
        return {"type": "truncated", "depth": current_depth}
    
    if not directory_path.exists() or not directory_path.is_dir():
        return {"type": "invalid"}
    
    structure = []
    file_types = {}
    total_size = 0
    file_count = 0
    dir_count = 0
    
    try:
        for item in directory_path.iterdir():
            if item.is_file():
                file_count += 1
                size = item.stat().st_size
                total_size += size
                ext = item.suffix.lower() or "no_extension"
                file_types[ext] = file_types.get(ext, 0) + 1
                
                structure.append({
                    "name": item.name,
                    "type": "file",
                    "size": size,
                    "extension": ext,
                    "path": str(item.relative_to(directory_path))
                })
            elif item.is_dir():
                dir_count += 1
                sub_analysis = analyze_directory(item, max_depth, current_depth + 1)
                structure.append({
                    "name": item.name,
                    "type": "directory",
                    "path": str(item.relative_to(directory_path)),
                    "contents": sub_analysis
                })
    except PermissionError:
        return {"type": "permission_denied"}
    
    return {
        "type": "directory",
        "file_count": file_count,
        "dir_count": dir_count,
        "total_size": total_size,
        "file_types": file_types,
        "items": structure
    }


def analyze_file_content(file_path: Path, file_type: str) -> Dict[str, Any]:
    """Analyze file content and extract metadata."""
    analysis = {
        "file_type": file_type,
        "size_bytes": file_path.stat().st_size,
        "readable": False,
        "content_summary": None,
        "metadata": {}
    }
    
    ext = file_path.suffix.lower()
    
    try:
        if ext in [".txt", ".md", ".py", ".js", ".ts", ".json", ".csv"]:
            # Text-based files
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            analysis["readable"] = True
            analysis["content_summary"] = {
                "length": len(content),
                "lines": content.count("\n") + 1,
                "preview": content[:500]
            }
            
            if ext == ".json":
                try:
                    data = json.loads(content)
                    analysis["metadata"]["json_structure"] = {
                        "type": type(data).__name__,
                        "keys": list(data.keys()) if isinstance(data, dict) else None,
                        "length": len(data) if isinstance(data, (list, dict)) else None
                    }
                except Exception:
                    pass
        
        elif ext in [".pdf"]:
            analysis["metadata"]["type"] = "pdf"
            # PDF analysis would go here
        
        elif ext in [".xlsx", ".xls"]:
            analysis["metadata"]["type"] = "excel"
            # Excel analysis would go here
        
        elif ext in [".docx", ".doc"]:
            analysis["metadata"]["type"] = "word"
            # Word analysis would go here
        
        elif ext in [".pptx", ".ppt"]:
            analysis["metadata"]["type"] = "powerpoint"
            # PowerPoint analysis would go here
        
        elif ext in [".png", ".jpg", ".jpeg", ".gif"]:
            analysis["metadata"]["type"] = "image"
            # Image analysis would go here
        
    except Exception as e:
        analysis["error"] = str(e)
    
    return analysis


def generate_ai_instructions(analysis: Dict[str, Any], file_type: str) -> List[Dict[str, Any]]:
    """Generate AI-suggested instructions based on file analysis."""
    instructions = []
    
    if analysis.get("readable"):
        if file_type in [".txt", ".md"]:
            instructions.append({
                "instruction_id": "summarize",
                "title": "Summarize Document",
                "description": "Generate a summary of the document content",
                "action_type": "summarize",
                "parameters": {},
                "confidence": 0.9
            })
            
            instructions.append({
                "instruction_id": "extract_key_points",
                "title": "Extract Key Points",
                "description": "Extract main points and topics from the document",
                "action_type": "extract",
                "parameters": {"type": "key_points"},
                "confidence": 0.85
            })
        
        elif file_type == ".json":
            instructions.append({
                "instruction_id": "validate_json",
                "title": "Validate JSON Structure",
                "description": "Validate and format the JSON structure",
                "action_type": "validate",
                "parameters": {},
                "confidence": 0.95
            })
            
            instructions.append({
                "instruction_id": "analyze_structure",
                "title": "Analyze JSON Structure",
                "description": "Analyze the JSON schema and data types",
                "action_type": "analyze",
                "parameters": {"type": "schema"},
                "confidence": 0.9
            })
        
        elif file_type == ".csv":
            instructions.append({
                "instruction_id": "analyze_data",
                "title": "Analyze CSV Data",
                "description": "Perform statistical analysis on the CSV data",
                "action_type": "analyze",
                "parameters": {"type": "statistics"},
                "confidence": 0.85
            })
            
            instructions.append({
                "instruction_id": "visualize_data",
                "title": "Create Visualizations",
                "description": "Generate charts and graphs from the data",
                "action_type": "visualize",
                "parameters": {},
                "confidence": 0.8
            })
        
        elif file_type in [".py", ".js", ".ts"]:
            instructions.append({
                "instruction_id": "review_code",
                "title": "Code Review",
                "description": "Review code for best practices and potential issues",
                "action_type": "review",
                "parameters": {"type": "code_review"},
                "confidence": 0.9
            })
            
            instructions.append({
                "instruction_id": "document_code",
                "title": "Generate Documentation",
                "description": "Generate documentation for the code",
                "action_type": "document",
                "parameters": {},
                "confidence": 0.85
            })
    
    elif file_type in [".pdf"]:
        instructions.append({
            "instruction_id": "extract_text",
            "title": "Extract Text from PDF",
            "description": "Extract and analyze text content from the PDF",
            "action_type": "extract",
            "parameters": {"type": "text"},
            "confidence": 0.8
        })
    
    elif file_type in [".xlsx", ".xls"]:
        instructions.append({
            "instruction_id": "analyze_spreadsheet",
            "title": "Analyze Spreadsheet",
            "description": "Analyze spreadsheet structure and data",
            "action_type": "analyze",
            "parameters": {"type": "spreadsheet"},
            "confidence": 0.85
        })
    
    # Always add general instructions
    instructions.append({
        "instruction_id": "general_analysis",
        "title": "General Analysis",
        "description": "Perform general analysis and provide insights",
        "action_type": "analyze",
        "parameters": {"type": "general"},
        "confidence": 0.7
    })
    
    return instructions


@router.get("/directory/analyze", response_model=DirectoryAnalysis)
async def analyze_workspace_directory(
    path: Optional[str] = None,
    max_depth: int = 3,
    current_user: dict = Depends(get_current_user)
):
    """Analyze the workspace directory structure."""
    if path:
        target_path = Path(path)
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
    else:
        target_path = CHAT_DOCUMENTS_DIR
    
    analysis = analyze_directory(target_path, max_depth=max_depth)
    
    if analysis.get("type") == "invalid":
        raise HTTPException(status_code=404, detail="Invalid directory path")
    
    return DirectoryAnalysis(
        path=str(target_path),
        total_files=analysis.get("file_count", 0),
        total_directories=analysis.get("dir_count", 0),
        file_types=analysis.get("file_types", {}),
        total_size_bytes=analysis.get("total_size", 0),
        structure=analysis.get("items", [])
    )


@router.post("/files/{document_id}/analyze", response_model=FileAnalysis)
async def analyze_uploaded_file(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Analyze an uploaded file and generate AI instructions."""
    doc = _load_metadata(document_id)
    file_path = Path(CHAT_DOCUMENTS_DIR) / document_id / doc["filename"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file_type = doc.get("file_type", "")
    analysis = analyze_file_content(file_path, file_type)
    instructions = generate_ai_instructions(analysis, f".{file_type}")
    
    return FileAnalysis(
        file_id=document_id,
        filename=doc["filename"],
        file_type=file_type,
        size_bytes=file_path.stat().st_size,
        analysis=analysis,
        suggested_actions=instructions
    )


@router.get("/files/{document_id}/instructions", response_model=List[AIInstruction])
async def get_file_instructions(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get AI-generated instructions for a file."""
    file_analysis = await analyze_uploaded_file(document_id, current_user)
    
    return [
        AIInstruction(**action) for action in file_analysis.suggested_actions
    ]


@router.post("/files/{document_id}/execute-instruction")
async def execute_ai_instruction(
    document_id: str,
    instruction_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Execute an AI instruction on a file."""
    # This would integrate with actual AI services
    # For now, return a placeholder response
    
    return {
        "document_id": document_id,
        "instruction_id": instruction_id,
        "status": "queued",
        "message": "Instruction queued for processing"
    }
