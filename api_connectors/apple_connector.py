"""Apple ecosystem connector for Notes, Calendar, and iCloud."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .universal_connector import (
    BaseConnector,
    ConnectorConfig,
    OperationResult,
    ResourceRef,
)
from assistant_core.cir import (
    CIRDocument,
    CIRNode,
    CalendarEvent,
    CalendarExtension,
    ContentType,
    DocumentMetadata,
    EventPriority,
    EventStatus,
    Provenance,
    SourceSystem,
)


class AppleConnector(BaseConnector):
    """Connector for Apple ecosystem services (Notes, Calendar, iCloud)."""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.notes_db_path = config.settings.get("notes_db_path", self._get_default_notes_path())
        self.calendar_db_path = config.settings.get(
            "calendar_db_path", self._get_default_calendar_path()
        )
        self.icloud_path = config.settings.get("icloud_path", self._get_default_icloud_path())
        self.enable_notes = config.settings.get("enable_notes", True)
        self.enable_calendar = config.settings.get("enable_calendar", True)
        self.enable_icloud = config.settings.get("enable_icloud", True)
        self.notes_connection = None
        self.calendar_connection = None

    def _get_default_notes_path(self) -> str:
        """Get default Notes database path."""

        home = Path.home()
        return f"{home}/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite"

    def _get_default_calendar_path(self) -> str:
        """Get default Calendar database path."""

        home = Path.home()
        return f"{home}/Library/Calendars/Calendar.sqlitedb"

    def _get_default_icloud_path(self) -> str:
        """Get default iCloud Drive path."""

        home = Path.home()
        return f"{home}/Library/Mobile Documents/com~apple~CloudDocs"

    async def connect(self) -> OperationResult:
        """Connect to Apple services."""

        try:
            connected_services = []
            errors = []

            if self.enable_notes:
                try:
                    if Path(self.notes_db_path).exists():
                        self.notes_connection = sqlite3.connect(self.notes_db_path)
                        self.notes_connection.row_factory = sqlite3.Row
                        connected_services.append("notes")
                    else:
                        errors.append("Notes database not found")
                except Exception as exc:  # pragma: no cover - passthrough
                    errors.append(f"Notes connection failed: {exc}")

            if self.enable_calendar:
                try:
                    if Path(self.calendar_db_path).exists():
                        self.calendar_connection = sqlite3.connect(self.calendar_db_path)
                        self.calendar_connection.row_factory = sqlite3.Row
                        connected_services.append("calendar")
                    else:
                        errors.append("Calendar database not found")
                except Exception as exc:  # pragma: no cover - passthrough
                    errors.append(f"Calendar connection failed: {exc}")

            if self.enable_icloud:
                try:
                    if Path(self.icloud_path).exists():
                        connected_services.append("icloud")
                    else:
                        errors.append("iCloud Drive not found")
                except Exception as exc:  # pragma: no cover - passthrough
                    errors.append(f"iCloud access failed: {exc}")

            if not connected_services:
                return OperationResult(
                    success=False,
                    error="No Apple services could be connected",
                    error_code="NO_SERVICES_AVAILABLE",
                )

            self.is_connected = True
            return OperationResult(
                success=True,
                data={
                    "status": "connected",
                    "connected_services": connected_services,
                    "errors": errors,
                    "capabilities": [
                        "notes_access",
                        "calendar_access",
                        "icloud_documents",
                        "event_management",
                        "note_creation",
                        "document_sync",
                    ],
                },
            )

        except Exception as exc:  # pragma: no cover - passthrough
            return OperationResult(success=False, error=str(exc))

    async def disconnect(self) -> OperationResult:
        """Disconnect from Apple services."""

        try:
            if self.notes_connection:
                self.notes_connection.close()
                self.notes_connection = None

            if self.calendar_connection:
                self.calendar_connection.close()
                self.calendar_connection = None

            self.is_connected = False
            return OperationResult(success=True, data={"status": "disconnected"})

        except Exception as exc:  # pragma: no cover - passthrough
            return OperationResult(success=False, error=str(exc))

    async def health_check(self) -> OperationResult:
        """Check Apple services health."""

        if not self.is_connected:
            return OperationResult(
                success=False,
                error="Not connected to Apple services",
                error_code="NOT_CONNECTED",
            )

        health_status: Dict[str, Any] = {}

        if self.notes_connection:
            try:
                cursor = self.notes_connection.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT WHERE ZTITLE IS NOT NULL"
                )
                note_count = cursor.fetchone()[0]
                health_status["notes"] = {"status": "healthy", "note_count": note_count}
            except Exception as exc:  # pragma: no cover - passthrough
                health_status["notes"] = {"status": "error", "error": str(exc)}

        if self.calendar_connection:
            try:
                cursor = self.calendar_connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM CalendarItem")
                event_count = cursor.fetchone()[0]
                health_status["calendar"] = {"status": "healthy", "event_count": event_count}
            except Exception as exc:  # pragma: no cover - passthrough
                health_status["calendar"] = {"status": "error", "error": str(exc)}

        if self.enable_icloud and Path(self.icloud_path).exists():
            try:
                file_count = len(list(Path(self.icloud_path).rglob("*")))
                health_status["icloud"] = {"status": "healthy", "file_count": file_count}
            except Exception as exc:  # pragma: no cover - passthrough
                health_status["icloud"] = {"status": "error", "error": str(exc)}

        self.last_health_check = datetime.utcnow()
        return OperationResult(
            success=True,
            data={
                "status": "healthy",
                "last_check": self.last_health_check,
                "services": health_status,
            },
        )

    async def list_resources(
        self, resource_type: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """List Apple resources (notes, events, documents)."""

        resources: List[ResourceRef] = []

        if resource_type in (None, "notes") and self.notes_connection:
            resources.extend(await self._list_notes(filters))

        if resource_type in (None, "events") and self.calendar_connection:
            resources.extend(await self._list_calendar_events(filters))

        if resource_type in (None, "documents") and self.enable_icloud:
            resources.extend(await self._list_icloud_documents(filters))

        return OperationResult(success=True, data=resources)

    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        """Get detailed metadata for Apple resource."""

        try:
            if resource_id.startswith("note:"):
                note_id = resource_id[5:]
                metadata = await self._get_note_metadata(note_id)
            elif resource_id.startswith("event:"):
                event_id = resource_id[6:]
                metadata = await self._get_event_metadata(event_id)
            elif resource_id.startswith("document:"):
                doc_path = resource_id[9:]
                metadata = await self._get_document_metadata(doc_path)
            else:
                return OperationResult(
                    success=False,
                    error="Invalid resource ID format",
                    error_code="INVALID_RESOURCE_ID",
                )

            return OperationResult(success=True, data=metadata)

        except Exception as exc:  # pragma: no cover - passthrough
            return OperationResult(success=False, error=str(exc))

    async def read_resource(
        self, resource_id: str, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Read Apple resource and convert to CIR."""

        try:
            if resource_id.startswith("note:"):
                note_id = resource_id[5:]
                cir_document = await self._read_note_as_cir(note_id, options)
            elif resource_id.startswith("event:"):
                event_id = resource_id[6:]
                cir_document = await self._read_event_as_cir(event_id, options)
            elif resource_id.startswith("document:"):
                doc_path = resource_id[9:]
                cir_document = await self._read_document_as_cir(doc_path, options)
            else:
                return OperationResult(
                    success=False,
                    error="Resource type not readable",
                    error_code="RESOURCE_NOT_READABLE",
                )

            return OperationResult(success=True, data=cir_document)

        except Exception as exc:  # pragma: no cover - passthrough
            return OperationResult(success=False, error=str(exc))

    async def write_resource(
        self, resource_id: str, cir_content: CIRDocument, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Update Apple resource."""

        try:
            if resource_id.startswith("note:"):
                note_id = resource_id[5:]
                result = await self._update_note(note_id, cir_content, options)
            elif resource_id.startswith("event:"):
                event_id = resource_id[6:]
                result = await self._update_event(event_id, cir_content, options)
            else:
                return OperationResult(
                    success=False,
                    error="Resource type not writable",
                    error_code="RESOURCE_NOT_WRITABLE",
                )

            return OperationResult(success=True, data=result)

        except Exception as exc:  # pragma: no cover - passthrough
            return OperationResult(success=False, error=str(exc))

    async def create_resource(
        self, resource_type: str, cir_content: CIRDocument, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Create new Apple resource."""

        try:
            if resource_type == "note":
                result = await self._create_note(cir_content, options)
            elif resource_type == "event":
                result = await self._create_event(cir_content, options)
            else:
                return OperationResult(
                    success=False,
                    error=f"Unsupported resource type: {resource_type}",
                    error_code="UNSUPPORTED_TYPE",
                )

            return OperationResult(success=True, data=result)

        except Exception as exc:  # pragma: no cover - passthrough
            return OperationResult(success=False, error=str(exc))

    async def delete_resource(self, resource_id: str) -> OperationResult:
        """Delete Apple resource."""

        try:
            if resource_id.startswith("note:"):
                note_id = resource_id[5:]
                result = await self._delete_note(note_id)
            elif resource_id.startswith("event:"):
                event_id = resource_id[6:]
                result = await self._delete_event(event_id)
            else:
                return OperationResult(
                    success=False,
                    error="Resource type not deletable",
                    error_code="RESOURCE_NOT_DELETABLE",
                )

            return OperationResult(success=True, data=result)

        except Exception as exc:  # pragma: no cover - passthrough
            return OperationResult(success=False, error=str(exc))

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, options: Optional[Dict[str, Any]] = None
    ) -> OperationResult:
        """Search Apple resources."""

        search_results: List[ResourceRef] = []

        if self.notes_connection:
            search_results.extend(await self._search_notes(query, filters))

        if self.calendar_connection:
            search_results.extend(await self._search_events(query, filters))

        if self.enable_icloud:
            search_results.extend(await self._search_documents(query, filters))

        search_results.sort(
            key=lambda item: item.modified_at or item.created_at or datetime.min,
            reverse=True,
        )

        limit = options.get("limit", 50) if options else 50
        search_results = search_results[:limit]

        return OperationResult(success=True, data=search_results)

    async def _list_notes(self, filters: Optional[Dict[str, Any]] = None) -> List[ResourceRef]:
        """List Apple Notes."""

        notes: List[ResourceRef] = []

        if not self.notes_connection:
            return notes

        cursor = self.notes_connection.cursor()
        query = """
            SELECT 
                ZICCLOUDSYNCINGOBJECT.Z_PK as note_id,
                ZICCLOUDSYNCINGOBJECT.ZTITLE as title,
                ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE as modified_date,
                ZICCLOUDSYNCINGOBJECT.ZCREATIONDATE as creation_date,
                ZICNOTEDATA.ZDATA as content
            FROM ZICCLOUDSYNCINGOBJECT
            LEFT JOIN ZICNOTEDATA ON ZICCLOUDSYNCINGOBJECT.ZNOTEDATA = ZICNOTEDATA.Z_PK
            WHERE ZICCLOUDSYNCINGOBJECT.ZTITLE IS NOT NULL
            """

        params: List[Any] = []
        if filters:
            if "created_after" in filters:
                apple_timestamp = (filters["created_after"] - datetime(2001, 1, 1)).total_seconds()
                query += " AND ZICCLOUDSYNCINGOBJECT.ZCREATIONDATE > ?"
                params.append(apple_timestamp)

            if "title_contains" in filters:
                query += " AND ZICCLOUDSYNCINGOBJECT.ZTITLE LIKE ?"
                params.append(f"%{filters['title_contains']}%")

        query += " ORDER BY ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE DESC"

        if filters and "limit" in filters:
            query += " LIMIT ?"
            params.append(filters["limit"])

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        except Exception:
            return notes

        for row in rows:
            creation_date = self._apple_timestamp_to_datetime(row["creation_date"])
            modified_date = self._apple_timestamp_to_datetime(row["modified_date"])
            notes.append(
                ResourceRef(
                    id=f"note:{row['note_id']}",
                    name=row["title"] or f"Note {row['note_id']}",
                    path=str(row["note_id"]),
                    resource_type="note",
                    created_at=creation_date,
                    modified_at=modified_date,
                    metadata={
                        "note_id": row["note_id"],
                        "has_content": row["content"] is not None,
                        "source": "apple_notes",
                    },
                )
            )

        return notes

    async def _read_note_as_cir(
        self, note_id: str, options: Optional[Dict[str, Any]] = None
    ) -> CIRDocument:
        """Read Apple Note as CIR document."""

        cursor = self.notes_connection.cursor()
        query = """
        SELECT 
            ZICCLOUDSYNCINGOBJECT.ZTITLE as title,
            ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE as modified_date,
            ZICCLOUDSYNCINGOBJECT.ZCREATIONDATE as creation_date,
            ZICNOTEDATA.ZDATA as content
        FROM ZICCLOUDSYNCINGOBJECT
        LEFT JOIN ZICNOTEDATA ON ZICCLOUDSYNCINGOBJECT.ZNOTEDATA = ZICNOTEDATA.Z_PK
        WHERE ZICCLOUDSYNCINGOBJECT.Z_PK = ?
        """

        cursor.execute(query, (note_id,))
        row = cursor.fetchone()

        if not row:
            raise Exception(f"Note {note_id} not found")

        content_text = ""
        if row["content"]:
            try:
                content_text = self._extract_note_text(row["content"])
            except Exception:
                content_text = "Content extraction not supported"

        return CIRDocument(
            title=row["title"] or f"Note {note_id}",
            document_type=SourceSystem.APPLE_NOTES,
            root=CIRNode(
                type=ContentType.NOTE,
                title=row["title"] or f"Note {note_id}",
                text=content_text,
                provenance=[
                    Provenance(
                        source_system=SourceSystem.APPLE_NOTES,
                        source_id=note_id,
                        extraction_method="sqlite_query",
                    )
                ],
            ),
            metadata=DocumentMetadata(
                source_format="apple_notes",
                source_path=note_id,
                created_at=self._apple_timestamp_to_datetime(row["creation_date"]),
                modified_at=self._apple_timestamp_to_datetime(row["modified_date"]),
            ),
        )

    async def _list_calendar_events(self, filters: Optional[Dict[str, Any]] = None) -> List[ResourceRef]:
        """List Calendar events."""

        events: List[ResourceRef] = []

        if not self.calendar_connection:
            return events

        cursor = self.calendar_connection.cursor()
        query = """
            SELECT 
                ROWID as event_id,
                summary as title,
                start_date,
                end_date,
                creation_date,
                last_modified
            FROM CalendarItem
            WHERE summary IS NOT NULL
            """

        params: List[Any] = []
        if filters:
            if "start_after" in filters:
                query += " AND start_date > ?"
                params.append(filters["start_after"].timestamp())

            if "end_before" in filters:
                query += " AND end_date < ?"
                params.append(filters["end_before"].timestamp())

        query += " ORDER BY start_date DESC"

        if filters and "limit" in filters:
            query += " LIMIT ?"
            params.append(filters["limit"])

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        except Exception:
            return events

        for row in rows:
            events.append(
                ResourceRef(
                    id=f"event:{row['event_id']}",
                    name=row["title"] or f"Event {row['event_id']}",
                    path=str(row["event_id"]),
                    resource_type="event",
                    created_at=datetime.fromtimestamp(row["creation_date"]) if row["creation_date"] else None,
                    modified_at=datetime.fromtimestamp(row["last_modified"]) if row["last_modified"] else None,
                    metadata={
                        "event_id": row["event_id"],
                        "start_date": datetime.fromtimestamp(row["start_date"]) if row["start_date"] else None,
                        "end_date": datetime.fromtimestamp(row["end_date"]) if row["end_date"] else None,
                        "source": "apple_calendar",
                    },
                )
            )

        return events

    async def _list_icloud_documents(self, filters: Optional[Dict[str, Any]] = None) -> List[ResourceRef]:
        """List iCloud Drive documents."""

        documents: List[ResourceRef] = []

        if not self.enable_icloud:
            return documents

        icloud_path = Path(self.icloud_path)
        supported_extensions = {".txt", ".md", ".rtf", ".pdf", ".doc", ".docx", ".pages"}

        try:
            for file_path in icloud_path.rglob("*"):
                if not file_path.is_file() or file_path.suffix.lower() not in supported_extensions:
                    continue

                if filters:
                    if "extension" in filters and file_path.suffix.lower() != filters["extension"]:
                        continue
                    if "min_size" in filters and file_path.stat().st_size < filters["min_size"]:
                        continue

                stat = file_path.stat()
                relative_path = file_path.relative_to(icloud_path)
                documents.append(
                    ResourceRef(
                        id=f"document:{relative_path}",
                        name=file_path.name,
                        path=str(relative_path),
                        resource_type="document",
                        size=stat.st_size,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        modified_at=datetime.fromtimestamp(stat.st_mtime),
                        metadata={
                            "file_extension": file_path.suffix,
                            "full_path": str(file_path),
                            "source": "icloud_drive",
                        },
                    )
                )
        except Exception:
            return documents

        return documents

    def _apple_timestamp_to_datetime(self, timestamp: Optional[float]) -> Optional[datetime]:
        """Convert Apple timestamp to datetime."""

        if timestamp is None:
            return None

        return datetime(2001, 1, 1) + timedelta(seconds=timestamp)

    def _extract_note_text(self, content_data: bytes) -> str:
        """Extract text from Apple Notes binary content."""

        try:
            content_str = content_data.decode("utf-8", errors="ignore")
            lines = []
            for line in content_str.split("\n"):
                clean_line = "".join(char for char in line if char.isprintable())
                if clean_line.strip():
                    lines.append(clean_line.strip())
            return "\n".join(lines)
        except Exception:
            return "Content extraction failed"

    async def _search_notes(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[ResourceRef]:
        """Search Apple Notes."""

        results: List[ResourceRef] = []

        if not self.notes_connection:
            return results

        cursor = self.notes_connection.cursor()
        search_query = """
            SELECT 
                ZICCLOUDSYNCINGOBJECT.Z_PK as note_id,
                ZICCLOUDSYNCINGOBJECT.ZTITLE as title,
                ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE as modified_date,
                ZICCLOUDSYNCINGOBJECT.ZCREATIONDATE as creation_date
            FROM ZICCLOUDSYNCINGOBJECT
            WHERE ZICCLOUDSYNCINGOBJECT.ZTITLE LIKE ?
            ORDER BY ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE DESC
            """

        try:
            cursor.execute(search_query, (f"%{query}%",))
            rows = cursor.fetchall()
        except Exception:
            return results

        for row in rows:
            results.append(
                ResourceRef(
                    id=f"note:{row['note_id']}",
                    name=row["title"] or f"Note {row['note_id']}",
                    path=str(row["note_id"]),
                    resource_type="note",
                    created_at=self._apple_timestamp_to_datetime(row["creation_date"]),
                    modified_at=self._apple_timestamp_to_datetime(row["modified_date"]),
                    metadata={
                        "search_query": query,
                        "search_type": "title_match",
                        "source": "apple_notes",
                    },
                )
            )

        return results

    async def _search_events(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[ResourceRef]:
        """Search Calendar events."""

        results: List[ResourceRef] = []

        if not self.calendar_connection:
            return results

        cursor = self.calendar_connection.cursor()
        search_query = """
            SELECT 
                ROWID as event_id,
                summary as title,
                start_date,
                end_date,
                creation_date,
                last_modified
            FROM CalendarItem
            WHERE summary LIKE ?
            ORDER BY start_date DESC
            """

        try:
            cursor.execute(search_query, (f"%{query}%",))
            rows = cursor.fetchall()
        except Exception:
            return results

        for row in rows:
            results.append(
                ResourceRef(
                    id=f"event:{row['event_id']}",
                    name=row["title"] or f"Event {row['event_id']}",
                    path=str(row["event_id"]),
                    resource_type="event",
                    created_at=datetime.fromtimestamp(row["creation_date"]) if row["creation_date"] else None,
                    modified_at=datetime.fromtimestamp(row["last_modified"]) if row["last_modified"] else None,
                    metadata={
                        "search_query": query,
                        "search_type": "title_match",
                        "source": "apple_calendar",
                        "start_date": datetime.fromtimestamp(row["start_date"]) if row["start_date"] else None,
                    },
                )
            )

        return results

    async def _search_documents(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[ResourceRef]:
        """Search iCloud documents."""

        results: List[ResourceRef] = []

        if not self.enable_icloud:
            return results

        icloud_path = Path(self.icloud_path)
        query_lower = query.lower()

        try:
            for file_path in icloud_path.rglob("*"):
                if not file_path.is_file() or query_lower not in file_path.name.lower():
                    continue

                stat = file_path.stat()
                relative_path = file_path.relative_to(icloud_path)
                results.append(
                    ResourceRef(
                        id=f"document:{relative_path}",
                        name=file_path.name,
                        path=str(relative_path),
                        resource_type="document",
                        size=stat.st_size,
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        modified_at=datetime.fromtimestamp(stat.st_mtime),
                        metadata={
                            "search_query": query,
                            "search_type": "filename_match",
                            "source": "icloud_drive",
                        },
                    )
                )
        except Exception:
            return results

        return results

    async def _create_note(
        self, cir_content: CIRDocument, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create new Apple Note (placeholder - requires AppleScript or private APIs)."""

        raise Exception("Note creation not implemented - requires AppleScript integration")

    async def _create_event(
        self, cir_content: CIRDocument, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create new Calendar event (placeholder - requires EventKit integration)."""

        raise Exception("Event creation not implemented - requires EventKit integration")

    async def _get_note_metadata(self, note_id: str) -> Dict[str, Any]:
        """Return metadata for a note resource."""

        cir_doc = await self._read_note_as_cir(note_id)
        return cir_doc.metadata.model_dump()

    async def _get_event_metadata(self, event_id: str) -> Dict[str, Any]:
        """Return metadata for a calendar event."""

        cir_doc = await self._read_event_as_cir(event_id)
        return cir_doc.metadata.model_dump()

    async def _get_document_metadata(self, doc_path: str) -> Dict[str, Any]:
        """Return metadata for an iCloud document."""

        full_path = Path(self.icloud_path) / doc_path
        stat = full_path.stat()
        return {
            "path": str(full_path),
            "size": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "created_at": datetime.fromtimestamp(stat.st_ctime),
        }

    async def _read_event_as_cir(
        self, event_id: str, options: Optional[Dict[str, Any]] = None
    ) -> CIRDocument:
        """Read Calendar event as CIR document."""

        cursor = self.calendar_connection.cursor()
        query = """
        SELECT 
            ROWID as event_id,
            summary as title,
            description,
            location,
            start_date,
            end_date,
            creation_date,
            last_modified
        FROM CalendarItem
        WHERE ROWID = ?
        """

        cursor.execute(query, (event_id,))
        row = cursor.fetchone()

        if not row:
            raise Exception(f"Event {event_id} not found")

        start_time = datetime.fromtimestamp(row["start_date"]) if row["start_date"] else None
        end_time = datetime.fromtimestamp(row["end_date"]) if row["end_date"] else None

        event_node = CIRNode(
            type=ContentType.NOTE,
            title=row["title"] or f"Event {event_id}",
            text=row["description"] or "",
            metadata={
                "location": row["location"],
                "start_time": start_time,
                "end_time": end_time,
            },
            provenance=[
                Provenance(
                    source_system=SourceSystem.APPLE_CALENDAR,
                    source_id=event_id,
                    extraction_method="sqlite_query",
                )
            ],
        )

        calendar_event = CalendarEvent(
            id=str(row["event_id"]),
            title=event_node.title or "",
            description=event_node.text or "",
            start_time=start_time,
            end_time=end_time,
            location=row["location"],
            status=EventStatus.CONFIRMED,
            priority=EventPriority.NORMAL,
            metadata={"source": "apple_calendar"},
        )

        calendar_extension = CalendarExtension(
            events=[calendar_event],
            calendar_name="Apple Calendar",
            metadata={"source": "apple_calendar"},
        )

        metadata = DocumentMetadata(
            source_format="apple_calendar",
            source_path=str(event_id),
            created_at=datetime.fromtimestamp(row["creation_date"]) if row["creation_date"] else None,
            modified_at=datetime.fromtimestamp(row["last_modified"]) if row["last_modified"] else None,
        )

        metadata.custom_fields["calendar_extension"] = calendar_extension.model_dump()

        return CIRDocument(
            title=row["title"] or f"Event {event_id}",
            document_type=SourceSystem.APPLE_CALENDAR,
            root=event_node,
            metadata=metadata,
        )

    async def _read_document_as_cir(
        self, doc_path: str, options: Optional[Dict[str, Any]] = None
    ) -> CIRDocument:
        """Read iCloud document metadata as CIR document."""

        full_path = Path(self.icloud_path) / doc_path
        stat = full_path.stat()
        metadata = DocumentMetadata(
            source_format=full_path.suffix,
            source_path=str(doc_path),
            file_size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
        )

        node = CIRNode(
            type=ContentType.DOCUMENT,
            title=full_path.name,
            text="",
            provenance=[
                Provenance(
                    source_system=SourceSystem.ICLOUD,
                    source_id=str(doc_path),
                    source_path=str(full_path),
                    extraction_method="filesystem",
                )
            ],
        )

        return CIRDocument(
            title=full_path.name,
            document_type=SourceSystem.ICLOUD,
            root=node,
            metadata=metadata,
        )

    async def _update_note(
        self, note_id: str, cir_content: CIRDocument, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Placeholder for updating an Apple Note."""

        raise Exception("Note update not implemented - requires AppleScript integration")

    async def _update_event(
        self, event_id: str, cir_content: CIRDocument, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Placeholder for updating a calendar event."""

        raise Exception("Event update not implemented - requires EventKit integration")

    async def _delete_note(self, note_id: str) -> Dict[str, Any]:
        """Placeholder for deleting an Apple Note."""

        raise Exception("Note deletion not implemented - requires AppleScript integration")

    async def _delete_event(self, event_id: str) -> Dict[str, Any]:
        """Placeholder for deleting a calendar event."""

        raise Exception("Event deletion not implemented - requires EventKit integration")


__all__ = ["AppleConnector"]
