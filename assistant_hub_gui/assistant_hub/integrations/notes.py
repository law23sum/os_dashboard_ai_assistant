"""Notes/Knowledge Base integration - scans local files."""

import os
from pathlib import Path
from typing import Dict, List
import sqlite3

from .base import BaseIntegration, IntegrationStatus


class NotesIntegration(BaseIntegration):
    """Integration for local notes and knowledge base files."""
    
    def __init__(self, conn: sqlite3.Connection, notes_path: str = None):
        super().__init__(conn, "Local Notes", "notes")
        self.notes_path = notes_path or os.path.expanduser("~/Documents/Notes")
        self.supported_extensions = {'.md', '.txt', '.rst', '.org'}
    
    def authenticate(self) -> bool:
        """No authentication needed for local files."""
        try:
            if not os.path.exists(self.notes_path):
                try:
                    os.makedirs(self.notes_path, exist_ok=True)
                except Exception as e:
                    self.update_status(False, f"Cannot create notes directory: {str(e)[:50]}")
                    return False
            self.update_status(True)
            return True
        except Exception as e:
            self.update_status(False, f"Notes directory error: {str(e)[:50]}")
            return False
    
    def sync(self) -> int:
        """Scan and index note files."""
        if not self.authenticate():
            self.update_status(False, "Notes directory not accessible")
            return 0
        
        count = 0
        try:
            for root, dirs, files in os.walk(self.notes_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.supported_extensions):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Create relative path as external_id
                            rel_path = os.path.relpath(file_path, self.notes_path)
                            
                            # Extract title from first line or filename
                            lines = content.split('\n')
                            title = lines[0].strip('#').strip() if lines else Path(file).stem
                            if not title:
                                title = Path(file).stem
                            
                            self.record_item(
                                external_id=rel_path,
                                item_kind="note",
                                title=title,
                                data={
                                    "path": file_path,
                                    "content_preview": content[:500],
                                    "size": len(content),
                                    "extension": Path(file).suffix
                                }
                            )
                            count += 1
                        except Exception as e:
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

