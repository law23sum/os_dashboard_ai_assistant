"""OneDrive integration wrapper for GUI."""

import os
from pathlib import Path
from typing import Dict
import sqlite3

from .base import BaseIntegration, IntegrationStatus
from .onedrive.service import OneDriveService
from .onedrive import OneDriveClient
from .msgraph import GraphClient


class OneDriveIntegration(BaseIntegration):
    """Integration for Microsoft OneDrive."""
    
    def __init__(self, conn: sqlite3.Connection, sync_root: str = None):
        super().__init__(conn, "OneDrive", "onedrive")
        self.sync_root = sync_root or os.path.expanduser("~/.assistant_hub/onedrive_sync")
        self.client = None
        self.service = None
    
    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph for OneDrive."""
        try:
            graph_client = GraphClient()
            self.client = OneDriveClient(graph_client)
            self.service = OneDriveService(self.sync_root, self.client)
            
            # Try to get drive info to verify auth
            drive_info = self.client.get_drive_info()
            self.update_status(True, item_count=0)
            return True
        except Exception as e:
            error_msg = str(e)
            if "credentials" in error_msg.lower() or "auth" in error_msg.lower() or "401" in error_msg:
                self.update_status(False, "Not authenticated. Please configure Microsoft Graph credentials.")
            else:
                self.update_status(False, error_msg)
            return False
    
    def sync(self) -> int:
        """Sync OneDrive files and folders."""
        if not self.authenticate():
            return 0
        
        count = 0
        try:
            # Sync common folders
            folders_to_sync = ["/Documents", "/Desktop", "/Pictures"]
            
            for folder_path in folders_to_sync:
                try:
                    items = self.client.list_drive_items(folder_path)
                    for item in items:
                        item_id = item.get("id")
                        item_name = item.get("name", "Unknown")
                        item_type = "folder" if "folder" in item else "file"
                        item_size = item.get("size", 0)
                        
                        if not item_id:
                            continue
                        
                        # Record in database
                        self.record_item(
                            external_id=item_id,
                            item_kind=item_type,
                            title=f"{folder_path}/{item_name}",
                            data={
                                "folder_path": folder_path,
                                "item_id": item_id,
                                "item_name": item_name,
                                "item_type": item_type,
                                "size": item_size,
                                "web_url": item.get("webUrl", ""),
                                "created_datetime": item.get("createdDateTime", ""),
                                "modified_datetime": item.get("lastModifiedDateTime", "")
                            }
                        )
                        count += 1
                except Exception as e:
                    # Folder might not exist, skip it
                    continue
            
            # Also sync root items
            try:
                root_items = self.client.list_drive_items("/")
                for item in root_items[:50]:  # Limit to first 50 root items
                    item_id = item.get("id")
                    item_name = item.get("name", "Unknown")
                    item_type = "folder" if "folder" in item else "file"
                    
                    if not item_id:
                        continue
                    
                    self.record_item(
                        external_id=item_id,
                        item_kind=item_type,
                        title=item_name,
                        data={
                            "folder_path": "/",
                            "item_id": item_id,
                            "item_name": item_name,
                            "item_type": item_type,
                            "size": item.get("size", 0),
                            "web_url": item.get("webUrl", ""),
                            "created_datetime": item.get("createdDateTime", ""),
                            "modified_datetime": item.get("lastModifiedDateTime", "")
                        }
                    )
                    count += 1
            except Exception:
                pass
            
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
    
    def download_file(self, item_id: str, local_path: str) -> bool:
        """Download a file from OneDrive to local path.
        
        Args:
            item_id: OneDrive item ID
            local_path: Local destination path
        
        Returns:
            True if successful
        """
        if not self.authenticate():
            return False
        
        try:
            file_content = self.client.download_file(item_id)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            with open(local_path, "wb") as f:
                f.write(file_content)
            
            return True
        except Exception as e:
            return False
    
    def upload_file(self, local_path: str, remote_path: str, overwrite: bool = False) -> bool:
        """Upload a local file to OneDrive.
        
        Args:
            local_path: Local file path
            remote_path: Remote path in OneDrive
            overwrite: Whether to overwrite existing file
        
        Returns:
            True if successful
        """
        if not self.authenticate():
            return False
        
        try:
            self.client.upload_file(local_path, remote_path, overwrite=overwrite)
            return True
        except Exception as e:
            return False

