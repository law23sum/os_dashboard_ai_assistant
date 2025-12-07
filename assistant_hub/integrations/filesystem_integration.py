"""Filesystem integration wrapper for GUI."""

import os
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3

from .base import BaseIntegration, IntegrationStatus
from .filesystem import discover_files, TRACKED_EXTENSIONS


class FilesystemIntegration(BaseIntegration):
    """Integration for local file system discovery."""
    
    def __init__(self, conn: sqlite3.Connection, root_path: str = None):
        super().__init__(conn, "Local Files", "filesystem")
        self.root_path = root_path or os.path.expanduser("~")
    
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
                            "size": file_path.stat().st_size if file_path.exists() else 0,
                            "modified": file_path.stat().st_mtime if file_path.exists() else 0
                        }
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
        if not hasattr(self, '_status') or not self._status:
            self._status = IntegrationStatus()
        return self._status

    def list_files(self, limit: int = 50, extension: Optional[str] = None) -> List[Dict[str, object]]:
        """Return a lightweight listing of tracked files for UI/API consumption.

        Args:
            limit: Maximum number of files to return to avoid UI overload.
            extension: Optional file extension filter (e.g., ".md").

        Returns:
            A list of dictionaries describing the discovered files.
        """

        if not self.authenticate():
            return []

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

