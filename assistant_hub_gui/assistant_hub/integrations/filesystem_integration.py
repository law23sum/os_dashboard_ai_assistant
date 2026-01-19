"""Filesystem integration wrapper for GUI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Any
from typing import Dict, List, Optional
import sqlite3

from .base import BaseIntegration, IntegrationStatus
from .filesystem import discover_files, TRACKED_EXTENSIONS


class FilesystemIntegration(BaseIntegration):
    """Integration for local file system discovery."""

    def __init__(self, conn: sqlite3.Connection, root_path: str = None):
        super().__init__(conn, "Local Files", "filesystem")
        self.root_path = root_path or os.path.expanduser("~")

    def available_actions(self) -> Dict[str, Dict[str, Any]]:
        base_actions = super().available_actions()
        base_actions.update(
            {
                "list_files": {
                    "label": "List Files",
                    "description": "List tracked files from the configured root path.",
                    "fields": [
                        {
                            "name": "extension",
                            "label": "Extension Filter",
                            "type": "select",
                            "choices": sorted(TRACKED_EXTENSIONS),
                            "placeholder": "Leave blank for all",
                        },
                        {
                            "name": "limit",
                            "label": "Limit",
                            "type": "text",
                            "placeholder": "50",
                        },
                    ],
                },
                "read_file": {
                    "label": "Read File",
                    "description": "Preview text content from a tracked file.",
                    "fields": [
                        {
                            "name": "path",
                            "label": "Full Path",
                            "type": "text",
                            "placeholder": "~/Documents/example.txt",
                        }
                    ],
                },
            }
        )
        return base_actions

    def authenticate(self) -> bool:
        """Check if root path is accessible."""
        if not os.path.exists(self.root_path):
            self.update_status(False, f"Path not found: {self.root_path}")
            return False
        self.update_status(True)
        return True

    def sync(self) -> int:
        """Discover and index tracked files."""
        if not self.authenticate():
            return 0

        count = 0
        try:
            root = Path(self.root_path)
            files = discover_files(root, TRACKED_EXTENSIONS)

            for file_path in files:
                try:
                    rel_path = os.path.relpath(str(file_path), self.root_path)
                    self.record_item(
                        external_id=rel_path,
                        item_kind="file",
                        title=file_path.name,
                        data={
                            "path": str(file_path),
                            "extension": file_path.suffix,
                            "size": file_path.stat().st_size
                            if file_path.exists()
                            else 0,
                            "modified": file_path.stat().st_mtime
                            if file_path.exists()
                            else 0,
                        },
                    )
                    count += 1
                except Exception:
                    continue

            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            self.update_status(False, str(e))
            return 0

    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, "_status") or not self._status:
            self._status = IntegrationStatus()
        return self._status

    def list_files(
        self, extension: str | None = None, limit: int | None = None
    ) -> List[str]:
        """Return a list of tracked file paths respecting the extension filter."""

    def list_files(
        self, limit: int = 50, extension: Optional[str] = None
    ) -> List[Dict[str, object]]:
        """Return a lightweight listing of tracked files for UI/API consumption.

        Args:
            limit: Maximum number of files to return to avoid UI overload.
            extension: Optional file extension filter (e.g., ".md").

        Returns:
            A list of dictionaries describing the discovered files.
        """

        if not self.authenticate():
            return []

        paths = []
        root = Path(self.root_path)
        extensions = TRACKED_EXTENSIONS
        if extension:
            extensions = [
                ext
                for ext in TRACKED_EXTENSIONS
                if ext.endswith(extension) or extension.endswith(ext)
            ]

        for file_path in discover_files(root, extensions):
            paths.append(str(file_path))
            if limit and len(paths) >= limit:
                break
        return paths

    def read_file(self, path: str, max_chars: int = 1200) -> Dict[str, Any]:
        """Return a short text preview from the requested file."""

        if not path:
            raise ValueError("A file path is required to read content")

        expanded = os.path.expanduser(path)
        target = Path(expanded)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        with target.open("r", errors="ignore") as handle:
            content = handle.read(max_chars)

        return {"path": str(target), "preview": content}

    def invoke_action(self, action: str, options: Dict[str, Any] | None = None) -> Any:
        options = options or {}
        if action == "list_files":
            extension = options.get("extension") or None
            limit = options.get("limit")
            try:
                limit_int = int(limit) if limit else None
            except ValueError:
                limit_int = None
            return self.list_files(extension=extension, limit=limit_int)
        if action == "read_file":
            return self.read_file(path=options.get("path", ""))

        return super().invoke_action(action, options)
        root = Path(self.root_path)
        files = discover_files(root, TRACKED_EXTENSIONS)

        items: List[Dict[str, object]] = []
        for file_path in files:
            if extension and file_path.suffix != extension:
                continue

            stat = file_path.stat() if file_path.exists() else None
            items.append(
                {
                    "name": file_path.name,
                    "path": str(file_path),
                    "extension": file_path.suffix,
                    "size": stat.st_size if stat else 0,
                    "modified": stat.st_mtime if stat else 0,
                }
            )

            if len(items) >= limit:
                break

        return items
