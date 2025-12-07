"""Apple Calendar integration for macOS."""

import os
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

from .base import BaseIntegration, IntegrationStatus


class AppleCalendarIntegration(BaseIntegration):
    """Integration for Apple Calendar on macOS."""

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "Apple Calendar", "calendar")

    def authenticate(self) -> bool:
        """Check if Apple Calendar is accessible."""
        try:
            # Check if Calendar.app exists
            result = subprocess.run(
                ["osascript", "-e", "tell application \"Calendar\" to get name of calendars"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.update_status(True)
                return True
            else:
                self.update_status(False, f"Apple Calendar not accessible: {result.stderr}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            self.update_status(False, f"Failed to access Apple Calendar: {str(e)}")
            return False

    def sync(self) -> int:
        """Sync calendar events from Apple Calendar."""
        if not self.authenticate():
            return 0

        try:
            # Use AppleScript to get calendar events
            script = '''
            tell application "Calendar"
                set eventList to {}
                set now to current date
                set oneWeekAgo to now - (7 * days)
                set oneMonthAhead to now + (30 * days)

                repeat with aCalendar in calendars
                    set calendarName to name of aCalendar
                    set theEvents to (every event of aCalendar whose start date ≥ oneWeekAgo and start date ≤ oneMonthAhead)

                    repeat with anEvent in theEvents
                        set eventData to {calendar:calendarName, summary:summary of anEvent, start_date:start date of anEvent, end_date:end date of anEvent, description:description of anEvent, location:location of anEvent}
                        set end of eventList to eventData
                    end repeat
                end repeat

                return eventList
            end tell
            '''

            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.update_status(False, f"AppleScript failed: {result.stderr}")
                return 0

            # Parse the result (this would need proper AppleScript result parsing)
            # For now, this is a placeholder
            count = 0

            # Placeholder event for testing
            self.record_item(
                external_id=f"apple_event_{datetime.now().isoformat()}",
                item_kind="event",
                title="Sample Apple Calendar Event",
                data={
                    "start": datetime.now().isoformat(),
                    "end": (datetime.now().replace(hour=datetime.now().hour + 1)).isoformat(),
                    "source": "Apple Calendar"
                }
            )
            count = 1

            self.update_status(True, item_count=count)
            return count

        except Exception as e:
            self.logger.exception("Apple Calendar sync failed")
            self.update_status(False, self._safe_truncate(str(e)))
            return 0

    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, '_status') or not self._status:
            self._status = IntegrationStatus()
        return self._status

    def _safe_truncate(self, text: str, max_length: int = 100) -> str:
        """Truncate text safely."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
