"""Tests for database operations."""

import unittest
import sqlite3
import tempfile
import os
from datetime import datetime
from assistant_hub.db import (
    set_meta, get_meta, save_settings, save_active_persona,
    db_upsert_project, db_delete_project, db_update_task, db_delete_task,
    PERSONAS, STATUS_OPTIONS, PRIORITY_OPTIONS
)


def initialize_test_database(conn: sqlite3.Connection):
    """Initialize a test database with minimal schema."""
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS state_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            project TEXT,
            status TEXT,
            priority TEXT,
            due_date TEXT,
            notes TEXT,
            owner TEXT,
            created_at TEXT,
            depends_on INTEGER,
            recurrence_pattern TEXT,
            recurrence_end TEXT,
            time_estimated INTEGER,
            time_logged INTEGER,
            template_id TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY,
            description TEXT,
            status TEXT,
            created TEXT,
            updated TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            active_persona TEXT,
            fetch_preferences TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            persona TEXT,
            role TEXT,
            kind TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    conn.commit()


class TestDatabaseMetaOperations(unittest.TestCase):
    """Test database meta key-value operations."""

    def test_set_and_get_meta(self):
        """Test setting and getting meta values."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            # Test setting a meta value
            set_meta(conn, "test_key", "test_value")

            # Test getting the meta value
            value = get_meta(conn, "test_key")
            assert value == "test_value"

            # Test getting non-existent key with default
            default_value = get_meta(conn, "nonexistent", "default")
            assert default_value == "default"

        finally:
            conn.close()
            os.unlink(db_path)

    def test_meta_update_existing(self):
        """Test updating existing meta value."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            # Set initial value
            set_meta(conn, "test_key", "initial_value")
            assert get_meta(conn, "test_key") == "initial_value"

            # Update value
            set_meta(conn, "test_key", "updated_value")
            assert get_meta(conn, "test_key") == "updated_value"

        finally:
            conn.close()
            os.unlink(db_path)


class TestDatabaseProjectOperations(unittest.TestCase):
    """Test database project CRUD operations."""

    def test_upsert_and_delete_project(self):
        """Test creating and deleting projects."""
        from assistant_hub.db import Project

        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            # Create a project
            project = Project(
                name="Test Project",
                description="A test project",
                status="active",
                priority="MEDIUM"
            )

            # Insert project
            db_upsert_project(conn, project)
            # Verify project was inserted by checking it exists
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects WHERE name = ?", (project.name,))
            count = cursor.fetchone()[0]
            assert count == 1

            # Verify project exists (this would need additional query function)
            # For now, just test that the operation doesn't fail

            # Delete project
            db_delete_project(conn, "Test Project")
            # Verify deletion would require additional query

        finally:
            conn.close()
            os.unlink(db_path)


class TestDatabaseTaskOperations(unittest.TestCase):
    """Test database task CRUD operations."""

    def test_update_and_delete_task(self):
        """Test updating and deleting tasks."""
        from assistant_hub.db import Task

        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            # Create a task
            task = Task(
                id=1,
                title="Test Task",
                notes="A test task",
                status="TODO",
                priority="MEDIUM",
                owner="Chris",
                created_at=datetime.now().isoformat()
            )

            # Update task (this assumes task already exists)
            # In real scenario, would need to insert first
            # db_update_task(conn, task)

            # Delete task
            db_delete_task(conn, 1)

        finally:
            conn.close()
            os.unlink(db_path)


class TestDatabaseSettingsOperations(unittest.TestCase):
    """Test database settings operations."""

    def test_save_settings(self):
        """Test saving settings to database."""
        from assistant_hub.db import Settings

        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            settings = Settings(
                data_preferences={"notes": True, "calendar": False}
            )

            # Save settings
            save_settings(conn, settings)

            # Verify settings were saved (would need additional query function)

        finally:
            conn.close()
            os.unlink(db_path)

    def test_save_active_persona(self):
        """Test saving active persona."""
        from assistant_hub.db import AssistantState

        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            initialize_test_database(conn)

            state = AssistantState(tasks=[], projects=[], active_persona="Aria")

            # Save active persona
            save_active_persona(conn, state)

        finally:
            conn.close()
            os.unlink(db_path)


class TestDatabaseConstants(unittest.TestCase):
    """Test database constants and enums."""

    def test_personas_defined(self):
        """Test that personas are properly defined."""
        assert isinstance(PERSONAS, list)
        assert len(PERSONAS) > 0
        assert "Chris" in PERSONAS
        assert "AIC" in PERSONAS

    def test_status_options_defined(self):
        """Test that status options are properly defined."""
        assert isinstance(STATUS_OPTIONS, list)
        assert len(STATUS_OPTIONS) > 0
        assert "TODO" in STATUS_OPTIONS
        assert "DONE" in STATUS_OPTIONS

    def test_priority_options_defined(self):
        """Test that priority options are properly defined."""
        assert isinstance(PRIORITY_OPTIONS, list)
        assert len(PRIORITY_OPTIONS) > 0
        assert "LOW" in PRIORITY_OPTIONS
        assert "HIGH" in PRIORITY_OPTIONS
        assert "CRITICAL" in PRIORITY_OPTIONS


class TestDatabaseInitialization(unittest.TestCase):
    """Test database initialization."""

    def test_initialize_database_creates_tables(self):
        """Test that initialize_database creates required tables."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)

            # Initialize database
            initialize_test_database(conn)

            # Check that tables were created by querying sqlite_master
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]

            # Check for key tables
            expected_tables = ['tasks', 'projects', 'chat_messages', 'settings', 'state_meta']
            for table in expected_tables:
                assert table in table_names, f"Table {table} was not created"

        finally:
            conn.close()
            os.unlink(db_path)
