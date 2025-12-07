#!/usr/bin/env python3
"""Script to add OneNote shared links to the dashboard."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from assistant_core.dashboard_engine import DashboardEngine

def add_onenote_link():
    """Add the OneNote link provided by the user."""
    onenote_url = "https://1drv.ms/f/c/1A669C62CAEE5CBC/AiNO-BB0GnZOm1LO1cVGZkI?e=BnWbjs"
    link_name = "OS Dashboard OneNote"

    dashboard_engine = DashboardEngine()

    print(f"Adding OneNote link: {link_name}")
    print(f"URL: {onenote_url}")

    success = dashboard_engine.add_onenote_link(link_name, onenote_url)

    if success:
        print("✅ OneNote link added successfully!")
        print("\nLink details:")
        links = dashboard_engine.get_onenote_links()
        if link_name in links:
            link_data = links[link_name]
            print(f"  Name: {link_name}")
            print(f"  URL: {link_data['url']}")
            print(f"  Added: {link_data['added_at']}")
    else:
        print("❌ Failed to add OneNote link")

    # Test link accessibility
    print("\nTesting link accessibility...")
    link_status = dashboard_engine.refresh_onenote_links()
    for status in link_status:
        if status['name'] == link_name:
            print(f"Status: {status['status']}")
            if status.get('error'):
                print(f"Error: {status['error']}")
            break

if __name__ == "__main__":
    add_onenote_link()
