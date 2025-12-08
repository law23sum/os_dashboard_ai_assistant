"""Tests for data aggregator functionality."""

import unittest
from datetime import datetime
from assistant_core.data_aggregator import DataAggregator


class TestDataAggregator(unittest.TestCase):
    """Test cases for DataAggregator."""

    def test_initialization(self):
        """Test DataAggregator initialization."""
        aggregator = DataAggregator()
        assert aggregator.normalized_data == {}

    def test_normalize_email_data(self):
        """Test email data normalization."""
        aggregator = DataAggregator()

        raw_emails = [
            {
                "id": "123",
                "subject": "Test Email",
                "from": {"email": "sender@example.com"},
                "timestamp": "2023-01-01T10:00:00Z",
                "body": "Test content"
            },
            {
                "id": "456",
                "subject": "Another Email",
                "from": {"email": "sender2@example.com"},
                "timestamp": "2023-01-02T11:00:00Z",
                "body": "More content"
            }
        ]

        normalized = aggregator.normalize_email_data(raw_emails)

        assert len(normalized) == 2
        assert normalized[0]["id"] == "123"
        assert normalized[0]["subject"] == "Test Email"
        assert normalized[0]["sender"] == "sender@example.com"
        assert normalized[0]["content"] == "Test content"
        assert normalized[0]["type"] == "email"
        assert isinstance(normalized[0]["timestamp"], datetime)

    def test_normalize_email_data_missing_fields(self):
        """Test email normalization with missing fields."""
        aggregator = DataAggregator()

        raw_emails = [
            {
                "id": "123",
                # Missing subject, from, timestamp, body
            }
        ]

        normalized = aggregator.normalize_email_data(raw_emails)

        assert len(normalized) == 1
        assert normalized[0]["id"] == "123"
        assert normalized[0]["subject"] == ""
        assert normalized[0]["sender"] == ""
        assert normalized[0]["content"] == ""
        assert normalized[0]["type"] == "email"

    def test_normalize_calendar_data(self):
        """Test calendar event data normalization."""
        aggregator = DataAggregator()

        raw_events = [
            {
                "id": "event1",
                "summary": "Meeting",
                "start": {"dateTime": "2023-01-01T10:00:00Z"},
                "end": {"dateTime": "2023-01-01T11:00:00Z"},
                "location": "Conference Room"
            }
        ]

        normalized = aggregator.normalize_calendar_data(raw_events)

        assert len(normalized) == 1
        assert normalized[0]["id"] == "event1"
        assert normalized[0]["title"] == "Meeting"
        assert normalized[0]["location"] == "Conference Room"
        assert normalized[0]["type"] == "calendar_event"
        assert isinstance(normalized[0]["start_time"], datetime)
        assert isinstance(normalized[0]["end_time"], datetime)

    def test_normalize_document_data(self):
        """Test document data normalization."""
        aggregator = DataAggregator()

        raw_docs = [
            {
                "id": "doc1",
                "name": "test.pdf",
                "mimeType": "application/pdf",
                "size": 1024,
                "modifiedTime": "2023-01-01T10:00:00Z"
            }
        ]

        normalized = aggregator.normalize_document_data(raw_docs)

        assert len(normalized) == 1
        assert normalized[0]["id"] == "doc1"
        assert normalized[0]["name"] == "test.pdf"
        assert normalized[0]["type"] == "pdf"
        assert normalized[0]["size"] == 1024
        assert normalized[0]["source"] == "document"
        assert isinstance(normalized[0]["modified_time"], datetime)

    def test_parse_timestamp_various_formats(self):
        """Test timestamp parsing with various formats."""
        aggregator = DataAggregator()

        # Test ISO format with milliseconds
        ts1 = aggregator._parse_timestamp("2023-01-01T10:00:00.123Z")
        assert ts1 is not None
        assert ts1.year == 2023

        # Test ISO format without milliseconds
        ts2 = aggregator._parse_timestamp("2023-01-01T10:00:00Z")
        assert ts2 is not None

        # Test date only format
        ts3 = aggregator._parse_timestamp("2023-01-01")
        assert ts3 is not None

        # Test invalid format
        ts4 = aggregator._parse_timestamp("invalid")
        assert ts4 is None

        # Test None input
        ts5 = aggregator._parse_timestamp(None)
        assert ts5 is None

    def test_aggregate_all_sources(self):
        """Test aggregating data from multiple sources."""
        aggregator = DataAggregator()

        sources_data = {
            "gmail": [
                {
                    "id": "email1",
                    "subject": "Test Email",
                    "from": {"email": "test@example.com"},
                    "timestamp": "2023-01-01T10:00:00Z",
                    "body": "Content"
                }
            ],
            "google_calendar": [
                {
                    "id": "event1",
                    "summary": "Meeting",
                    "start": {"dateTime": "2023-01-01T10:00:00Z"},
                    "end": {"dateTime": "2023-01-01T11:00:00Z"}
                }
            ],
            "word": [
                {
                    "id": "doc1",
                    "name": "test.docx",
                    "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "size": 2048,
                    "modifiedTime": "2023-01-01T10:00:00Z"
                }
            ]
        }

        aggregated = aggregator.aggregate_all_sources(sources_data)

        assert len(aggregated["emails"]) == 1
        assert len(aggregated["calendar_events"]) == 1
        assert len(aggregated["documents"]) == 1
        assert len(aggregated["tasks"]) == 0

        # Verify email data
        assert aggregated["emails"][0]["id"] == "email1"
        assert aggregated["emails"][0]["type"] == "email"

        # Verify calendar data
        assert aggregated["calendar_events"][0]["id"] == "event1"
        assert aggregated["calendar_events"][0]["type"] == "calendar_event"

        # Verify document data
        assert aggregated["documents"][0]["id"] == "doc1"
        assert aggregated["documents"][0]["type"] == "vnd.openxmlformats-officedocument.wordprocessingml.document"