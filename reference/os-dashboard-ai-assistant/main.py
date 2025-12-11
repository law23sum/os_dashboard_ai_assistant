"""
Main application for OS Dashboard AI Assistant
Example usage of all API integrations
"""
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

from api_manager import APIManager, get_api_manager
from config import get_config, validate_config
from logger import setup_logger

async def main():
    """Main application entry point"""
    logger = setup_logger("MainApp")
    logger.info("Starting OS Dashboard AI Assistant...")
    
    try:
        # Get API manager
        api_manager = await get_api_manager()
        
        # Initialize all APIs
        initialization_results = await api_manager.initialize()
        
        # Check which APIs are available
        available_apis = [api for api, status in initialization_results.items() if status]
        logger.info(f"Available APIs: {available_apis}")
        
        if not available_apis:
            logger.error("No APIs available. Please check your configuration.")
            return
        
        # Run example operations
        await run_examples(api_manager, available_apis)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        # Cleanup
        if 'api_manager' in locals():
            await api_manager.shutdown()
        logger.info("Application shutdown complete")

async def run_examples(api_manager: APIManager, available_apis: list):
    """Run example operations for available APIs"""
    logger = setup_logger("Examples")
    
    # OpenAI Examples
    if "openai" in available_apis:
        logger.info("=== OpenAI Examples ===")
        try:
            # Chat completion
            response = await api_manager.chat_completion(
                "Hello! Can you help me organize my day?",
                system_prompt="You are a helpful AI assistant for productivity."
            )
            logger.info(f"ChatGPT Response: {response[:100]}...")
            
            # Generate embeddings
            embeddings = await api_manager.clients["openai"].generate_embeddings(
                ["Hello world", "AI assistant", "Productivity tools"]
            )
            logger.info(f"Generated {len(embeddings)} embeddings")
            
        except Exception as e:
            logger.error(f"OpenAI example failed: {e}")
    
    # Microsoft Office Examples
    if "microsoft" in available_apis:
        logger.info("=== Microsoft Office Examples ===")
        try:
            # Create Word document
            doc_result = await api_manager.create_document(
                title="Meeting Notes",
                content="Today's meeting covered project updates and next steps.",
                doc_type="word"
            )
            logger.info(f"Created document: {doc_result.get('name', 'Unknown')}")
            
            # List OneDrive files
            files = await api_manager.clients["microsoft"].list_files()
            logger.info(f"Found {len(files)} files in OneDrive")
            
            # Get OneNote notebooks
            notebooks = await api_manager.clients["microsoft"].get_onenote_notebooks()
            logger.info(f"Found {len(notebooks)} OneNote notebooks")
            
        except Exception as e:
            logger.error(f"Microsoft example failed: {e}")
    
    # Google Examples
    if "google" in available_apis:
        logger.info("=== Google APIs Examples ===")
        try:
            # Get recent emails
            emails = await api_manager.clients["google"].get_emails(
                query="is:unread",
                max_results=5
            )
            logger.info(f"Found {len(emails)} unread emails")
            
            # Get upcoming calendar events
            events = await api_manager.clients["google"].get_calendar_events(max_results=5)
            logger.info(f"Found {len(events)} upcoming events")
            
            # Create a test calendar event
            tomorrow = datetime.now() + timedelta(days=1)
            event_result = await api_manager.create_calendar_event(
                title="AI Assistant Demo",
                start_time=tomorrow.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=tomorrow.replace(hour=15, minute=0, second=0, microsecond=0),
                description="Demo of OS Dashboard AI Assistant",
                service="google"
            )
            logger.info(f"Created calendar event: {event_result.get('title', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Google example failed: {e}")
    
    # Git Examples
    if "git" in available_apis:
        logger.info("=== Git Examples ===")
        try:
            # Get repositories
            repos = await api_manager.clients["git"].get_repositories()
            logger.info(f"Found {len(repos)} repositories")
            
            # Get issues from first repo (if any)
            if repos:
                issues = await api_manager.clients["git"].get_issues(
                    repo_name=repos[0]['full_name'],
                    state="open"
                )
                logger.info(f"Found {len(issues)} open issues in {repos[0]['name']}")
            
        except Exception as e:
            logger.error(f"Git example failed: {e}")
    
    # Adobe Examples
    if "adobe" in available_apis:
        logger.info("=== Adobe Examples ===")
        try:
            # Get Creative Cloud assets (placeholder)
            assets = await api_manager.clients["adobe"].get_creative_cloud_assets()
            logger.info(f"Found {len(assets)} Creative Cloud assets")
            
        except Exception as e:
            logger.error(f"Adobe example failed: {e}")
    
    # Apple Calendar Examples
    if "apple_calendar" in available_apis:
        logger.info("=== Apple Calendar Examples ===")
        try:
            # Get calendars
            calendars = await api_manager.clients["apple_calendar"].get_calendars()
            logger.info(f"Found {len(calendars)} Apple calendars")
            
            # Get upcoming events
            events = await api_manager.clients["apple_calendar"].get_events(max_results=5)
            logger.info(f"Found {len(events)} upcoming Apple calendar events")
            
        except Exception as e:
            logger.error(f"Apple Calendar example failed: {e}")

async def interactive_mode():
    """Interactive mode for testing API operations"""
    logger = setup_logger("Interactive")
    
    # Initialize API manager
    api_manager = await get_api_manager()
    await api_manager.initialize()
    
    logger.info("=== Interactive Mode ===")
    logger.info("Available commands:")
    logger.info("1. chat <message> - Chat with AI")
    logger.info("2. email <to> <subject> <body> - Send email")
    logger.info("3. calendar <title> <description> - Create calendar event")
    logger.info("4. status - Check API status")
    logger.info("5. quit - Exit")
    
    while True:
        try:
            command = input("\n> ").strip().split()
            
            if not command:
                continue
            
            if command[0] == "quit":
                break
            elif command[0] == "chat" and len(command) > 1:
                message = " ".join(command[1:])
                response = await api_manager.chat_completion(message)
                print(f"AI: {response}")
            elif command[0] == "email" and len(command) >= 4:
                to, subject = command[1], command[2]
                body = " ".join(command[3:])
                success = await api_manager.send_email(to, subject, body)
                print(f"Email sent: {success}")
            elif command[0] == "calendar" and len(command) >= 2:
                title = command[1]
                description = " ".join(command[2:]) if len(command) > 2 else ""
                tomorrow = datetime.now() + timedelta(days=1)
                event = await api_manager.create_calendar_event(
                    title, tomorrow, tomorrow + timedelta(hours=1), description
                )
                print(f"Event created: {event}")
            elif command[0] == "status":
                status = await api_manager.get_status()
                for name, api_status in status.items():
                    print(f"{name}: {'✅' if api_status.connected else '❌'}")
            else:
                print("Unknown command or insufficient arguments")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Command failed: {e}")
    
    await api_manager.shutdown()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())