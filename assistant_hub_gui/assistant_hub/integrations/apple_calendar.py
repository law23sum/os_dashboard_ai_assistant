"""Apple Calendar integration using EventKit."""

import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3

from .base import BaseIntegration, IntegrationStatus

# Try to import EventKit via PyObjC
try:
    from AppKit import NSWorkspace
    from EventKit import (
        EKEventStore,
        EKAuthorizationStatus,
        EKEntityTypeEvent,
        EKEvent,
    )
    EVENTKIT_AVAILABLE = True
except ImportError:
    EVENTKIT_AVAILABLE = False


class AppleCalendarIntegration(BaseIntegration):
    """Integration for Apple Calendar using EventKit."""
    
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "Apple Calendar", "calendar")
        self._event_store = None
        self._authorization_status = None
    
    def authenticate(self) -> bool:
        """Check EventKit authorization status."""
        if not EVENTKIT_AVAILABLE:
            self.update_status(False, "EventKit not available. Install PyObjC: pip install pyobjc-framework-EventKit")
            return False
        
        if sys.platform != "darwin":
            self.update_status(False, "Apple Calendar integration is only available on macOS")
            return False
        
        try:
            self._event_store = EKEventStore.alloc().init()
            
            # Request authorization if needed
            status = self._event_store.authorizationStatusForEntityType_(EKEntityTypeEvent)
            self._authorization_status = status
            
            if status == EKAuthorizationStatus.EKAuthorizationStatusNotDetermined:
                # Request authorization (async - user will see system prompt)
                # Note: This is asynchronous, so we can't check immediately
                self._event_store.requestAccessToEntityType_completion_(
                    EKEntityTypeEvent,
                    lambda granted, error: None
                )
                # Status won't update immediately, but we'll check on next attempt
                self.update_status(False, "Please grant calendar access when prompted, then try again")
                return False
            
            if status == EKAuthorizationStatus.EKAuthorizationStatusAuthorized:
                self.update_status(True)
                return True
            elif status == EKAuthorizationStatus.EKAuthorizationStatusDenied:
                self.update_status(False, "Calendar access denied. Please grant permission in System Settings > Privacy & Security > Calendars")
                return False
            elif status == EKAuthorizationStatus.EKAuthorizationStatusRestricted:
                self.update_status(False, "Calendar access is restricted")
                return False
            else:
                self.update_status(False, "Calendar access not determined")
                return False
                
        except Exception as e:
            self.update_status(False, f"Authentication failed: {str(e)[:100]}")
            return False
    
    def sync(self) -> int:
        """Sync calendar events from Apple Calendar."""
        if not self.authenticate():
            return 0
        
        try:
            events = self._fetch_events()
            count = 0
            
            self.ensure_source()
            
            for event in events:
                event_id = event.get("id")
                title = event.get("title") or "(No title)"
                if not event_id:
                    continue
                
                self.record_item(
                    external_id=event_id,
                    item_kind="event",
                    title=title,
                    data={
                        "start": event.get("start"),
                        "end": event.get("end"),
                        "location": event.get("location"),
                        "notes": event.get("notes"),
                        "calendar": event.get("calendar"),
                        "all_day": event.get("all_day"),
                        "attendees": event.get("attendees", []),
                        "url": event.get("url"),
                    },
                )
                count += 1
            
            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            error_msg = str(e)[:100] if len(str(e)) > 100 else str(e)
            self.update_status(False, f"Sync failed: {error_msg}")
            return 0
    
    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, '_status') or not self._status:
            self._status = IntegrationStatus()
        return self._status
    
    def _fetch_events(self) -> List[Dict]:
        """Fetch events from Apple Calendar using EventKit."""
        if not self._event_store:
            return []
        
        try:
            # Get all calendars
            calendars = self._event_store.calendarsForEntityType_(EKEntityTypeEvent)
            
            # Create a predicate for events from now to 90 days in the future
            now = datetime.now()
            start_date = now
            end_date = now + timedelta(days=90)
            
            # Convert to NSDate
            from Foundation import NSDate
            start_nsdate = NSDate.dateWithTimeIntervalSince1970_(start_date.timestamp())
            end_nsdate = NSDate.dateWithTimeIntervalSince1970_(end_date.timestamp())
            
            # Create predicate
            predicate = self._event_store.predicateForEventsWithStartDate_endDate_calendars_(
                start_nsdate,
                end_nsdate,
                calendars
            )
            
            # Fetch events
            ek_events = self._event_store.eventsMatchingPredicate_(predicate)
            
            events = []
            for ek_event in ek_events:
                # Extract event data
                event_id = ek_event.eventIdentifier()
                title = ek_event.title() or "(No title)"
                
                # Get dates
                start_date_obj = ek_event.startDate()
                end_date_obj = ek_event.endDate()
                
                start_iso = None
                end_iso = None
                if start_date_obj:
                    start_iso = datetime.fromtimestamp(start_date_obj.timeIntervalSince1970()).isoformat()
                if end_date_obj:
                    end_iso = datetime.fromtimestamp(end_date_obj.timeIntervalSince1970()).isoformat()
                
                # Get calendar name
                calendar = ek_event.calendar()
                calendar_name = calendar.title() if calendar else None
                
                # Get other properties
                location = ek_event.location()
                notes = ek_event.notes()
                url = ek_event.URL()
                url_str = url.absoluteString() if url else None
                
                # Get attendees
                attendees = []
                if ek_event.attendees():
                    for attendee in ek_event.attendees():
                        if attendee:
                            attendee_name = attendee.name() or ""
                            attendee_email = attendee.url().resourceSpecifier() if attendee.url() else ""
                            attendees.append({
                                "name": attendee_name,
                                "email": attendee_email
                            })
                
                events.append({
                    "id": event_id,
                    "title": title,
                    "start": start_iso,
                    "end": end_iso,
                    "location": location or "",
                    "notes": notes or "",
                    "calendar": calendar_name or "",
                    "all_day": ek_event.isAllDay(),
                    "attendees": attendees,
                    "url": url_str or "",
                })
            
            return events
            
        except Exception as e:
            # Log error but return empty list
            if hasattr(self, 'logger'):
                self.logger.exception("Failed to fetch Apple Calendar events")
            error_msg = str(e)
            self.update_status(False, f"Failed to fetch events: {error_msg[:100]}")
            return []

