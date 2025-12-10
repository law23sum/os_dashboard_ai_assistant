"""Code analysis tools for developers."""

import os
from pathlib import Path
from typing import Dict, List, Optional
import re

from .ai import generate_ai_reply, openai_available, get_agent_model


# Supported file extensions by language
LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
    "c": [".c", ".h"],
    "go": [".go"],
    "rust": [".rs"],
    "ruby": [".rb"],
    "php": [".php"],
    "swift": [".swift"],
    "kotlin": [".kt"],
    "scala": [".scala"],
}


def detect_language(file_path: str) -> Optional[str]:
    """Detect programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return lang
    return None


def read_code_file(file_path: str, max_lines: int = 2000) -> Optional[str]:
    """Read a code file, limiting size for analysis."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            if len(lines) > max_lines:
                # Return first and last portions
                first = "".join(lines[: max_lines // 2])
                last = "".join(lines[-max_lines // 2 :])
                return f"{first}\n\n[... {len(lines) - max_lines} lines omitted ...]\n\n{last}"
            return "".join(lines)
    except Exception as e:
        return None


def analyze_code_file(file_path: str, analysis_type: str = "review") -> Dict:
    """Analyze a code file.

    Args:
        file_path: Path to code file
        analysis_type: "review" | "documentation" | "refactor" | "bugs"

    Returns:
        Dict with analysis results
    """
    if not os.path.exists(file_path):
        return {"error": "File not found", "file_path": file_path}

    language = detect_language(file_path)
    if not language:
        return {"error": "Unsupported file type", "file_path": file_path}

    code_content = read_code_file(file_path)
    if not code_content:
        return {"error": "Could not read file", "file_path": file_path}

    if not openai_available():
        return {
            "error": "OpenAI API not available",
            "file_path": file_path,
            "language": language,
        }

    # Build prompt based on analysis type
    prompts = {
        "review": f"""Review this {language} code for:
1. Code quality and best practices
2. Potential bugs and issues
3. Performance concerns
4. Security vulnerabilities
5. Maintainability

Provide specific, actionable feedback.""",
        "documentation": f"""Generate documentation for this {language} code:
1. Function/class descriptions
2. Parameter documentation
3. Return value documentation
4. Usage examples
5. Any important notes

Format as clear, professional documentation.""",
        "refactor": f"""Suggest refactoring improvements for this {language} code:
1. Code structure improvements
2. Naming conventions
3. Design patterns that could be applied
4. Code organization
5. Readability enhancements

Provide specific suggestions with examples.""",
        "bugs": f"""Analyze this {language} code for bugs:
1. Logic errors
2. Edge cases not handled
3. Type issues
4. Potential runtime errors
5. Off-by-one errors or boundary conditions

List each bug with severity and suggested fix.""",
    }

    prompt = prompts.get(analysis_type, prompts["review"])

    full_prompt = f"""{prompt}

File: {os.path.basename(file_path)}
Language: {language}

Code:
```{language}
{code_content}
```"""

    try:
        analysis = generate_ai_reply(
            full_prompt,
            system_prompt=f"You are an expert {language} code reviewer. Provide clear, specific, actionable feedback.",
            model=get_agent_model("AIC"),
        )

        return {
            "file_path": file_path,
            "language": language,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "code_length": len(code_content),
            "lines_analyzed": code_content.count("\n"),
        }
    except Exception as e:
        return {"error": str(e), "file_path": file_path, "language": language}


def analyze_project_structure(project_path: str) -> Dict:
    """Analyze overall project structure and architecture.

    Args:
        project_path: Root directory of project

    Returns:
        Dict with structure analysis
    """
    if not os.path.isdir(project_path):
        return {"error": "Directory not found", "project_path": project_path}

    # Collect file information
    code_files = []
    languages = {}
    total_lines = 0

    for root, dirs, files in os.walk(project_path):
        # Skip common directories
        skip_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "build",
            "dist",
        }
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            language = detect_language(file_path)
            if language:
                rel_path = os.path.relpath(file_path, project_path)
                code_files.append(rel_path)
                languages[language] = languages.get(language, 0) + 1

                # Count lines
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        total_lines += len(f.readlines())
                except Exception:
                    pass

    # Analyze structure
    structure_info = {
        "project_path": project_path,
        "total_code_files": len(code_files),
        "languages": languages,
        "total_lines": total_lines,
        "file_structure": _analyze_file_structure(code_files),
    }

    # Get AI analysis if available
    if openai_available() and code_files:
        try:
            prompt = f"""Analyze this project structure:

Languages: {', '.join(languages.keys())}
Total Files: {len(code_files)}
Total Lines: {total_lines:,}

File Structure:
{chr(10).join(code_files[:50])}  # Show first 50 files
{'...' if len(code_files) > 50 else ''}

Provide:
1. Architecture assessment
2. Organization quality
3. Potential improvements
4. Missing patterns or best practices
"""

            ai_analysis = generate_ai_reply(
                prompt,
                system_prompt="You are a software architecture expert. Analyze project structure and provide insights.",
                model=get_agent_model("AIC"),
            )

            structure_info["ai_analysis"] = ai_analysis
        except Exception:
            pass

    return structure_info


def _analyze_file_structure(files: List[str]) -> Dict:
    """Analyze file structure patterns."""
    structure = {
        "has_tests": any("test" in f.lower() or "spec" in f.lower() for f in files),
        "has_docs": any("readme" in f.lower() or "doc" in f.lower() for f in files),
        "has_config": any("config" in f.lower() or "setup" in f.lower() for f in files),
        "directories": {},
    }

    # Count files by directory
    for file in files:
        dir_path = os.path.dirname(file) or "."
        if dir_path not in structure["directories"]:
            structure["directories"][dir_path] = 0
        structure["directories"][dir_path] += 1

    return structure
