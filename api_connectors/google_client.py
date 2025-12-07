"""Google Client - Handles OAuth and API calls for Gmail and Google Calendar."""

import os
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleClient:
    """Client for Google API services (Gmail, Calendar)."""

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]

    def __init__(self, credentials_path: str = None, token_path: str = None):
        self.credentials_path = credentials_path or 'config/credentials/client_secret.json'
        self.token_path = token_path or 'config/credentials/token.pickle'
        self.creds = None
        self.services = {}

    def authenticate(self) -> bool:
        """Authenticate with Google APIs."""
        try:
            # Load existing credentials
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)

            # Refresh or get new credentials if needed
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)

                # Save credentials
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)

            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def get_gmail_service(self):
        """Get Gmail API service."""
        if 'gmail' not in self.services:
            if not self.creds:
                if not self.authenticate():
                    return None
            self.services['gmail'] = build('gmail', 'v1', credentials=self.creds)
        return self.services['gmail']

    def get_calendar_service(self):
        """Get Calendar API service."""
        if 'calendar' not in self.services:
            if not self.creds:
                if not self.authenticate():
                    return None
            self.services['calendar'] = build('calendar', 'v3', credentials=self.creds)
        return self.services['calendar']

    def get_emails(self, max_results: int = 10) -> List[Dict]:
        """Fetch recent emails."""
        service = self.get_gmail_service()
        if not service:
            return []

        try:
            results = service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])

            emails = []
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId='me', id=msg['id']).execute()
                emails.append(self._parse_email(msg_data))

            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def get_calendar_events(self, max_results: int = 10) -> List[Dict]:
        """Fetch upcoming calendar events."""
        service = self.get_calendar_service()
        if not service:
            return []

        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId='primary', timeMin=now,
                maxResults=max_results, singleEvents=True,
                orderBy='startTime').execute()
            events = events_result.get('items', [])

            return [self._parse_event(event) for event in events]
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []

    def _parse_email(self, msg_data: Dict) -> Dict:
        """Parse Gmail message data."""
        headers = msg_data.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

        return {
            'id': msg_data['id'],
            'subject': subject,
            'from': sender,
            'timestamp': msg_data.get('internalDate'),
            'snippet': msg_data.get('snippet', '')
        }

    def _parse_event(self, event: Dict) -> Dict:
        """Parse Calendar event data."""
        return {
            'id': event['id'],
            'summary': event.get('summary', ''),
            'start': event.get('start', {}),
            'end': event.get('end', {}),
            'location': event.get('location', ''),
            'description': event.get('description', '')
        }
