"""Google Calendar integration."""

import os
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

import requests

from .base import BaseIntegration, IntegrationStatus


class GoogleCalendarIntegration(BaseIntegration):
    """Integration for Google Calendar."""
    
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "Google Calendar", "calendar")
        self.credentials_path = os.path.expanduser("~/.assistant_hub/google_calendar_credentials.json")
        self.token_path = os.path.expanduser("~/.assistant_hub/google_calendar_token.json")
        self._api_base = "https://www.googleapis.com/calendar/v3"

    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        token = self._load_access_token()
        if not token:
            return False

        try:
            resp = requests.get(
                "https://www.googleapis.com/oauth2/v1/tokeninfo",
                params={"access_token": token},
                timeout=8,
            )
            if resp.status_code != 200:
                self.update_status(False, f"Token invalid: {resp.text[:120]}")
                return False
        except requests.RequestException as exc:
            self.update_status(False, f"Auth check failed: {self._safe_truncate(str(exc))}")
            return False

        self.update_status(True)
        return True

    def sync(self) -> int:
        """Sync calendar events."""
        if not self.authenticate():
            return 0

        try:
            events = self._fetch_events()
            count = 0
            for event in events:
                event_id = event.get("id")
                title = event.get("summary") or "(No title)"
                if not event_id:
                    continue

                start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
                end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")

                self.record_item(
                    external_id=event_id,
                    item_kind="event",
                    title=title,
                    data={
                        "status": event.get("status"),
                        "start": start,
                        "end": end,
                        "htmlLink": event.get("htmlLink"),
                        "location": event.get("location"),
                        "updated": event.get("updated"),
                        "created": event.get("created"),
                        "attendees": event.get("attendees", []),
                    },
                )
                count += 1

            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            self.logger.exception("Google Calendar sync failed")
            self.update_status(False, self._safe_truncate(str(e)))
            return 0

    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, '_status') or not self._status:
            self._status = IntegrationStatus()
        return self._status

    def _fetch_events(self) -> List[Dict]:
        """Fetch events from Google Calendar API."""
        token = self._load_access_token()
        if not token:
            return []

        now = datetime.utcnow().isoformat() + "Z"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "singleEvents": True,
            "orderBy": "startTime",
            "timeMin": now,
            "maxResults": 50,
        }

        resp = requests.get(
            f"{self._api_base}/calendars/primary/events",
            headers=headers,
            params=params,
            timeout=10,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Calendar API error: {resp.status_code} {resp.text}")

        payload = resp.json()
        return payload.get("items", [])

    def _load_access_token(self) -> Optional[str]:
        """Load an access token from env or token file."""
        if os.getenv("GOOGLE_CALENDAR_TOKEN"):
            return os.getenv("GOOGLE_CALENDAR_TOKEN")

        if os.path.exists(self.token_path):
            try:
                import json

                with open(self.token_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    token = data.get("access_token") or data.get("token")
                    if token:
                        return token
            except Exception as exc:
                self.logger.error("Failed to read Google Calendar token: %s", exc)

        self.update_status(False, "No Google Calendar token configured")
        return None

