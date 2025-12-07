"""Microsoft Graph Client - Handles OAuth and API calls for Word, Excel, PowerPoint, and OneNote via Microsoft Graph API."""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class MSGraphClient:
    """Client for Microsoft Graph API services."""

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, client_id: str = None, tenant_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.getenv('MS_CLIENT_ID')
        self.tenant_id = tenant_id or os.getenv('MS_TENANT_ID')
        self.client_secret = client_secret or os.getenv('MS_CLIENT_SECRET')
        self.access_token = None

    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph API."""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default'
            }

            response = requests.post(token_url, data=token_data)
            response.raise_for_status()

            self.access_token = response.json()['access_token']
            return True
        except Exception as e:
            print(f"Microsoft Graph authentication failed: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_drive_files(self, drive_id: str = 'me/drive', max_results: int = 10) -> List[Dict]:
        """Get files from OneDrive."""
        if not self.access_token and not self.authenticate():
            return []

        try:
            url = f"{self.BASE_URL}/{drive_id}/root/children"
            params = {'$top': max_results}
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            files = response.json().get('value', [])
            return [self._parse_drive_item(item) for item in files]
        except Exception as e:
            print(f"Error fetching OneDrive files: {e}")
            return []

    def get_word_documents(self, folder_path: str = None) -> List[Dict]:
        """Get Word documents."""
        files = self.get_drive_files()
        word_docs = [
            f for f in files
            if f.get('file_type') in ['docx', 'doc']
        ]
        return word_docs

    def get_excel_files(self, folder_path: str = None) -> List[Dict]:
        """Get Excel files."""
        files = self.get_drive_files()
        excel_files = [
            f for f in files
            if f.get('file_type') in ['xlsx', 'xls']
        ]
        return excel_files

    def get_onenote_pages(self, notebook_id: str = None) -> List[Dict]:
        """Get OneNote pages."""
        if not self.access_token and not self.authenticate():
            return []

        try:
            url = f"{self.BASE_URL}/me/onenote/pages"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            pages = response.json().get('value', [])
            return [self._parse_onenote_page(page) for page in pages]
        except Exception as e:
            print(f"Error fetching OneNote pages: {e}")
            return []

    def _parse_drive_item(self, item: Dict) -> Dict:
        """Parse OneDrive item data."""
        return {
            'id': item['id'],
            'name': item['name'],
            'file_type': item.get('file', {}).get('mimeType', '').split('/')[-1],
            'size': item.get('size', 0),
            'last_modified': item.get('lastModifiedDateTime'),
            'web_url': item.get('webUrl')
        }

    def _parse_onenote_page(self, page: Dict) -> Dict:
        """Parse OneNote page data."""
        return {
            'id': page['id'],
            'title': page['title'],
            'created_time': page.get('createdDateTime'),
            'last_modified': page.get('lastModifiedDateTime'),
            'content_url': page.get('contentUrl'),
            'links': page.get('links', {})
        }
