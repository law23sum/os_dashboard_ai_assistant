"""
Unified Search and Embedding System

Provides semantic search, vector embeddings, and cross-connector search capabilities
"""

import asyncio
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from datetime import datetime

from .cir import CIRDocument, ContentType, SourceSystem


@dataclass
class ResourceRef:
    """Reference to a resource in a connector"""
    id: str
    name: str
    type: str
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OperationResult:
    """Standard result format for operations"""
    success: bool
    data: Any = None
    error: Optional[str] = None


class BaseConnector:
    """Base class for connectors"""
    def __init__(self):
        self.is_connected = False

    async def connect(self):
        self.is_connected = True

    async def list_resources(self):
        return OperationResult(success=True, data=[])

    async def read_resource(self, resource_id: str):
        return OperationResult(success=True, data=None)


@dataclass
class SearchResult:
    """Unified search result across all connectors"""

    resource_ref: ResourceRef
    relevance_score: float
    search_type: str  # 'text', 'semantic', 'metadata', 'hybrid'
    connector_name: str
    snippet: str = ""
    highlights: List[str] = None
    embedding_distance: Optional[float] = None
    metadata_matches: Dict[str, Any] = None

    def __post_init__(self):
        if self.highlights is None:
            self.highlights = []
        if self.metadata_matches is None:
            self.metadata_matches = {}


@dataclass
class SearchQuery:
    """Structured search query with multiple search modes"""

    text: str
    filters: Dict[str, Any] = None
    connectors: List[str] = None  # Specific connectors to search
    search_types: List[str] = None  # 'text', 'semantic', 'metadata'
    limit: int = 50
    include_content: bool = False
    date_range: Tuple[Optional[datetime], Optional[datetime]] = None
    content_types: List[ContentType] = None
    source_systems: List[SourceSystem] = None

    def __post_init__(self):
        if self.filters is None:
            self.filters = {}
        if self.search_types is None:
            self.search_types = ['text', 'semantic']
        if self.content_types is None:
            self.content_types = []
        if self.source_systems is None:
            self.source_systems = []


class EmbeddingEngine:
    """Vector embedding engine for semantic search"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # Default for MiniLM
        self.embeddings_cache = {}
        self.cache_file = "embeddings_cache.json"
        self._load_cache()

    async def initialize(self):
        """Initialize the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            return True
        except ImportError:
            print("Warning: sentence-transformers not available. Semantic search disabled.")
            return False
        except Exception as e:
            print(f"Warning: Failed to initialize embedding model: {e}")
            return False

    def _load_cache(self):
        """Load embeddings cache from disk"""
        try:
            if Path(self.cache_file).exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Convert lists back to numpy arrays
                    for key, value in cache_data.items():
                        if isinstance(value, list):
                            self.embeddings_cache[key] = np.array(value)
        except Exception:
            self.embeddings_cache = {}

    def _save_cache(self):
        """Save embeddings cache to disk"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            cache_data = {}
            for key, value in self.embeddings_cache.items():
                if isinstance(value, np.ndarray):
                    cache_data[key] = value.tolist()
                else:
                    cache_data[key] = value

            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception:
            pass

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text with caching"""
        if not self.model:
            return None

        # Create cache key
        cache_key = hashlib.md5(text.encode()).hexdigest()

        # Check cache
        if cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]

        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)

            # Cache the result
            self.embeddings_cache[cache_key] = embedding

            # Periodically save cache
            if len(self.embeddings_cache) % 100 == 0:
                self._save_cache()

            return embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)

        except Exception:
            return 0.0


class SearchIndex:
    """In-memory search index for fast text and metadata search"""

    def __init__(self):
        self.documents = {}  # resource_id -> document_data
        self.text_index = {}  # word -> set of resource_ids
        self.metadata_index = {}  # field -> value -> set of resource_ids
        self.embeddings_index = {}  # resource_id -> embedding

    def add_document(self, resource_ref: ResourceRef, content: str = "",
                    embedding: Optional[np.ndarray] = None):
        """Add document to search index"""
        resource_id = resource_ref.id

        # Store document data
        self.documents[resource_id] = {
            'resource_ref': resource_ref,
            'content': content,
            'indexed_at': datetime.utcnow()
        }

        # Index text content
        if content:
            words = self._tokenize(content)
            for word in words:
                if word not in self.text_index:
                    self.text_index[word] = set()
                self.text_index[word].add(resource_id)

        # Index metadata
        if resource_ref.metadata:
            for field, value in resource_ref.metadata.items():
                if field not in self.metadata_index:
                    self.metadata_index[field] = {}

                value_str = str(value).lower()
                if value_str not in self.metadata_index[field]:
                    self.metadata_index[field][value_str] = set()
                self.metadata_index[field][value_str].add(resource_id)

        # Store embedding
        if embedding is not None:
            self.embeddings_index[resource_id] = embedding

    def remove_document(self, resource_id: str):
        """Remove document from search index"""
        if resource_id not in self.documents:
            return

        # Remove from text index
        content = self.documents[resource_id]['content']
        if content:
            words = self._tokenize(content)
            for word in words:
                if word in self.text_index:
                    self.text_index[word].discard(resource_id)
                    if not self.text_index[word]:
                        del self.text_index[word]

        # Remove from metadata index
        resource_ref = self.documents[resource_id]['resource_ref']
        if resource_ref.metadata:
            for field, value in resource_ref.metadata.items():
                value_str = str(value).lower()
                if field in self.metadata_index and value_str in self.metadata_index[field]:
                    self.metadata_index[field][value_str].discard(resource_id)
                    if not self.metadata_index[field][value_str]:
                        del self.metadata_index[field][value_str]

        # Remove from embeddings
        self.embeddings_index.pop(resource_id, None)

        # Remove document
        del self.documents[resource_id]

    def search_text(self, query: str, limit: int = 50) -> List[Tuple[str, float]]:
        """Search text content and return (resource_id, score) pairs"""
        query_words = self._tokenize(query)
        if not query_words:
            return []

        # Find documents containing query words
        candidate_docs = set()
        word_scores = {}

        for word in query_words:
            if word in self.text_index:
                docs_with_word = self.text_index[word]
                candidate_docs.update(docs_with_word)

                # Simple TF-IDF-like scoring
                idf = len(self.documents) / len(docs_with_word) if docs_with_word else 1
                word_scores[word] = idf

        # Score documents
        doc_scores = []
        for doc_id in candidate_docs:
            content = self.documents[doc_id]['content'].lower()
            score = 0

            for word in query_words:
                if word in content:
                    tf = content.count(word)
                    score += tf * word_scores.get(word, 1)

            if score > 0:
                doc_scores.append((doc_id, score))

        # Sort by score and limit
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        return doc_scores[:limit]

    def search_metadata(self, filters: Dict[str, Any]) -> List[str]:
        """Search metadata and return matching resource IDs"""
        if not filters:
            return list(self.documents.keys())

        matching_docs = None

        for field, value in filters.items():
            field_matches = set()

            if field in self.metadata_index:
                value_str = str(value).lower()

                # Exact match
                if value_str in self.metadata_index[field]:
                    field_matches.update(self.metadata_index[field][value_str])

                # Partial match for string values
                if isinstance(value, str):
                    for indexed_value, docs in self.metadata_index[field].items():
                        if value_str in indexed_value:
                            field_matches.update(docs)

            # Intersect with previous results
            if matching_docs is None:
                matching_docs = field_matches
            else:
                matching_docs = matching_docs.intersection(field_matches)

        return list(matching_docs) if matching_docs else []

    def search_semantic(self, query_embedding: np.ndarray, limit: int = 50,
                       threshold: float = 0.3) -> List[Tuple[str, float]]:
        """Search using semantic similarity"""
        if not self.embeddings_index:
            return []

        similarities = []

        for resource_id, embedding in self.embeddings_index.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            if similarity >= threshold:
                similarities.append((resource_id, similarity))

        # Sort by similarity and limit
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        import re
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out very short words
        return [word for word in words if len(word) > 2]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            return float(np.dot(a, b) / (norm_a * norm_b))
        except Exception:
            return 0.0


class UnifiedSearchEngine:
    """Main search engine that coordinates across all connectors"""

    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.embedding_engine = EmbeddingEngine()
        self.search_index = SearchIndex()
        self.is_initialized = False
        self.indexing_tasks = {}

    async def initialize(self):
        """Initialize the search engine"""
        if self.is_initialized:
            return

        # Initialize embedding engine
        await self.embedding_engine.initialize()

        self.is_initialized = True

    def register_connector(self, name: str, connector: BaseConnector):
        """Register a connector for search"""
        self.connectors[name] = connector

    async def index_connector_resources(self, connector_name: str,
                                      resource_types: List[str] = None,
                                      force_reindex: bool = False):
        """Index all resources from a connector"""
        if connector_name not in self.connectors:
            raise ValueError(f"Connector {connector_name} not registered")

        connector = self.connectors[connector_name]

        if not connector.is_connected:
            await connector.connect()

        try:
            # List resources
            if resource_types:
                all_resources = []
                for resource_type in resource_types:
                    result = await connector.list_resources(resource_type=resource_type)
                    if result.success:
                        all_resources.extend(result.data)
            else:
                result = await connector.list_resources()
                if not result.success:
                    raise Exception(f"Failed to list resources: {result.error}")
                all_resources = result.data

            # Index each resource
            indexed_count = 0
            for resource_ref in all_resources:
                try:
                    await self._index_resource(connector_name, connector, resource_ref, force_reindex)
                    indexed_count += 1
                except Exception as e:
                    print(f"Failed to index {resource_ref.id}: {e}")
                    continue

            return indexed_count

        except Exception as e:
            raise Exception(f"Failed to index connector {connector_name}: {e}")

    async def _index_resource(self, connector_name: str, connector: BaseConnector,
                            resource_ref: ResourceRef, force_reindex: bool = False):
        """Index a single resource"""
        resource_id = f"{connector_name}:{resource_ref.id}"

        # Check if already indexed
        if not force_reindex and resource_id in self.search_index.documents:
            return

        # Try to read resource content
        content = ""
        embedding = None

        try:
            # Read resource as CIR
            read_result = await connector.read_resource(resource_ref.id)
            if read_result.success:
                cir_document = read_result.data
                content = cir_document.get_all_text()

                # Generate embedding if we have content
                if content and self.embedding_engine.model:
                    embedding = self.embedding_engine.get_embedding(content)

        except Exception:
            # Continue with just metadata if content reading fails
            pass

        # Add to search index
        self.search_index.add_document(resource_ref, content, embedding)

    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform unified search across connectors"""
        if not self.is_initialized:
            await self.initialize()

        all_results = []

        # Determine which connectors to search
        connectors_to_search = query.connectors or list(self.connectors.keys())

        # Perform different types of searches
        for search_type in query.search_types:
            if search_type == 'text':
                text_results = await self._search_text(query, connectors_to_search)
                all_results.extend(text_results)

            elif search_type == 'semantic':
                semantic_results = await self._search_semantic(query, connectors_to_search)
                all_results.extend(semantic_results)

            elif search_type == 'metadata':
                metadata_results = await self._search_metadata(query, connectors_to_search)
                all_results.extend(metadata_results)

        # Deduplicate and merge results
        merged_results = self._merge_search_results(all_results)

        # Apply filters
        filtered_results = self._apply_filters(merged_results, query)

        # Sort by relevance
        filtered_results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Limit results
        return filtered_results[:query.limit]

    async def _search_text(self, query: SearchQuery, connectors: List[str]) -> List[SearchResult]:
        """Perform text-based search"""
        results = []

        # Search in index
        text_matches = self.search_index.search_text(query.text, limit=query.limit * 2)

        for resource_id, score in text_matches:
            if resource_id in self.search_index.documents:
                doc_data = self.search_index.documents[resource_id]
                resource_ref = doc_data['resource_ref']

                # Extract connector name from resource_id
                connector_name = resource_id.split(':', 1)[0] if ':' in resource_id else 'unknown'

                if connector_name in connectors:
                    # Generate snippet
                    snippet = self._generate_snippet(doc_data['content'], query.text)

                    results.append(SearchResult(
                        resource_ref=resource_ref,
                        relevance_score=score,
                        search_type='text',
                        connector_name=connector_name,
                        snippet=snippet,
                        highlights=self._extract_highlights(doc_data['content'], query.text)
                    ))

        return results

    async def _search_semantic(self, query: SearchQuery, connectors: List[str]) -> List[SearchResult]:
        """Perform semantic search using embeddings"""
        if not self.embedding_engine.model:
            return []

        results = []

        # Generate query embedding
        query_embedding = self.embedding_engine.get_embedding(query.text)
        if query_embedding is None:
            return []

        # Search in embeddings index
        semantic_matches = self.search_index.search_semantic(
            query_embedding,
            limit=query.limit * 2,
            threshold=0.3
        )

        for resource_id, similarity in semantic_matches:
            if resource_id in self.search_index.documents:
                doc_data = self.search_index.documents[resource_id]
                resource_ref = doc_data['resource_ref']

                # Extract connector name
                connector_name = resource_id.split(':', 1)[0] if ':' in resource_id else 'unknown'

                if connector_name in connectors:
                    # Generate snippet
                    snippet = self._generate_snippet(doc_data['content'], query.text)

                    results.append(SearchResult(
                        resource_ref=resource_ref,
                        relevance_score=similarity,
                        search_type='semantic',
                        connector_name=connector_name,
                        snippet=snippet,
                        embedding_distance=1.0 - similarity
                    ))

        return results

    async def _search_metadata(self, query: SearchQuery, connectors: List[str]) -> List[SearchResult]:
        """Perform metadata-based search"""
        results = []

        # Search in metadata index
        metadata_matches = self.search_index.search_metadata(query.filters)

        for resource_id in metadata_matches:
            if resource_id in self.search_index.documents:
                doc_data = self.search_index.documents[resource_id]
                resource_ref = doc_data['resource_ref']

                # Extract connector name
                connector_name = resource_id.split(':', 1)[0] if ':' in resource_id else 'unknown'

                if connector_name in connectors:
                    # Calculate metadata match score
                    match_score = self._calculate_metadata_score(resource_ref.metadata, query.filters)

                    results.append(SearchResult(
                        resource_ref=resource_ref,
                        relevance_score=match_score,
                        search_type='metadata',
                        connector_name=connector_name,
                        metadata_matches=self._find_metadata_matches(resource_ref.metadata, query.filters)
                    ))

        return results

    def _merge_search_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Merge duplicate results from different search types"""
        merged = {}

        for result in results:
            resource_id = result.resource_ref.id

            if resource_id not in merged:
                merged[resource_id] = result
            else:
                # Combine scores and search types
                existing = merged[resource_id]

                # Use highest relevance score
                if result.relevance_score > existing.relevance_score:
                    existing.relevance_score = result.relevance_score

                # Combine search types
                if result.search_type not in existing.search_type:
                    existing.search_type += f", {result.search_type}"

                # Merge highlights
                if result.highlights:
                    existing.highlights.extend(result.highlights)
                    existing.highlights = list(set(existing.highlights))  # Remove duplicates

                # Use better snippet if available
                if result.snippet and len(result.snippet) > len(existing.snippet):
                    existing.snippet = result.snippet

        return list(merged.values())

    def _apply_filters(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Apply additional filters to search results"""
        filtered = results

        # Filter by date range
        if query.date_range and any(query.date_range):
            start_date, end_date = query.date_range
            filtered = [
                r for r in filtered
                if self._date_in_range(r.resource_ref.created_at or r.resource_ref.modified_at,
                                     start_date, end_date)
            ]

        # Filter by content types
        if query.content_types:
            # This would require additional metadata about content types
            pass

        # Filter by source systems
        if query.source_systems:
            # This would require additional metadata about source systems
            pass

        return filtered

    def _generate_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate a snippet around the query match"""
        if not content or not query:
            return content[:max_length] if content else ""

        content_lower = content.lower()
        query_lower = query.lower()

        # Find first occurrence of query
        pos = content_lower.find(query_lower)
        if pos == -1:
            return content[:max_length]

        # Calculate snippet boundaries
        start = max(0, pos - max_length // 2)
        end = min(len(content), start + max_length)

        snippet = content[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def _extract_highlights(self, content: str, query: str, max_highlights: int = 5) -> List[str]:
        """Extract highlighted phrases around query matches"""
        if not content or not query:
            return []

        highlights = []
        content_lower = content.lower()
        query_words = query.lower().split()

        for word in query_words:
            pos = 0
            while pos < len(content_lower) and len(highlights) < max_highlights:
                pos = content_lower.find(word, pos)
                if pos == -1:
                    break

                # Extract context around the word
                start = max(0, pos - 20)
                end = min(len(content), pos + len(word) + 20)
                highlight = content[start:end].strip()

                if highlight and highlight not in highlights:
                    highlights.append(highlight)

                pos += len(word)

        return highlights

    def _calculate_metadata_score(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> float:
        """Calculate relevance score based on metadata matches"""
        if not metadata or not filters:
            return 0.0

        matches = 0
        total_filters = len(filters)

        for field, value in filters.items():
            if field in metadata:
                metadata_value = str(metadata[field]).lower()
                filter_value = str(value).lower()

                if filter_value in metadata_value:
                    matches += 1

        return matches / total_filters if total_filters > 0 else 0.0

    def _find_metadata_matches(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Find which metadata fields match the filters"""
        matches = {}

        if not metadata or not filters:
            return matches

        for field, value in filters.items():
            if field in metadata:
                metadata_value = str(metadata[field]).lower()
                filter_value = str(value).lower()

                if filter_value in metadata_value:
                    matches[field] = metadata[field]

        return matches

    def _date_in_range(self, date: Optional[datetime], start: Optional[datetime],
                      end: Optional[datetime]) -> bool:
        """Check if date is within the specified range"""
        if not date:
            return True

        if start and date < start:
            return False

        if end and date > end:
            return False

        return True

    async def get_search_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        stats = {
            "total_documents": len(self.search_index.documents),
            "total_embeddings": len(self.search_index.embeddings_index),
            "text_index_size": len(self.search_index.text_index),
            "metadata_fields": len(self.search_index.metadata_index),
            "connectors_registered": len(self.connectors),
            "embedding_model": self.embedding_engine.model_name,
            "embedding_dimension": self.embedding_engine.dimension,
            "cache_size": len(self.embedding_engine.embeddings_cache)
        }

        # Per-connector statistics
        connector_stats = {}
        for connector_name in self.connectors:
            connector_docs = [
                doc_id for doc_id in self.search_index.documents
                if doc_id.startswith(f"{connector_name}:")
            ]
            connector_stats[connector_name] = len(connector_docs)

        stats["documents_per_connector"] = connector_stats

        return stats

    async def reindex_all(self, force: bool = False):
        """Reindex all connectors"""
        total_indexed = 0

        for connector_name in self.connectors:
            try:
                count = await self.index_connector_resources(connector_name, force_reindex=force)
                total_indexed += count
                print(f"Indexed {count} documents from {connector_name}")
            except Exception as e:
                print(f"Failed to reindex {connector_name}: {e}")

        # Save embeddings cache
        self.embedding_engine._save_cache()

        return total_indexed

    async def cleanup_index(self):
        """Clean up stale entries in the search index"""
        stale_docs = []

        for resource_id, doc_data in self.search_index.documents.items():
            # Check if the resource still exists
            connector_name = resource_id.split(':', 1)[0] if ':' in resource_id else None
            if connector_name and connector_name in self.connectors:
                connector = self.connectors[connector_name]
                try:
                    # Try to get metadata to verify existence
                    result = await connector.get_resource_metadata(doc_data['resource_ref'].id)
                    if not result.success:
                        stale_docs.append(resource_id)
                except Exception:
                    stale_docs.append(resource_id)

        # Remove stale documents
        for resource_id in stale_docs:
            self.search_index.remove_document(resource_id)

        return len(stale_docs)
