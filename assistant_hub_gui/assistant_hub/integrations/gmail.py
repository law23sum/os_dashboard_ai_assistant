"""Gmail integration."""

import os
from typing import Dict, List, Optional
import sqlite3

import requests

from .base import BaseIntegration, IntegrationStatus


class GmailIntegration(BaseIntegration):
    """Integration for Gmail."""

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "Gmail", "mail")
        self.credentials_path = os.path.expanduser(
            "~/.assistant_hub/gmail_credentials.json"
        )
        self.token_path = os.path.expanduser("~/.assistant_hub/gmail_token.json")
        self._api_base = "https://gmail.googleapis.com/gmail/v1"

    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
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
            self.update_status(
                False, f"Auth check failed: {self._safe_truncate(str(exc))}"
            )
            return False

        self.update_status(True)
        return True

    def sync(self) -> int:
        """Sync emails."""
        if not self.authenticate():
            return 0

        try:
            messages = self._fetch_messages()
            count = 0
            for msg in messages:
                msg_id = msg.get("id")
                if not msg_id:
                    continue

                details = self._fetch_message_detail(msg_id)
                headers = {
                    h.get("name"): h.get("value")
                    for h in details.get("payload", {}).get("headers", [])
                }
                subject = headers.get("Subject", "(No subject)")
                sender = headers.get("From", "")
                date = headers.get("Date", "")

                self.record_item(
                    external_id=msg_id,
                    item_kind="email",
                    title=subject,
                    data={
                        "from": sender,
                        "date": date,
                        "snippet": details.get("snippet"),
                        "labelIds": details.get("labelIds", []),
                    },
                )
                count += 1

            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            self.logger.exception("Gmail sync failed")
            self.update_status(False, self._safe_truncate(str(e)))
            return 0

    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, "_status") or not self._status:
            self._status = IntegrationStatus()
        return self._status

    def _fetch_messages(self) -> List[Dict]:
        """Fetch messages from Gmail API."""
        token = self._load_access_token()
        if not token:
            return []

        headers = {"Authorization": f"Bearer {token}"}
        params = {"maxResults": 25, "labelIds": "INBOX"}

        resp = requests.get(
            f"{self._api_base}/users/me/messages",
            headers=headers,
            params=params,
            timeout=10,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Gmail API error: {resp.status_code} {resp.text}")

        return resp.json().get("messages", [])

    def _fetch_message_detail(self, message_id: str) -> Dict:
        """Fetch a single message details."""
        token = self._load_access_token()
        if not token:
            return {}

        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(
            f"{self._api_base}/users/me/messages/{message_id}",
            headers=headers,
            params={
                "format": "metadata",
                "metadataHeaders": ["Subject", "From", "Date"],
            },
            timeout=10,
        )

        if resp.status_code != 200:
            raise RuntimeError(f"Gmail message error: {resp.status_code} {resp.text}")

        return resp.json()

    def _load_access_token(self) -> Optional[str]:
        """Load an access token from env or token file."""
        if os.getenv("GMAIL_TOKEN"):
            return os.getenv("GMAIL_TOKEN")

        if os.path.exists(self.token_path):
            try:
                import json

                with open(self.token_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    token = data.get("access_token") or data.get("token")
                    if token:
                        return token
            except Exception as exc:
                self.logger.error("Failed to read Gmail token: %s", exc)

        self.update_status(False, "No Gmail token configured")
        return None
