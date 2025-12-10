"""
Google APIs Client for Gmail and Calendar integration
"""

import asyncio
import base64
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import get_api_config
from ..logging_config import setup_logger


class GoogleClient:
    """Google APIs client for Gmail and Calendar"""

    def __init__(self):
        self.config = get_api_config()
        self.logger = setup_logger("GoogleClient")
        self.credentials = None
        self.gmail_service = None
        self.calendar_service = None

    async def initialize(self) -> bool:
        """Initialize Google API clients"""
        try:
            # Load or create credentials
            await self._authenticate()

            # Build services
            self.gmail_service = build("gmail", "v1", credentials=self.credentials)
            self.calendar_service = build(
                "calendar", "v3", credentials=self.credentials
            )

            self.logger.info("Google API clients initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Google clients: {e}")
            raise

    async def _authenticate(self):
        """Handle Google OAuth authentication"""
        try:
            # Load existing credentials
            if os.path.exists(self.config.google_token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.config.google_token_file, self.config.google_scopes
                )

            # If credentials are not valid, refresh or re-authenticate
            if not self.credentials or not self.credentials.valid:
                if (
                    self.credentials
                    and self.credentials.expired
                    and self.credentials.refresh_token
                ):
                    self.credentials.refresh(Request())
                else:
                    # Run OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.google_credentials_file, self.config.google_scopes
                    )
                    self.credentials = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.config.google_token_file, "w") as token:
                    token.write(self.credentials.to_json())

        except Exception as e:
            self.logger.error(f"Google authentication failed: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Google APIs are accessible"""
        try:
            # Test Gmail API
            self.gmail_service.users().getProfile(userId="me").execute()

            # Test Calendar API
            self.calendar_service.calendarList().list().execute()

            return True
        except Exception as e:
            self.logger.error(f"Google APIs health check failed: {e}")
            return False

    # Gmail Operations
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachments: List[str] = None,
        cc: str = None,
        bcc: str = None,
        html_body: str = None,
    ) -> bool:
        """Send email via Gmail"""
        try:
            # Create message
            message = MIMEMultipart()
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = cc
            if bcc:
                message["bcc"] = bcc

            # Add body
            if html_body:
                message.attach(MIMEText(html_body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename= {os.path.basename(file_path)}",
                            )
                            message.attach(part)

            # Send message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {"raw": raw_message}

            result = (
                self.gmail_service.users()
                .messages()
                .send(userId="me", body=send_message)
                .execute()
            )

            self.logger.info(f"Email sent successfully. Message ID: {result['id']}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise

    async def get_emails(
        self, query: str = "", max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get emails from Gmail"""
        try:
            # Search for messages
            results = (
                self.gmail_service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])
            emails = []

            for message in messages:
                # Get full message details
                msg = (
                    self.gmail_service.users()
                    .messages()
                    .get(userId="me", id=message["id"])
                    .execute()
                )

                # Extract email data
                headers = msg["payload"].get("headers", [])
                email_data = {
                    "id": msg["id"],
                    "thread_id": msg["threadId"],
                    "snippet": msg["snippet"],
                    "date": next(
                        (h["value"] for h in headers if h["name"] == "Date"), ""
                    ),
                    "from": next(
                        (h["value"] for h in headers if h["name"] == "From"), ""
                    ),
                    "to": next((h["value"] for h in headers if h["name"] == "To"), ""),
                    "subject": next(
                        (h["value"] for h in headers if h["name"] == "Subject"), ""
                    ),
                }

                # Get body
                if "parts" in msg["payload"]:
                    for part in msg["payload"]["parts"]:
                        if part["mimeType"] == "text/plain":
                            data = part["body"]["data"]
                            email_data["body"] = base64.urlsafe_b64decode(data).decode(
                                "utf-8"
                            )
                            break
                else:
                    if msg["payload"]["body"].get("data"):
                        data = msg["payload"]["body"]["data"]
                        email_data["body"] = base64.urlsafe_b64decode(data).decode(
                            "utf-8"
                        )

                emails.append(email_data)

            return emails

        except Exception as e:
            self.logger.error(f"Failed to get emails: {e}")
            raise

    async def mark_email_read(self, message_id: str) -> bool:
        """Mark email as read"""
        try:
            self.gmail_service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()

            return True

        except Exception as e:
            self.logger.error(f"Failed to mark email as read: {e}")
            raise

    # Calendar Operations
    async def create_calendar_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        attendees: List[str] = None,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """Create calendar event"""
        try:
            event = {
                "summary": title,
                "description": description,
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC",
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC",
                },
            }

            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]

            created_event = (
                self.calendar_service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )

            return {
                "id": created_event["id"],
                "title": created_event["summary"],
                "start_time": created_event["start"]["dateTime"],
                "end_time": created_event["end"]["dateTime"],
                "html_link": created_event["htmlLink"],
            }

        except Exception as e:
            self.logger.error(f"Failed to create calendar event: {e}")
            raise

    async def get_calendar_events(
        self,
        calendar_id: str = "primary",
        max_results: int = 10,
        time_min: datetime = None,
    ) -> List[Dict[str, Any]]:
        """Get calendar events"""
        try:
            if not time_min:
                time_min = datetime.utcnow()

            events_result = (
                self.calendar_service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min.isoformat() + "Z",
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            return [
                {
                    "id": event["id"],
                    "title": event.get("summary", "No Title"),
                    "start_time": event["start"].get(
                        "dateTime", event["start"].get("date")
                    ),
                    "end_time": event["end"].get("dateTime", event["end"].get("date")),
                    "description": event.get("description", ""),
                    "html_link": event.get("htmlLink", ""),
                }
                for event in events
            ]

        except Exception as e:
            self.logger.error(f"Failed to get calendar events: {e}")
            raise

    async def update_calendar_event(
        self, event_id: str, updates: Dict[str, Any], calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Update calendar event"""
        try:
            # Get existing event
            event = (
                self.calendar_service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )

            # Apply updates
            for key, value in updates.items():
                if key == "title":
                    event["summary"] = value
                elif key == "description":
                    event["description"] = value
                elif key == "start_time":
                    event["start"]["dateTime"] = value.isoformat()
                elif key == "end_time":
                    event["end"]["dateTime"] = value.isoformat()

            # Update event
            updated_event = (
                self.calendar_service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )

            return {
                "id": updated_event["id"],
                "title": updated_event["summary"],
                "start_time": updated_event["start"]["dateTime"],
                "end_time": updated_event["end"]["dateTime"],
            }

        except Exception as e:
            self.logger.error(f"Failed to update calendar event: {e}")
            raise

    async def delete_calendar_event(
        self, event_id: str, calendar_id: str = "primary"
    ) -> bool:
        """Delete calendar event"""
        try:
            self.calendar_service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()

            return True

        except Exception as e:
            self.logger.error(f"Failed to delete calendar event: {e}")
            raise

    async def get_calendars(self) -> List[Dict[str, Any]]:
        """Get list of calendars"""
        try:
            calendar_list = self.calendar_service.calendarList().list().execute()

            return [
                {
                    "id": calendar["id"],
                    "name": calendar["summary"],
                    "description": calendar.get("description", ""),
                    "primary": calendar.get("primary", False),
                }
                for calendar in calendar_list["items"]
            ]

        except Exception as e:
            self.logger.error(f"Failed to get calendars: {e}")
            raise

    async def shutdown(self):
        """Shutdown Google client"""
        self.credentials = None
        self.gmail_service = None
        self.calendar_service = None
        self.logger.info("Google client shutdown complete")
