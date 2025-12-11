"""
Basic usage examples for OS Dashboard AI Assistant
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_manager import get_api_manager
from logger import setup_logger

async def basic_ai_chat():
    """Example: Basic AI chat functionality"""
    logger = setup_logger("BasicChat")
    
    api_manager = await get_api_manager()
    await api_manager.initialize()
    
    try:
        # Simple chat
        response = await api_manager.chat_completion(
            "What are 3 ways to improve productivity?"
        )
        logger.info(f"AI Response: {response}")
        
        # Chat with system prompt
        response = await api_manager.chat_completion(
            "Help me plan my day",
            system_prompt="You are a productivity expert who helps people organize their schedules."
        )
        logger.info(f"Productivity AI: {response}")
        
    except Exception as e:
        logger.error(f"AI chat failed: {e}")
    finally:
        await api_manager.shutdown()

async def document_creation():
    """Example: Create documents in different formats"""
    logger = setup_logger("DocumentCreation")
    
    api_manager = await get_api_manager()
    await api_manager.initialize()
    
    try:
        # Create Word document
        word_doc = await api_manager.create_document(
            title="Project Status Report",
            content="""
            # Project Status Report
            
            ## Overview
            This report provides an update on the current project status.
            
            ## Key Achievements
            - Completed API integrations
            - Implemented error handling
            - Created documentation
            
            ## Next Steps
            - User testing
            - Performance optimization
            - Deployment preparation
            """,
            doc_type="word"
        )
        logger.info(f"Created Word document: {word_doc}")
        
        # Create PowerPoint presentation
        ppt_doc = await api_manager.create_document(
            title="Quarterly Review",
            content="Q4 performance metrics and goals for next quarter",
            doc_type="powerpoint"
        )
        logger.info(f"Created PowerPoint: {ppt_doc}")
        
    except Exception as e:
        logger.error(f"Document creation failed: {e}")
    finally:
        await api_manager.shutdown()

async def email_and_calendar():
    """Example: Email and calendar management"""
    logger = setup_logger("EmailCalendar")
    
    api_manager = await get_api_manager()
    await api_manager.initialize()
    
    try:
        # Send email (replace with actual email)
        # await api_manager.send_email(
        #     to="colleague@example.com",
        #     subject="AI Assistant Test",
        #     body="This email was sent by the OS Dashboard AI Assistant!"
        # )
        # logger.info("Email sent successfully")
        
        # Create calendar event for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        event = await api_manager.create_calendar_event(
            title="AI Assistant Demo",
            start_time=start_time,
            end_time=end_time,
            description="Demonstration of the OS Dashboard AI Assistant capabilities",
            service="google"
        )
        logger.info(f"Created calendar event: {event}")
        
        # Get upcoming events
        if "google" in api_manager.clients:
            events = await api_manager.clients["google"].get_calendar_events(max_results=5)
            logger.info(f"Upcoming events: {len(events)}")
            for event in events[:3]:
                logger.info(f"  - {event['title']} at {event['start_time']}")
        
    except Exception as e:
        logger.error(f"Email/Calendar operations failed: {e}")
    finally:
        await api_manager.shutdown()

async def git_operations():
    """Example: Git and GitHub operations"""
    logger = setup_logger("GitOperations")
    
    api_manager = await get_api_manager()
    await api_manager.initialize()
    
    try:
        if "git" in api_manager.clients:
            # Get repositories
            repos = await api_manager.clients["git"].get_repositories()
            logger.info(f"Found {len(repos)} repositories")
            
            # Show first few repositories
            for repo in repos[:3]:
                logger.info(f"  - {repo['name']}: {repo['description']}")
            
            # Get issues from first repository (if any)
            if repos:
                issues = await api_manager.clients["git"].get_issues(
                    repo_name=repos[0]['full_name'],
                    state="open"
                )
                logger.info(f"Open issues in {repos[0]['name']}: {len(issues)}")
        
    except Exception as e:
        logger.error(f"Git operations failed: {e}")
    finally:
        await api_manager.shutdown()

async def comprehensive_workflow():
    """Example: Comprehensive workflow using multiple APIs"""
    logger = setup_logger("ComprehensiveWorkflow")
    
    api_manager = await get_api_manager()
    await api_manager.initialize()
    
    try:
        # Step 1: Get AI assistance for planning
        planning_response = await api_manager.chat_completion(
            "I need to create a project status report. What sections should I include?",
            system_prompt="You are a project management expert."
        )
        logger.info("AI Planning Assistance received")
        
        # Step 2: Create the document based on AI suggestions
        document = await api_manager.create_document(
            title="Weekly Project Status",
            content=f"""
            # Weekly Project Status Report
            
            Based on AI recommendations:
            {planning_response}
            
            ## Current Status
            All API integrations are complete and functional.
            
            ## Completed This Week
            - OpenAI integration
            - Microsoft Office APIs
            - Google Services integration
            - GitHub integration
            - Adobe PDF services
            
            ## Next Week Goals
            - User interface development
            - Performance testing
            - Documentation updates
            """,
            doc_type="word"
        )
        logger.info("Status report document created")
        
        # Step 3: Schedule follow-up meeting
        next_week = datetime.now() + timedelta(days=7)
        meeting_time = next_week.replace(hour=14, minute=0, second=0, microsecond=0)
        
        meeting = await api_manager.create_calendar_event(
            title="Project Status Review",
            start_time=meeting_time,
            end_time=meeting_time + timedelta(hours=1),
            description="Review weekly project status report and plan next steps"
        )
        logger.info("Follow-up meeting scheduled")
        
        # Step 4: Get final AI summary
        summary = await api_manager.chat_completion(
            "Summarize what we accomplished: created a status report and scheduled a follow-up meeting",
            system_prompt="Provide a brief, professional summary."
        )
        logger.info(f"Workflow Summary: {summary}")
        
    except Exception as e:
        logger.error(f"Comprehensive workflow failed: {e}")
    finally:
        await api_manager.shutdown()

async def main():
    """Run all examples"""
    logger = setup_logger("Examples")
    logger.info("Running OS Dashboard AI Assistant Examples...")
    
    examples = [
        ("Basic AI Chat", basic_ai_chat),
        ("Document Creation", document_creation),
        ("Email and Calendar", email_and_calendar),
        ("Git Operations", git_operations),
        ("Comprehensive Workflow", comprehensive_workflow),
    ]
    
    for name, example_func in examples:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {name}")
        logger.info(f"{'='*50}")
        
        try:
            await example_func()
            logger.info(f"✅ {name} completed successfully")
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")
        
        # Small delay between examples
        await asyncio.sleep(1)
    
    logger.info("\n🎉 All examples completed!")

if __name__ == "__main__":
    asyncio.run(main())