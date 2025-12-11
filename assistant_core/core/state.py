"""Application state management for the OS Dashboard AI Assistant."""

from typing import Any, Optional
from datetime import datetime


class ApplicationState:
    """Manages the application state and configuration."""

    def __init__(self):
        """Initialize the application state."""
        self.start_time = datetime.now()
        self.config = {}
        self.tasks = []
        self.projects = []
        self.chat_history = []
        self.active_persona = "AIC"

    def update_config(self, key: str, value: Any):
        """Update configuration setting."""
        self.config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration setting."""
        return self.config.get(key, default)

    def add_task(self, task: dict):
        """Add a task to the state."""
        self.tasks.append(task)

    def get_tasks(self):
        """Get all tasks."""
        return self.tasks

    def add_project(self, project: dict):
        """Add a project to the state."""
        self.projects.append(project)

    def get_projects(self):
        """Get all projects."""
        return self.projects

    def add_chat_message(self, message: dict):
        """Add a chat message to history."""
        self.chat_history.append(message)

    def get_chat_history(self):
        """Get chat history."""
        return self.chat_history

    def set_active_persona(self, persona: str):
        """Set the active AI persona."""
        self.active_persona = persona

    def get_active_persona(self) -> str:
        """Get the active AI persona."""
        return self.active_persona


def load_state() -> ApplicationState:
    """Load the application state (placeholder for future database integration)."""
    return ApplicationState()


def save_state(state: ApplicationState) -> None:
    """Save the application state (placeholder for future database integration)."""
    # For now, state is kept in memory only
    pass
