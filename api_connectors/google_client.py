"""
Google Workspace API Client

Integrates with Gmail, Google Calendar, Google Drive, and Google Docs
"""

import asyncio
import json
import base64
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
import pickle
import os

import aiohttp
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .base import BaseAPIConnector, APIResponse, RateLimit

logger = logging.getLogger(__name__)


class GoogleWorkspaceClient(BaseAPIConnector):
    """Google Workspace API client"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Google API configuration
        self.client_secret_file = config.get("client_secret_file")
        self.token_pickle_file = config.get("token_pickle_file", "token.pickle")
        self.scopes = config.get("scopes", [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents'
        ])

        # Google API services
        self.gmail_service = None
        self.calendar_service = None
        self.drive_service = None
        self.docs_service = None

        # Credentials
        self.creds = None
        self._authenticated = False

    def _setup_rate_limiter(self) -> 'RateLimiter':
        """Setup rate limiter for Google APIs"""
        # Google APIs have various limits, conservative approach
        rate_limit = RateLimit(
            requests_per_minute=100,   # Conservative limit
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_limit=20
        )
        return super()._setup_rate_limiter(rate_limit)

    async def authenticate(self) -> bool:
        """Authenticate with Google APIs"""
        try:
            # Load existing credentials
            if os.path.exists(self.token_pickle_file):
                with open(self.token_pickle_file, 'rb') as token:
                    self.creds = pickle.load(token)

            # Refresh or get new credentials if needed
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Run OAuth flow (this would need to be handled in GUI/desktop app)
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secret_file, self.scopes
                    )
                    # For server-side, this would need different handling
                    self.creds = flow.run_local_server(port=0)

                # Save credentials
                with open(self.token_pickle_file, 'wb') as token:
                    pickle.dump(self.creds, token)

            # Build API services
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)

            self._authenticated = True
            self.logger.info("Google Workspace authentication successful")
            return True

        except Exception as e:
            self.logger.error(f"Google authentication failed: {e}")
            return False

    async def test_connection(self) -> APIResponse:
        """Test Google API connection"""
        try:
            # Test with a simple profile request
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            return APIResponse(success=True, data={"email": profile.get("emailAddress")})
        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def _make_http_request(self, method: str, endpoint: str,
                               data: Optional[Dict[str, Any]],
                               headers: Optional[Dict[str, str]],
                               params: Optional[Dict[str, Any]]) -> APIResponse:
        """Make HTTP request to Google APIs"""
        # This is a simplified implementation
        # In practice, you'd use the specific service methods
        try:
            # For now, return a not implemented response
            # Real implementation would route to specific Google API services
            return APIResponse(success=False, error="Direct HTTP requests not implemented for Google APIs")
        except Exception as e:
            return APIResponse(success=False, error=str(e))

    # Gmail Operations

    async def list_emails(self, max_results: int = 20, query: str = "") -> APIResponse:
        """List Gmail messages"""
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            # Get full message details
            detailed_messages = []
            for msg in messages[:5]:  # Limit to avoid rate limits
                msg_detail = self.gmail_service.users().messages().get(
                    userId='me', id=msg['id']
                ).execute()
                detailed_messages.append(msg_detail)

            return APIResponse(success=True, data={
                "messages": detailed_messages,
                "total": len(messages)
            })

        except HttpError as e:
            return APIResponse(success=False, error=f"Gmail API error: {e}")

    async def send_email(self, to: str, subject: str, body: str) -> APIResponse:
        """Send email via Gmail"""
        try:
            message = {
                'raw': base64.urlsafe_b64encode(
                    f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}".encode('utf-8')
                ).decode('utf-8')
            }

            result = self.gmail_service.users().messages().send(
                userId='me', body=message
            ).execute()

            return APIResponse(success=True, data=result)

        except HttpError as e:
            return APIResponse(success=False, error=f"Gmail send error: {e}")

    # Google Calendar Operations

    async def list_calendar_events(self, calendar_id: str = 'primary',
                                 max_results: int = 10) -> APIResponse:
        """List Google Calendar events"""
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'

            events_result = self.calendar_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return APIResponse(success=True, data=events_result.get('items', []))

        except HttpError as e:
            return APIResponse(success=False, error=f"Calendar API error: {e}")

    async def create_calendar_event(self, summary: str, start_time: str,
                                  end_time: str, description: str = "") -> APIResponse:
        """Create Google Calendar event"""
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                }
            }

            result = self.calendar_service.events().insert(
                calendarId='primary', body=event
            ).execute()

            return APIResponse(success=True, data=result)

        except HttpError as e:
            return APIResponse(success=False, error=f"Calendar create error: {e}")

    # Google Drive Operations

    async def list_drive_files(self, query: str = "", max_results: int = 20) -> APIResponse:
        """List Google Drive files"""
        try:
            results = self.drive_service.files().list(
                q=query,
                pageSize=max_results,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
            ).execute()

            return APIResponse(success=True, data=results.get('files', []))

        except HttpError as e:
            return APIResponse(success=False, error=f"Drive API error: {e}")

    async def upload_file(self, local_path: str, remote_name: str = None) -> APIResponse:
        """Upload file to Google Drive"""
        try:
            from googleapiclient.http import MediaFileUpload

            if not remote_name:
                remote_name = os.path.basename(local_path)

            file_metadata = {'name': remote_name}
            media = MediaFileUpload(local_path, resumable=True)

            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            return APIResponse(success=True, data=file)

        except HttpError as e:
            return APIResponse(success=False, error=f"Drive upload error: {e}")

    async def download_file(self, file_id: str, local_path: str) -> APIResponse:
        """Download file from Google Drive"""
        try:
            request = self.drive_service.files().get_media(fileId=file_id)

            with open(local_path, 'wb') as f:
                downloader = request.execute()
                f.write(downloader)

            return APIResponse(success=True, data={"local_path": local_path})

        except HttpError as e:
            return APIResponse(success=False, error=f"Drive download error: {e}")

    # Google Docs Operations

    async def list_google_docs(self) -> APIResponse:
        """List Google Docs files"""
        try:
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.document'",
                fields="files(id, name, modifiedTime)"
            ).execute()

            return APIResponse(success=True, data=results.get('files', []))

        except HttpError as e:
            return APIResponse(success=False, error=f"Docs API error: {e}")

    async def get_document_content(self, document_id: str) -> APIResponse:
        """Get Google Doc content"""
        try:
            doc = self.docs_service.documents().get(documentId=document_id).execute()
            return APIResponse(success=True, data=doc)

        except HttpError as e:
            return APIResponse(success=False, error=f"Docs content error: {e}")

    async def create_google_doc(self, title: str, content: str = "") -> APIResponse:
        """Create a new Google Doc"""
        try:
            doc_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.document'
            }

            doc = self.drive_service.files().create(body=doc_metadata).execute()

            if content:
                # Add content to the document
                requests = [{
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }]

                self.docs_service.documents().batchUpdate(
                    documentId=doc['id'], body={'requests': requests}
                ).execute()

            return APIResponse(success=True, data=doc)

        except HttpError as e:
            return APIResponse(success=False, error=f"Docs create error: {e}")

    # Google Sheets Operations

    async def list_google_sheets(self) -> APIResponse:
        """List Google Sheets files"""
        try:
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                fields="files(id, name, modifiedTime)"
            ).execute()

            return APIResponse(success=True, data=results.get('files', []))

        except HttpError as e:
            return APIResponse(success=False, error=f"Sheets API error: {e}")

    async def get_sheet_data(self, spreadsheet_id: str, range_name: str = "A1:Z100") -> APIResponse:
        """Get Google Sheet data"""
        try:
            from googleapiclient.discovery import build
            sheets_service = build('sheets', 'v4', credentials=self.creds)

            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name
            ).execute()

            return APIResponse(success=True, data=result.get('values', []))

        except HttpError as e:
            return APIResponse(success=False, error=f"Sheets data error: {e}")

    # Google Slides Operations

    async def list_google_slides(self) -> APIResponse:
        """List Google Slides files"""
        try:
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.presentation'",
                fields="files(id, name, modifiedTime)"
            ).execute()

            return APIResponse(success=True, data=results.get('files', []))

        except HttpError as e:
            return APIResponse(success=False, error=f"Slides API error: {e}")
