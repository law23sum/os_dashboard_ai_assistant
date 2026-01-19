"""Data Aggregator - Processes and normalizes data from various sources."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


# Compatibility types for modules that import CIR structures from this module.
class DocumentType(Enum):
    DOCUMENT = "document"
    REPORT = "report"


class SourceType(Enum):
    LOCAL = "local"
    REMOTE = "remote"


@dataclass
class CIRDocument:
    id: str = ""
    content: str = ""
    doc_type: DocumentType = DocumentType.DOCUMENT
    source: SourceType = SourceType.LOCAL


class DataAggregator:
    """Aggregates and normalizes data from various API connectors."""

    def __init__(self):
        self.normalized_data = {}

    def normalize_email_data(self, raw_emails: List[Dict]) -> List[Dict]:
        """Normalize email data to common format."""
        normalized = []
        for email in raw_emails:
            normalized.append(
                {
                    "id": email.get("id"),
                    "subject": email.get("subject", ""),
                    "sender": email.get("from", {}).get("email", ""),
                    "timestamp": self._parse_timestamp(email.get("timestamp")),
                    "content": email.get("body", ""),
                    "type": "email",
                }
            )
        return normalized

    def normalize_calendar_data(self, raw_events: List[Dict]) -> List[Dict]:
        """Normalize calendar event data to common format."""
        normalized = []
        for event in raw_events:
            normalized.append(
                {
                    "id": event.get("id"),
                    "title": event.get("summary", ""),
                    "start_time": self._parse_timestamp(
                        event.get("start", {}).get("dateTime")
                    ),
                    "end_time": self._parse_timestamp(
                        event.get("end", {}).get("dateTime")
                    ),
                    "location": event.get("location", ""),
                    "type": "calendar_event",
                }
            )
        return normalized

    def normalize_document_data(self, raw_docs: List[Dict]) -> List[Dict]:
        """Normalize document data to common format."""
        normalized = []
        for doc in raw_docs:
            normalized.append(
                {
                    "id": doc.get("id"),
                    "name": doc.get("name", ""),
                    "type": doc.get("mimeType", "").split("/")[-1],
                    "size": doc.get("size", 0),
                    "modified_time": self._parse_timestamp(doc.get("modifiedTime")),
                    "source": "document",
                }
            )
        return normalized

    def _parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Parse various timestamp formats into datetime objects."""
        if not timestamp:
            return None

        if isinstance(timestamp, str):
            # Try common formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
        return None

    def aggregate_all_sources(
        self, sources_data: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """Aggregate data from all sources into normalized format."""
        aggregated = {"emails": [], "calendar_events": [], "documents": [], "tasks": []}

        for source_type, data in sources_data.items():
            if source_type == "gmail":
                aggregated["emails"].extend(self.normalize_email_data(data))
            elif source_type in ["google_calendar", "apple_calendar"]:
                aggregated["calendar_events"].extend(self.normalize_calendar_data(data))
            elif source_type in ["word", "excel", "onenote", "pdf"]:
                aggregated["documents"].extend(self.normalize_document_data(data))

        return aggregated
