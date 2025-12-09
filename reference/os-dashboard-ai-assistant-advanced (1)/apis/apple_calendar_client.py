"""
Apple Calendar (CalDAV) Client for calendar integration
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

try:
    import caldav
    from caldav import DAVClient
    CALDAV_AVAILABLE = True
except ImportError:
    CALDAV_AVAILABLE = False

from config import get_config
from logger import setup_logger

class AppleCalendarClient:
    """Apple Calendar client using CalDAV protocol"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger("AppleCalendarClient")
        self.client = None
        self.principal = None
        self.calendars = {}
        
    async def initialize(self) -> bool:
        """Initialize Apple Calendar client"""
        try:
            if not CALDAV_AVAILABLE:
                self.logger.warning("CalDAV library not available. Install with: pip install caldav")
                return False
            
            # Create CalDAV client
            self.client = DAVClient(
                url=self.config.caldav_url,
                username=self.config.caldav_username,
                password=self.config.caldav_password
            )
            
            # Get principal
            self.principal = self.client.principal()
            
            # Load calendars
            await self._load_calendars()
            
            self.logger.info("Apple Calendar client initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Apple Calendar client: {e}")
            raise
    
    async def _load_calendars(self):
        """Load available calendars"""
        try:
            calendar_list = self.principal.calendars()
            
            for calendar in calendar_list:
                self.calendars[calendar.name] = calendar
                
        except Exception as e:
            self.logger.error(f"Failed to load calendars: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if CalDAV server is accessible"""
        try:
            if not CALDAV_AVAILABLE:
                return False
            
            # Try to get principal info
            self.principal.get_properties([caldav.dav.DisplayName()])
            return True
            
        except Exception as e:
            self.logger.error(f"Apple Calendar health check failed: {e}")
            return False
    
    async def get_calendars(self) -> List[Dict[str, Any]]:
        """Get list of available calendars"""
        try:
            calendars_info = []
            
            for name, calendar in self.calendars.items():
                try:
                    props = calendar.get_properties([
                        caldav.dav.DisplayName(),
                        caldav.cdav.CalendarDescription()
                    ])
                    
                    calendars_info.append({
                        'name': name,
                        'display_name': props.get(caldav.dav.DisplayName.tag, name),
                        'description': props.get(caldav.cdav.CalendarDescription.tag, ''),
                        'url': str(calendar.url)
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to get properties for calendar {name}: {e}")
                    calendars_info.append({
                        'name': name,
                        'display_name': name,
                        'description': '',
                        'url': str(calendar.url)
                    })
            
            return calendars_info
            
        except Exception as e:
            self.logger.error(f"Failed to get calendars: {e}")
            raise
    
    async def create_event(self, title: str, start_time: datetime, end_time: datetime,
                          description: str = "", calendar_name: str = None,
                          location: str = "", attendees: List[str] = None) -> Dict[str, Any]:
        """Create a calendar event"""
        try:
            # Select calendar
            if calendar_name and calendar_name in self.calendars:
                calendar = self.calendars[calendar_name]
            else:
                # Use first available calendar
                calendar = list(self.calendars.values())[0]
            
            # Generate unique ID
            event_id = str(uuid.uuid4())
            
            # Create iCalendar event
            ical_event = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OS Dashboard AI Assistant//EN
BEGIN:VEVENT
UID:{event_id}
DTSTART:{start_time.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end_time.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:{title}
DESCRIPTION:{description}
LOCATION:{location}
CREATED:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
LAST-MODIFIED:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
SEQUENCE:0
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR"""
            
            # Add attendees if provided
            if attendees:
                attendee_lines = []
                for attendee in attendees:
                    attendee_lines.append(f"ATTENDEE:mailto:{attendee}")
                
                # Insert attendees before END:VEVENT
                ical_event = ical_event.replace("END:VEVENT", "\n".join(attendee_lines) + "\nEND:VEVENT")
            
            # Save event to calendar
            event = calendar.save_event(ical_event)
            
            return {
                'id': event_id,
                'title': title,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'description': description,
                'location': location,
                'calendar': calendar.name,
                'url': str(event.url) if hasattr(event, 'url') else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create event: {e}")
            raise
    
    async def get_events(self, calendar_name: str = None, start_date: datetime = None,
                        end_date: datetime = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get calendar events"""
        try:
            if not start_date:
                start_date = datetime.utcnow()
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            events = []
            
            # Select calendars to search
            calendars_to_search = []
            if calendar_name and calendar_name in self.calendars:
                calendars_to_search = [self.calendars[calendar_name]]
            else:
                calendars_to_search = list(self.calendars.values())
            
            for calendar in calendars_to_search:
                try:
                    # Search for events in date range
                    calendar_events = calendar.date_search(start_date, end_date)
                    
                    for event in calendar_events[:max_results]:
                        try:
                            # Parse event data
                            event_data = event.data
                            
                            # Extract basic information
                            event_info = {
                                'id': self._extract_field(event_data, 'UID'),
                                'title': self._extract_field(event_data, 'SUMMARY'),
                                'description': self._extract_field(event_data, 'DESCRIPTION'),
                                'location': self._extract_field(event_data, 'LOCATION'),
                                'start_time': self._parse_datetime(self._extract_field(event_data, 'DTSTART')),
                                'end_time': self._parse_datetime(self._extract_field(event_data, 'DTEND')),
                                'calendar': calendar.name,
                                'status': self._extract_field(event_data, 'STATUS'),
                                'url': str(event.url) if hasattr(event, 'url') else None
                            }
                            
                            events.append(event_info)
                            
                        except Exception as e:
                            self.logger.warning(f"Failed to parse event: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.warning(f"Failed to search calendar {calendar.name}: {e}")
                    continue
            
            return events[:max_results]
            
        except Exception as e:
            self.logger.error(f"Failed to get events: {e}")
            raise
    
    def _extract_field(self, ical_data: str, field_name: str) -> str:
        """Extract field value from iCalendar data"""
        try:
            lines = ical_data.split('\n')
            for line in lines:
                if line.startswith(f"{field_name}:"):
                    return line.split(':', 1)[1].strip()
                elif line.startswith(f"{field_name};"):
                    # Handle fields with parameters
                    return line.split(':', 1)[1].strip()
            return ""
        except Exception:
            return ""
    
    def _parse_datetime(self, dt_string: str) -> str:
        """Parse datetime string from iCalendar format"""
        try:
            if not dt_string:
                return ""
            
            # Remove timezone info for simplicity
            dt_string = dt_string.replace('Z', '').replace('T', '')
            
            if len(dt_string) >= 8:
                # Parse YYYYMMDDHHMMSS format
                year = int(dt_string[:4])
                month = int(dt_string[4:6])
                day = int(dt_string[6:8])
                
                if len(dt_string) >= 14:
                    hour = int(dt_string[8:10])
                    minute = int(dt_string[10:12])
                    second = int(dt_string[12:14])
                else:
                    hour = minute = second = 0
                
                dt = datetime(year, month, day, hour, minute, second)
                return dt.isoformat()
            
            return dt_string
            
        except Exception:
            return dt_string
    
    async def update_event(self, event_id: str, updates: Dict[str, Any],
                          calendar_name: str = None) -> Dict[str, Any]:
        """Update calendar event"""
        try:
            # This is a simplified implementation
            # In practice, you'd need to find the event, modify it, and save it back
            
            self.logger.warning("Event update functionality requires more complex CalDAV operations")
            
            return {
                'id': event_id,
                'status': 'update_pending',
                'message': 'Event update requires manual implementation'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update event: {e}")
            raise
    
    async def delete_event(self, event_id: str, calendar_name: str = None) -> bool:
        """Delete calendar event"""
        try:
            # This is a simplified implementation
            # In practice, you'd need to find the event and delete it
            
            self.logger.warning("Event deletion functionality requires more complex CalDAV operations")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete event: {e}")
            raise
    
    async def create_calendar(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new calendar"""
        try:
            # Create calendar
            calendar = self.principal.make_calendar(name=name)
            
            # Set description if provided
            if description:
                calendar.set_properties({caldav.cdav.CalendarDescription(): description})
            
            # Add to local cache
            self.calendars[name] = calendar
            
            return {
                'name': name,
                'description': description,
                'url': str(calendar.url),
                'status': 'created'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create calendar: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown Apple Calendar client"""
        self.calendars.clear()
        self.principal = None
        self.client = None
        self.logger.info("Apple Calendar client shutdown complete")