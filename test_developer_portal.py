#!/usr/bin/env python3
"""
Test script for the Developer Portal System
"""

import asyncio
import sys
import os

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from assistant_core.developer_portal import DeveloperPortalSystem

async def test_developer_portal():
    """Test the developer portal system functionality"""

    print("🔧 Initializing Developer Portal System...")

    # Initialize the portal
    portal = DeveloperPortalSystem()
    await portal.initialize()

    print("✅ Developer Portal System initialized")

    # Test search functionality
    print("\n🔍 Testing search functionality...")
    search_results = await portal.search_documentation("authentication")
    print(f"Search results for 'authentication': {len(search_results)} found")

    for result in search_results[:3]:  # Show first 3 results
        print(f"  - {result['title']} (score: {result['score']})")

    # Test OpenAPI generation
    print("\n📋 Testing OpenAPI specification generation...")
    openapi_spec = await portal.generate_openapi_spec()
    print(f"OpenAPI spec generated with {len(openapi_spec.get('paths', {}))} paths")

    # Test code examples retrieval
    print("\n💻 Testing code examples retrieval...")
    examples = await portal.get_code_examples_by_category()
    print(f"Total code examples: {len(examples)}")

    for example in examples[:2]:  # Show first 2 examples
        print(f"  - {example['title']} ({example['difficulty']}) - {len(example['languages'])} languages")

    # Test analytics
    print("\n📊 Testing analytics generation...")
    analytics = await portal.get_analytics_report(7)
    print(f"Analytics report generated:")
    print(f"  - Total page views: {analytics['total_page_views']}")
    print(f"  - Total searches: {analytics['total_searches']}")
    print(f"  - Documentation pages: {analytics['documentation_stats']['total_pages']}")

    # Test dashboard data
    print("\n📈 Testing dashboard data generation...")
    dashboard = await portal.get_portal_dashboard_data()
    print(f"Dashboard data generated:")
    print(f"  - Documentation: {dashboard['documentation']}")
    print(f"  - API endpoints: {dashboard['api_documentation']['total_endpoints']}")
    print(f"  - Code examples: {dashboard['code_examples']['total_examples']}")

    # Test HTML generation
    print("\n🌐 Testing HTML generation...")
    homepage_html = await portal.generate_portal_html()
    print(f"Homepage HTML generated: {len(homepage_html)} characters")

    doc_page_html = await portal.generate_portal_html("getting-started")
    if "Getting Started" in doc_page_html:
        print("Documentation page HTML generated successfully")
    else:
        print("Documentation page HTML generation failed")

    # Test creating new content
    print("\n📝 Testing content creation...")
    new_page_id = await portal.create_documentation_page({
        "title": "Test API Guide",
        "content": "# Test API Guide\n\nThis is a test documentation page.",
        "type": "guide",
        "status": "published",
        "author": "Test System",
        "tags": ["test", "api"]
    })
    print(f"New documentation page created with ID: {new_page_id}")

    # Test support ticket creation
    print("\n🎫 Testing support ticket creation...")
    ticket_id = await portal.create_support_ticket({
        "developer_id": "test-developer-123",
        "type": "technical",
        "title": "Test Support Ticket",
        "description": "This is a test support ticket for the developer portal.",
        "priority": "medium"
    })
    print(f"Support ticket created with ID: {ticket_id}")

    # Test feedback recording
    print("\n💬 Testing feedback recording...")
    await portal.record_feedback(new_page_id, {
        "rating": 5,
        "comment": "Great documentation!",
        "helpful": True,
        "user_id": "test-user"
    })
    print("Feedback recorded successfully")

    # Shutdown
    await portal.shutdown()
    print("\n🛑 Developer Portal System shutdown complete")

    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_developer_portal())
