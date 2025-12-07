"""High-level OneDrive service operations."""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pathlib import Path
import os

from .client import OneDriveClient


class OneDriveService:
    """High-level service for OneDrive operations."""
    
    def __init__(self, local_sync_root: Optional[str] = None, client: Optional[OneDriveClient] = None):
        """Initialize OneDrive service.
        
        Args:
            local_sync_root: Local directory for syncing OneDrive files
            client: OneDriveClient instance (creates new if not provided)
        """
        self.client = client
        self.local_sync_root = local_sync_root or os.path.expanduser("~/.assistant_hub/onedrive_sync")
        
        # Ensure sync directory exists
        os.makedirs(self.local_sync_root, exist_ok=True)
    
    def sync_folder_to_local(
        self,
        remote_folder: str = "/Documents",
        local_folder: Optional[str] = None,
        drive: str = "me"
    ) -> List[str]:
        """Sync a OneDrive folder to local disk.
        
        Args:
            remote_folder: Remote folder path in OneDrive
            local_folder: Local destination (defaults to sync_root + remote_folder)
            drive: Drive identifier
        
        Returns:
            List of synced file paths
        """
        if local_folder is None:
            local_folder = os.path.join(self.local_sync_root, remote_folder.lstrip("/"))
        
        os.makedirs(local_folder, exist_ok=True)
        
        items = self.client.list_drive_items(remote_folder, drive)
        synced_files = []
        
        for item in items:
            item_name = item.get("name", "")
            item_id = item.get("id", "")
            item_type = "folder" if "folder" in item else "file"
            
            if item_type == "folder":
                # Recursively sync subfolder
                subfolder_path = f"{remote_folder.rstrip('/')}/{item_name}"
                sub_local = os.path.join(local_folder, item_name)
                synced_files.extend(self.sync_folder_to_local(subfolder_path, sub_local, drive))
            else:
                # Download file
                try:
                    file_content = self.client.download_file(item_id, drive)
                    local_path = os.path.join(local_folder, item_name)
                    
                    with open(local_path, "wb") as f:
                        f.write(file_content)
                    
                    synced_files.append(local_path)
                except Exception as e:
                    print(f"Error syncing {item_name}: {e}")
        
        return synced_files
    
    def upload_local_file(
        self,
        local_path: str,
        remote_path: str,
        drive: str = "me",
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Upload a local file to OneDrive.
        
        Args:
            local_path: Local file path
            remote_path: Remote path in OneDrive
            drive: Drive identifier
            overwrite: Whether to overwrite existing file
        
        Returns:
            Uploaded item dictionary
        """
        return self.client.upload_file(local_path, remote_path, drive, overwrite)
    
    def list_files(
        self,
        folder_path: str = "/",
        file_extensions: Optional[List[str]] = None,
        drive: str = "me"
    ) -> List[Dict[str, Any]]:
        """List files in a OneDrive folder, optionally filtered by extension.
        
        Args:
            folder_path: Folder path to list
            file_extensions: Optional list of extensions to filter (e.g., [".docx", ".pdf"])
            drive: Drive identifier
        
        Returns:
            List of file items
        """
        items = self.client.list_drive_items(folder_path, drive)
        files = [item for item in items if "file" in item]
        
        if file_extensions:
            files = [
                f for f in files
                if any(f.get("name", "").lower().endswith(ext.lower()) for ext in file_extensions)
            ]
        
        return files
    
    def search_files(
        self,
        query: str,
        file_extensions: Optional[List[str]] = None,
        drive: str = "me"
    ) -> List[Dict[str, Any]]:
        """Search for files in OneDrive.
        
        Args:
            query: Search query
            file_extensions: Optional list of extensions to filter
            drive: Drive identifier
        
        Returns:
            List of matching file items
        """
        items = self.client.search_items(query, drive)
        files = [item for item in items if "file" in item]
        
        if file_extensions:
            files = [
                f for f in files
                if any(f.get("name", "").lower().endswith(ext.lower()) for ext in file_extensions)
            ]
        
        return files
    
    def get_file_info(self, item_id: str, drive: str = "me") -> Dict[str, Any]:
        """Get detailed information about a file.
        
        Args:
            item_id: Item ID or path
            drive: Drive identifier
        
        Returns:
            File information dictionary
        """
        return self.client.get_item(item_id, drive)
    
    def create_folder(self, folder_path: str, drive: str = "me") -> Dict[str, Any]:
        """Create a folder in OneDrive.
        
        Args:
            folder_path: Path where folder should be created
            drive: Drive identifier
        
        Returns:
            Created folder dictionary
        """
        return self.client.create_folder(folder_path, drive)
    
    def delete_file(self, item_id: str, drive: str = "me") -> bool:
        """Delete a file from OneDrive.
        
        Args:
            item_id: Item ID or path
            drive: Drive identifier
        
        Returns:
            True if successful
        """
        return self.client.delete_item(item_id, drive)

