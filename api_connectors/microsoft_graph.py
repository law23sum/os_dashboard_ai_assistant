"""Microsoft Graph Connector providing unified access to Microsoft 365 resources.

This module offers a mock-friendly implementation that fits the internal
``BaseConnector`` interface. It focuses on transforming Graph responses into
our light-weight CIR structures (``CIRDocument`` with ``Section`` and
``ContentBlock`` instances) so downstream components can operate on a
consistent schema even when the Graph SDK is unavailable in the environment.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .universal_connector import (
    BaseConnector,
    CIRDocument,
    ConnectorCapability,
    ConnectorConfig,
    ContentBlock,
    ContentBlockType,
    OperationResult,
    Section,
)


@dataclass
class ResourceRef:
    """Reference to a Microsoft 365 resource."""

    id: str
    name: str
    resource_type: str
    path: Optional[str] = None
    size: Optional[int] = None
    modified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MicrosoftGraphConnector(BaseConnector):
    """Connector for Microsoft Graph API (Word, Excel, PowerPoint, OneDrive, OneNote)."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.graph_client = None
        self.access_token = None
        self.supported_types = {
            "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "powerpoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "onenote": "application/onenote",
            "pdf": "application/pdf",
        }

    async def connect(self) -> OperationResult:
        """Establish connection to Microsoft Graph using provided credentials."""
        try:
            await self._authenticate()
            await self._test_connection()
            self.is_connected = True
            return OperationResult(success=True, data={"status": "connected", "endpoint": "graph.microsoft.com"})
        except Exception as exc:  # pragma: no cover - network dependent
            return OperationResult(success=False, error=str(exc), error_code="CONNECTION_FAILED")

    async def disconnect(self) -> OperationResult:
        """Clear any connection state."""
        self.graph_client = None
        self.access_token = None
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})

    async def health_check(self) -> OperationResult:
        """Perform a lightweight Graph call to validate connectivity."""
        if not self.is_connected:
            return OperationResult(success=False, error="Not connected", error_code="NOT_CONNECTED")

        try:
            await self._make_graph_request("GET", "/me")
            self.last_health_check = datetime.utcnow()
            return OperationResult(success=True, data={"status": "healthy", "last_check": self.last_health_check})
        except Exception as exc:  # pragma: no cover - network dependent
            return OperationResult(success=False, error=str(exc), error_code="HEALTH_CHECK_FAILED")

    async def list_resources(self, resource_type: str = None, filters: Dict[str, Any] = None) -> OperationResult:
        """List accessible resources across OneDrive and OneNote."""
        if not self.is_connected:
            return OperationResult(success=False, error="Not connected", error_code="NOT_CONNECTED")

        try:
            resources: List[ResourceRef] = []
            if not resource_type or resource_type == "onedrive":
                resources.extend(await self._list_onedrive_files(filters))
            if not resource_type or resource_type == "onenote":
                resources.extend(await self._list_onenote_notebooks(filters))

            if filters:
                resources = self._apply_filters(resources, filters)

            return OperationResult(success=True, data=resources)
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        """Return basic metadata for a given resource id."""
        try:
            resource_info = await self._get_resource_info(resource_id)
            return OperationResult(success=True, data=resource_info)
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def read_resource(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        """Read resource content and convert to CIRDocument."""
        try:
            resource_info = await self._get_resource_info(resource_id)
            resource_type = resource_info.get("type")

            if resource_type == "word":
                return await self._read_word_document(resource_id, options)
            if resource_type == "excel":
                return await self._read_excel_workbook(resource_id, options)
            if resource_type == "powerpoint":
                return await self._read_powerpoint_presentation(resource_id, options)
            if resource_type == "onenote":
                return await self._read_onenote_page(resource_id, options)

            return await self._read_generic_file(resource_id, options)
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def write_resource(
        self, resource_id: str, cir_content: CIRDocument, options: Dict[str, Any] = None
    ) -> OperationResult:
        """Placeholder write implementation that echoes the CIR metadata."""
        try:
            return OperationResult(success=True, data={"updated_resource_id": resource_id, "title": cir_content.title})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def create_resource(
        self, resource_type: str, cir_content: CIRDocument, options: Dict[str, Any] = None
    ) -> OperationResult:
        """Create a new Graph resource (mocked)."""
        try:
            new_id = f"{resource_type}_{datetime.utcnow().timestamp()}"
            return OperationResult(success=True, data={"created_resource_id": new_id, "title": cir_content.title})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def delete_resource(self, resource_id: str) -> OperationResult:
        """Delete a resource via Graph API (mocked)."""
        try:
            await self._make_graph_request("DELETE", f"/me/drive/items/{resource_id}")
            return OperationResult(success=True, data={"deleted_resource_id": resource_id})
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    async def search(self, query: str, filters: Dict[str, Any] = None, options: Dict[str, Any] = None) -> OperationResult:
        """Perform a Microsoft Search API query (mocked)."""
        try:
            limit = options.get("limit", 25) if options else 25
            results = [
                ResourceRef(
                    id=f"result_{i}",
                    name=f"Result {i}",
                    path=f"https://graph.microsoft.com/mock/{i}",
                    resource_type="driveItem",
                    metadata={"summary": f"Match for '{query}'", "score": 1.0 / (i + 1)},
                )
                for i in range(limit)
            ]
            if filters:
                results = self._apply_filters(results, filters)
            return OperationResult(success=True, data=results)
        except Exception as exc:
            return OperationResult(success=False, error=str(exc))

    # ------------------------------------------------------------------
    # Private helpers
    async def _authenticate(self):
        tenant_id = self.config.credentials.get("tenant_id")
        client_id = self.config.credentials.get("client_id")
        client_secret = self.config.credentials.get("client_secret")

        if not all([tenant_id, client_id, client_secret]):
            raise ValueError("Missing required credentials for Microsoft Graph")

        self.access_token = "mock_access_token"

    async def _test_connection(self):
        await self._make_graph_request("GET", "/me")

    async def _make_graph_request(self, method: str, endpoint: str, data: Any = None) -> Dict[str, Any]:
        await asyncio.sleep(0.05)

        if endpoint == "/me":
            return {"id": "user123", "displayName": "Test User"}
        if endpoint.startswith("/me/drive/root/children"):
            return {"value": []}
        if endpoint.startswith("/me/onenote/notebooks"):
            return {"value": []}
        return {}

    async def _list_onedrive_files(self, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        response = await self._make_graph_request("GET", "/me/drive/root/children")
        items = response.get("value", [])

        resources: List[ResourceRef] = []
        for item in items:
            mime_type = item.get("file", {}).get("mimeType")
            file_type = self._get_file_type_from_mime(mime_type)
            resources.append(
                ResourceRef(
                    id=item["id"],
                    name=item["name"],
                    path=item.get("webUrl"),
                    resource_type=file_type,
                    size=item.get("size"),
                    modified_at=self._parse_datetime(item.get("lastModifiedDateTime")),
                    created_at=self._parse_datetime(item.get("createdDateTime")),
                    metadata=item,
                )
            )
        return resources

    async def _list_onenote_notebooks(self, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        response = await self._make_graph_request("GET", "/me/onenote/notebooks")
        notebooks = response.get("value", [])

        return [
            ResourceRef(
                id=notebook["id"],
                name=notebook.get("displayName", ""),
                resource_type="onenote_notebook",
                created_at=self._parse_datetime(notebook.get("createdDateTime")),
                modified_at=self._parse_datetime(notebook.get("lastModifiedDateTime")),
                metadata=notebook,
            )
            for notebook in notebooks
        ]

    def _get_file_type_from_mime(self, mime_type: Optional[str]) -> str:
        mime_to_type = {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "word",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "powerpoint",
            "application/pdf": "pdf",
            "text/plain": "text",
            "application/json": "json",
        }
        if not mime_type:
            return "unknown"
        return mime_to_type.get(mime_type, "unknown")

    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        if not datetime_str:
            return None
        try:
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except Exception:
            return None

    async def _get_resource_info(self, resource_id: str) -> Dict[str, Any]:
        response = await self._make_graph_request("GET", f"/me/drive/items/{resource_id}")
        file_info = response.get("file", {})
        mime_type = file_info.get("mimeType", "")
        return {
            "id": resource_id,
            "name": response.get("name", ""),
            "type": self._get_file_type_from_mime(mime_type),
            "mime_type": mime_type,
            "size": response.get("size", 0),
            "modified": response.get("lastModifiedDateTime"),
            "created": response.get("createdDateTime"),
        }

    def _apply_filters(self, resources: List[ResourceRef], filters: Dict[str, Any]) -> List[ResourceRef]:
        filtered = resources
        if "file_type" in filters:
            filtered = [r for r in filtered if r.resource_type == filters["file_type"]]
        if "modified_after" in filters:
            modified_after = filters["modified_after"]
            filtered = [r for r in filtered if r.modified_at and r.modified_at > modified_after]
        if "name_contains" in filters:
            name_filter = filters["name_contains"].lower()
            filtered = [r for r in filtered if name_filter in r.name.lower()]
        return filtered

    async def _read_word_document(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        section = Section(
            title="Word Document",
            content_blocks=[ContentBlock(block_type=ContentBlockType.TEXT, content="Document content would be extracted here")],
        )
        cir_document = CIRDocument(title="Word Document", document_type="word", sections=[section], metadata={"id": resource_id})
        return OperationResult(success=True, data=cir_document)

    async def _read_excel_workbook(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        table_block = ContentBlock(
            block_type=ContentBlockType.TABLE,
            content={"headers": ["Column A", "Column B", "Column C"], "rows": [["Data 1", "Data 2", "Data 3"]]},
        )
        section = Section(title="Excel Workbook", content_blocks=[table_block])
        cir_document = CIRDocument(title="Excel Workbook", document_type="excel", sections=[section], metadata={"id": resource_id})
        return OperationResult(success=True, data=cir_document)

    async def _read_powerpoint_presentation(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        sections = [
            Section(
                title=f"Slide {i + 1}",
                content_blocks=[ContentBlock(block_type=ContentBlockType.TEXT, content=f"Content of slide {i + 1}")],
            )
            for i in range(3)
        ]
        cir_document = CIRDocument(
            title="PowerPoint Presentation", document_type="powerpoint", sections=sections, metadata={"id": resource_id}
        )
        return OperationResult(success=True, data=cir_document)

    async def _read_onenote_page(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        section = Section(
            title="OneNote Page",
            content_blocks=[ContentBlock(block_type=ContentBlockType.TEXT, content="OneNote page content")],
        )
        cir_document = CIRDocument(title="OneNote Page", document_type="onenote", sections=[section], metadata={"id": resource_id})
        return OperationResult(success=True, data=cir_document)

    async def _read_generic_file(self, resource_id: str, options: Dict[str, Any] = None) -> OperationResult:
        section = Section(
            title="Generic File",
            content_blocks=[ContentBlock(block_type=ContentBlockType.TEXT, content="Generic file content")],
        )
        cir_document = CIRDocument(title="Generic File", document_type="generic", sections=[section], metadata={"id": resource_id})
        return OperationResult(success=True, data=cir_document)


__all__ = ["MicrosoftGraphConnector", "ResourceRef"]
