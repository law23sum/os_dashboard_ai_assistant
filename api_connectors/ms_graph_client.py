"""
Microsoft Graph API Client

Unified API for Office 365, OneDrive, OneNote, Outlook, and more
"""

import asyncio
import json
import base64
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging

import aiohttp
from msal import ConfidentialClientApplication, PublicClientApplication

from .base import BaseAPIConnector, APIResponse, RateLimit

logger = logging.getLogger(__name__)


class MicrosoftGraphClient(BaseAPIConnector):
    """Microsoft Graph API client for Office 365 services"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Microsoft Graph configuration
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.tenant_id = config.get("tenant_id")
        self.scopes = config.get("scopes", ["https://graph.microsoft.com/.default"])

        # Authentication
        self.app = None
        self.token = None
        self._authenticated = False

        # Base URLs
        self.base_url = "https://graph.microsoft.com/v1.0"

        # Initialize MSAL app
        self._setup_msal_app()

    def _setup_msal_app(self):
        """Setup Microsoft Authentication Library application"""
        try:
            if self.client_secret:
                # Confidential client (server-side)
                self.app = ConfidentialClientApplication(
                    client_id=self.client_id,
                    client_credential=self.client_secret,
                    authority=f"https://login.microsoftonline.com/{self.tenant_id}"
                )
            else:
                # Public client (desktop/mobile)
                self.app = PublicClientApplication(
                    client_id=self.client_id,
                    authority=f"https://login.microsoftonline.com/{self.tenant_id}"
                )
        except Exception as e:
            self.logger.error(f"Failed to setup MSAL app: {e}")

    def _setup_rate_limiter(self) -> 'RateLimiter':
        """Setup rate limiter for Microsoft Graph API"""
        # Microsoft Graph has a limit of 10,000 requests per 10 minutes
        rate_limit = RateLimit(
            requests_per_minute=1000,  # Conservative limit
            requests_per_hour=5000,
            requests_per_day=10000,
            burst_limit=50
        )
        return super()._setup_rate_limiter(rate_limit)

    async def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph API"""
        try:
            if not self.app:
                return False

            # For confidential client, get token directly
            if isinstance(self.app, ConfidentialClientApplication):
                result = self.app.acquire_token_for_client(scopes=self.scopes)
                if "access_token" in result:
                    self.token = result
                    self._authenticated = True
                    self.logger.info("Microsoft Graph authentication successful")
                    return True
                else:
                    self.logger.error(f"Authentication failed: {result.get('error_description')}")
                    return False

            # For public client, would need interactive flow
            # This is handled separately in GUI/desktop apps
            self.logger.warning("Public client authentication requires interactive flow")
            return False

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False

    async def test_connection(self) -> APIResponse:
        """Test Microsoft Graph API connection"""
        # Test with a simple user profile request
        return await self.make_request("GET", "/me")

    async def _make_http_request(self, method: str, endpoint: str,
                               data: Optional[Dict[str, Any]],
                               headers: Optional[Dict[str, str]],
                               params: Optional[Dict[str, Any]]) -> APIResponse:
        """Make HTTP request to Microsoft Graph API"""
        try:
            url = f"{self.base_url}{endpoint}"

            # Prepare headers
            request_headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json"
            }
            if headers:
                request_headers.update(headers)

            # Prepare request
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=request_headers, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "POST":
                    async with session.post(url, headers=request_headers, json=data, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "PUT":
                    async with session.put(url, headers=request_headers, json=data, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "PATCH":
                    async with session.patch(url, headers=request_headers, json=data, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=request_headers, params=params) as response:
                        return await self._process_response(response)
                else:
                    return APIResponse(success=False, error=f"Unsupported method: {method}")

        except Exception as e:
            self.logger.error(f"HTTP request failed: {e}")
            return APIResponse(success=False, error=str(e))

    async def _process_response(self, response: aiohttp.ClientResponse) -> APIResponse:
        """Process HTTP response"""
        try:
            status_code = response.status

            if status_code >= 200 and status_code < 300:
                try:
                    data = await response.json()
                except:
                    data = await response.text()

                return APIResponse(
                    success=True,
                    data=data,
                    status_code=status_code,
                    headers=dict(response.headers)
                )
            else:
                error_text = await response.text()
                return APIResponse(
                    success=False,
                    error=error_text,
                    status_code=status_code,
                    headers=dict(response.headers)
                )

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    # OneDrive Operations

    async def list_drive_files(self, folder_path: str = "") -> APIResponse:
        """List files in OneDrive"""
        endpoint = f"/me/drive/root{':' + folder_path if folder_path else ''}/children"
        return await self.make_request("GET", endpoint)

    async def upload_file(self, local_path: str, remote_path: str) -> APIResponse:
        """Upload file to OneDrive"""
        try:
            with open(local_path, 'rb') as f:
                file_content = f.read()

            # Get upload session
            endpoint = f"/me/drive/root:{remote_path}:/createUploadSession"
            session_response = await self.make_request("POST", endpoint, {
                "@microsoft.graph.conflictBehavior": "replace"
            })

            if not session_response.success:
                return session_response

            upload_url = session_response.data["uploadUrl"]

            # Upload file content
            headers = {
                "Content-Length": str(len(file_content)),
                "Content-Range": f"bytes 0-{len(file_content)-1}/{len(file_content)}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.put(upload_url, data=file_content, headers=headers) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        return APIResponse(success=True, data=data, status_code=response.status)
                    else:
                        error = await response.text()
                        return APIResponse(success=False, error=error, status_code=response.status)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def download_file(self, remote_path: str, local_path: str) -> APIResponse:
        """Download file from OneDrive"""
        try:
            endpoint = f"/me/drive/root:{remote_path}:/content"
            response = await self.make_request("GET", endpoint)

            if response.success:
                with open(local_path, 'wb') as f:
                    f.write(response.data)
                return APIResponse(success=True, data={"local_path": local_path})
            else:
                return response

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    # OneNote Operations

    async def list_notebooks(self) -> APIResponse:
        """List OneNote notebooks"""
        return await self.make_request("GET", "/me/onenote/notebooks")

    async def list_sections(self, notebook_id: str) -> APIResponse:
        """List sections in a notebook"""
        endpoint = f"/me/onenote/notebooks/{notebook_id}/sections"
        return await self.make_request("GET", endpoint)

    async def list_pages(self, section_id: str) -> APIResponse:
        """List pages in a section"""
        endpoint = f"/me/onenote/sections/{section_id}/pages"
        return await self.make_request("GET", endpoint)

    async def get_page_content(self, page_id: str) -> APIResponse:
        """Get OneNote page content"""
        endpoint = f"/me/onenote/pages/{page_id}/content"
        return await self.make_request("GET", endpoint)

    async def create_page(self, section_id: str, html_content: str, title: str = "") -> APIResponse:
        """Create a new OneNote page"""
        endpoint = f"/me/onenote/sections/{section_id}/pages"

        # Create multipart request
        boundary = "MyPartBoundary"
        body_parts = [
            f"--{boundary}",
            'Content-Disposition: form-data; name="Presentation"',
            'Content-Type: text/html',
            '',
            f'<html><head><title>{title}</title></head><body>{html_content}</body></html>',
            f"--{boundary}--"
        ]

        body = "\r\n".join(body_parts).encode('utf-8')

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }

        return await self.make_request("POST", endpoint, data=body, headers=headers)

    # Office 365 Operations

    async def list_emails(self, folder: str = "inbox", limit: int = 20) -> APIResponse:
        """List emails from Outlook"""
        endpoint = f"/me/mailFolders/{folder}/messages"
        params = {"$top": limit, "$orderby": "receivedDateTime desc"}
        return await self.make_request("GET", endpoint, params=params)

    async def send_email(self, to: List[str], subject: str, body: str,
                        content_type: str = "Text") -> APIResponse:
        """Send email via Outlook"""
        endpoint = "/me/sendMail"

        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": content_type,
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": addr}} for addr in to]
            }
        }

        return await self.make_request("POST", endpoint, email_data)

    async def list_calendar_events(self, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> APIResponse:
        """List calendar events"""
        endpoint = "/me/calendar/events"

        params = {}
        if start_date and end_date:
            params["$filter"] = f"start/dateTime ge '{start_date}' and start/dateTime le '{end_date}'"

        return await self.make_request("GET", endpoint, params=params)

    async def create_calendar_event(self, subject: str, start_time: str,
                                  end_time: str, location: str = "",
                                  description: str = "") -> APIResponse:
        """Create calendar event"""
        endpoint = "/me/calendar/events"

        event_data = {
            "subject": subject,
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC"
            },
            "location": {
                "displayName": location
            },
            "body": {
                "contentType": "text",
                "content": description
            }
        }

        return await self.make_request("POST", endpoint, event_data)

    # Word Operations

    async def list_word_documents(self) -> APIResponse:
        """List Word documents"""
        endpoint = "/me/drive/root/search(q='.docx')"
        return await self.make_request("GET", endpoint)

    async def get_word_document_content(self, item_id: str) -> APIResponse:
        """Get Word document content"""
        endpoint = f"/me/drive/items/{item_id}/content"
        return await self.make_request("GET", endpoint)

    # Excel Operations

    async def list_excel_files(self) -> APIResponse:
        """List Excel files"""
        endpoint = "/me/drive/root/search(q='.xlsx')"
        return await self.make_request("GET", endpoint)

    async def get_excel_worksheets(self, item_id: str) -> APIResponse:
        """Get Excel worksheets"""
        endpoint = f"/me/drive/items/{item_id}/workbook/worksheets"
        return await self.make_request("GET", endpoint)

    async def get_excel_data(self, item_id: str, worksheet_id: str,
                           range_address: str = "A1:Z100") -> APIResponse:
        """Get Excel worksheet data"""
        endpoint = f"/me/drive/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{range_address}')"
        return await self.make_request("GET", endpoint)

    # PowerPoint Operations

    async def list_powerpoint_files(self) -> APIResponse:
        """List PowerPoint files"""
        endpoint = "/me/drive/root/search(q='.pptx')"
        return await self.make_request("GET", endpoint)

    # Teams/Chat Operations (if available)

    async def list_teams_chats(self) -> APIResponse:
        """List Teams chats"""
        endpoint = "/me/chats"
        return await self.make_request("GET", endpoint)

    async def send_teams_message(self, chat_id: str, message: str) -> APIResponse:
        """Send message in Teams chat"""
        endpoint = f"/chats/{chat_id}/messages"

        message_data = {
            "body": {
                "content": message,
                "contentType": "text"
            }
        }

        return await self.make_request("POST", endpoint, message_data)
