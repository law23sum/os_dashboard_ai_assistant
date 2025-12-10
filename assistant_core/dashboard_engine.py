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
        self.plugin_marketplace = None
        self.security_framework = None
        self.dashboard_state = {
            "last_updated": None,
            "data_sources": {},
            "display_model": {},
        }

    def update_dashboard_data(
        self, sources_data: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
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

    def _prepare_display_model(
        self, aggregated_data: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """Prepare data for dashboard display."""
        # Today's events
        today = datetime.now().date()
        todays_events = [
            event
            for event in aggregated_data["calendar_events"]
            if event.get("start_time") and event["start_time"].date() == today
        ]

        # Recent emails (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_emails = [
            email
            for email in aggregated_data["emails"]
            if email.get("timestamp") and email["timestamp"] > yesterday
        ]

        # Recent documents (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_docs = [
            doc
            for doc in aggregated_data["documents"]
            if doc.get("modified_time") and doc["modified_time"] > week_ago
        ]

        # OneNote data
        onenote_links = self.onenote_viewer.get_all_link_statuses()

        # Security data (simplified for now)
        security_summary = {
            "security_score": 85.0,  # Placeholder - would come from security framework
            "active_incidents": 0,
            "compliance_score": 92.0,
        }

        return {
            "summary": {
                "total_emails": len(aggregated_data["emails"]),
                "total_events": len(aggregated_data["calendar_events"]),
                "total_documents": len(aggregated_data["documents"]),
                "todays_events_count": len(todays_events),
                "recent_emails_count": len(recent_emails),
                "recent_docs_count": len(recent_docs),
                "onenote_links_count": len(onenote_links),
                "onenote_accessible_count": len(
                    [l for l in onenote_links if l.get("status") == "accessible"]
                ),
                "security_score": security_summary["security_score"],
                "active_security_incidents": security_summary["active_incidents"],
                "compliance_score": security_summary["compliance_score"],
            },
            "todays_events": todays_events[:10],  # Show top 10
            "recent_emails": recent_emails[:5],  # Show top 5
            "recent_documents": recent_docs[:10],  # Show top 10
            "onenote_links": onenote_links[:5],  # Show top 5 OneNote links
            "security_status": security_summary,
            "last_updated": datetime.now().isoformat(),
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

    # Plugin marketplace methods
    async def initialize_plugin_marketplace(self):
        """Initialize the plugin marketplace."""
        try:
            from .plugin_marketplace import PluginMarketplace

            if not self.plugin_marketplace:
                self.plugin_marketplace = PluginMarketplace()
            await self.plugin_marketplace.initialize()
        except ImportError as e:
            print(f"Plugin marketplace not available: {e}")
            self.plugin_marketplace = None

    async def search_plugins(self, **kwargs):
        """Search plugins in marketplace."""
        if not self.plugin_marketplace:
            return {"error": "Plugin marketplace not available"}
        return await self.plugin_marketplace.search_plugins(**kwargs)

    async def get_plugin_details(self, plugin_id: str):
        """Get detailed plugin information."""
        if not self.plugin_marketplace:
            return {"error": "Plugin marketplace not available"}
        return await self.plugin_marketplace.get_plugin_details(plugin_id)

    async def install_plugin(self, plugin_id: str, version: str = None):
        """Install a plugin from marketplace."""
        if not self.plugin_marketplace:
            return {"status": "error", "message": "Plugin marketplace not available"}
        return await self.plugin_marketplace.install_plugin(plugin_id, version)

    async def uninstall_plugin(self, plugin_id: str):
        """Uninstall a plugin."""
        if not self.plugin_marketplace:
            return {"status": "error", "message": "Plugin marketplace not available"}
        return await self.plugin_marketplace.uninstall_plugin(plugin_id)

    async def get_plugin_marketplace_stats(self):
        """Get marketplace statistics."""
        if not self.plugin_marketplace:
            return {"error": "Plugin marketplace not available"}
        return await self.plugin_marketplace.get_marketplace_stats()

    async def execute_plugin(self, plugin_id: str, method: str, *args, **kwargs):
        """Execute a plugin method."""
        if not self.plugin_marketplace:
            raise Exception("Plugin marketplace not available")
        return await self.plugin_marketplace.execute_plugin(
            plugin_id, method, *args, **kwargs
        )

    # Security framework methods
    async def initialize_security_framework(self):
        """Initialize the security framework."""
        try:
            from .security_framework import EnterpriseSecurityFramework

            if not self.security_framework:
                self.security_framework = EnterpriseSecurityFramework()
            await self.security_framework.initialize()
        except ImportError as e:
            print(f"Security framework not available: {e}")
            self.security_framework = None

    async def get_security_dashboard(self):
        """Get security monitoring data."""
        if not self.security_framework:
            return {"error": "Security framework not available"}
        return await self.security_framework.generate_security_dashboard()

    async def detect_security_threats(self, event_data: Dict[str, Any]):
        """Detect security threats from event data."""
        if not self.security_framework:
            return []
        return await self.security_framework.detect_threats(event_data)

    async def run_compliance_assessment(self, framework: str):
        """Run compliance assessment for a framework."""
        if not self.security_framework:
            return {"error": "Security framework not available"}
        try:
            from .security_framework import ComplianceFramework

            framework_enum = ComplianceFramework(framework)
            return await self.security_framework.run_compliance_assessment(
                framework_enum
            )
        except Exception as e:
            return {"error": str(e)}

    async def classify_and_protect_data(self, data: Dict[str, Any], context: str = ""):
        """Classify and apply data protection."""
        if not self.security_framework:
            return {"error": "Security framework not available"}
        try:
            classification = await self.security_framework.classify_data(data, context)
            protected_data = await self.security_framework.apply_data_protection(
                data, classification
            )
            return {
                "classification": classification.value,
                "protected_data": protected_data,
            }
        except Exception as e:
            return {"error": str(e)}
