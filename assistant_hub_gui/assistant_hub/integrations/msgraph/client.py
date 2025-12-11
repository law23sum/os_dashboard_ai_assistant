"""
Microsoft Graph API Client for Office 365 integration
Handles Word, PowerPoint, Excel, OneNote
"""

import asyncio
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

import msal
from msgraph import GraphServiceClient
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.models.workbook import Workbook
from msgraph.generated.models.notebook import Notebook

from config import get_api_config

try:
    from ...logging_config import setup_logger
except ImportError:
    try:
        from assistant_hub_gui.assistant_hub.logging_config import setup_logger  # type: ignore
    except ImportError:
        import logging

        def setup_logger(name: str) -> logging.Logger:
            return logging.getLogger(name)


class MicrosoftClient:
    """Microsoft Graph API client for Office 365 services"""

    def __init__(self):
        self.config = get_api_config()
        self.logger = setup_logger("MicrosoftClient")
        self.app = None
        self.graph_client = None
        self.access_token = None

    async def initialize(self) -> bool:
        """Initialize Microsoft Graph client"""
        try:
            # Create MSAL app
            self.app = msal.ConfidentialClientApplication(
                client_id=self.config.microsoft_client_id,
                client_credential=self.config.microsoft_client_secret,
                authority=f"https://login.microsoftonline.com/{self.config.microsoft_tenant_id}",
            )

            # Get access token
            await self._get_access_token()

            # Initialize Graph client
            self.graph_client = GraphServiceClient(
                credentials=self._get_credentials(),
                scopes=["https://graph.microsoft.com/.default"],
            )

            self.logger.info("Microsoft Graph client initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Microsoft client: {e}")
            raise

    async def _get_access_token(self):
        """Get access token using client credentials flow"""
        try:
            result = self.app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )

            if "access_token" in result:
                self.access_token = result["access_token"]
            else:
                raise Exception(
                    f"Failed to acquire token: {result.get('error_description', 'Unknown error')}"
                )

        except Exception as e:
            self.logger.error(f"Token acquisition failed: {e}")
            raise

    def _get_credentials(self):
        """Get credentials for Graph client"""

        class TokenCredential:
            def __init__(self, token):
                self.token = token

            async def get_token(self, *scopes, **kwargs):
                class AccessToken:
                    def __init__(self, token):
                        self.token = token
                        self.expires_on = datetime.now() + timedelta(hours=1)

                return AccessToken(self.token)

        return TokenCredential(self.access_token)

    async def health_check(self) -> bool:
        """Check if Microsoft Graph API is accessible"""
        try:
            # Try to get user info
            user = await self.graph_client.me.get()
            return True
        except Exception as e:
            self.logger.error(f"Microsoft Graph health check failed: {e}")
            return False

    # Word Document Operations
    async def create_word_document(
        self, title: str, content: str, folder_path: str = None
    ) -> Dict[str, Any]:
        """Create a new Word document"""
        try:
            # Create document content
            doc_content = f"""
            <html>
            <head><title>{title}</title></head>
            <body>
                <h1>{title}</h1>
                <div>{content}</div>
            </body>
            </html>
            """

            # Upload to OneDrive
            file_name = f"{title}.docx"
            drive_item = await self._upload_file(
                file_name, doc_content.encode(), folder_path
            )

            return {
                "id": drive_item.id,
                "name": drive_item.name,
                "web_url": drive_item.web_url,
                "type": "word_document",
            }

        except Exception as e:
            self.logger.error(f"Word document creation failed: {e}")
            raise

    async def get_word_document(self, document_id: str) -> Dict[str, Any]:
        """Get Word document content"""
        try:
            drive_item = await self.graph_client.me.drive.items.by_drive_item_id(
                document_id
            ).get()

            # Get document content
            content_response = await self.graph_client.me.drive.items.by_drive_item_id(
                document_id
            ).content.get()

            return {
                "id": drive_item.id,
                "name": drive_item.name,
                "content": content_response,
                "last_modified": drive_item.last_modified_date_time,
            }

        except Exception as e:
            self.logger.error(f"Failed to get Word document: {e}")
            raise

    # PowerPoint Operations
    async def create_powerpoint_presentation(
        self, title: str, slides_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a new PowerPoint presentation"""
        try:
            # Create basic presentation structure
            presentation_content = {"title": title, "slides": slides_data}

            # Convert to basic format and upload
            file_name = f"{title}.pptx"
            content = json.dumps(presentation_content).encode()

            drive_item = await self._upload_file(file_name, content)

            return {
                "id": drive_item.id,
                "name": drive_item.name,
                "web_url": drive_item.web_url,
                "type": "powerpoint_presentation",
            }

        except Exception as e:
            self.logger.error(f"PowerPoint creation failed: {e}")
            raise

    # Excel Operations
    async def create_excel_workbook(
        self, title: str, worksheets_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a new Excel workbook"""
        try:
            # Create workbook structure
            workbook_content = {"title": title, "worksheets": worksheets_data}

            file_name = f"{title}.xlsx"
            content = json.dumps(workbook_content).encode()

            drive_item = await self._upload_file(file_name, content)

            return {
                "id": drive_item.id,
                "name": drive_item.name,
                "web_url": drive_item.web_url,
                "type": "excel_workbook",
            }

        except Exception as e:
            self.logger.error(f"Excel workbook creation failed: {e}")
            raise

    async def update_excel_worksheet(
        self,
        workbook_id: str,
        worksheet_name: str,
        range_address: str,
        values: List[List[Any]],
    ) -> bool:
        """Update Excel worksheet data"""
        try:
            # Update worksheet range
            await self.graph_client.me.drive.items.by_drive_item_id(
                workbook_id
            ).workbook.worksheets.by_worksheet_id(worksheet_name).range(
                address=range_address
            ).patch(
                {"values": values}
            )

            return True

        except Exception as e:
            self.logger.error(f"Excel worksheet update failed: {e}")
            raise

    # OneNote Operations
    async def create_onenote_page(
        self, notebook_id: str, section_id: str, title: str, content: str
    ) -> Dict[str, Any]:
        """Create a new OneNote page"""
        try:
            page_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <meta name="created" content="{datetime.now().isoformat()}" />
            </head>
            <body>
                <div>
                    <h1>{title}</h1>
                    <p>{content}</p>
                </div>
            </body>
            </html>
            """

            page = await self.graph_client.me.onenote.sections.by_onenote_section_id(
                section_id
            ).pages.post({"title": title, "content": page_content})

            return {
                "id": page.id,
                "title": page.title,
                "web_url": page.links.one_note_web_url.href,
                "type": "onenote_page",
            }

        except Exception as e:
            self.logger.error(f"OneNote page creation failed: {e}")
            raise

    async def get_onenote_notebooks(self) -> List[Dict[str, Any]]:
        """Get all OneNote notebooks"""
        try:
            notebooks = await self.graph_client.me.onenote.notebooks.get()

            return [
                {
                    "id": notebook.id,
                    "name": notebook.display_name,
                    "web_url": notebook.links.one_note_web_url.href,
                }
                for notebook in notebooks.value
            ]

        except Exception as e:
            self.logger.error(f"Failed to get OneNote notebooks: {e}")
            raise

    # File Operations
    async def _upload_file(
        self, file_name: str, content: bytes, folder_path: str = None
    ) -> DriveItem:
        """Upload file to OneDrive"""
        try:
            if folder_path:
                upload_path = f"{folder_path}/{file_name}"
            else:
                upload_path = file_name

            drive_item = await self.graph_client.me.drive.root.item_with_path(
                upload_path
            ).content.put(content)

            return drive_item

        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            raise

    async def list_files(self, folder_path: str = None) -> List[Dict[str, Any]]:
        """List files in OneDrive"""
        try:
            if folder_path:
                items = await self.graph_client.me.drive.root.item_with_path(
                    folder_path
                ).children.get()
            else:
                items = await self.graph_client.me.drive.root.children.get()

            return [
                {
                    "id": item.id,
                    "name": item.name,
                    "type": item.file.mime_type if item.file else "folder",
                    "size": item.size,
                    "web_url": item.web_url,
                    "last_modified": item.last_modified_date_time,
                }
                for item in items.value
            ]

        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            raise

    # Unified document creation method
    async def create_document(
        self, title: str, content: str, doc_type: str = "word"
    ) -> Dict[str, Any]:
        """Create document of specified type"""
        if doc_type.lower() == "word":
            return await self.create_word_document(title, content)
        elif doc_type.lower() == "powerpoint":
            # Convert content to slides format
            slides_data = [{"title": title, "content": content}]
            return await self.create_powerpoint_presentation(title, slides_data)
        elif doc_type.lower() == "excel":
            # Convert content to worksheet format
            worksheets_data = [{"name": "Sheet1", "data": content}]
            return await self.create_excel_workbook(title, worksheets_data)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    async def shutdown(self):
        """Shutdown Microsoft client"""
        self.access_token = None
        self.graph_client = None
        self.logger.info("Microsoft client shutdown complete")


class GraphClient(MicrosoftClient):
    """Backward compatible alias for existing integrations."""
    pass
