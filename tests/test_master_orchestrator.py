#!/usr/bin/env python3
"""
Tests for Master Orchestrator System

Comprehensive test suite for all orchestrator components.
"""

import json
import pytest
import tempfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestProjectDiscovery:
    """Test project discovery functionality."""
    
    def test_discover_single_project(self, tmp_path):
        """Test discovering a single git project."""
        # Create a mock git repository
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()
        
        # Import here to avoid issues if module not available
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path, max_depth=2)
            projects = orchestrator.discover_projects()
            
            assert len(projects) == 1
            assert projects[0].name == "test-project"
            assert projects[0].path == project_dir
        except ImportError as e:
            pytest.skip(f"Cannot import orchestrator: {e}")
    
    def test_discover_multiple_projects(self, tmp_path):
        """Test discovering multiple git projects."""
        # Create multiple mock repositories
        for i in range(3):
            project_dir = tmp_path / f"project-{i}"
            project_dir.mkdir()
            (project_dir / ".git").mkdir()
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path, max_depth=2)
            projects = orchestrator.discover_projects()
            
            assert len(projects) == 3
            project_names = {p.name for p in projects}
            assert project_names == {"project-0", "project-1", "project-2"}
        except ImportError:
            pytest.skip("Cannot import orchestrator")
    
    def test_discover_nested_projects(self, tmp_path):
        """Test discovering nested git projects."""
        # Create nested structure
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / ".git").mkdir()
        
        child = parent / "child"
        child.mkdir()
        (child / ".git").mkdir()
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path, max_depth=3)
            projects = orchestrator.discover_projects()
            
            # Should find parent but not child (stops at first .git)
            assert len(projects) == 1
            assert projects[0].name == "parent"
        except ImportError:
            pytest.skip("Cannot import orchestrator")
    
    def test_max_depth_limit(self, tmp_path):
        """Test that max_depth is respected."""
        # Create deep structure
        current = tmp_path
        for i in range(5):
            current = current / f"level-{i}"
            current.mkdir()
        
        (current / ".git").mkdir()
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            # With depth 3, shouldn't find it
            orchestrator = MasterOrchestrator(root=tmp_path, max_depth=3)
            projects = orchestrator.discover_projects()
            assert len(projects) == 0
            
            # With depth 6, should find it
            orchestrator = MasterOrchestrator(root=tmp_path, max_depth=6)
            projects = orchestrator.discover_projects()
            assert len(projects) == 1
        except ImportError:
            pytest.skip("Cannot import orchestrator")


class TestProjectAnalysis:
    """Test project analysis functionality."""
    
    def test_detect_ai_autofix_script(self, tmp_path):
        """Test detection of ai_auto_fix.py script."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()
        
        scripts_dir = project_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "ai_auto_fix.py").touch()
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path)
            projects = orchestrator.discover_projects()
            
            assert len(projects) == 1
            assert projects[0].has_ai_autofix is True
        except ImportError:
            pytest.skip("Cannot import orchestrator")
    
    def test_detect_tests(self, tmp_path):
        """Test detection of test directories."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()
        (project_dir / "tests").mkdir()
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path)
            projects = orchestrator.discover_projects()
            
            assert len(projects) == 1
            assert projects[0].has_tests is True
        except ImportError:
            pytest.skip("Cannot import orchestrator")
    
    def test_find_todo_files(self, tmp_path):
        """Test finding TODO files."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        (project_dir / ".git").mkdir()
        (project_dir / "TODO.md").touch()
        (project_dir / "REMAINING_TODOS.md").touch()
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path)
            projects = orchestrator.discover_projects()
            
            assert len(projects) == 1
            assert len(projects[0].todo_files) == 2
        except ImportError:
            pytest.skip("Cannot import orchestrator")


class TestTODOExtraction:
    """Test TODO extraction functionality."""
    
    def test_extract_simple_todo(self, tmp_path):
        """Test extracting a simple TODO."""
        todo_file = tmp_path / "TODO.md"
        todo_file.write_text("- [ ] Fix the bug\n")
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator, ProjectInfo
            
            orchestrator = MasterOrchestrator(root=tmp_path)
            project = ProjectInfo(
                path=tmp_path,
                name="test",
                todo_files=[todo_file],
            )
            
            todos = orchestrator.extract_todos(project)
            
            assert len(todos) == 1
            assert "Fix the bug" in todos[0].content
            assert todos[0].priority == "normal"
            assert todos[0].completed is False
        except ImportError:
            pytest.skip("Cannot import orchestrator")
    
    def test_extract_priority_todos(self, tmp_path):
        """Test extracting TODOs with different priorities."""
        todo_file = tmp_path / "TODO.md"
        todo_file.write_text("""
- [ ] CRITICAL: Fix security vulnerability
- [ ] HIGH: Improve performance
- [ ] TODO: Refactor code
- [ ] LOW: Update documentation
        """)
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator, ProjectInfo
            
            orchestrator = MasterOrchestrator(root=tmp_path)
            project = ProjectInfo(
                path=tmp_path,
                name="test",
                todo_files=[todo_file],
            )
            
            todos = orchestrator.extract_todos(project)
            
            assert len(todos) == 4
            priorities = [t.priority for t in todos]
            assert "critical" in priorities
            assert "high" in priorities
            assert "normal" in priorities
            assert "low" in priorities
        except ImportError:
            pytest.skip("Cannot import orchestrator")
    
    def test_skip_completed_todos(self, tmp_path):
        """Test that completed TODOs are marked correctly."""
        todo_file = tmp_path / "TODO.md"
        todo_file.write_text("""
- [x] Completed task
- [ ] Pending task
        """)
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator, ProjectInfo
            
            orchestrator = MasterOrchestrator(root=tmp_path)
            project = ProjectInfo(
                path=tmp_path,
                name="test",
                todo_files=[todo_file],
            )
            
            todos = orchestrator.extract_todos(project)
            
            assert len(todos) == 2
            completed = [t for t in todos if t.completed]
            pending = [t for t in todos if not t.completed]
            
            assert len(completed) == 1
            assert len(pending) == 1
        except ImportError:
            pytest.skip("Cannot import orchestrator")


class TestStatusReport:
    """Test status report generation."""
    
    def test_generate_basic_report(self, tmp_path):
        """Test generating a basic status report."""
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path, log_dir=tmp_path / "logs")
            report = orchestrator.generate_status_report()
            
            assert "timestamp" in report
            assert "root" in report
            assert "total_projects" in report
            assert "projects" in report
            assert "todos" in report
            assert "monitors" in report
            
            assert report["total_projects"] == 0
            assert report["todos"]["total"] == 0
        except ImportError:
            pytest.skip("Cannot import orchestrator")
    
    def test_report_structure(self, tmp_path):
        """Test the structure of the status report."""
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(root=tmp_path, log_dir=tmp_path / "logs")
            report = orchestrator.generate_status_report()
            
            # Check todos structure
            assert "by_priority" in report["todos"]
            assert "critical" in report["todos"]["by_priority"]
            assert "high" in report["todos"]["by_priority"]
            assert "normal" in report["todos"]["by_priority"]
            assert "low" in report["todos"]["by_priority"]
            
            # Check monitors structure
            assert "running" in report["monitors"]
            assert "healthy" in report["monitors"]
            assert "stopped" in report["monitors"]
            assert "error" in report["monitors"]
        except ImportError:
            pytest.skip("Cannot import orchestrator")


class TestCodexSpawner:
    """Test codex spawner functionality."""
    
    def test_read_status_report(self, tmp_path):
        """Test reading status report."""
        status_file = tmp_path / "logs" / "status_report.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        status_data = {
            "timestamp": "2025-12-19 10:00:00",
            "projects": {
                "test-project": {
                    "path": str(tmp_path / "test-project"),
                    "todo_count": 5,
                }
            }
        }
        
        status_file.write_text(json.dumps(status_data))
        
        try:
            from scripts.codex_spawner import CodexSpawner
            
            spawner = CodexSpawner(log_dir=tmp_path / "logs")
            sessions = spawner.read_todos_from_status()
            
            # Should process the project with TODOs
            assert isinstance(sessions, list)
        except ImportError:
            pytest.skip("Cannot import codex_spawner")


class TestSelfHealingEngine:
    """Test self-healing engine functionality."""
    
    def test_detect_error_pattern(self):
        """Test error pattern detection."""
        try:
            from scripts.self_healing_engine import SelfHealingEngine
            
            engine = SelfHealingEngine()
            
            # Test module not found error
            log_line = "ModuleNotFoundError: No module named 'requests'"
            error = engine.detect_error(log_line)
            
            assert error is not None
            assert error.severity == "high"
            assert error.category == "dependency"
        except ImportError:
            pytest.skip("Cannot import self_healing_engine")
    
    def test_pattern_frequency_tracking(self):
        """Test that error frequency is tracked."""
        try:
            from scripts.self_healing_engine import SelfHealingEngine
            
            engine = SelfHealingEngine()
            
            log_line = "ModuleNotFoundError: No module named 'requests'"
            
            # Detect same error multiple times
            for _ in range(3):
                error = engine.detect_error(log_line)
            
            # Frequency should be tracked
            assert error is not None
            assert error.frequency >= 3
        except ImportError:
            pytest.skip("Cannot import self_healing_engine")


class TestInteractiveShell:
    """Test interactive shell functionality."""
    
    def test_load_projects(self, tmp_path):
        """Test loading projects from status report."""
        status_file = tmp_path / "logs" / "status_report.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        status_data = {
            "projects": {
                "test-1": {"path": "/path/to/test-1"},
                "test-2": {"path": "/path/to/test-2"},
            }
        }
        
        status_file.write_text(json.dumps(status_data))
        
        try:
            from scripts.interactive_shell import ProjectShell
            
            with patch.object(ProjectShell, 'cmdloop'):
                shell = ProjectShell()
                shell.status_file = status_file
                shell._load_projects()
                
                assert len(shell.projects) == 2
                assert "test-1" in shell.projects
                assert "test-2" in shell.projects
        except ImportError:
            pytest.skip("Cannot import interactive_shell")


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_workflow(self, tmp_path):
        """Test a complete workflow from discovery to reporting."""
        # Create mock projects
        for i in range(2):
            project_dir = tmp_path / f"project-{i}"
            project_dir.mkdir()
            (project_dir / ".git").mkdir()
            
            # Add TODO file
            todo_file = project_dir / "TODO.md"
            todo_file.write_text(f"- [ ] Task {i}\n")
        
        try:
            from os_dashboard_ai_assistant import MasterOrchestrator
            
            orchestrator = MasterOrchestrator(
                root=tmp_path,
                log_dir=tmp_path / "logs",
                watch_todos=True,
            )
            
            # Discover projects
            projects = orchestrator.discover_projects()
            assert len(projects) == 2
            
            # Generate status report
            report = orchestrator.generate_status_report()
            assert report["total_projects"] == 2
            
            # Extract TODOs
            all_todos = []
            for project in orchestrator.projects.values():
                todos = orchestrator.extract_todos(project)
                all_todos.extend(todos)
            
            assert len(all_todos) == 2
        except ImportError:
            pytest.skip("Cannot import orchestrator")


# Fixtures
@pytest.fixture
def mock_status_report(tmp_path):
    """Create a mock status report."""
    status_file = tmp_path / "logs" / "status_report.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "timestamp": "2025-12-19 10:00:00",
        "root": str(tmp_path),
        "total_projects": 3,
        "projects": {
            "project-1": {
                "path": str(tmp_path / "project-1"),
                "status": "healthy",
                "branch": "main",
                "has_ai_autofix": True,
                "has_tests": True,
                "todo_count": 5,
            },
            "project-2": {
                "path": str(tmp_path / "project-2"),
                "status": "running",
                "branch": "develop",
                "has_ai_autofix": False,
                "has_tests": True,
                "todo_count": 0,
            },
            "project-3": {
                "path": str(tmp_path / "project-3"),
                "status": "stopped",
                "branch": "main",
                "has_ai_autofix": True,
                "has_tests": False,
                "todo_count": 3,
            },
        },
        "todos": {
            "total": 8,
            "by_priority": {
                "critical": 1,
                "high": 2,
                "normal": 4,
                "low": 1,
            },
            "completed": 3,
        },
        "monitors": {
            "running": 1,
            "healthy": 1,
            "stopped": 1,
            "error": 0,
        },
    }
    
    status_file.write_text(json.dumps(data, indent=2))
    return status_file


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
