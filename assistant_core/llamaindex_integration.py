#!/usr/bin/env python3
"""
LlamaIndex Integration - Enhanced RAG and Data Augmentation

This module integrates LlamaIndex to enhance the existing semantic search
and RAG capabilities. LlamaIndex provides:
- Advanced document indexing and retrieval
- Query engines with better context management
- Multi-document query capabilities
- Better chunking and embedding strategies

License: LlamaIndex is MIT licensed (safe for commercial use)
"""

import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Try to import LlamaIndex components
LLAMAINDEX_IMPORT_ERROR: Optional[str] = None
try:
    from llama_index.core import (
        VectorStoreIndex,
        Document,
        Settings,
        StorageContext,
        load_index_from_storage,
    )
    from llama_index.core.node_parser import SimpleNodeParser
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI
    from llama_index.core.storage.docstore import SimpleDocumentStore
    from llama_index.core.storage.index_store import SimpleIndexStore
    from llama_index.core.vector_stores import SimpleVectorStore
    LLAMAINDEX_AVAILABLE = True
except Exception as e:
    LLAMAINDEX_AVAILABLE = False
    LLAMAINDEX_IMPORT_ERROR = str(e)
    logger.debug("LlamaIndex integration unavailable: %s", e)


class LlamaIndexRAGEngine:
    """
    Enhanced RAG engine using LlamaIndex for better document retrieval
    and context management.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        Initialize LlamaIndex RAG engine.

        Args:
            storage_path: Path to store indices (default: ./data/llamaindex)
            openai_api_key: OpenAI API key (default: from env)
            model_name: LLM model to use
            embedding_model: Embedding model to use
        """
        if not LLAMAINDEX_AVAILABLE:
            raise ImportError(
                "LlamaIndex is not installed. Install with: pip install llama-index"
            )

        self.storage_path = Path(storage_path or "./data/llamaindex")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Get API key
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var.")

        # Configure LlamaIndex settings
        Settings.llm = OpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0.2,
        )
        Settings.embed_model = OpenAIEmbedding(
            model_name=embedding_model,
            api_key=api_key,
        )

        # Initialize or load index
        self.index = self._load_or_create_index()
        self.query_engine = None

    def _load_or_create_index(self) -> VectorStoreIndex:
        """Load existing index or create new one"""
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=str(self.storage_path)
            )
            index = load_index_from_storage(storage_context)
            logger.info(f"Loaded existing index from {self.storage_path}")
            return index
        except Exception:
            # Create new index
            logger.info("Creating new LlamaIndex")
            index = VectorStoreIndex([])
            return index

    def add_documents(
        self,
        documents: List[Union[str, Dict[str, Any]]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add documents to the index.

        Args:
            documents: List of document texts or dicts with 'text' and metadata
            metadata: Optional metadata to attach to all documents
        """
        if not documents:
            return

        # Convert to LlamaIndex Document format
        llama_docs = []
        for doc in documents:
            if isinstance(doc, str):
                doc_obj = Document(text=doc, metadata=metadata or {})
            elif isinstance(doc, dict):
                text = doc.get("text", doc.get("content", ""))
                doc_metadata = {**(metadata or {}), **doc.get("metadata", {})}
                doc_obj = Document(text=text, metadata=doc_metadata)
            else:
                continue

            llama_docs.append(doc_obj)

        # Add to index
        for doc in llama_docs:
            self.index.insert(doc)

        # Persist index
        self.index.storage_context.persist(persist_dir=str(self.storage_path))
        logger.info(f"Added {len(llama_docs)} documents to index")

    def query(
        self,
        query_text: str,
        similarity_top_k: int = 5,
        response_mode: str = "compact",
    ) -> Dict[str, Any]:
        """
        Query the index and get relevant context.

        Args:
            query_text: Query string
            similarity_top_k: Number of top results to retrieve
            response_mode: Response mode ('default', 'compact', 'tree_summarize')

        Returns:
            Dict with 'response', 'source_nodes', and 'metadata'
        """
        if not self.query_engine:
            # Create query engine with retriever
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=similarity_top_k,
            )
            self.query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                response_mode=response_mode,
            )

        # Query
        response = self.query_engine.query(query_text)

        # Extract source nodes
        source_nodes = []
        for node in response.source_nodes:
            source_nodes.append({
                "text": node.text,
                "score": node.score,
                "metadata": node.metadata,
            })

        return {
            "response": str(response),
            "source_nodes": source_nodes,
            "query": query_text,
            "metadata": {
                "model": Settings.llm.model,
                "embedding_model": Settings.embed_model.model_name,
            },
        }

    def get_context_for_query(
        self, query_text: str, max_chunks: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context chunks for a query without generating a response.
        Useful for augmenting prompts with context.

        Args:
            query_text: Query string
            max_chunks: Maximum number of context chunks

        Returns:
            List of context chunks with text and metadata
        """
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=max_chunks,
        )

        nodes = retriever.retrieve(query_text)

        return [
            {
                "text": node.text,
                "score": node.score,
                "metadata": node.metadata,
            }
            for node in nodes
        ]

    def clear_index(self) -> None:
        """Clear all documents from the index"""
        self.index = VectorStoreIndex([])
        self.query_engine = None
        logger.info("Index cleared")

    def save(self) -> None:
        """Persist the index to disk"""
        self.index.storage_context.persist(persist_dir=str(self.storage_path))
        logger.info(f"Index saved to {self.storage_path}")


def create_rag_engine(
    storage_path: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> Optional[LlamaIndexRAGEngine]:
    """
    Factory function to create a LlamaIndex RAG engine.

    Returns None if LlamaIndex is not available (graceful degradation).
    """
    if not LLAMAINDEX_AVAILABLE:
        logger.debug("LlamaIndex not available. Returning None.")
        return None

    try:
        return LlamaIndexRAGEngine(
            storage_path=storage_path,
            openai_api_key=openai_api_key,
        )
    except Exception as e:
        logger.error(f"Failed to create LlamaIndex RAG engine: {e}")
        return None
