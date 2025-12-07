"""Code analysis tools for developers."""

import os
from typing import Dict, List, Optional
from pathlib import Path

from .ai import generate_ai_reply, openai_available, get_agent_model


def analyze_code_file(file_path: str, analysis_type: str = "review") -> Dict:
    """Analyze a code file using AI."""
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"Cannot read file: {str(e)}"}
    
    if not openai_available():
        return {"error": "OpenAI API not available"}
    
    file_ext = Path(file_path).suffix
    language = _detect_language(file_ext)
    
    prompts = {
        "review": f"""Review this {language} code file and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Performance concerns
4. Best practices suggestions
5. Security considerations

File: {file_path}
Code:
{content[:8000]}  # Limit to 8000 chars
""",
        "documentation": f"""Generate comprehensive documentation for this {language} code file:
1. Function/class descriptions
2. Parameter documentation
3. Return value documentation
4. Usage examples
5. Notes on important implementation details

File: {file_path}
Code:
{content[:8000]}
""",
        "refactor": f"""Suggest refactoring improvements for this {language} code:
1. Code structure improvements
2. Naming suggestions
3. Duplication elimination
4. Design pattern recommendations
5. Maintainability improvements

File: {file_path}
Code:
{content[:8000]}
""",
        "bugs": f"""Analyze this {language} code for potential bugs:
1. Logic errors
2. Edge cases not handled
3. Type mismatches
4. Null pointer risks
5. Race conditions (if applicable)

File: {file_path}
Code:
{content[:8000]}
"""
    }
    
    prompt = prompts.get(analysis_type, prompts["review"])
    
    try:
        response = generate_ai_reply(
            prompt,
            system_prompt=f"You are an expert {language} code reviewer providing detailed, actionable feedback.",
            model=get_agent_model("AIC")
        )
        
        return {
            "file_path": file_path,
            "language": language,
            "analysis_type": analysis_type,
            "analysis": response,
            "file_size": len(content),
            "lines": len(content.split('\n'))
        }
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def _detect_language(extension: str) -> str:
    """Detect programming language from file extension."""
    lang_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".sql": "SQL",
        ".html": "HTML",
        ".css": "CSS",
        ".sh": "Bash",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".json": "JSON"
    }
    return lang_map.get(extension.lower(), "Unknown")


def analyze_project_structure(project_path: str) -> Dict:
    """Analyze overall project structure and architecture."""
    if not os.path.exists(project_path):
        return {"error": "Project path not found"}
    
    if not openai_available():
        return {"error": "OpenAI API not available"}
    
    # Get project structure
    structure = _get_project_structure(project_path)
    
    prompt = f"""Analyze this project structure and provide:
1. Architecture assessment
2. Organization quality
3. Potential improvements
4. Missing components
5. Best practices recommendations

Project Structure:
{structure[:4000]}
"""
    
    try:
        response = generate_ai_reply(
            prompt,
            system_prompt="You are an expert software architect analyzing project structure and organization.",
            model=get_agent_model("AIC")
        )
        
        return {
            "project_path": project_path,
            "structure": structure,
            "analysis": response
        }
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def _get_project_structure(path: str, max_depth: int = 3, current_depth: int = 0) -> str:
    """Get a text representation of project structure."""
    if current_depth >= max_depth:
        return ""
    
    lines = []
    try:
        items = sorted(os.listdir(path))
        for item in items:
            if item.startswith('.') and item not in ['.git']:
                continue
            
            item_path = os.path.join(path, item)
            indent = "  " * current_depth
            
            if os.path.isdir(item_path):
                lines.append(f"{indent}{item}/")
                if current_depth < max_depth - 1:
                    sub_structure = _get_project_structure(item_path, max_depth, current_depth + 1)
                    lines.append(sub_structure)
            else:
                lines.append(f"{indent}{item}")
    except Exception:
        pass
    
    return "\n".join(lines)

