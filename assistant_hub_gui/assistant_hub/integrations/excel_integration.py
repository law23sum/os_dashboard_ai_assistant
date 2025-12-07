"""Excel integration wrapper for GUI."""

import os
from pathlib import Path
from typing import Dict
import sqlite3

from .base import BaseIntegration, IntegrationStatus
from .excel import ExcelService


class ExcelIntegration(BaseIntegration):
    """Integration for Microsoft Excel spreadsheets."""
    
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "Excel", "excel")
        self.service = ExcelService()
    
    def authenticate(self) -> bool:
        """Check if Excel integration is available."""
        try:
            import openpyxl
            self.update_status(True)
            return True
        except ImportError:
            self.update_status(False, "openpyxl package not installed")
            return False
    
    def sync(self) -> int:
        """Scan for Excel files in common locations."""
        if not self.authenticate():
            return 0
        
        count = 0
        try:
            # Scan common document locations
            doc_paths = [
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Downloads"),
            ]
            
            for base_path in doc_paths:
                if not os.path.exists(base_path):
                    continue
                
                for root, dirs, files in os.walk(base_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if file.endswith(('.xlsx', '.xls', '.csv')):
                            file_path = os.path.join(root, file)
                            try:
                                rel_path = os.path.relpath(file_path, base_path)
                                self.record_item(
                                    external_id=rel_path,
                                    item_kind="spreadsheet",
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

