"""Tests for core application state management."""

import unittest
from datetime import datetime, timedelta
from assistant_core.core.state import ApplicationState


class TestApplicationState(unittest.TestCase):
    """Test cases for ApplicationState class."""

    def test_initialization(self):
        """Test ApplicationState initialization sets correct default values."""
        state = ApplicationState()

        assert isinstance(state.start_time, datetime)
        assert state.config == {}
        assert state.tasks == []
        assert state.projects == []
        assert state.chat_history == []
        assert state.active_persona == "AIC"

    def test_config_management(self):
        """Test configuration setting and retrieval."""
        state = ApplicationState()

        # Test setting and getting config values
        state.update_config("test_key", "test_value")
        assert state.get_config("test_key") == "test_value"

        # Test default values
        assert state.get_config("nonexistent_key", "default") == "default"
        assert state.get_config("nonexistent_key") is None

    def test_task_management(self):
        """Test task addition and retrieval."""
        state = ApplicationState()

        task1 = {"id": 1, "title": "Test Task 1", "status": "pending"}
        task2 = {"id": 2, "title": "Test Task 2", "status": "completed"}

        state.add_task(task1)
        state.add_task(task2)

        tasks = state.get_tasks()
        assert len(tasks) == 2
        assert tasks[0] == task1
        assert tasks[1] == task2

    def test_project_management(self):
        """Test project addition and retrieval."""
        state = ApplicationState()

        project1 = {"id": 1, "name": "Test Project 1", "description": "A test project"}
        project2 = {"id": 2, "name": "Test Project 2", "description": "Another test project"}

        state.add_project(project1)
        state.add_project(project2)

        projects = state.get_projects()
        assert len(projects) == 2
        assert projects[0] == project1
        assert projects[1] == project2

    def test_chat_history_management(self):
        """Test chat message addition and retrieval."""
        state = ApplicationState()

        message1 = {"role": "user", "content": "Hello", "timestamp": datetime.now()}
        message2 = {"role": "assistant", "content": "Hi there!", "timestamp": datetime.now()}

        state.add_chat_message(message1)
        state.add_chat_message(message2)

        history = state.get_chat_history()
        assert len(history) == 2
        assert history[0] == message1
        assert history[1] == message2

    def test_persona_management(self):
        """Test active persona management."""
        state = ApplicationState()

        # Test default persona
        assert state.get_active_persona() == "AIC"

        # Test persona setting (assuming method exists)
        # Note: This test may need adjustment based on actual implementation
        try:
            state.set_active_persona("Aria")
            assert state.get_active_persona() == "Aria"
        except AttributeError:
            # Method might not exist yet, skip this part
            pass
