"""Project discovery module for the master orchestrator.

This module handles discovery and analysis of git repositories in the workspace.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple

from utils.exceptions import ProjectDiscoveryError
from utils.logger import get_logger, LogContext

logger = get_logger(__name__)


@dataclass
class ProjectInfo:
    """Information about a discovered project."""
    
    path: Path
    name: str
    has_ai_autofix: bool = False
    has_tests: bool = False
    git_branch: Optional[str] = None
    todo_files: List[Path] = field(default_factory=list)
    monitor_process: Optional[subprocess.Popen] = None
    last_health_check: float = 0.0
    status: str = "discovered"  # discovered, running, healthy, unhealthy, error


class ProjectDiscovery:
    """Handles discovery and analysis of git repositories."""
    
    # Directories to skip during discovery
    SKIP_DIRS = {
        "node_modules",
        "__pycache__",
        "venv",
        ".venv",
        ".mypy_cache",
        ".git",
        ".svn",
        ".hg",
        "dist",
        "build",
        ".tox",
        ".pytest_cache",
    }
    
    # TODO file patterns to search for
    TODO_PATTERNS = [
        "TODO.md",
        "TODOS.md",
        "TODO.txt",
        "REMAINING_TODOS.md",
        "OSD_TODO.md",
        "FUTURE_TODOS.md",
        ".todo",
        "todo.json",
    ]
    
    def __init__(self, root: Path, max_depth: int = 4) -> None:
        """Initialize project discovery.
        
        Args:
            root: Root directory to search
            max_depth: Maximum directory depth to search
        """
        self.root = root.expanduser().resolve()
        self.max_depth = max_depth
        
        if not self.root.exists():
            raise ProjectDiscoveryError(
                f"Root directory does not exist: {self.root}",
                error_code="ROOT_NOT_FOUND",
                context={"root": str(self.root)},
            )
    
    def discover_projects(self) -> List[ProjectInfo]:
        """Discover all git projects in the workspace.
        
        Returns:
            List of discovered projects
        
        Raises:
            ProjectDiscoveryError: If discovery fails
        """
        context = LogContext(operation="discover_projects")
        logger.info("Starting project discovery", extra={"context": context})
        
        projects: List[ProjectInfo] = []
        queue: List[Tuple[Path, int]] = [(self.root, 0)]
        seen: Set[Path] = set()
        
        try:
            while queue:
                current, depth = queue.pop(0)
                
                if current in seen or depth > self.max_depth:
                    continue
                
                seen.add(current)
                
                # Check if this is a git repository
                git_dir = current / ".git"
                if git_dir.exists():
                    try:
                        project = self._analyze_project(current)
                        projects.append(project)
                        logger.info(
                            f"Found project: {project.name}",
                            extra={"context": LogContext(project_id=project.name)},
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to analyze project at {current}: {e}",
                            extra={"context": context},
                        )
                    continue
                
                # Explore subdirectories
                try:
                    for child in current.iterdir():
                        if not child.is_dir():
                            continue
                        if child.name.startswith(".") and child.name != ".git":
                            continue
                        if child.name in self.SKIP_DIRS:
                            continue
                        queue.append((child, depth + 1))
                except (PermissionError, OSError) as e:
                    logger.warning(
                        f"Cannot access {current}: {e}",
                        extra={"context": context},
                    )
                    continue
            
            logger.info(
                f"Discovery complete: found {len(projects)} projects",
                extra={"context": context},
            )
            return projects
            
        except Exception as e:
            raise ProjectDiscoveryError(
                "Project discovery failed",
                error_code="DISCOVERY_FAILED",
                context={"root": str(self.root), "max_depth": self.max_depth},
                cause=e,
            ) from e
    
    def _analyze_project(self, path: Path) -> ProjectInfo:
        """Analyze a project and gather information.
        
        Args:
            path: Path to project directory
        
        Returns:
            ProjectInfo with project details
        """
        name = path.name
        
        # Check for AI auto-fix script
        has_ai_autofix = (path / "scripts" / "ai_auto_fix.py").exists()
        
        # Check for tests
        has_tests = (
            (path / "tests").exists()
            or (path / "test").exists()
            or (path / "pytest.ini").exists()
            or (path / "package.json").exists()
        )
        
        # Get current git branch
        git_branch = self._get_git_branch(path)
        
        # Find TODO files
        todo_files = self._find_todo_files(path)
        
        return ProjectInfo(
            path=path,
            name=name,
            has_ai_autofix=has_ai_autofix,
            has_tests=has_tests,
            git_branch=git_branch,
            todo_files=todo_files,
        )
    
    def _get_git_branch(self, repo: Path) -> Optional[str]:
        """Get the current git branch.
        
        Args:
            repo: Path to git repository
        
        Returns:
            Current branch name or None if unavailable
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.warning(f"Git branch check timed out for {repo}")
        except Exception as e:
            logger.debug(f"Could not get git branch for {repo}: {e}")
        
        return None
    
    def _find_todo_files(self, repo: Path) -> List[Path]:
        """Find TODO-related files in a repository.
        
        Args:
            repo: Path to repository
        
        Returns:
            List of TODO file paths
        """
        todo_files: List[Path] = []
        
        for pattern in self.TODO_PATTERNS:
            todo_file = repo / pattern
            if todo_file.exists():
                todo_files.append(todo_file)
        
        return todo_files


