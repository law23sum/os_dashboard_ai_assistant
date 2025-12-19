"""AI Directory Analysis and Instruction Suggestion Router.

When users interact with AI, this module enables:
- Full directory visibility for AI context
- File analysis and understanding
- AI-generated instruction suggestions based on file assessment
"""

from __future__ import annotations

import json
import mimetypes
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field

from assistant_hub_gui.assistant_hub.config import DATA_DIR

router = APIRouter()

CHAT_DOCUMENTS_DIR = DATA_DIR / "chat_documents"
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]  # Project root


class DirectoryEntry(BaseModel):
    """Directory entry information."""
    name: str
    path: str
    is_directory: bool
    size_bytes: int
    modified_at: str
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    readable: bool = True


class DirectoryStructure(BaseModel):
    """Full directory structure."""
    root_path: str
    total_files: int
    total_directories: int
    total_size_bytes: int
    entries: List[DirectoryEntry]
    tree_view: str


class FileAnalysis(BaseModel):
    """AI analysis of a file."""
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
    content_preview: Optional[str] = None
    structure_analysis: Dict[str, Any]
    suggested_actions: List[Dict[str, Any]]
    ai_assessment: str
    confidence_score: float


class InstructionSuggestion(BaseModel):
    """AI-generated instruction suggestion."""
    id: str
    category: str
    action: str
    description: str
    prompt_template: str
    confidence: float
    requirements: List[str]
    estimated_complexity: str  # "simple", "moderate", "complex"


class ContextAnalysis(BaseModel):
    """Full context analysis for AI interaction."""
    session_id: str
    directory_summary: Dict[str, Any]
    uploaded_files: List[Dict[str, Any]]
    suggested_instructions: List[InstructionSuggestion]
    context_summary: str
    ai_capabilities: List[str]


# File type analysis rules
FILE_ANALYSIS_RULES = {
    ".csv": {
        "category": "data",
        "actions": ["analyze_data", "visualize", "transform", "export"],
        "analysis_type": "tabular"
    },
    ".json": {
        "category": "data",
        "actions": ["validate", "transform", "query", "format"],
        "analysis_type": "structured"
    },
    ".xlsx": {
        "category": "spreadsheet",
        "actions": ["analyze", "chart", "pivot", "export"],
        "analysis_type": "tabular"
    },
    ".pdf": {
        "category": "document",
        "actions": ["extract_text", "summarize", "search", "annotate"],
        "analysis_type": "document"
    },
    ".docx": {
        "category": "document",
        "actions": ["edit", "summarize", "format", "convert"],
        "analysis_type": "document"
    },
    ".pptx": {
        "category": "presentation",
        "actions": ["summarize", "extract_content", "convert", "generate_notes"],
        "analysis_type": "presentation"
    },
    ".py": {
        "category": "code",
        "actions": ["analyze", "refactor", "document", "test"],
        "analysis_type": "code"
    },
    ".js": {
        "category": "code",
        "actions": ["analyze", "refactor", "document", "lint"],
        "analysis_type": "code"
    },
    ".ts": {
        "category": "code",
        "actions": ["analyze", "refactor", "document", "type_check"],
        "analysis_type": "code"
    },
    ".md": {
        "category": "documentation",
        "actions": ["format", "convert", "summarize", "expand"],
        "analysis_type": "text"
    },
    ".txt": {
        "category": "text",
        "actions": ["analyze", "summarize", "format", "search"],
        "analysis_type": "text"
    },
    ".html": {
        "category": "web",
        "actions": ["parse", "extract", "convert", "validate"],
        "analysis_type": "markup"
    },
    ".xml": {
        "category": "data",
        "actions": ["parse", "validate", "transform", "query"],
        "analysis_type": "markup"
    },
}

# Instruction templates by file category
INSTRUCTION_TEMPLATES = {
    "data": [
        {
            "action": "analyze_structure",
            "description": "Analyze the structure and content of this data file",
            "prompt": "Analyze the structure of {filename}. Identify column types, data patterns, and potential issues.",
            "complexity": "simple"
        },
        {
            "action": "generate_insights",
            "description": "Generate insights and statistics from the data",
            "prompt": "Generate key insights from {filename}. Include summary statistics, trends, and notable patterns.",
            "complexity": "moderate"
        },
        {
            "action": "clean_data",
            "description": "Identify and suggest fixes for data quality issues",
            "prompt": "Review {filename} for data quality issues. Identify missing values, outliers, and inconsistencies.",
            "complexity": "moderate"
        },
        {
            "action": "transform_data",
            "description": "Transform or reshape the data for analysis",
            "prompt": "Suggest transformations for {filename} to improve analysis readiness.",
            "complexity": "complex"
        }
    ],
    "document": [
        {
            "action": "summarize",
            "description": "Create a summary of the document",
            "prompt": "Provide a comprehensive summary of {filename}, highlighting key points and conclusions.",
            "complexity": "simple"
        },
        {
            "action": "extract_key_info",
            "description": "Extract key information and entities",
            "prompt": "Extract key information from {filename}: names, dates, amounts, and important terms.",
            "complexity": "moderate"
        },
        {
            "action": "generate_outline",
            "description": "Generate a structured outline",
            "prompt": "Create a structured outline of {filename} with main sections and subsections.",
            "complexity": "simple"
        },
        {
            "action": "draft_response",
            "description": "Draft a response or follow-up document",
            "prompt": "Based on {filename}, draft a professional response addressing the main points.",
            "complexity": "complex"
        }
    ],
    "code": [
        {
            "action": "code_review",
            "description": "Review code for quality and best practices",
            "prompt": "Review {filename} for code quality, best practices, and potential improvements.",
            "complexity": "moderate"
        },
        {
            "action": "add_documentation",
            "description": "Add or improve code documentation",
            "prompt": "Add comprehensive documentation to {filename}, including docstrings and comments.",
            "complexity": "moderate"
        },
        {
            "action": "identify_bugs",
            "description": "Identify potential bugs and issues",
            "prompt": "Analyze {filename} for potential bugs, security issues, and edge cases.",
            "complexity": "complex"
        },
        {
            "action": "suggest_tests",
            "description": "Suggest unit tests",
            "prompt": "Generate unit test suggestions for {filename} covering main functionality.",
            "complexity": "complex"
        }
    ],
    "presentation": [
        {
            "action": "create_speaker_notes",
            "description": "Generate speaker notes",
            "prompt": "Create speaker notes for each slide in {filename}.",
            "complexity": "moderate"
        },
        {
            "action": "summarize_presentation",
            "description": "Create a presentation summary",
            "prompt": "Summarize the key messages and takeaways from {filename}.",
            "complexity": "simple"
        },
        {
            "action": "suggest_improvements",
            "description": "Suggest presentation improvements",
            "prompt": "Review {filename} and suggest improvements for clarity and impact.",
            "complexity": "moderate"
        }
    ],
    "text": [
        {
            "action": "analyze_content",
            "description": "Analyze text content and structure",
            "prompt": "Analyze the content of {filename}. Identify themes, tone, and key messages.",
            "complexity": "simple"
        },
        {
            "action": "improve_writing",
            "description": "Suggest writing improvements",
            "prompt": "Review {filename} and suggest improvements for clarity, grammar, and style.",
            "complexity": "moderate"
        },
        {
            "action": "expand_content",
            "description": "Expand or elaborate on content",
            "prompt": "Expand on the content in {filename} with additional details and examples.",
            "complexity": "complex"
        }
    ],
    "spreadsheet": [
        {
            "action": "analyze_spreadsheet",
            "description": "Analyze spreadsheet structure and formulas",
            "prompt": "Analyze {filename}: identify sheets, formulas, and data relationships.",
            "complexity": "moderate"
        },
        {
            "action": "create_charts",
            "description": "Suggest charts and visualizations",
            "prompt": "Suggest appropriate charts and visualizations for the data in {filename}.",
            "complexity": "moderate"
        },
        {
            "action": "audit_formulas",
            "description": "Audit formulas for errors",
            "prompt": "Audit formulas in {filename} for errors, circular references, and inefficiencies.",
            "complexity": "complex"
        }
    ]
}


def _get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def _get_file_category(filename: str) -> str:
    ext = _get_file_extension(filename)
    if ext in FILE_ANALYSIS_RULES:
        return FILE_ANALYSIS_RULES[ext]["category"]
    return "unknown"


def _build_tree_view(entries: List[DirectoryEntry], prefix: str = "") -> str:
    """Build a text-based tree view of directory structure."""
    lines = []
    sorted_entries = sorted(entries, key=lambda e: (not e.is_directory, e.name.lower()))
    
    for i, entry in enumerate(sorted_entries):
        is_last = i == len(sorted_entries) - 1
        connector = "└── " if is_last else "├── "
        
        if entry.is_directory:
            lines.append(f"{prefix}{connector}📁 {entry.name}/")
        else:
            icon = "📄"
            if entry.file_type in ["py", "js", "ts"]:
                icon = "🐍" if entry.file_type == "py" else "📜"
            elif entry.file_type in ["json", "xml", "csv"]:
                icon = "📊"
            elif entry.file_type in ["pdf", "docx"]:
                icon = "📑"
            lines.append(f"{prefix}{connector}{icon} {entry.name}")
    
    return "\n".join(lines)


def _analyze_file_content(filepath: Path, max_preview: int = 2000) -> Dict[str, Any]:
    """Analyze file content and structure."""
    ext = filepath.suffix.lower()
    analysis = {
        "line_count": 0,
        "word_count": 0,
        "char_count": 0,
        "encoding": "unknown",
        "has_headers": False,
        "structure_type": "unknown"
    }
    
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        analysis["encoding"] = "utf-8"
        analysis["char_count"] = len(content)
        analysis["line_count"] = content.count("\n") + 1
        analysis["word_count"] = len(content.split())
        
        # Specific analysis by type
        if ext == ".csv":
            lines = content.split("\n")
            if lines:
                analysis["has_headers"] = True
                analysis["column_count"] = len(lines[0].split(","))
                analysis["row_count"] = len(lines) - 1
                analysis["structure_type"] = "tabular"
        
        elif ext == ".json":
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    analysis["structure_type"] = "object"
                    analysis["key_count"] = len(data)
                elif isinstance(data, list):
                    analysis["structure_type"] = "array"
                    analysis["item_count"] = len(data)
            except json.JSONDecodeError:
                analysis["structure_type"] = "invalid_json"
        
        elif ext in [".py", ".js", ".ts"]:
            analysis["structure_type"] = "code"
            analysis["function_count"] = content.count("def ") + content.count("function ")
            analysis["class_count"] = content.count("class ")
            analysis["import_count"] = content.count("import ")
        
    except Exception as e:
        analysis["error"] = str(e)
    
    return analysis


@router.get("/directory", response_model=DirectoryStructure)
async def get_directory_structure(
    path: Optional[str] = None,
    max_depth: int = Query(3, le=5),
    include_hidden: bool = False
) -> DirectoryStructure:
    """Get directory structure for AI context."""
    
    if path:
        # Validate path is within allowed directories
        target = Path(path)
        if not target.is_absolute():
            target = WORKSPACE_ROOT / path
        target = target.resolve()
        
        # Security check
        if not str(target).startswith(str(WORKSPACE_ROOT)):
            raise HTTPException(status_code=403, detail="Access denied to this path")
    else:
        target = WORKSPACE_ROOT
    
    if not target.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    
    entries = []
    total_size = 0
    total_files = 0
    total_dirs = 0
    
    def scan_directory(dir_path: Path, current_depth: int = 0):
        nonlocal total_size, total_files, total_dirs
        
        if current_depth >= max_depth:
            return
        
        try:
            for item in dir_path.iterdir():
                if not include_hidden and item.name.startswith("."):
                    continue
                if item.name in ["__pycache__", "node_modules", ".git", "venv", ".venv"]:
                    continue
                
                try:
                    stat = item.stat()
                    modified = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
                    
                    if item.is_dir():
                        total_dirs += 1
                        entries.append(DirectoryEntry(
                            name=item.name,
                            path=str(item.relative_to(WORKSPACE_ROOT)),
                            is_directory=True,
                            size_bytes=0,
                            modified_at=modified
                        ))
                        scan_directory(item, current_depth + 1)
                    else:
                        total_files += 1
                        total_size += stat.st_size
                        mime = mimetypes.guess_type(item.name)[0]
                        entries.append(DirectoryEntry(
                            name=item.name,
                            path=str(item.relative_to(WORKSPACE_ROOT)),
                            is_directory=False,
                            size_bytes=stat.st_size,
                            modified_at=modified,
                            file_type=item.suffix.lstrip(".").lower(),
                            mime_type=mime
                        ))
                except PermissionError:
                    entries.append(DirectoryEntry(
                        name=item.name,
                        path=str(item.relative_to(WORKSPACE_ROOT)),
                        is_directory=item.is_dir(),
                        size_bytes=0,
                        modified_at="",
                        readable=False
                    ))
        except PermissionError:
            pass
    
    scan_directory(target)
    tree = _build_tree_view(entries)
    
    return DirectoryStructure(
        root_path=str(target.relative_to(WORKSPACE_ROOT)) if target != WORKSPACE_ROOT else ".",
        total_files=total_files,
        total_directories=total_dirs,
        total_size_bytes=total_size,
        entries=entries,
        tree_view=tree
    )


@router.get("/analyze/{document_id}", response_model=FileAnalysis)
async def analyze_file(document_id: str) -> FileAnalysis:
    """Analyze an uploaded file and suggest AI actions."""
    
    doc_dir = CHAT_DOCUMENTS_DIR / document_id
    metadata_path = doc_dir / "metadata.json"
    
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    metadata = json.loads(metadata_path.read_text())
    filepath = doc_dir / metadata["filename"]
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Document file not found")
    
    # Get basic info
    ext = _get_file_extension(metadata["filename"])
    category = _get_file_category(metadata["filename"])
    
    # Analyze content
    structure = _analyze_file_content(filepath)
    
    # Read preview
    preview = None
    if metadata.get("preview_type") == "text":
        try:
            preview = filepath.read_text(encoding="utf-8", errors="ignore")[:2000]
        except Exception:
            pass
    
    # Generate suggested actions
    rules = FILE_ANALYSIS_RULES.get(ext, {})
    actions = rules.get("actions", ["view", "download"])
    
    suggested_actions = []
    templates = INSTRUCTION_TEMPLATES.get(category, [])
    
    for template in templates:
        suggested_actions.append({
            "id": f"{category}_{template['action']}",
            "action": template["action"],
            "description": template["description"],
            "prompt": template["prompt"].format(filename=metadata["filename"]),
            "complexity": template["complexity"]
        })
    
    # Generate AI assessment
    assessment_parts = [
        f"This is a {category} file ({metadata['file_type'].upper()}).",
    ]
    
    if structure.get("line_count"):
        assessment_parts.append(f"It contains {structure['line_count']} lines and {structure.get('word_count', 0)} words.")
    
    if structure.get("structure_type") == "tabular":
        assessment_parts.append(f"It appears to be tabular data with {structure.get('column_count', '?')} columns.")
    
    if structure.get("function_count"):
        assessment_parts.append(f"It contains {structure['function_count']} functions/methods.")
    
    assessment_parts.append(f"Recommended actions: {', '.join(actions[:3])}.")
    
    return FileAnalysis(
        file_id=document_id,
        filename=metadata["filename"],
        file_type=metadata.get("file_type", "unknown"),
        size_bytes=metadata.get("size_bytes", 0),
        content_preview=preview,
        structure_analysis=structure,
        suggested_actions=suggested_actions,
        ai_assessment=" ".join(assessment_parts),
        confidence_score=0.85
    )


@router.post("/context", response_model=ContextAnalysis)
async def get_ai_context(
    include_directory: bool = True,
    include_documents: bool = True,
    persona: str = "AIC"
) -> ContextAnalysis:
    """Get full context for AI interaction including directory and uploaded files."""
    
    session_id = uuid4().hex[:12]
    
    # Get directory summary if requested
    directory_summary = {}
    if include_directory:
        dir_struct = await get_directory_structure(max_depth=2)
        directory_summary = {
            "total_files": dir_struct.total_files,
            "total_directories": dir_struct.total_directories,
            "total_size_bytes": dir_struct.total_size_bytes,
            "file_types": {}
        }
        
        # Count file types
        for entry in dir_struct.entries:
            if not entry.is_directory and entry.file_type:
                ft = entry.file_type
                directory_summary["file_types"][ft] = directory_summary["file_types"].get(ft, 0) + 1
    
    # Get uploaded documents
    uploaded_files = []
    if include_documents:
        for meta_file in CHAT_DOCUMENTS_DIR.glob("*/metadata.json"):
            try:
                meta = json.loads(meta_file.read_text())
                uploaded_files.append({
                    "id": meta["id"],
                    "filename": meta["original_name"],
                    "file_type": meta.get("file_type"),
                    "category": meta.get("category"),
                    "size_bytes": meta.get("size_bytes", 0),
                    "uploaded_at": meta.get("uploaded_at")
                })
            except Exception:
                continue
        
        # Sort by upload time
        uploaded_files.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    
    # Generate suggested instructions
    suggestions = []
    seen_categories = set()
    
    for doc in uploaded_files[:5]:
        category = doc.get("category", "text")
        if category in seen_categories:
            continue
        seen_categories.add(category)
        
        templates = INSTRUCTION_TEMPLATES.get(category, INSTRUCTION_TEMPLATES.get("text", []))
        for i, template in enumerate(templates[:2]):
            suggestions.append(InstructionSuggestion(
                id=f"sug_{uuid4().hex[:8]}",
                category=category,
                action=template["action"],
                description=template["description"],
                prompt_template=template["prompt"],
                confidence=0.9 - (i * 0.1),
                requirements=[f"Requires {category} file"],
                estimated_complexity=template["complexity"]
            ))
    
    # Add general suggestions
    general_suggestions = [
        InstructionSuggestion(
            id=f"sug_{uuid4().hex[:8]}",
            category="general",
            action="explore_workspace",
            description="Explore the workspace and understand the project structure",
            prompt_template="Analyze the workspace structure and provide an overview of the project.",
            confidence=0.95,
            requirements=[],
            estimated_complexity="simple"
        ),
        InstructionSuggestion(
            id=f"sug_{uuid4().hex[:8]}",
            category="general",
            action="find_files",
            description="Find specific files or content in the workspace",
            prompt_template="Search for files containing {search_term} in the workspace.",
            confidence=0.9,
            requirements=[],
            estimated_complexity="simple"
        ),
    ]
    suggestions.extend(general_suggestions)
    
    # Build context summary
    context_parts = [
        f"Workspace contains {directory_summary.get('total_files', 0)} files.",
        f"You have {len(uploaded_files)} uploaded documents available.",
    ]
    
    if uploaded_files:
        recent = uploaded_files[0]["filename"]
        context_parts.append(f"Most recent: {recent}.")
    
    context_parts.append(f"AI Persona: {persona}.")
    
    return ContextAnalysis(
        session_id=session_id,
        directory_summary=directory_summary,
        uploaded_files=uploaded_files,
        suggested_instructions=suggestions,
        context_summary=" ".join(context_parts),
        ai_capabilities=[
            "file_analysis",
            "content_generation",
            "code_review",
            "data_analysis",
            "document_summarization",
            "workflow_automation",
            "search_and_discovery"
        ]
    )


@router.post("/suggest-instructions")
async def suggest_instructions_for_file(
    document_id: str,
    max_suggestions: int = Query(5, le=10)
) -> List[InstructionSuggestion]:
    """Get AI instruction suggestions for a specific file."""
    
    # Analyze the file first
    analysis = await analyze_file(document_id)
    category = _get_file_category(analysis.filename)
    
    suggestions = []
    templates = INSTRUCTION_TEMPLATES.get(category, INSTRUCTION_TEMPLATES.get("text", []))
    
    for template in templates[:max_suggestions]:
        suggestions.append(InstructionSuggestion(
            id=f"sug_{uuid4().hex[:8]}",
            category=category,
            action=template["action"],
            description=template["description"],
            prompt_template=template["prompt"].format(filename=analysis.filename),
            confidence=0.85,
            requirements=[f"File: {analysis.filename}"],
            estimated_complexity=template["complexity"]
        ))
    
    return suggestions
