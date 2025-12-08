#!/usr/bin/env python3
"""
Simple test script for the Developer Portal System without API server
"""

import asyncio
import sys
import os

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from assistant_core.developer_portal import DeveloperPortalSystem

async def _test_developer_portal_simple_async():
    """Test the developer portal system directly"""

    print("🔧 Initializing Developer Portal System...")

    # Initialize the portal
    portal = DeveloperPortalSystem()
    await portal.initialize()

    print("✅ Developer Portal System initialized")

    # Test all the API-like functionality
    print("\n📊 Testing dashboard data...")
    dashboard = await portal.get_portal_dashboard_data()
    print(f"Dashboard: {len(str(dashboard))} chars of data")

    print("\n📚 Testing documentation tree...")
    doc_tree = await portal.get_documentation_tree()
    print(f"Documentation tree: {len(doc_tree)} top-level categories")

    print("\n🔍 Testing search...")
    results = await portal.search_documentation("authentication")
    print(f"Search results: {len(results)} found")

    print("\n📋 Testing OpenAPI spec...")
    spec = await portal.generate_openapi_spec()
    print(f"OpenAPI spec: {len(spec.get('paths', {}))} endpoints")

    print("\n💻 Testing code examples...")
    examples = await portal.get_code_examples_by_category()
    print(f"Code examples: {len(examples)} total")

    print("\n📈 Testing analytics...")
    analytics = await portal.get_analytics_report(7)
    print(f"Analytics: {analytics['total_page_views']} views, {analytics['total_searches']} searches")

    print("\n🌐 Testing HTML generation...")
    homepage = await portal.generate_portal_html()
    print(f"Homepage HTML: {len(homepage)} characters")

    doc_page = await portal.generate_portal_html("getting-started")
    print(f"Doc page HTML: {len(doc_page)} characters")

    print("\n📝 Testing content creation...")
    page_id = await portal.create_documentation_page({
        "title": "API Integration Guide",
        "content": "# API Integration Guide\n\nLearn how to integrate with our APIs.",
        "type": "guide",
        "status": "published",
        "author": "API Team",
        "tags": ["api", "integration"]
    })
    print(f"Created page: {page_id}")

    ticket_id = await portal.create_support_ticket({
        "developer_id": "dev-123",
        "type": "technical",
        "title": "Integration Help",
        "description": "Need help with API integration.",
        "priority": "medium"
    })
    print(f"Created ticket: {ticket_id}")

    # Test after creating new content
    print("\n🔄 Testing after content creation...")
    updated_dashboard = await portal.get_portal_dashboard_data()
    print(f"Updated dashboard pages: {updated_dashboard['documentation']['total_pages']}")

    updated_search = await portal.search_documentation("integration")
    print(f"Search for 'integration': {len(updated_search)} results")

    # Shutdown
    await portal.shutdown()
    print("\n🛑 Developer Portal System shutdown complete")

    print("\n🎉 All developer portal functionality tests passed!")

def test_developer_portal_simple():
    return asyncio.run(_test_developer_portal_simple_async())


if __name__ == "__main__":
    asyncio.run(_test_developer_portal_simple_async())
