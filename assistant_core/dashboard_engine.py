"""Dashboard Engine - Manages the state of the dashboard, decides which data to fetch, and prepares the final display model."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .data_aggregator import DataAggregator
from .onenote_viewer import OneNoteViewer


class DashboardEngine:
    """Manages dashboard state and data preparation."""

    def __init__(self):
        self.data_aggregator = DataAggregator()
        self.onenote_viewer = OneNoteViewer()
        self.dashboard_state = {
            "last_updated": None,
            "data_sources": {},
            "display_model": {}
        }

    def update_dashboard_data(self, sources_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Update dashboard with new data from all sources."""
        # Aggregate and normalize data
        aggregated_data = self.data_aggregator.aggregate_all_sources(sources_data)

        # Update dashboard state
        self.dashboard_state["last_updated"] = datetime.now()
        self.dashboard_state["data_sources"] = sources_data

        # Prepare display model
        display_model = self._prepare_display_model(aggregated_data)

        self.dashboard_state["display_model"] = display_model
        return display_model

    def _prepare_display_model(self, aggregated_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Prepare data for dashboard display."""
        # Today's events
        today = datetime.now().date()
        todays_events = [
            event for event in aggregated_data["calendar_events"]
            if event.get("start_time") and event["start_time"].date() == today
        ]

        # Recent emails (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_emails = [
            email for email in aggregated_data["emails"]
            if email.get("timestamp") and email["timestamp"] > yesterday
        ]

        # Recent documents (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_docs = [
            doc for doc in aggregated_data["documents"]
            if doc.get("modified_time") and doc["modified_time"] > week_ago
        ]

        # OneNote data
        onenote_links = self.onenote_viewer.get_all_link_statuses()

        return {
            "summary": {
                "total_emails": len(aggregated_data["emails"]),
                "total_events": len(aggregated_data["calendar_events"]),
                "total_documents": len(aggregated_data["documents"]),
                "todays_events_count": len(todays_events),
                "recent_emails_count": len(recent_emails),
                "recent_docs_count": len(recent_docs),
                "onenote_links_count": len(onenote_links),
                "onenote_accessible_count": len([l for l in onenote_links if l.get('status') == 'accessible'])
            },
            "todays_events": todays_events[:10],  # Show top 10
            "recent_emails": recent_emails[:5],    # Show top 5
            "recent_documents": recent_docs[:10], # Show top 10
            "onenote_links": onenote_links[:5],   # Show top 5 OneNote links
            "last_updated": datetime.now().isoformat()
        }

    def get_dashboard_state(self) -> Dict[str, Any]:
        """Get current dashboard state."""
        return self.dashboard_state

    def should_refresh_data(self, max_age_minutes: int = 5) -> bool:
        """Check if data should be refreshed based on age."""
        if not self.dashboard_state["last_updated"]:
            return True

        age = datetime.now() - self.dashboard_state["last_updated"]
        return age.total_seconds() > (max_age_minutes * 60)

    def add_onenote_link(self, name: str, url: str) -> bool:
        """Add a OneNote shared link to the dashboard."""
        return self.onenote_viewer.add_shared_link(name, url)

    def get_onenote_links(self) -> Dict[str, Dict]:
        """Get all OneNote shared links."""
        return self.onenote_viewer.get_shared_links()

    def refresh_onenote_links(self) -> List[Dict[str, Any]]:
        """Refresh status of all OneNote links."""
        return self.onenote_viewer.get_all_link_statuses()
