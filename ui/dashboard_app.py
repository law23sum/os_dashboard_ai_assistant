"""Dashboard App - File containing the UI framework setup (Flask routes, Streamlit layout)."""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
from pathlib import Path


class DashboardApp:
    """Flask-based dashboard application."""

    def __init__(self, dashboard_engine=None, port: int = 8080):
        self.app = Flask(__name__,
                        template_folder=str(Path(__file__).parent),
                        static_folder=str(Path(__file__).parent / "assets"))
        self.dashboard_engine = dashboard_engine
        self.port = port
        self.setup_routes()

    def setup_routes(self):
        """Set up Flask routes."""

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/dashboard-data')
        def get_dashboard_data():
            if self.dashboard_engine:
                data = self.dashboard_engine.get_dashboard_state()
                return jsonify(data.get('display_model', {}))
            return jsonify({"error": "Dashboard engine not available"})

        @self.app.route('/api/refresh')
        def refresh_data():
            if self.dashboard_engine:
                # In a real implementation, this would trigger data refresh
                # For now, return current data
                data = self.dashboard_engine.get_dashboard_state()
                return jsonify({
                    "success": True,
                    "data": data.get('display_model', {})
                })
            return jsonify({"success": False, "error": "Dashboard engine not available"})

        @self.app.route('/api/onenote/add-link', methods=['POST'])
        def add_onenote_link():
            if not self.dashboard_engine:
                return jsonify({"success": False, "error": "Dashboard engine not available"})

            data = request.get_json()
            name = data.get('name')
            url = data.get('url')

            if not name or not url:
                return jsonify({"success": False, "error": "Name and URL are required"})

            success = self.dashboard_engine.add_onenote_link(name, url)
            if success:
                # Refresh the dashboard data
                dashboard_data = self.dashboard_engine.get_dashboard_state()
                return jsonify({
                    "success": True,
                    "data": dashboard_data.get('display_model', {})
                })
            return jsonify({"success": False, "error": "Failed to add OneNote link"})

        @self.app.route('/api/onenote/links')
        def get_onenote_links():
            if not self.dashboard_engine:
                return jsonify({"success": False, "error": "Dashboard engine not available"})

            links = self.dashboard_engine.get_onenote_links()
            return jsonify({"success": True, "links": links})

    def run(self, debug: bool = False):
        """Run the Flask application."""
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)


def run_ui(dashboard_engine=None, port: int = 8080):
    """Run the dashboard UI."""
    app = DashboardApp(dashboard_engine, port)
    print(f"Starting dashboard on http://localhost:{port}")
    app.run(debug=True)


# Alternative Streamlit implementation (commented out)
"""
import streamlit as st

def run_streamlit_dashboard(dashboard_engine):
    st.title("OS Dashboard AI Assistant")

    if dashboard_engine:
        data = dashboard_engine.get_dashboard_state()
        display_model = data.get('display_model', {})

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Today's Events", display_model.get('summary', {}).get('todays_events_count', 0))
        with col2:
            st.metric("Recent Emails", display_model.get('summary', {}).get('recent_emails_count', 0))
        with col3:
            st.metric("Recent Documents", display_model.get('summary', {}).get('recent_docs_count', 0))

        # Events
        st.subheader("Today's Events")
        events = display_model.get('todays_events', [])
        if events:
            for event in events:
                st.write(f"• {event.get('title', 'Untitled')} at {event.get('start_time', '')}")
        else:
            st.write("No events today")

        # Recent emails
        st.subheader("Recent Emails")
        emails = display_model.get('recent_emails', [])
        if emails:
            for email in emails:
                st.write(f"• {email.get('subject', 'No subject')} from {email.get('sender', 'Unknown')}")
        else:
            st.write("No recent emails")

if __name__ == "__main__":
    run_streamlit_dashboard(None)
"""
