"""
Main API Manager for OS Dashboard AI Assistant
Coordinates all API integrations
"""
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from config import get_api_config, validate_api_config
from ..logging_config import setup_logger

# Import individual API clients
from ai_layer.openai_client import OpenAIClient
from integrations.msgraph.client import MicrosoftClient
from integrations.google_client import GoogleClient
from integrations.git_client import GitClient
from integrations.adobe_client import AdobeClient
from integrations.apple_calendar import AppleCalendarClient


@dataclass
class APIStatus:
    """Status information for an API"""
    name: str
    connected: bool
    last_check: datetime
    error_message: Optional[str] = None


class APIManager:
    """Main API Manager that coordinates all integrations"""

    def __init__(self):
        self.config = get_api_config()
        self.logger = setup_logger("APIManager")
        self.clients: Dict[str, Any] = {}
        self.status: Dict[str, APIStatus] = {}

    async def initialize(self) -> Dict[str, bool]:
        """Initialize all API clients"""
        self.logger.info("Initializing OS Dashboard AI Assistant API Manager...")

        # Validate configuration
        validation_results = validate_api_config()
        self.logger.info(f"Configuration validation: {validation_results}")

        initialization_results = {}

        # Initialize OpenAI Client
        if validation_results["openai"]:
            try:
                self.clients["openai"] = OpenAIClient()
                await self.clients["openai"].initialize()
                initialization_results["openai"] = True
                self.logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                initialization_results["openai"] = False

        # Initialize Microsoft Client
        if validation_results["microsoft"]:
            try:
                self.clients["microsoft"] = MicrosoftClient()
                await self.clients["microsoft"].initialize()
                initialization_results["microsoft"] = True
                self.logger.info("✅ Microsoft Graph client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Microsoft client: {e}")
                initialization_results["microsoft"] = False

        # Initialize Google Client
        if validation_results["google"]:
            try:
                self.clients["google"] = GoogleClient()
                await self.clients["google"].initialize()
                initialization_results["google"] = True
                self.logger.info("✅ Google APIs client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Google client: {e}")
                initialization_results["google"] = False

        # Initialize Git Client
        if validation_results["github"]:
            try:
                self.clients["git"] = GitClient()
                await self.clients["git"].initialize()
                initialization_results["git"] = True
                self.logger.info("✅ Git client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Git client: {e}")
                initialization_results["git"] = False

        # Initialize Adobe Client
        if validation_results["adobe"]:
            try:
                self.clients["adobe"] = AdobeClient()
                await self.clients["adobe"].initialize()
                initialization_results["adobe"] = True
                self.logger.info("✅ Adobe client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Adobe client: {e}")
                initialization_results["adobe"] = False

        # Initialize Apple Calendar Client
        if validation_results["caldav"]:
            try:
                self.clients["apple_calendar"] = AppleCalendarClient()
                await self.clients["apple_calendar"].initialize()
                initialization_results["apple_calendar"] = True
                self.logger.info("✅ Apple Calendar client initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Apple Calendar client: {e}")
                initialization_results["apple_calendar"] = False

        self.logger.info(f"API Manager initialization complete. Results: {initialization_results}")
        return initialization_results

    async def get_status(self) -> Dict[str, APIStatus]:
        """Get status of all API connections"""
        status_results = {}

        for name, client in self.clients.items():
            try:
                is_connected = await client.health_check()
                status_results[name] = APIStatus(
                    name=name,
                    connected=is_connected,
                    last_check=datetime.now()
                )
            except Exception as e:
                status_results[name] = APIStatus(
                    name=name,
                    connected=False,
                    last_check=datetime.now(),
                    error_message=str(e)
                )

        self.status = status_results
        return status_results

    # Unified API Methods
    async def chat_completion(self, message: str, **kwargs) -> str:
        """Send message to ChatGPT"""
        if "openai" in self.clients:
            return await self.clients["openai"].chat_completion(message, **kwargs)
        raise Exception("OpenAI client not available")

    async def create_document(self, title: str, content: str, doc_type: str = "word") -> Dict[str, Any]:
        """Create a document in Microsoft Office"""
        if "microsoft" in self.clients:
            return await self.clients["microsoft"].create_document(title, content, doc_type)
        raise Exception("Microsoft client not available")

    async def send_email(self, to: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Send email via Gmail"""
        if "google" in self.clients:
            return await self.clients["google"].send_email(to, subject, body, attachments)
        raise Exception("Google client not available")

    async def create_calendar_event(self, title: str, start_time: datetime, end_time: datetime,
                                  description: str = "", service: str = "google") -> Dict[str, Any]:
        """Create calendar event"""
        if service == "google" and "google" in self.clients:
            return await self.clients["google"].create_calendar_event(title, start_time, end_time, description)
        elif service == "apple" and "apple_calendar" in self.clients:
            return await self.clients["apple_calendar"].create_event(title, start_time, end_time, description)
        raise Exception(f"{service} calendar client not available")

    async def git_operations(self, operation: str, **kwargs) -> Any:
        """Perform Git operations"""
        if "git" in self.clients:
            return await self.clients["git"].execute_operation(operation, **kwargs)
        raise Exception("Git client not available")

    async def process_pdf(self, file_path: str, operation: str = "extract_text") -> Any:
        """Process PDF with Adobe services"""
        if "adobe" in self.clients:
            return await self.clients["adobe"].process_pdf(file_path, operation)
        raise Exception("Adobe client not available")

    async def shutdown(self):
        """Gracefully shutdown all clients"""
        self.logger.info("Shutting down API Manager...")

        for name, client in self.clients.items():
            try:
                if hasattr(client, 'shutdown'):
                    await client.shutdown()
                self.logger.info(f"✅ {name} client shutdown successfully")
            except Exception as e:
                self.logger.error(f"❌ Error shutting down {name} client: {e}")

        self.clients.clear()
        self.logger.info("API Manager shutdown complete")


# Global API Manager instance
api_manager = APIManager()


async def get_api_manager() -> APIManager:
    """Get the global API manager instance"""
    return api_manager
