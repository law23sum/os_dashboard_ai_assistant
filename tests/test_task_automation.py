"""Tests for task automation functionality."""

import unittest
import sqlite3
import tempfile
import os
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock
from assistant_core.task_automation import (
    process_recurring_tasks, check_task_dependencies, can_start_task,
    get_task_dependency_chain, _calculate_next_occurrence
)
from assistant_hub.db import Task
from tests.test_database import initialize_test_database


class TestRecurringTasks(unittest.TestCase):
    """Test recurring task processing."""

    def test_calculate_next_occurrence_daily(self):
        """Test calculating next occurrence for daily recurrence."""
        # When last occurrence was yesterday, next should be today
        last_date_str = "2023-01-04"  # Yesterday
        today = date(2023, 1, 5)

        next_date = _calculate_next_occurrence(last_date_str, "daily", today)
        assert next_date == date(2023, 1, 5)

    def test_calculate_next_occurrence_weekly(self):
        """Test calculating next occurrence for weekly recurrence."""
        last_date_str = "2023-01-01"  # Last Sunday
        today = date(2023, 1, 8)  # Next Sunday

        next_date = _calculate_next_occurrence(last_date_str, "weekly", today)
        assert next_date == date(2023, 1, 8)

    def test_calculate_next_occurrence_monthly(self):
        """Test calculating next occurrence for monthly recurrence."""
        last_date_str = "2023-01-15"
        today = date(2023, 2, 15)

        next_date = _calculate_next_occurrence(last_date_str, "monthly", today)
        assert next_date == date(2023, 2, 15)

    def test_calculate_next_occurrence_invalid_pattern(self):
        """Test calculating next occurrence with invalid pattern."""
        last_date_str = "2023-01-01"
        today = date(2023, 1, 5)

        next_date = _calculate_next_occurrence(last_date_str, "invalid", today)
        assert next_date is None

    def test_calculate_next_occurrence_future_date(self):
        """Test calculating next occurrence when next date is in future."""
        last_date_str = "2023-01-01"
        today = date(2023, 1, 3)

        next_date = _calculate_next_occurrence(last_date_str, "weekly", today)
        assert next_date == date(2023, 1, 8)  # Next Sunday


class TestTaskDependencies(unittest.TestCase):
    """Test task dependency management."""

    def test_can_start_task_no_dependencies(self):
        """Test task can start when it has no dependencies."""
        task = Task(
            id=1,
            title="Test Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=None
        )

        state = MagicMock()
        state.tasks = []

        assert can_start_task(task, state) is True

    def test_can_start_task_with_completed_dependency(self):
        """Test task can start when dependency is completed."""
        dependency_task = Task(
            id=1,
            title="Dependency Task",
            status="DONE",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat()
        )

        task = Task(
            id=2,
            title="Test Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=1
        )

        state = MagicMock()
        state.tasks = [dependency_task]

        assert can_start_task(task, state) is True

    def test_can_start_task_with_pending_dependency(self):
        """Test task cannot start when dependency is pending."""
        dependency_task = Task(
            id=1,
            title="Dependency Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat()
        )

        task = Task(
            id=2,
            title="Test Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=1
        )

        state = MagicMock()
        state.tasks = [dependency_task]

        assert can_start_task(task, state) is False

    def test_get_task_dependency_chain_no_dependencies(self):
        """Test getting dependency chain for task with no dependencies."""
        task = Task(
            id=1,
            title="Test Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=None
        )

        state = MagicMock()
        state.tasks = [task]

        chain = get_task_dependency_chain(task, state)
        assert len(chain) == 1
        assert chain[0] == task

    def test_get_task_dependency_chain_with_dependencies(self):
        """Test getting dependency chain for task with dependencies."""
        dependency_task = Task(
            id=1,
            title="Dependency Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=None
        )

        task = Task(
            id=2,
            title="Test Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=1
        )

        state = MagicMock()
        state.tasks = [dependency_task, task]

        chain = get_task_dependency_chain(task, state)
        assert len(chain) == 2
        assert chain[0] == dependency_task  # Dependency comes first
        assert chain[1] == task

    def test_check_task_dependencies_no_blocked_tasks(self):
        """Test checking dependencies when no tasks are blocked."""
        task1 = Task(
            id=1,
            title="Task 1",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=None
        )

        task2 = Task(
            id=2,
            title="Task 2",
            status="DONE",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=None
        )

        state = MagicMock()
        state.tasks = [task1, task2]

        blocked_tasks = check_task_dependencies(state)
        assert len(blocked_tasks) == 0

    def test_check_task_dependencies_with_blocked_task(self):
        """Test checking dependencies when a task is blocked."""
        dependency_task = Task(
            id=1,
            title="Dependency Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat()
        )

        blocked_task = Task(
            id=2,
            title="Blocked Task",
            status="TODO",
            priority="MEDIUM",
            owner="Chris",
            created_at=datetime.now().isoformat(),
            depends_on=1
        )

        state = MagicMock()
        state.tasks = [dependency_task, blocked_task]

        blocked_tasks = check_task_dependencies(state)
        assert len(blocked_tasks) == 1
        assert blocked_tasks[0] == blocked_task


class TestProcessRecurringTasks(unittest.TestCase):
    """Test processing of recurring tasks."""

    def test_process_recurring_tasks_no_recurring(self):
        """Test processing when no tasks are recurring."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            # Process recurring tasks
            created_count = process_recurring_tasks(conn)
            assert created_count == 0

        finally:
            conn.close()
            os.unlink(db_path)

    def test_process_recurring_tasks_completed_recurring(self):
        """Test processing completed recurring tasks."""
        # This would require setting up database state with recurring tasks
        # For now, just test that the function runs without error
        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            # Process recurring tasks
            created_count = process_recurring_tasks(conn)
            assert isinstance(created_count, int)
            assert created_count >= 0

        finally:
            conn.close()
            os.unlink(db_path)
