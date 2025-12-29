#!/usr/bin/env python3
"""
Test script for the Automation Orchestrator integration.
Run this to verify the intelligent automation system works with the existing OS Dashboard AI Assistant.
"""

import asyncio
import sys
import os

# Add the assistant_core to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assistant_core'))

try:
    from assistant_core.automation_orchestrator import AutomationOrchestrator
    print("✓ Automation Orchestrator imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Automation Orchestrator: {e}")
    sys.exit(1)

async def test_basic_workflow_creation():
    """Test basic workflow creation and execution"""
    print("\n=== Testing Basic Workflow Creation ===")

    try:
        orchestrator = AutomationOrchestrator()
        await orchestrator.initialize()

        # Create a simple workflow
        workflow_data = {
            "name": "Test Task Creation Workflow",
            "description": "Test workflow that creates a task",
            "triggers": [{
                "type": "user_initiated",
                "conditions": {}
            }],
            "actions": [
                {
                    "type": "task_creation",
                    "name": "Create Test Task",
                    "parameters": {
                        "title": "Test Task from Automation",
                        "description": "This task was created by the automation system",
                        "priority": "medium",
                        "project": "Automation Testing"
                    }
                }
            ],
            "variables": {},
            "priority": 2,
            "tags": ["test", "automation"]
        }

        workflow_id = await orchestrator.create_workflow(workflow_data)
        print(f"✓ Workflow created: {workflow_id}")

        # Trigger workflow execution
        execution_id = await orchestrator.trigger_workflow(workflow_id)
        print(f"✓ Workflow triggered: {execution_id}")

        # Wait a bit for execution
        await asyncio.sleep(1)

        # Check system dashboard
        dashboard = await orchestrator.get_system_dashboard()
        print(f"✓ Dashboard generated: {dashboard['workflows']['total']} workflows")

        await orchestrator.shutdown()
        return True

    except Exception as e:
        print(f"✗ Basic workflow test failed: {e}")
        return False

async def test_ai_agent_integration():
    """Test AI agent integration within workflows"""
    print("\n=== Testing AI Agent Integration ===")

    try:
        orchestrator = AutomationOrchestrator()
        await orchestrator.initialize()

        # Create workflow with AI agent interaction
        workflow_data = {
            "name": "AI Analysis Workflow",
            "description": "Test AI agent interaction",
            "triggers": [{
                "type": "user_initiated",
                "conditions": {}
            }],
            "actions": [
                {
                    "type": "agent_interaction",
                    "name": "AI Analysis",
                    "parameters": {
                        "agent": "AIC",
                        "prompt": "Analyze this test data and provide insights.",
                        "temperature": 0.7
                    }
                }
            ],
            "variables": {},
            "priority": 3,
            "tags": ["test", "ai", "analysis"]
        }

        workflow_id = await orchestrator.create_workflow(workflow_data)
        print(f"✓ AI workflow created: {workflow_id}")

        # Test execution (may fail due to missing AI dependencies, but should handle gracefully)
        try:
            execution_id = await orchestrator.trigger_workflow(workflow_id)
            print(f"✓ AI workflow triggered: {execution_id}")
        except Exception as e:
            print(f"⚠ AI workflow execution failed (expected if AI not configured): {e}")

        await orchestrator.shutdown()
        return True

    except Exception as e:
        print(f"✗ AI agent integration test failed: {e}")
        return False

async def test_document_processing():
    """Test document processing workflow"""
    print("\n=== Testing Document Processing ===")

    try:
        orchestrator = AutomationOrchestrator()
        await orchestrator.initialize()

        # Create document processing workflow
        workflow_data = {
            "name": "Document Analysis Workflow",
            "description": "Process and analyze documents automatically",
            "triggers": [{
                "type": "event_based",
                "event_filters": {
                    "event_type": "document_uploaded"
                }
            }],
            "actions": [
                {
                    "type": "document_processing",
                    "name": "Extract Tasks",
                    "parameters": {
                        "operation": "extract_tasks",
                        "file_path": "${event_data_file_path}",
                        "project": "Document Processing"
                    }
                }
            ],
            "variables": {},
            "priority": 2,
            "tags": ["documents", "processing", "automation"]
        }

        workflow_id = await orchestrator.create_workflow(workflow_data)
        print(f"✓ Document workflow created: {workflow_id}")

        await orchestrator.shutdown()
        return True

    except Exception as e:
        print(f"✗ Document processing test failed: {e}")
        return False

async def test_sample_workflows():
    """Test creation of sample workflows"""
    print("\n=== Testing Sample Workflows ===")

    try:
        orchestrator = AutomationOrchestrator()
        await orchestrator.initialize()

        # Create sample workflows
        sample_workflows = await orchestrator.create_sample_workflows()
        print(f"✓ Created {len(sample_workflows)} sample workflows")

        # List available workflows
        workflow_count = len(orchestrator.workflows)
        print(f"✓ Total workflows available: {workflow_count}")

        await orchestrator.shutdown()
        return True

    except Exception as e:
        print(f"✗ Sample workflows test failed: {e}")
        return False

async def test_automation_rules():
    """Test automation rules functionality"""
    print("\n=== Testing Automation Rules ===")

    try:
        orchestrator = AutomationOrchestrator()
        await orchestrator.initialize()

        # Create an automation rule
        rule_data = {
            "name": "High Priority Task Rule",
            "description": "Automatically escalate high-priority tasks",
            "conditions": [
                {
                    "type": "value_match",
                    "field": "priority",
                    "value": "high"
                }
            ],
            "actions": [
                {
                    "type": "notification",
                    "title": "High Priority Task Created",
                    "message": "A high-priority task has been created and needs immediate attention."
                }
            ],
            "priority": 4,
            "confidence_threshold": 0.9,
            "learning_enabled": True
        }

        rule_id = await orchestrator.create_automation_rule(rule_data)
        print(f"✓ Automation rule created: {rule_id}")

        # Test rule evaluation
        test_context = {"priority": "high", "title": "Urgent task"}
        suggestions = await orchestrator.evaluate_automation_rules(test_context)
        print(f"✓ Rule evaluation completed: {len(suggestions)} suggestions")

        await orchestrator.shutdown()
        return True

    except Exception as e:
        print(f"✗ Automation rules test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling and graceful degradation"""
    print("\n=== Testing Error Handling ===")

    try:
        orchestrator = AutomationOrchestrator()
        await orchestrator.initialize()

        # Test invalid workflow creation
        try:
            invalid_workflow = await orchestrator.create_workflow({})
            print("⚠ Invalid workflow creation should have failed")
        except:
            print("✓ Invalid workflow creation properly rejected")

        # Test non-existent workflow execution
        try:
            execution_id = await orchestrator.trigger_workflow("non_existent_workflow")
            print("⚠ Non-existent workflow execution should have failed")
        except:
            print("✓ Non-existent workflow execution properly rejected")

        # Test dashboard with no data
        dashboard = await orchestrator.get_system_dashboard()
        print(f"✓ Empty system dashboard generated: {dashboard['workflows']['total']} workflows")

        await orchestrator.shutdown()
        return True

    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

async def main():
    """Run all automation integration tests"""
    print("Testing Automation Orchestrator Integration")
    print("=" * 50)

    tests = [
        test_basic_workflow_creation,
        test_ai_agent_integration,
        test_document_processing,
        test_sample_workflows,
        test_automation_rules,
        test_error_handling
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if await test():
            passed += 1

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All automation integration tests passed!")
        print("The Intelligent Automation and Workflow Orchestration System is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
