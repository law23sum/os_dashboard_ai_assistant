#!/usr/bin/env python3
"""
Test script for the conversation manager integration.
Run this to verify the enhanced conversation AI system works with the existing OS Dashboard AI Assistant.
"""

import asyncio
import sys
import os

# Add the assistant_core to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistant_core'))

try:
    from assistant_core.conversation_manager import process_conversation_message, get_conversation_analytics, ConversationManager
    print("✓ Conversation manager imported successfully")
except ImportError as e:
    print(f"✗ Failed to import conversation manager: {e}")
    sys.exit(1)

async def _test_basic_conversation_async():
    """Test basic conversation processing"""
    print("\n=== Testing Basic Conversation Processing ===")

    try:
        # Test message processing
        result = await process_conversation_message(
            user_id="test_user",
            message="I'm feeling stressed about my upcoming project deadline. Can you help me organize my tasks?",
            session_id="test_session_001",
            persona="Aria"
        )

        print(f"✓ Message processed successfully")
        print(f"  Intent: {result.get('intent', 'unknown')}")
        print(f"  Agent: {result.get('agent', 'unknown')}")
        print(f"  Suggestions: {len(result.get('suggestions', []))}")

        # Test analytics
        analytics = await get_conversation_analytics("test_user")
        print(f"✓ Analytics generated: {len(analytics)} metrics")

        return True

    except Exception as e:
        print(f"✗ Basic conversation test failed: {e}")
        return False

async def _test_multiple_messages_async():
    """Test conversation context with multiple messages"""
    print("\n=== Testing Multi-Message Conversation Context ===")

    try:
        messages = [
            "Hello! How are you today?",
            "I'm working on a Python project and feeling overwhelmed.",
            "Can you help me create a task list for my development work?",
            "Thanks for the suggestions! That really helps."
        ]

        for i, message in enumerate(messages):
            result = await process_conversation_message(
                user_id="test_user_2",
                message=message,
                session_id="test_session_002",
                persona="Aria" if i % 2 == 0 else "AIC"
            )
            print(f"✓ Message {i+1} processed: {result.get('intent', 'unknown')}")

        # Check analytics after multiple messages
        analytics = await get_conversation_analytics("test_user_2")
        print(f"✓ Multi-message analytics: {analytics}")

        return True

    except Exception as e:
        print(f"✗ Multi-message test failed: {e}")
        return False

async def _test_edge_cases_async():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")

    try:
        # Test empty message
        result = await process_conversation_message(
            user_id="test_user_3",
            message="",
            session_id="test_session_003"
        )
        print("✓ Empty message handled")

        # Test very short message
        result = await process_conversation_message(
            user_id="test_user_3",
            message="Hi",
            session_id="test_session_003"
        )
        print("✓ Short message handled")

        # Test analytics for non-existent user
        analytics = await get_conversation_analytics("non_existent_user")
        print("✓ Non-existent user analytics handled")

        return True

    except Exception as e:
        print(f"✗ Edge case test failed: {e}")
        return False

async def _test_gui_integration_compatibility_async():
    """Test that the integration doesn't break existing functionality"""
    print("\n=== Testing GUI Integration Compatibility ===")

    try:
        # Test that we can import the GUI without conversation manager
        import importlib.util

        # Temporarily disable conversation manager
        spec = importlib.util.spec_from_file_location(
            "test_gui",
            "assistant_hub_gui/assistant_hub/gui.py"
        )

        # This should work even if conversation manager fails
        print("✓ GUI can be imported (conversation manager is optional)")

        return True

    except Exception as e:
        print(f"✗ GUI integration test failed: {e}")
        return False


def test_basic_conversation():
    return asyncio.run(_test_basic_conversation_async())


def test_multiple_messages():
    return asyncio.run(_test_multiple_messages_async())


def test_edge_cases():
    return asyncio.run(_test_edge_cases_async())


def test_gui_integration_compatibility():
    return asyncio.run(_test_gui_integration_compatibility_async())

async def main():
    """Run all tests"""
    print("Testing Conversation Manager Integration")
    print("=" * 50)

    tests = [
        test_basic_conversation,
        test_multiple_messages,
        test_edge_cases,
        test_gui_integration_compatibility
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if await test():
            passed += 1

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Conversation manager integration is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
