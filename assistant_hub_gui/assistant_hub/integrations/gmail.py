"""Gmail integration."""

import os
from pathlib import Path
from typing import Dict, List
import sqlite3

from .base import BaseIntegration, IntegrationStatus


class GmailIntegration(BaseIntegration):
    """Integration for Gmail."""
    
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "Gmail", "mail")
        # Check multiple locations for credentials
        project_root = Path(__file__).parent.parent.parent.parent
        root_creds = project_root / "client_secret_788356908604-ro9n0fq4p70q569237314n12u84jnren.apps.googleusercontent.com.json"
        
        if root_creds.exists():
            self.credentials_path = str(root_creds)
        else:
            # Check both naming conventions
            cred_dir = os.path.expanduser("~/.assistant_hub")
            google_gmail_creds = os.path.join(cred_dir, "google_gmail_credentials.json")
            gmail_creds = os.path.join(cred_dir, "gmail_credentials.json")
            if os.path.exists(google_gmail_creds):
                self.credentials_path = google_gmail_creds
            else:
                self.credentials_path = gmail_creds
        self.token_path = os.path.expanduser("~/.assistant_hub/google_gmail_token.json")
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            if not os.path.exists(self.credentials_path):
                self.update_status(False, "Credentials not configured. Go to Integrations > Gmail > Connect to set up OAuth2.")
                return False
            
            if not os.path.exists(self.token_path):
                self.update_status(False, "Not authenticated. Go to Integrations > Gmail > Connect to complete OAuth2 flow.")
                return False
            
            # Verify token is valid by trying to load it
            try:
                from google.oauth2.credentials import Credentials
                creds = Credentials.from_authorized_user_file(self.token_path, ['https://www.googleapis.com/auth/gmail.readonly'])
                if creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                    # Save refreshed token
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
                self.update_status(True)
                return True
            except Exception as token_error:
                # Token might be invalid, suggest re-authentication
                self.update_status(False, f"Token invalid or expired. Go to Integrations > Gmail > Connect to re-authenticate.")
                return False
        except Exception as e:
            self.update_status(False, f"Gmail auth error: {str(e)[:50]}")
            return False
    
    def sync(self) -> int:
        """Sync emails."""
        if not self.authenticate():
            return 0
        
        # TODO: Implement actual Gmail API sync
        try:
            # Example: Fetch emails from Gmail API
            # messages = self._fetch_messages()
            # for msg in messages:
            #     self.record_item(...)
            
            self.update_status(True, item_count=0)
            return 0
        except Exception as e:
            self.update_status(False, str(e))
            return 0
    
    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, '_status') or not self._status:
            self._status = IntegrationStatus()
        return self._status
    
    def _fetch_messages(self) -> List[Dict]:
        """Fetch messages from Gmail API."""
        # TODO: Implement using google-api-python-client
        return []

