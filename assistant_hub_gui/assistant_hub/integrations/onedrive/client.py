"""OneDrive client for Microsoft Graph API."""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..msgraph import GraphClient


class OneDriveClient:
    """Client for interacting with OneDrive via Microsoft Graph API."""
    
    def __init__(self, graph_client: GraphClient):
        self.graph = graph_client
    
    def list_drive_items(self, folder_path: str = "/", drive: str = "me") -> List[Dict[str, Any]]:
        """List items in a OneDrive folder.
        
        Args:
            folder_path: Path to folder (e.g., "/Documents" or "/")
            drive: Drive identifier ("me" for personal, "drive" for default, or drive ID)
        
        Returns:
            List of item dictionaries with id, name, size, etc.
        """
        # Normalize path
        if folder_path == "/" or folder_path == "":
            path = ""
        else:
            path = folder_path.strip("/")
            path = f":/{path}:"
        
        endpoint = f"/{drive}/drive/root{path}/children"
        
        try:
            response = self.graph.get(endpoint)
            return response.get("value", [])
        except Exception as e:
            # If path doesn't exist, try listing root
            if path and "404" in str(e):
                try:
                    response = self.graph.get(f"/{drive}/drive/root/children")
                    return response.get("value", [])
                except Exception:
                    return []
            raise
    
    def get_item(self, item_id: str, drive: str = "me") -> Dict[str, Any]:
        """Get details of a specific OneDrive item.
        
        Args:
            item_id: Item ID or path
            drive: Drive identifier
        
        Returns:
            Item dictionary with metadata
        """
        # If item_id looks like a path, convert it
        if item_id.startswith("/") or ":" in item_id:
            if item_id.startswith("/"):
                item_id = item_id[1:]
            item_id = item_id.replace("/", ":")
            endpoint = f"/{drive}/drive/root:/{item_id}"
        else:
            endpoint = f"/{drive}/drive/items/{item_id}"
        
        return self.graph.get(endpoint)
    
    def download_file(self, item_id: str, drive: str = "me") -> bytes:
        """Download a file from OneDrive.
        
        Args:
            item_id: Item ID or path
            drive: Drive identifier
        
        Returns:
            File contents as bytes
        """
        import requests
        
        # Get download URL
        item = self.get_item(item_id, drive)
        download_url = item.get("@microsoft.graph.downloadUrl")
        
        if not download_url:
            # Try direct download endpoint
            if item_id.startswith("/") or ":" in item_id:
                if item_id.startswith("/"):
                    item_id = item_id[1:]
                item_id = item_id.replace("/", ":")
                endpoint = f"/{drive}/drive/root:/{item_id}:/content"
            else:
                endpoint = f"/{drive}/drive/items/{item_id}/content"
            
            token = self.graph.auth.get_token()
            response = requests.get(
                f"{self.graph.base_url}{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            response.raise_for_status()
            return response.content
        
        # Use download URL
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        return response.content
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        drive: str = "me",
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Upload a file to OneDrive.
        
        Args:
            local_path: Local file path
            remote_path: Remote path in OneDrive (e.g., "/Documents/file.txt")
            drive: Drive identifier
            overwrite: Whether to overwrite existing file
        
        Returns:
            Uploaded item dictionary
        """
        import os
        
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        # Normalize remote path
        remote_path = remote_path.strip("/")
        remote_path = remote_path.replace("/", ":")
        
        # Read file
        with open(local_path, "rb") as f:
            file_content = f.read()
        
        # Use upload session for large files (>4MB)
        file_size = len(file_content)
        if file_size > 4 * 1024 * 1024:
            return self._upload_large_file(local_path, remote_path, drive, overwrite)
        
        # Simple upload for small files
        endpoint = f"/{drive}/drive/root:/{remote_path}:/content"
        
        token = self.graph.auth.get_token()
        import requests
        response = requests.put(
            f"{self.graph.base_url}{endpoint}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream"
            },
            data=file_content,
            timeout=60
        )
        
        if response.status_code == 409 and not overwrite:
            raise FileExistsError(f"File already exists: {remote_path}")
        
        response.raise_for_status()
        return response.json()
    
    def _upload_large_file(
        self,
        local_path: str,
        remote_path: str,
        drive: str,
        overwrite: bool
    ) -> Dict[str, Any]:
        """Upload large file using upload session."""
        import os
        import requests
        
        file_size = os.path.getsize(local_path)
        remote_path = remote_path.strip("/").replace("/", ":")
        
        # Create upload session
        endpoint = f"/{drive}/drive/root:/{remote_path}:/createUploadSession"
        session_data = {
            "item": {
                "@microsoft.graph.conflictBehavior": "replace" if overwrite else "fail",
                "name": os.path.basename(remote_path)
            }
        }
        
        session = self.graph.post(endpoint, json=session_data)
        upload_url = session["uploadUrl"]
        
        # Upload in chunks
        chunk_size = 320 * 1024  # 320KB chunks
        with open(local_path, "rb") as f:
            offset = 0
            while offset < file_size:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                chunk_end = offset + len(chunk) - 1
                content_range = f"bytes {offset}-{chunk_end}/{file_size}"
                
                response = requests.put(
                    upload_url,
                    headers={
                        "Content-Length": str(len(chunk)),
                        "Content-Range": content_range
                    },
                    data=chunk,
                    timeout=60
                )
                
                if response.status_code in (200, 201):
                    return response.json()
                
                response.raise_for_status()
                offset += len(chunk)
        
        raise Exception("Upload failed")
    
    def create_folder(self, folder_path: str, drive: str = "me") -> Dict[str, Any]:
        """Create a folder in OneDrive.
        
        Args:
            folder_path: Path where folder should be created (e.g., "/Documents/NewFolder")
            drive: Drive identifier
        
        Returns:
            Created folder dictionary
        """
        folder_name = Path(folder_path).name
        parent_path = str(Path(folder_path).parent).replace("\\", "/")
        
        if parent_path == "/" or parent_path == ".":
            endpoint = f"/{drive}/drive/root/children"
        else:
            parent_path = parent_path.strip("/").replace("/", ":")
            endpoint = f"/{drive}/drive/root:/{parent_path}:/children"
        
        folder_data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        
        return self.graph.post(endpoint, json=folder_data)
    
    def delete_item(self, item_id: str, drive: str = "me") -> bool:
        """Delete an item from OneDrive.
        
        Args:
            item_id: Item ID or path
            drive: Drive identifier
        
        Returns:
            True if successful
        """
        if item_id.startswith("/") or ":" in item_id:
            if item_id.startswith("/"):
                item_id = item_id[1:]
            item_id = item_id.replace("/", ":")
            endpoint = f"/{drive}/drive/root:/{item_id}:"
        else:
            endpoint = f"/{drive}/drive/items/{item_id}"
        
        import requests
        token = self.graph.auth.get_token()
        response = requests.delete(
            f"{self.graph.base_url}{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        response.raise_for_status()
        return True
    
    def search_items(self, query: str, drive: str = "me") -> List[Dict[str, Any]]:
        """Search for items in OneDrive.
        
        Args:
            query: Search query
            drive: Drive identifier
        
        Returns:
            List of matching items
        """
        endpoint = f"/{drive}/drive/root/search(q='{query}')"
        try:
            response = self.graph.get(endpoint)
            return response.get("value", [])
        except Exception:
            return []
    
    def get_drive_info(self, drive: str = "me") -> Dict[str, Any]:
        """Get information about the drive.
        
        Args:
            drive: Drive identifier
        
        Returns:
            Drive information dictionary
        """
        return self.graph.get(f"/{drive}/drive")

