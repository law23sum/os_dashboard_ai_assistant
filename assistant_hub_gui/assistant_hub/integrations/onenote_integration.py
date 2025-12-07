"""OneNote integration wrapper for GUI."""

import os
from pathlib import Path
from typing import Dict
import sqlite3

from .base import BaseIntegration, IntegrationStatus

# Optional imports - will be checked in authenticate()
try:
    from .onenote.service import OneNoteService
    from .onenote import OneNoteClient
    from .msgraph import GraphClient
    from .msgraph.auth import GraphCredentials
    ONENOTE_MODULES_AVAILABLE = True
except ImportError:
    ONENOTE_MODULES_AVAILABLE = False
    GraphCredentials = None


class OneNoteIntegration(BaseIntegration):
    """Integration for Microsoft OneNote."""
    
    def __init__(self, conn: sqlite3.Connection, mirror_root: str = None):
        super().__init__(conn, "OneNote", "onenote")
        self.mirror_root = mirror_root or os.path.expanduser("~/.assistant_hub/onenote_mirror")
        self.client = None
        self.service = None
    
    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph for OneNote."""
        if not ONENOTE_MODULES_AVAILABLE:
            self.update_status(False, "OneNote modules not available. Install required dependencies.")
            return False
        
        try:
            # GraphCredentials should be imported at module level, but check if available
            if GraphCredentials is None:
                try:
                    from .msgraph.auth import GraphCredentials
                except ImportError as e:
                    module_name = str(e).split("'")[1] if "'" in str(e) else "msgraph.auth"
                    self.update_status(False, f"Module not found: {module_name}. Install required dependencies.")
                    return False
            
            # Check if credentials are configured first (pass connection to load from DB)
            try:
                creds = GraphCredentials.from_env(conn=self.conn)
                if not creds.tenant_id or not creds.client_id or not creds.client_secret:
                    self.update_status(False, "Not authenticated. Configure Microsoft Graph credentials.")
                    return False
            except Exception as e:
                self.update_status(False, f"Credentials error: {str(e)[:50]}")
                return False
            
            # Pass connection to GraphClient so it can load credentials from database
            # Use delegated auth for /me/ endpoints
            graph_client = GraphClient(conn=self.conn, use_delegated=True)
            self.client = OneNoteClient(graph_client)
            self.service = OneNoteService(self.mirror_root, self.client)
            
            # Try to list notebooks to verify auth
            try:
                notebooks = self.client.list_notebooks()
                self.update_status(True, item_count=len(notebooks) if notebooks else 0)
                return True
            except Exception as auth_error:
                error_msg = str(auth_error)
                # Check if we need to authenticate
                if "No valid access token" in error_msg or "authenticate" in error_msg.lower():
                    # Try to authenticate interactively
                    try:
                        from .msgraph.auth import GraphDelegatedAuth
                        delegated_auth = GraphDelegatedAuth(
                            GraphCredentials.from_env(conn=self.conn),
                            conn=self.conn
                        )
                        delegated_auth.authenticate_interactive()
                        # Retry with new token
                        graph_client = GraphClient(auth=delegated_auth, conn=self.conn)
                        self.client = OneNoteClient(graph_client)
                        notebooks = self.client.list_notebooks()
                        self.update_status(True, item_count=len(notebooks) if notebooks else 0)
                        return True
                    except Exception as interactive_error:
                        self.update_status(
                            False,
                            f"Authentication required. Error: {str(interactive_error)[:80]}"
                        )
                        return False
                raise
        except Exception as e:
            error_msg = str(e)
            # Provide more specific error messages
            if "400" in error_msg and ("Bad Request" in error_msg or "/me/" in error_msg):
                self.update_status(
                    False, 
                    "OneNote requires delegated permissions (user sign-in). "
                    "Current setup uses app-only auth which doesn't support /me/ endpoints."
                )
            elif "401" in error_msg or "Unauthorized" in error_msg:
                self.update_status(False, "Authentication failed. Check credentials and permissions.")
            elif "DELEGATED" in error_msg or "delegated" in error_msg.lower():
                self.update_status(
                    False,
                    "OneNote requires user sign-in (delegated permissions). "
                    "App-only authentication is not supported for /me/ endpoints."
                )
            elif "credentials" in error_msg.lower() or "auth" in error_msg.lower() or "Authentication" in error_msg:
                self.update_status(False, "Not authenticated. Configure Microsoft Graph credentials.")
            elif "Module" in error_msg or "ImportError" in error_msg or "No module" in error_msg:
                self.update_status(False, "Required modules not installed. Check dependencies.")
            else:
                # Truncate long error messages for display
                display_msg = error_msg[:100] + "..." if len(error_msg) > 100 else error_msg
                self.update_status(False, display_msg)
            return False
    
    def sync(self) -> int:
        """Sync OneNote notebooks, sections, and pages."""
        if not self.authenticate():
            return 0
        
        count = 0
        try:
            notebooks = self.client.list_notebooks()
            if not notebooks:
                self.update_status(True, item_count=0)
                return 0
            
            for notebook in notebooks:
                notebook_id = notebook.get("id")
                notebook_name = notebook.get("displayName", "Unknown")
                if not notebook_id:
                    continue
                
                sections = self.client.list_sections(notebook_id)
                for section in sections:
                    section_id = section.get("id")
                    section_name = section.get("displayName", "Unknown")
                    if not section_id:
                        continue
                    
                    pages = self.client.list_pages(section_id)
                    for page in pages:
                        page_id = page.get("id")
                        page_title = page.get("title", "Untitled")
                        if not page_id:
                            continue
                        
                        self.record_item(
                            external_id=page_id,
                            item_kind="page",
                            title=f"{notebook_name} > {section_name} > {page_title}",
                            data={
                                "notebook_id": notebook_id,
                                "notebook_name": notebook_name,
                                "section_id": section_id,
                                "section_name": section_name,
                                "page_id": page_id,
                                "page_title": page_title
                            }
                        )
                        count += 1
            
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

