"""TODO management module for the master orchestrator.

This module handles extraction, tracking, and management of TODO items
across all projects.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from utils.exceptions import ValidationError
from utils.logger import get_logger, LogContext

logger = get_logger(__name__)


@dataclass
class TodoItem:
    """A TODO item extracted from project files."""
    
    project: str
    file: Path
    line_number: int
    content: str
    priority: str = "normal"  # low, normal, high, critical
    completed: bool = False
    
    def __post_init__(self) -> None:
        """Validate TODO item."""
        if self.priority not in {"low", "normal", "high", "critical"}:
            raise ValidationError(
                f"Invalid priority: {self.priority}",
                error_code="INVALID_PRIORITY",
                context={"priority": self.priority},
            )


class TodoManager:
    """Manages TODO extraction and tracking."""
    
    # Priority keywords
    CRITICAL_KEYWORDS = {"critical", "urgent", "asap", "blocker", "p0"}
    HIGH_KEYWORDS = {"important", "high", "p1", "priority"}
    LOW_KEYWORDS = {"low", "someday", "maybe", "p3", "nice-to-have"}
    
    # Completion markers
    COMPLETION_MARKERS = {"- [x]", "✓", "✅", "[done]", "[completed]"}
    
    def extract_todos(self, project_name: str, todo_files: List[Path]) -> List[TodoItem]:
        """Extract TODO items from project files.
        
        Args:
            project_name: Name of the project
            todo_files: List of TODO file paths
        
        Returns:
            List of extracted TODO items
        """
        context = LogContext(operation="extract_todos", project_id=project_name)
        todos: List[TodoItem] = []
        
        for todo_file in todo_files:
            try:
                file_todos = self._extract_from_file(project_name, todo_file)
                todos.extend(file_todos)
            except Exception as e:
                logger.warning(
                    f"Error reading TODO file {todo_file}: {e}",
                    extra={"context": context},
                )
        
        logger.info(
            f"Extracted {len(todos)} TODOs from {project_name}",
            extra={"context": context},
        )
        
        return todos
    
    def _extract_from_file(self, project_name: str, todo_file: Path) -> List[TodoItem]:
        """Extract TODOs from a single file.
        
        Args:
            project_name: Name of the project
            todo_file: Path to TODO file
        
        Returns:
            List of TODO items from the file
        """
        todos: List[TodoItem] = []
        
        try:
            with todo_file.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            logger.debug(f"Could not read {todo_file}: {e}")
            return todos
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Match TODO patterns
            if not self._is_todo_line(line):
                continue
            
            priority = self._determine_priority(line)
            completed = self._is_completed(line)
            
            todo = TodoItem(
                project=project_name,
                file=todo_file,
                line_number=line_num,
                content=line,
                priority=priority,
                completed=completed,
            )
            todos.append(todo)
        
        return todos
    
    def _is_todo_line(self, line: str) -> bool:
        """Check if a line contains a TODO marker.
        
        Args:
            line: Line to check
        
        Returns:
            True if line contains TODO marker
        """
        line_lower = line.lower()
        return any(
            marker in line_lower
            for marker in ["- [ ]", "todo:", "fixme:", "hack:", "note:", "xxx:"]
        )
    
    def _determine_priority(self, line: str) -> str:
        """Determine priority from TODO line.
        
        Args:
            line: TODO line content
        
        Returns:
            Priority level (low, normal, high, critical)
        """
        line_lower = line.lower()
        
        if any(keyword in line_lower for keyword in self.CRITICAL_KEYWORDS):
            return "critical"
        elif any(keyword in line_lower for keyword in self.HIGH_KEYWORDS):
            return "high"
        elif any(keyword in line_lower for keyword in self.LOW_KEYWORDS):
            return "low"
        else:
            return "normal"
    
    def _is_completed(self, line: str) -> bool:
        """Check if TODO is marked as completed.
        
        Args:
            line: TODO line content
        
        Returns:
            True if TODO is completed
        """
        line_lower = line.lower()
        return any(marker in line_lower for marker in self.COMPLETION_MARKERS)
    
    def filter_by_priority(
        self, todos: List[TodoItem], priorities: List[str]
    ) -> List[TodoItem]:
        """Filter TODOs by priority.
        
        Args:
            todos: List of TODO items
            priorities: List of priority levels to include
        
        Returns:
            Filtered list of TODO items
        """
        return [todo for todo in todos if todo.priority in priorities and not todo.completed]
    
    def group_by_project(self, todos: List[TodoItem]) -> dict[str, List[TodoItem]]:
        """Group TODOs by project.
        
        Args:
            todos: List of TODO items
        
        Returns:
            Dictionary mapping project names to TODO lists
        """
        grouped: dict[str, List[TodoItem]] = {}
        
        for todo in todos:
            if todo.project not in grouped:
                grouped[todo.project] = []
            grouped[todo.project].append(todo)
        
        return grouped
    
    def format_for_codex(self, todos: List[TodoItem]) -> str:
        """Format TODOs for codex consumption.
        
        Args:
            todos: List of TODO items to format
        
        Returns:
            Formatted string for codex
        """
        lines = [
            "=" * 80,
            "HIGH-PRIORITY TODOS - ACTION REQUIRED",
            "=" * 80,
            "",
            f"Found {len(todos)} high-priority TODO items that need attention:",
            "",
        ]
        
        # Group by project
        by_project = self.group_by_project(todos)
        
        for project_name, project_todos in sorted(by_project.items()):
            lines.append(f"## {project_name}")
            lines.append("")
            
            for todo in project_todos:
                lines.append(f"  [{todo.priority.upper()}] {todo.content}")
                lines.append(f"    Location: {todo.file.name}:{todo.line_number}")
                lines.append("")
        
        lines.extend([
            "",
            "=" * 80,
            "NEXT STEPS:",
            "=" * 80,
            "",
            "1. Review each TODO item and assess feasibility",
            "2. Create implementation tasks for each actionable item",
            "3. Execute fixes and improvements systematically",
            "4. Mark items as complete when finished",
            "5. Re-run this analysis to track progress",
            "",
        ])
        
        return "\n".join(lines)

