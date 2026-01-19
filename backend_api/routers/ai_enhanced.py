"""
Enhanced AI router with directory analysis and file interaction capabilities.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
import json
from datetime import datetime

from backend_api.deps import get_current_user
from backend_api.security import AuthUser
from backend_api.routers.logs import log_event

router = APIRouter()


@router.post("/ai/analyze-directory")
async def analyze_directory(
    request_data: dict,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Analyze a directory and provide AI-powered insights.
    Returns file structure, recommendations, and suggested actions.
    """
    directory_path = request_data.get('path', '/')
    
    # Security: Restrict to workspace directory
    workspace_root = Path(__file__).parent.parent.parent
    target_path = (workspace_root / directory_path).resolve()
    
    if not str(target_path).startswith(str(workspace_root)):
        raise HTTPException(status_code=403, detail="Access denied: Path outside workspace")
    
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Directory not found")
    
    # Analyze directory structure
    analysis = {
        "path": str(target_path.relative_to(workspace_root)),
        "absolute_path": str(target_path),
        "type": "directory" if target_path.is_dir() else "file",
        "files": [],
        "directories": [],
        "total_size": 0,
        "file_types": {},
        "recommendations": [],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if target_path.is_dir():
        for item in target_path.iterdir():
            try:
                item_info = {
                    "name": item.name,
                    "path": str(item.relative_to(workspace_root)),
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    "type": "directory" if item.is_dir() else "file",
                }
                
                if item.is_file():
                    analysis["files"].append(item_info)
                    analysis["total_size"] += item_info["size"]
                    
                    # Track file types
                    ext = item.suffix.lower()
                    analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
                else:
                    analysis["directories"].append(item_info)
            except PermissionError:
                continue
    
    # Generate AI recommendations
    analysis["recommendations"] = generate_recommendations(analysis)
    
    # Log activity
    log_event(
        level="INFO",
        message=f"Directory analyzed: {directory_path}",
        service="ai_assistant",
        action="analyze_directory",
        resource=directory_path,
        user_id=current_user.id,
        username=current_user.email or current_user.display_name
    )
    
    return analysis


@router.post("/ai/analyze-file")
async def analyze_file(
    request_data: dict,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Analyze a specific file and provide AI-powered insights.
    """
    file_path = request_data.get('path')
    
    if not file_path:
        raise HTTPException(status_code=400, detail="File path is required")
    
    # Security: Restrict to workspace directory
    workspace_root = Path(__file__).parent.parent.parent
    target_file = (workspace_root / file_path).resolve()
    
    if not str(target_file).startswith(str(workspace_root)):
        raise HTTPException(status_code=403, detail="Access denied: Path outside workspace")
    
    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Analyze file
    analysis = {
        "path": str(target_file.relative_to(workspace_root)),
        "absolute_path": str(target_file),
        "name": target_file.name,
        "size": target_file.stat().st_size,
        "extension": target_file.suffix,
        "modified": datetime.fromtimestamp(target_file.stat().st_mtime).isoformat(),
        "is_text": is_text_file(target_file),
        "is_code": is_code_file(target_file),
        "language": detect_language(target_file),
        "insights": [],
        "suggested_actions": [],
    }
    
    # Read content if text file
    if analysis["is_text"] and target_file.stat().st_size < 1_000_000:  # Max 1MB
        try:
            with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                analysis["content_preview"] = content[:500] if len(content) > 500 else content
                analysis["line_count"] = content.count('\n') + 1
                analysis["char_count"] = len(content)
                
                # Generate insights based on content
                analysis["insights"] = generate_file_insights(content, target_file)
        except Exception as e:
            analysis["read_error"] = str(e)
    
    # Generate suggested actions
    analysis["suggested_actions"] = generate_file_actions(analysis)
    
    # Log activity
    log_event(
        level="INFO",
        message=f"File analyzed: {file_path}",
        service="ai_assistant",
        action="analyze_file",
        resource=file_path,
        user_id=current_user.id,
        username=current_user.email or current_user.display_name
    )
    
    return analysis


@router.post("/ai/suggest-actions")
async def suggest_actions(
    request_data: dict,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get AI-suggested actions based on uploaded file or directory context.
    """
    context = request_data.get('context', {})
    file_type = context.get('file_type')
    file_content = context.get('content')
    
    suggestions = []
    
    # Generate context-aware suggestions
    if file_type in ['pdf', 'docx', 'txt']:
        suggestions.extend([
            {
                "action": "extract_text",
                "label": "Extract and analyze text content",
                "priority": "high"
            },
            {
                "action": "summarize",
                "label": "Generate summary",
                "priority": "high"
            },
            {
                "action": "extract_keywords",
                "label": "Extract keywords and topics",
                "priority": "medium"
            },
        ])
    
    if file_type in ['xlsx', 'csv']:
        suggestions.extend([
            {
                "action": "analyze_data",
                "label": "Analyze data patterns",
                "priority": "high"
            },
            {
                "action": "generate_charts",
                "label": "Generate visualizations",
                "priority": "medium"
            },
            {
                "action": "data_quality_check",
                "label": "Check data quality",
                "priority": "medium"
            },
        ])
    
    if file_type in ['py', 'js', 'ts', 'java', 'cpp']:
        suggestions.extend([
            {
                "action": "code_review",
                "label": "Perform code review",
                "priority": "high"
            },
            {
                "action": "find_bugs",
                "label": "Find potential bugs",
                "priority": "high"
            },
            {
                "action": "suggest_improvements",
                "label": "Suggest improvements",
                "priority": "medium"
            },
            {
                "action": "generate_tests",
                "label": "Generate unit tests",
                "priority": "medium"
            },
        ])
    
    if file_type in ['json', 'yaml', 'xml']:
        suggestions.extend([
            {
                "action": "validate_structure",
                "label": "Validate structure",
                "priority": "high"
            },
            {
                "action": "format_prettify",
                "label": "Format and prettify",
                "priority": "low"
            },
        ])
    
    # Add general suggestions
    suggestions.extend([
        {
            "action": "search_similar",
            "label": "Find similar files",
            "priority": "low"
        },
        {
            "action": "backup",
            "label": "Create backup",
            "priority": "low"
        },
    ])
    
    return {
        "suggestions": suggestions,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }


def is_text_file(path: Path) -> bool:
    """Check if file is likely a text file."""
    text_extensions = {'.txt', '.md', '.json', '.xml', '.html', '.css', '.js', '.ts', 
                      '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.sh', '.yaml', 
                      '.yml', '.csv', '.log', '.ini', '.conf', '.cfg'}
    return path.suffix.lower() in text_extensions


def is_code_file(path: Path) -> bool:
    """Check if file is a code file."""
    code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.c', '.cpp', 
                      '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift', 
                      '.kt', '.scala', '.r', '.m', '.sh', '.bat'}
    return path.suffix.lower() in code_extensions


def detect_language(path: Path) -> Optional[str]:
    """Detect programming language from file extension."""
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript React',
        '.jsx': 'JavaScript React',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
    }
    return language_map.get(path.suffix.lower())


def generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on directory analysis."""
    recommendations = []
    
    # Check for large files
    if analysis["total_size"] > 100_000_000:  # 100MB
        recommendations.append("Consider archiving or compressing large files")
    
    # Check file organization
    if len(analysis["files"]) > 50:
        recommendations.append("Directory contains many files. Consider organizing into subdirectories")
    
    # Check for specific patterns
    if '.py' in analysis.get("file_types", {}):
        recommendations.append("Python project detected. Ensure requirements.txt is present")
    
    if '.js' in analysis.get("file_types", {}) or '.ts' in analysis.get("file_types", {}):
        recommendations.append("JavaScript/TypeScript project detected. Check for package.json")
    
    return recommendations


def generate_file_insights(content: str, path: Path) -> List[str]:
    """Generate insights from file content."""
    insights = []
    
    lines = content.split('\n')
    
    # Code-specific insights
    if is_code_file(path):
        if len(lines) > 500:
            insights.append(f"Large file with {len(lines)} lines. Consider refactoring.")
        
        if 'TODO' in content or 'FIXME' in content:
            insights.append("Contains TODO or FIXME comments requiring attention")
        
        if 'import' in content[:200]:
            insights.append("File has external dependencies")
    
    # Configuration file insights
    if path.suffix in ['.json', '.yaml', '.yml', '.toml']:
        insights.append("Configuration file detected")
    
    return insights


def generate_file_actions(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate suggested actions for a file."""
    actions = []
    
    if analysis.get("is_text"):
        actions.append({
            "action": "view",
            "label": "View in editor",
            "icon": "eye"
        })
        actions.append({
            "action": "edit",
            "label": "Edit file",
            "icon": "edit"
        })
    
    if analysis.get("is_code"):
        actions.append({
            "action": "analyze_code",
            "label": "Run code analysis",
            "icon": "code"
        })
        actions.append({
            "action": "format",
            "label": "Format code",
            "icon": "sparkles"
        })
    
    actions.append({
        "action": "download",
        "label": "Download file",
        "icon": "download"
    })
    
    actions.append({
        "action": "delete",
        "label": "Delete file",
        "icon": "trash",
        "danger": True
    })
    
    return actions
