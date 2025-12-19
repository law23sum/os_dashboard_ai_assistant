#!/usr/bin/env python3
"""Unified Project Orchestrator - Master control for all git repositories.

This script implements the OS Dashboard AI Assistant's vision of a unified
orchestration system that:
1. Discovers all git repositories in the workspace
2. Executes AI auto-fix scripts to find and resolve bugs
3. Reads remaining TODOs from each project
4. Triggers codex continuation for pending work
5. Provides structured reporting for dashboards

Per Technical Spec V6 Section 5.3 (Unix/Kernel Execution Layer) and
Section 8.13 (Auto-Remediation Playbooks), this orchestrator provides
governed, auditable automation across all projects.

Examples:
    # Scan and report on all projects
    python scripts/unified_project_orchestrator.py --root ~/Projects --report-only

    # Execute auto-fix across all projects
    python scripts/unified_project_orchestrator.py --root ~/Projects --execute

    # Execute with TODO continuation handoff
    python scripts/unified_project_orchestrator.py --root ~/Projects --execute --continue-todos

    # Export structured JSON for dashboard consumption
    python scripts/unified_project_orchestrator.py --root . --output workspace_health.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".next",
    "coverage", ".tox", "eggs", ".eggs"
}

# TODO file patterns to search for
TODO_FILE_PATTERNS = [
    "TODO.md", "TODO.txt", "TODOS.md", "TODO",
    "REMAINING_TODOS.md", "FUTURE_TODOS.md",
    "ROADMAP.md", ".todo", "tasks.md", "backlog.md"
]

# Manifest file for per-project configuration
MANIFEST_FILE = ".osdash-auto.json"


@dataclass
class TodoItem:
    """Represents a single TODO item extracted from project files."""
    id: str
    content: str
    source_file: str
    line_number: int
    priority: str = "normal"  # low, normal, high, critical
    status: str = "pending"   # pending, in_progress, completed
    category: str = "general" # general, bug, feature, enhancement, security
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectManifest:
    """Per-project configuration manifest (.osdash-auto.json)."""
    enabled: bool = True
    test_command: Optional[str] = None
    lint_command: Optional[str] = None
    autofix_enabled: bool = True
    todo_continuation: bool = True
    skip_patterns: List[str] = field(default_factory=list)
    custom_scripts: Dict[str, str] = field(default_factory=dict)
    notes: str = ""
    
    @classmethod
    def load(cls, path: Path) -> "ProjectManifest":
        manifest_file = path / MANIFEST_FILE
        if manifest_file.exists():
            try:
                data = json.loads(manifest_file.read_text())
                return cls(
                    enabled=data.get("enabled", True),
                    test_command=data.get("test_command"),
                    lint_command=data.get("lint_command"),
                    autofix_enabled=data.get("autofix_enabled", True),
                    todo_continuation=data.get("todo_continuation", True),
                    skip_patterns=data.get("skip_patterns", []),
                    custom_scripts=data.get("custom_scripts", {}),
                    notes=data.get("notes", ""),
                )
            except Exception:
                pass
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectHealth:
    """Health status for a single project."""
    path: Path
    name: str
    has_git: bool = True
    has_autofix_script: bool = False
    has_tests: bool = False
    has_manifest: bool = False
    manifest: Optional[ProjectManifest] = None
    todos: List[TodoItem] = field(default_factory=list)
    autofix_status: str = "not_run"  # not_run, running, passed, failed, skipped
    test_status: str = "not_run"
    lint_status: str = "not_run"
    last_checked: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "name": self.name,
            "has_git": self.has_git,
            "has_autofix_script": self.has_autofix_script,
            "has_tests": self.has_tests,
            "has_manifest": self.has_manifest,
            "manifest": self.manifest.to_dict() if self.manifest else None,
            "todos": [t.to_dict() for t in self.todos],
            "autofix_status": self.autofix_status,
            "test_status": self.test_status,
            "lint_status": self.lint_status,
            "last_checked": self.last_checked,
            "errors": self.errors,
            "warnings": self.warnings,
            "health_score": self.calculate_health_score(),
        }
    
    def calculate_health_score(self) -> int:
        """Calculate a 0-100 health score for the project."""
        score = 50  # Base score
        
        if self.has_autofix_script:
            score += 10
        if self.has_tests:
            score += 10
        if self.has_manifest:
            score += 5
        
        if self.autofix_status == "passed":
            score += 15
        elif self.autofix_status == "failed":
            score -= 20
            
        if self.test_status == "passed":
            score += 15
        elif self.test_status == "failed":
            score -= 20
        
        # Penalize for errors and warnings
        score -= len(self.errors) * 5
        score -= len(self.warnings) * 2
        
        # Bonus for having manageable TODO count
        todo_count = len(self.todos)
        if todo_count == 0:
            score += 5
        elif todo_count <= 5:
            score += 3
        elif todo_count > 20:
            score -= 5
        
        return max(0, min(100, score))


@dataclass
class WorkspaceReport:
    """Complete workspace health report."""
    root: Path
    scan_timestamp: str
    projects: List[ProjectHealth]
    total_todos: int = 0
    aggregated_todos: List[TodoItem] = field(default_factory=list)
    continuation_payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": str(self.root),
            "scan_timestamp": self.scan_timestamp,
            "summary": {
                "total_projects": len(self.projects),
                "healthy_projects": sum(1 for p in self.projects if p.calculate_health_score() >= 70),
                "warning_projects": sum(1 for p in self.projects if 40 <= p.calculate_health_score() < 70),
                "critical_projects": sum(1 for p in self.projects if p.calculate_health_score() < 40),
                "total_todos": self.total_todos,
                "average_health": sum(p.calculate_health_score() for p in self.projects) // max(1, len(self.projects)),
            },
            "projects": [p.to_dict() for p in self.projects],
            "aggregated_todos": [t.to_dict() for t in self.aggregated_todos],
            "continuation_payload": self.continuation_payload,
        }


class TodoExtractor:
    """Extract TODO items from project files."""
    
    # Patterns for extracting TODOs from markdown files
    MD_TODO_PATTERN = re.compile(
        r'^[-*]\s*\[([xX ])\]\s*(.+)$',
        re.MULTILINE
    )
    
    # Patterns for inline code TODOs
    CODE_TODO_PATTERN = re.compile(
        r'#\s*TODO[:\s]*(.+)$|//\s*TODO[:\s]*(.+)$|/\*\s*TODO[:\s]*(.+)\*/',
        re.MULTILINE | re.IGNORECASE
    )
    
    # Priority keywords
    PRIORITY_KEYWORDS = {
        "critical": ["critical", "urgent", "asap", "blocker", "p0"],
        "high": ["high", "important", "priority", "p1"],
        "low": ["low", "minor", "eventually", "p3", "nice-to-have"],
    }
    
    # Category keywords
    CATEGORY_KEYWORDS = {
        "bug": ["bug", "fix", "error", "issue", "broken"],
        "feature": ["feature", "add", "implement", "create", "new"],
        "enhancement": ["enhance", "improve", "optimize", "refactor", "update"],
        "security": ["security", "auth", "permission", "vulnerability", "secure"],
    }
    
    def extract_from_project(self, project_path: Path) -> List[TodoItem]:
        """Extract all TODOs from a project."""
        todos: List[TodoItem] = []
        
        # Search for TODO files
        for pattern in TODO_FILE_PATTERNS:
            for todo_file in project_path.glob(f"**/{pattern}"):
                if any(skip in str(todo_file) for skip in DEFAULT_SKIP_DIRS):
                    continue
                todos.extend(self._extract_from_markdown(todo_file))
        
        # Search for inline TODOs in source files
        for ext in ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.sh"]:
            for source_file in project_path.glob(f"**/{ext}"):
                if any(skip in str(source_file) for skip in DEFAULT_SKIP_DIRS):
                    continue
                todos.extend(self._extract_from_code(source_file))
        
        return todos
    
    def _extract_from_markdown(self, file_path: Path) -> List[TodoItem]:
        """Extract TODOs from markdown files."""
        todos: List[TodoItem] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            for line_num, line in enumerate(content.splitlines(), start=1):
                match = self.MD_TODO_PATTERN.match(line.strip())
                if match:
                    checkbox, text = match.groups()
                    status = "completed" if checkbox.lower() == "x" else "pending"
                    todos.append(TodoItem(
                        id=self._generate_id(file_path, line_num, text),
                        content=text.strip(),
                        source_file=str(file_path),
                        line_number=line_num,
                        priority=self._detect_priority(text),
                        status=status,
                        category=self._detect_category(text),
                    ))
        except Exception:
            pass
        return todos
    
    def _extract_from_code(self, file_path: Path) -> List[TodoItem]:
        """Extract inline TODOs from source code."""
        todos: List[TodoItem] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            for line_num, line in enumerate(content.splitlines(), start=1):
                match = self.CODE_TODO_PATTERN.search(line)
                if match:
                    text = match.group(1) or match.group(2) or match.group(3)
                    if text:
                        todos.append(TodoItem(
                            id=self._generate_id(file_path, line_num, text),
                            content=text.strip(),
                            source_file=str(file_path),
                            line_number=line_num,
                            priority=self._detect_priority(text),
                            status="pending",
                            category=self._detect_category(text),
                        ))
        except Exception:
            pass
        return todos
    
    def _generate_id(self, file_path: Path, line: int, content: str) -> str:
        """Generate a unique ID for a TODO item."""
        data = f"{file_path}:{line}:{content}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _detect_priority(self, text: str) -> str:
        """Detect priority from TODO text."""
        text_lower = text.lower()
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return priority
        return "normal"
    
    def _detect_category(self, text: str) -> str:
        """Detect category from TODO text."""
        text_lower = text.lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return category
        return "general"


class UnifiedOrchestrator:
    """Master orchestrator for all git projects."""
    
    def __init__(
        self,
        root: Path,
        max_depth: int = 4,
        skip_dirs: Optional[Iterable[str]] = None,
        include_patterns: Optional[Sequence[str]] = None,
        exclude_patterns: Optional[Sequence[str]] = None,
        execute: bool = False,
        continue_todos: bool = False,
        verbose: bool = True,
    ):
        self.root = root.expanduser().resolve()
        self.max_depth = max_depth
        self.skip_dirs = set(skip_dirs or DEFAULT_SKIP_DIRS)
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.execute = execute
        self.continue_todos = continue_todos
        self.verbose = verbose
        self.todo_extractor = TodoExtractor()
        self._python = sys.executable
    
    def discover_projects(self) -> List[Path]:
        """Discover all git repositories under the root."""
        repos: List[Path] = []
        queue: List[Tuple[Path, int]] = [(self.root, 0)]
        
        while queue:
            current, depth = queue.pop()
            git_marker = current / ".git"
            
            if git_marker.exists():
                if self._should_include(current):
                    repos.append(current)
                continue
            
            if depth >= self.max_depth:
                continue
            
            try:
                for child in current.iterdir():
                    if not child.is_dir():
                        continue
                    if child.name in self.skip_dirs:
                        continue
                    queue.append((child, depth + 1))
            except PermissionError:
                continue
        
        return sorted(set(repos))
    
    def _should_include(self, path: Path) -> bool:
        """Check if a project should be included based on patterns."""
        path_str = str(path)
        
        if self.include_patterns:
            if not any(p in path_str for p in self.include_patterns):
                return False
        
        if self.exclude_patterns:
            if any(p in path_str for p in self.exclude_patterns):
                return False
        
        return True
    
    def analyze_project(self, project_path: Path) -> ProjectHealth:
        """Analyze a single project's health."""
        health = ProjectHealth(
            path=project_path,
            name=project_path.name,
            last_checked=datetime.now(timezone.utc).isoformat(),
        )
        
        # Check for autofix script
        autofix_script = project_path / "scripts" / "ai_auto_fix.py"
        health.has_autofix_script = autofix_script.exists()
        
        # Check for tests
        health.has_tests = (
            (project_path / "tests").is_dir() or
            (project_path / "pytest.ini").exists() or
            (project_path / "package.json").exists()
        )
        
        # Load manifest
        health.manifest = ProjectManifest.load(project_path)
        health.has_manifest = (project_path / MANIFEST_FILE).exists()
        
        # Extract TODOs
        try:
            health.todos = self.todo_extractor.extract_from_project(project_path)
        except Exception as e:
            health.warnings.append(f"Failed to extract TODOs: {e}")
        
        # Check for common issues
        if not health.has_autofix_script:
            health.warnings.append("No ai_auto_fix.py script found")
        if not health.has_tests:
            health.warnings.append("No test directory found")
        if not health.has_manifest:
            health.warnings.append("No .osdash-auto.json manifest found")
        
        return health
    
    def run_autofix(self, project: ProjectHealth) -> bool:
        """Run AI auto-fix on a project."""
        if not project.has_autofix_script:
            project.autofix_status = "skipped"
            return False
        
        if project.manifest and not project.manifest.autofix_enabled:
            project.autofix_status = "skipped"
            return False
        
        script_path = project.path / "scripts" / "ai_auto_fix.py"
        
        self._log(f"🔧 Running auto-fix for {project.name}...")
        project.autofix_status = "running"
        
        try:
            result = subprocess.run(
                [self._python, str(script_path), "--logs-only", "--no-daemon", "--verify-seconds", "10"],
                cwd=project.path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode == 0:
                project.autofix_status = "passed"
                self._log(f"✅ Auto-fix passed for {project.name}")
                return True
            else:
                project.autofix_status = "failed"
                project.errors.append(f"Auto-fix failed: {result.stderr[:500]}")
                self._log(f"❌ Auto-fix failed for {project.name}")
                return False
                
        except subprocess.TimeoutExpired:
            project.autofix_status = "failed"
            project.errors.append("Auto-fix timed out")
            return False
        except Exception as e:
            project.autofix_status = "failed"
            project.errors.append(f"Auto-fix error: {e}")
            return False
    
    def run_tests(self, project: ProjectHealth) -> bool:
        """Run tests on a project."""
        if not project.has_tests:
            project.test_status = "skipped"
            return False
        
        # Determine test command
        test_cmd: Optional[List[str]] = None
        
        if project.manifest and project.manifest.test_command:
            test_cmd = shlex.split(project.manifest.test_command)
        elif (project.path / "pytest.ini").exists() or (project.path / "tests").is_dir():
            test_cmd = [self._python, "-m", "pytest", "-q", "--tb=short"]
        elif (project.path / "package.json").exists():
            test_cmd = ["npm", "test", "--", "--runInBand", "--passWithNoTests"]
        
        if not test_cmd:
            project.test_status = "skipped"
            return False
        
        self._log(f"🧪 Running tests for {project.name}...")
        project.test_status = "running"
        
        try:
            result = subprocess.run(
                test_cmd,
                cwd=project.path,
                capture_output=True,
                text=True,
                timeout=300,
            )
            
            if result.returncode == 0:
                project.test_status = "passed"
                self._log(f"✅ Tests passed for {project.name}")
                return True
            else:
                project.test_status = "failed"
                project.errors.append(f"Tests failed: {result.stdout[:500]}")
                self._log(f"❌ Tests failed for {project.name}")
                return False
                
        except subprocess.TimeoutExpired:
            project.test_status = "failed"
            project.errors.append("Tests timed out")
            return False
        except Exception as e:
            project.test_status = "failed"
            project.errors.append(f"Test error: {e}")
            return False
    
    def generate_continuation_payload(self, report: WorkspaceReport) -> Dict[str, Any]:
        """Generate payload for codex continuation."""
        # Collect all pending high-priority TODOs
        critical_todos = [
            t for t in report.aggregated_todos
            if t.status == "pending" and t.priority in ("critical", "high")
        ]
        
        # Collect failed projects
        failed_projects = [
            p for p in report.projects
            if p.autofix_status == "failed" or p.test_status == "failed"
        ]
        
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workspace_root": str(report.root),
            "continuation_required": len(critical_todos) > 0 or len(failed_projects) > 0,
            "priority_todos": [t.to_dict() for t in critical_todos[:20]],
            "failed_projects": [
                {
                    "name": p.name,
                    "path": str(p.path),
                    "errors": p.errors,
                    "autofix_status": p.autofix_status,
                    "test_status": p.test_status,
                }
                for p in failed_projects
            ],
            "recommended_actions": [],
            "context_for_next_session": "",
        }
        
        # Build recommended actions
        if critical_todos:
            payload["recommended_actions"].append({
                "action": "address_critical_todos",
                "description": f"Address {len(critical_todos)} critical/high priority TODOs",
                "items": [t.content for t in critical_todos[:5]],
            })
        
        if failed_projects:
            payload["recommended_actions"].append({
                "action": "fix_failed_projects",
                "description": f"Fix {len(failed_projects)} projects with failing tests/autofix",
                "projects": [p.name for p in failed_projects],
            })
        
        # Build context string for next session
        context_lines = [
            "## Workspace Continuation Context",
            f"Scanned: {len(report.projects)} projects",
            f"Healthy: {sum(1 for p in report.projects if p.calculate_health_score() >= 70)}",
            f"Critical TODOs: {len(critical_todos)}",
            "",
            "### Priority Items:",
        ]
        
        for todo in critical_todos[:10]:
            context_lines.append(f"- [{todo.priority.upper()}] {todo.content}")
        
        payload["context_for_next_session"] = "\n".join(context_lines)
        
        return payload
    
    def orchestrate(self) -> WorkspaceReport:
        """Run the full orchestration workflow."""
        self._log(f"🔍 Scanning workspace: {self.root}")
        
        # Discover projects
        project_paths = self.discover_projects()
        self._log(f"📁 Found {len(project_paths)} git repositories")
        
        # Analyze each project
        projects: List[ProjectHealth] = []
        all_todos: List[TodoItem] = []
        
        for path in project_paths:
            self._log(f"\n📦 Analyzing: {path.name}")
            health = self.analyze_project(path)
            
            if self.execute and health.manifest and health.manifest.enabled:
                # Run auto-fix
                self.run_autofix(health)
                
                # Run tests
                self.run_tests(health)
            
            projects.append(health)
            all_todos.extend(health.todos)
        
        # Create report
        report = WorkspaceReport(
            root=self.root,
            scan_timestamp=datetime.now(timezone.utc).isoformat(),
            projects=projects,
            total_todos=len(all_todos),
            aggregated_todos=all_todos,
        )
        
        # Generate continuation payload
        report.continuation_payload = self.generate_continuation_payload(report)
        
        # Handle TODO continuation
        if self.continue_todos and report.continuation_payload.get("continuation_required"):
            self._trigger_continuation(report)
        
        return report
    
    def _trigger_continuation(self, report: WorkspaceReport) -> None:
        """Trigger a new codex session with remaining TODOs."""
        self._log("\n🔄 Triggering TODO continuation...")
        
        # Write continuation file for next session
        continuation_file = self.root / ".osdash-continuation.json"
        continuation_file.write_text(
            json.dumps(report.continuation_payload, indent=2),
            encoding="utf-8"
        )
        
        self._log(f"📝 Continuation payload written to: {continuation_file}")
        self._log("💡 Next codex session should read this file to continue work")
        
        # Print context for manual handoff
        print("\n" + "="*60)
        print("CONTINUATION CONTEXT FOR NEXT SESSION")
        print("="*60)
        print(report.continuation_payload.get("context_for_next_session", ""))
        print("="*60)
    
    def _log(self, message: str) -> None:
        """Print a log message if verbose."""
        if self.verbose:
            print(message)


# Compatibility aliases and wrapper functions for API usage
UnifiedProjectOrchestrator = UnifiedOrchestrator


def discover_git_repos(root: Path, max_depth: int = 5) -> List[Path]:
    """Discover all git repositories under the root directory."""
    orchestrator = UnifiedOrchestrator(root=root, max_depth=max_depth, verbose=False)
    return orchestrator.discover_projects()


def create_project_status(repo_path: Path) -> ProjectHealth:
    """Create a project status/health object for a repository."""
    orchestrator = UnifiedOrchestrator(root=repo_path.parent, verbose=False)
    return orchestrator.analyze_project(repo_path)


def detect_project_capabilities(project_path: Path) -> Dict[str, Any]:
    """Detect project capabilities (languages, frameworks, etc.)."""
    health = create_project_status(project_path)
    return health.metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unified Project Orchestrator - Master control for all git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Scan and report on all projects
    python scripts/unified_project_orchestrator.py --root ~/Projects --report-only

    # Execute auto-fix across all projects
    python scripts/unified_project_orchestrator.py --root ~/Projects --execute

    # Execute with TODO continuation handoff
    python scripts/unified_project_orchestrator.py --root ~/Projects --execute --continue-todos
        """
    )
    
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Workspace root to scan for git repositories",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="Maximum directory depth to scan",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Only process projects matching this pattern (repeatable)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Skip projects matching this pattern (repeatable)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute auto-fix and tests on discovered projects",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate report without executing anything",
    )
    parser.add_argument(
        "--continue-todos",
        action="store_true",
        help="Trigger continuation session for remaining TODOs",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file for JSON report",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )
    
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    orchestrator = UnifiedOrchestrator(
        root=args.root,
        max_depth=args.max_depth,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        execute=args.execute and not args.report_only,
        continue_todos=args.continue_todos,
        verbose=not args.quiet,
    )
    
    report = orchestrator.orchestrate()
    
    # Output report
    report_dict = report.to_dict()
    
    if args.output:
        args.output.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")
        print(f"\n📊 Report written to: {args.output}")
    else:
        print(json.dumps(report_dict, indent=2))
    
    # Print summary
    summary = report_dict["summary"]
    print(f"\n{'='*60}")
    print("WORKSPACE HEALTH SUMMARY")
    print(f"{'='*60}")
    print(f"Total Projects:    {summary['total_projects']}")
    print(f"Healthy (70+):     {summary['healthy_projects']}")
    print(f"Warning (40-69):   {summary['warning_projects']}")
    print(f"Critical (<40):    {summary['critical_projects']}")
    print(f"Total TODOs:       {summary['total_todos']}")
    print(f"Average Health:    {summary['average_health']}%")
    print(f"{'='*60}")
    
    # Return exit code based on health
    if summary['critical_projects'] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())