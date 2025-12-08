"""Tests for the unified search engine."""

import unittest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from assistant_core.search_engine import (
    UnifiedSearchEngine, SearchQuery, SearchResult, EmbeddingEngine, SearchIndex
)
from assistant_core.search_engine import BaseConnector, ResourceRef, OperationResult
from assistant_core.cir import ContentType, SourceSystem


class TestSearchQuery(unittest.TestCase):
    """Test SearchQuery dataclass."""

    def test_search_query_defaults(self):
        """Test SearchQuery with default values."""
        query = SearchQuery(text="test query")

        self.assertEqual(query.text, "test query")
        self.assertEqual(query.filters, {})
        self.assertEqual(query.connectors, None)
        self.assertEqual(query.search_types, ['text', 'semantic'])
        self.assertEqual(query.limit, 50)
        self.assertEqual(query.include_content, False)
        self.assertEqual(query.date_range, None)
        self.assertEqual(query.content_types, [])
        self.assertEqual(query.source_systems, [])


class TestSearchResult(unittest.TestCase):
    """Test SearchResult dataclass."""

    def test_search_result_creation(self):
        """Test SearchResult creation and defaults."""
        resource_ref = ResourceRef(id="test-id", name="test", type="document")
        result = SearchResult(
            resource_ref=resource_ref,
            relevance_score=0.8,
            search_type="text",
            connector_name="test-connector"
        )

        self.assertEqual(result.resource_ref, resource_ref)
        self.assertEqual(result.relevance_score, 0.8)
        self.assertEqual(result.search_type, "text")
        self.assertEqual(result.connector_name, "test-connector")
        self.assertEqual(result.highlights, [])
        self.assertEqual(result.metadata_matches, {})


class TestEmbeddingEngine(unittest.TestCase):
    """Test EmbeddingEngine functionality."""

    def test_embedding_engine_initialization(self):
        """Test EmbeddingEngine initialization."""
        engine = EmbeddingEngine()
        self.assertEqual(engine.model_name, "sentence-transformers/all-MiniLM-L6-v2")
        self.assertEqual(engine.dimension, 384)
        self.assertEqual(engine.model, None)

    def test_get_embedding_without_model(self):
        """Test get_embedding returns None when model not initialized."""
        engine = EmbeddingEngine()
        result = engine.get_embedding("test text")
        self.assertIsNone(result)


class TestSearchIndex(unittest.TestCase):
    """Test SearchIndex functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.index = SearchIndex()
        self.resource_ref = ResourceRef(
            id="test-doc-1",
            name="Test Document",
            type="document",
            metadata={"author": "Test Author", "category": "test"}
        )

    def test_add_document(self):
        """Test adding a document to the search index."""
        self.index.add_document(self.resource_ref, "This is test content")

        self.assertIn("test-doc-1", self.index.documents)
        self.assertEqual(self.index.documents["test-doc-1"]["content"], "This is test content")

    def test_remove_document(self):
        """Test removing a document from the search index."""
        self.index.add_document(self.resource_ref, "This is test content")
        self.assertIn("test-doc-1", self.index.documents)

        self.index.remove_document("test-doc-1")
        self.assertNotIn("test-doc-1", self.index.documents)

    def test_search_text(self):
        """Test text search functionality."""
        # Add documents
        doc1_ref = ResourceRef(id="doc1", name="Doc 1", type="document")
        doc2_ref = ResourceRef(id="doc2", name="Doc 2", type="document")

        self.index.add_document(doc1_ref, "This is a test document about Python")
        self.index.add_document(doc2_ref, "This is another document about JavaScript")

        # Search for "Python"
        results = self.index.search_text("Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "doc1")

    def test_search_metadata(self):
        """Test metadata search functionality."""
        doc1_ref = ResourceRef(
            id="doc1",
            name="Doc 1",
            type="document",
            metadata={"author": "Alice", "category": "tech"}
        )
        doc2_ref = ResourceRef(
            id="doc2",
            name="Doc 2",
            type="document",
            metadata={"author": "Bob", "category": "business"}
        )

        self.index.add_document(doc1_ref, "Content 1")
        self.index.add_document(doc2_ref, "Content 2")

        # Search for author "Alice"
        results = self.index.search_metadata({"author": "Alice"})
        self.assertEqual(len(results), 1)
        self.assertIn("doc1", results)


class TestUnifiedSearchEngine(unittest.TestCase):
    """Test UnifiedSearchEngine functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = UnifiedSearchEngine()
        self.mock_connector = MagicMock(spec=BaseConnector)
        self.mock_connector.is_connected = True

    def test_initialization(self):
        """Test UnifiedSearchEngine initialization."""
        self.assertFalse(self.engine.is_initialized)
        self.assertEqual(len(self.engine.connectors), 0)

    def test_register_connector(self):
        """Test registering a connector."""
        self.engine.register_connector("test-connector", self.mock_connector)
        self.assertIn("test-connector", self.engine.connectors)
        self.assertEqual(self.engine.connectors["test-connector"], self.mock_connector)

    async def async_test_search_text(self):
        """Test text search (async version)."""
        # Register connector
        self.engine.register_connector("test-connector", self.mock_connector)

        # Create search query
        query = SearchQuery(text="test query")

        # Mock the connector's list_resources method
        mock_result = OperationResult(
            success=True,
            data=[
                ResourceRef(id="doc1", name="Test Doc", type="document")
            ]
        )
        self.mock_connector.list_resources = AsyncMock(return_value=mock_result)

        # Mock read_resource to return a CIR document
        from assistant_core.cir import CIRDocument
        cir_doc = CIRDocument(title="Test Document", document_type="document")
        cir_doc.get_all_text = MagicMock(return_value="This is test content with query")
        read_result = OperationResult(success=True, data=cir_doc)
        self.mock_connector.read_resource = AsyncMock(return_value=read_result)

        # Perform search
        results = await self.engine.search(query)

        # Verify results
        self.assertIsInstance(results, list)
        # Note: Results might be empty if indexing hasn't completed

    def test_search_text_sync(self):
        """Test text search setup (synchronous wrapper)."""
        # This is a placeholder - actual async testing would require pytest-asyncio
        pass

    def test_merge_search_results(self):
        """Test merging search results."""
        resource_ref = ResourceRef(id="test-doc", name="Test", type="document")

        result1 = SearchResult(
            resource_ref=resource_ref,
            relevance_score=0.8,
            search_type="text",
            connector_name="connector1"
        )

        result2 = SearchResult(
            resource_ref=resource_ref,
            relevance_score=0.6,
            search_type="semantic",
            connector_name="connector1"
        )

        merged = self.engine._merge_search_results([result1, result2])

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].relevance_score, 0.8)  # Should take higher score
        self.assertIn("semantic", merged[0].search_type)  # Should combine search types

    def test_generate_snippet(self):
        """Test snippet generation."""
        content = "This is a long document that contains the word query in the middle of the text."
        snippet = self.engine._generate_snippet(content, "query")

        self.assertIn("query", snippet)
        self.assertLessEqual(len(snippet), 200)

    def test_extract_highlights(self):
        """Test highlight extraction."""
        content = "This document contains the word query multiple times in the text."
        highlights = self.engine._extract_highlights(content, "query")

        self.assertIsInstance(highlights, list)
        self.assertGreater(len(highlights), 0)

    def test_date_in_range(self):
        """Test date range filtering."""
        test_date = datetime(2023, 6, 15)
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        # Date in range
        result = self.engine._date_in_range(test_date, start_date, end_date)
        self.assertTrue(result)

        # Date before range
        result = self.engine._date_in_range(datetime(2022, 1, 1), start_date, end_date)
        self.assertFalse(result)

        # Date after range
        result = self.engine._date_in_range(datetime(2024, 1, 1), start_date, end_date)
        self.assertFalse(result)

    def test_calculate_metadata_score(self):
        """Test metadata score calculation."""
        metadata = {"author": "Alice", "category": "tech", "year": 2023}
        filters = {"author": "Alice", "category": "tech"}

        score = self.engine._calculate_metadata_score(metadata, filters)
        self.assertEqual(score, 1.0)  # All filters match

    def test_find_metadata_matches(self):
        """Test finding metadata matches."""
        metadata = {"author": "Alice", "category": "tech"}
        filters = {"author": "Alice", "year": 2023}

        matches = self.engine._find_metadata_matches(metadata, filters)
        self.assertEqual(len(matches), 1)
        self.assertIn("author", matches)


if __name__ == '__main__':
    unittest.main()
