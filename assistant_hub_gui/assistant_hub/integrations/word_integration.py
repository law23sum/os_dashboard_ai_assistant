"""Word integration wrapper for GUI."""

import os
from pathlib import Path
from typing import Dict
import sqlite3

from .base import BaseIntegration, IntegrationStatus


class WordIntegration(BaseIntegration):
    """Integration for Microsoft Word documents."""
    
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "Word", "word")
        # WordIntegration works independently - doesn't need WordService for file scanning
    
    def authenticate(self) -> bool:
        """Check if Word integration is available."""
        # Word integration can discover files even without python-docx
        # Only advanced editing features require python-docx
        self.update_status(True)
        return True
    
    def sync(self) -> int:
        """Scan for Word documents in common locations."""
        # File discovery works without python-docx
        
        count = 0
        try:
            # Scan common document locations
            doc_paths = [
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Desktop"),
            ]
            
            for base_path in doc_paths:
                if not os.path.exists(base_path):
                    continue
                
                for root, dirs, files in os.walk(base_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if file.endswith(('.docx', '.doc')):
                            file_path = os.path.join(root, file)
                            try:
                                rel_path = os.path.relpath(file_path, base_path)
                                self.record_item(
                                    external_id=rel_path,
                                    item_kind="document",
                                    title=Path(file).stem,
                                    data={
                                        "path": file_path,
                                        "extension": Path(file).suffix,
                                        "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
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

