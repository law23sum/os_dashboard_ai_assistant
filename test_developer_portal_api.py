#!/usr/bin/env python3
"""
Test script for the Developer Portal API endpoints
"""

import asyncio
import sys
import os
import time
import threading
import requests
from pathlib import Path

from assistant_hub.config import DB_PATH, ensure_data_directories

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from assistant_core.core.api_server import start_api_server

def test_developer_portal_api():
    """Test the developer portal API endpoints"""

    # Start API server in background thread
    ensure_data_directories()
    db_path = Path(DB_PATH)
    if not db_path.exists():
        print("❌ Database not found. Please run the main application first.")
        return

    print("🚀 Starting API server...")
    server = start_api_server(db_path, host="127.0.0.1", port=8070)

    # Give server time to start
    time.sleep(2)

    try:
        base_url = "http://127.0.0.1:8070"

        print("🔍 Testing developer portal endpoints...")

        # Test dashboard endpoint
        print("\n📊 Testing /developer-portal/dashboard...")
        response = requests.get(f"{base_url}/developer-portal/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            print("✅ Dashboard data retrieved:")
            print(f"   - Documentation pages: {dashboard['documentation']['total_pages']}")
            print(f"   - API endpoints: {dashboard['api_documentation']['total_endpoints']}")
            print(f"   - Code examples: {dashboard['code_examples']['total_examples']}")
        else:
            print(f"❌ Dashboard endpoint failed: {response.status_code}")

        # Test documentation tree endpoint
        print("\n📚 Testing /developer-portal/docs...")
        response = requests.get(f"{base_url}/developer-portal/docs")
        if response.status_code == 200:
            docs = response.json()
            print("✅ Documentation tree retrieved")
            print(f"   - Tree contains: {list(docs['documentation_tree'].keys())}")
        else:
            print(f"❌ Docs endpoint failed: {response.status_code}")

        # Test search endpoint
        print("\n🔍 Testing /developer-portal/search...")
        response = requests.get(f"{base_url}/developer-portal/search?q=authentication")
        if response.status_code == 200:
            search_results = response.json()
            print("✅ Search completed:")
            print(f"   - Query: {search_results['query']}")
            print(f"   - Results found: {len(search_results['results'])}")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")

        # Test OpenAPI spec endpoint
        print("\n📋 Testing /developer-portal/api-spec...")
        response = requests.get(f"{base_url}/developer-portal/api-spec")
        if response.status_code == 200:
            spec = response.json()
            print("✅ OpenAPI spec retrieved:")
            print(f"   - Title: {spec.get('info', {}).get('title', 'N/A')}")
            print(f"   - Version: {spec.get('info', {}).get('version', 'N/A')}")
            print(f"   - Paths: {len(spec.get('paths', {}))}")
        else:
            print(f"❌ API spec endpoint failed: {response.status_code}")

        # Test code examples endpoint
        print("\n💻 Testing /developer-portal/examples...")
        response = requests.get(f"{base_url}/developer-portal/examples")
        if response.status_code == 200:
            examples = response.json()
            print("✅ Code examples retrieved:")
            print(f"   - Examples count: {len(examples['examples'])}")
        else:
            print(f"❌ Examples endpoint failed: {response.status_code}")

        # Test analytics endpoint
        print("\n📈 Testing /developer-portal/analytics...")
        response = requests.get(f"{base_url}/developer-portal/analytics?days=7")
        if response.status_code == 200:
            analytics = response.json()
            print("✅ Analytics report retrieved:")
            print(f"   - Period: {analytics['period_days']} days")
            print(f"   - Total views: {analytics['total_page_views']}")
            print(f"   - Total searches: {analytics['total_searches']}")
        else:
            print(f"❌ Analytics endpoint failed: {response.status_code}")

        # Test HTML generation
        print("\n🌐 Testing HTML portal page...")
        response = requests.get(f"{base_url}/developer-portal")
        if response.status_code == 200:
            html_content = response.text
            print("✅ Portal homepage HTML generated:")
            print(f"   - HTML length: {len(html_content)} characters")
            if "Dashboard AI Developer Portal" in html_content:
                print("   - Contains expected title ✓")
        else:
            print(f"❌ Portal HTML endpoint failed: {response.status_code}")

        # Test POST endpoints
        print("\n📝 Testing POST endpoints...")

        # Create a test documentation page
        test_page = {
            "title": "API Test Page",
            "content": "# API Test Page\n\nThis is a test page for API testing.",
            "type": "guide",
            "status": "draft",
            "author": "API Test",
            "tags": ["test", "api"]
        }

        response = requests.post(f"{base_url}/developer-portal/docs", json=test_page)
        if response.status_code == 200:
            result = response.json()
            print("✅ Documentation page created:")
            print(f"   - Page ID: {result['page_id']}")
        else:
            print(f"❌ Create page failed: {response.status_code}")

        # Create a test support ticket
        test_ticket = {
            "developer_id": "test-developer-api",
            "type": "technical",
            "title": "API Test Ticket",
            "description": "This is a test support ticket created via API.",
            "priority": "low"
        }

        response = requests.post(f"{base_url}/developer-portal/support", json=test_ticket)
        if response.status_code == 200:
            result = response.json()
            print("✅ Support ticket created:")
            print(f"   - Ticket ID: {result['ticket_id']}")
        else:
            print(f"❌ Create ticket failed: {response.status_code}")

        print("\n🎉 All API endpoint tests completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Shutdown server
        print("\n🛑 Shutting down API server...")
        server.shutdown()

if __name__ == "__main__":
    test_developer_portal_api()
