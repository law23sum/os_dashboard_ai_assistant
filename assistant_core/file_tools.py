#!/usr/bin/env python3
"""
Enhanced file and tool management for Responses API.

This module provides capabilities inspired by the Assistants API deep dive:
- File upload and management
- Code interpreter integration
- File search with vector stores (including batch operations, chunking, expiration policies)
- Image handling with detail levels
- Message annotations (file citations, file paths)
- Context window management
- Tool resource configuration with ranking options
- Response inspection and debugging tools

Key Features:
- Vector Store CRUD operations (create, read, update, delete, list)
- Batch file operations (up to 500 files per batch)
- Per-file chunking configuration
- Expiration policies for cost management
- Ranking options (score thresholds, hybrid search weights)
- File search result inspection and debugging

Migration note: These features work with the Responses API, replacing
the deprecated Assistants API patterns.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class FileManager:
    """Manage file uploads and attachments for Responses API."""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def upload_file(
        self,
        file_path: Union[str, Path],
        purpose: str = "assistants",
        max_size_mb: int = 512,
    ) -> Dict[str, Any]:
        """
        Upload a file to OpenAI.
        
        Args:
            file_path: Path to file to upload
            purpose: File purpose - "assistants" for tool use, "vision" for image input
            max_size_mb: Maximum file size in MB (default: 512MB)
            
        Returns:
            File object with id, filename, purpose, etc.
        """
        if OpenAI is None:
            raise RuntimeError("OpenAI SDK not installed")
        
        path = Path(file_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(
                f"File size {size_mb:.2f}MB exceeds maximum {max_size_mb}MB"
            )
        
        with path.open("rb") as f:
            file_obj = self.client.files.create(
                file=(path.name, f),
                purpose=purpose,
            )
        
        return {
            "id": file_obj.id,
            "filename": file_obj.filename,
            "purpose": file_obj.purpose,
            "bytes": file_obj.bytes,
            "created_at": file_obj.created_at,
            "local_path": str(path),
        }
    
    def upload_multiple_files(
        self,
        file_paths: List[Union[str, Path]],
        purpose: str = "assistants",
    ) -> List[Dict[str, Any]]:
        """Upload multiple files."""
        return [self.upload_file(path, purpose) for path in file_paths]
    
    def get_file(self, file_id: str) -> Dict[str, Any]:
        """Retrieve file information."""
        file_obj = self.client.files.retrieve(file_id)
        return {
            "id": file_obj.id,
            "filename": file_obj.filename,
            "purpose": file_obj.purpose,
            "bytes": file_obj.bytes,
            "created_at": file_obj.created_at,
        }
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        result = self.client.files.delete(file_id)
        return result.deleted


class VectorStoreManager:
    """Manage vector stores for file search."""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def create_vector_store(
        self,
        name: str,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_after: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a vector store for file search.
        
        Supports up to 10,000 files per vector store.
        
        Args:
            name: Name of the vector store
            file_ids: Optional list of file IDs to add immediately
            metadata: Optional metadata dictionary
            expires_after: Optional expiration policy dict with:
                - "anchor": "last_active_at" (only supported value)
                - "days": int (number of days after last active)
        
        Returns:
            Dictionary with vector store details
        """
        payload: Dict[str, Any] = {"name": name}
        if metadata:
            payload["metadata"] = metadata
        if expires_after:
            payload["expires_after"] = expires_after
        
        vector_store = self.client.beta.vector_stores.create(**payload)
        
        # Add files if provided
        if file_ids:
            for file_id in file_ids:
                self.client.beta.vector_stores.files.create_and_poll(
                    vector_store_id=vector_store.id,
                    file_id=file_id,
                )
        
        return {
            "id": vector_store.id,
            "name": vector_store.name,
            "created_at": vector_store.created_at,
            "file_counts": getattr(vector_store, "file_counts", {}),
            "expires_after": getattr(vector_store, "expires_after", None),
            "usage_bytes": getattr(vector_store, "usage_bytes", None),
        }
    
    def list_vector_stores(
        self,
        limit: int = 100,
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """List all vector stores."""
        result = self.client.beta.vector_stores.list(limit=limit, order=order)
        return [
            {
                "id": vs.id,
                "name": vs.name,
                "created_at": vs.created_at,
                "file_counts": getattr(vs, "file_counts", {}),
                "usage_bytes": getattr(vs, "usage_bytes", None),
                "expires_after": getattr(vs, "expires_after", None),
            }
            for vs in result.data
        ]
    
    def get_vector_store(self, vector_store_id: str) -> Dict[str, Any]:
        """Retrieve a vector store by ID."""
        vs = self.client.beta.vector_stores.retrieve(vector_store_id)
        return {
            "id": vs.id,
            "name": vs.name,
            "created_at": vs.created_at,
            "file_counts": getattr(vs, "file_counts", {}),
            "usage_bytes": getattr(vs, "usage_bytes", None),
            "expires_after": getattr(vs, "expires_after", None),
            "status": getattr(vs, "status", None),
        }
    
    def update_vector_store(
        self,
        vector_store_id: str,
        name: Optional[str] = None,
        expires_after: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update a vector store."""
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if expires_after is not None:
            payload["expires_after"] = expires_after
        
        vs = self.client.beta.vector_stores.update(vector_store_id, **payload)
        return {
            "id": vs.id,
            "name": vs.name,
            "created_at": vs.created_at,
            "file_counts": getattr(vs, "file_counts", {}),
            "usage_bytes": getattr(vs, "usage_bytes", None),
            "expires_after": getattr(vs, "expires_after", None),
        }
    
    def delete_vector_store(self, vector_store_id: str) -> bool:
        """Delete a vector store."""
        result = self.client.beta.vector_stores.delete(vector_store_id)
        return getattr(result, "deleted", True)
    
    def add_files_to_vector_store(
        self,
        vector_store_id: str,
        file_ids: List[str],
        chunking_strategy: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Add files to an existing vector store.
        
        Args:
            vector_store_id: ID of the vector store
            file_ids: List of file IDs to add
            chunking_strategy: Optional chunking strategy dict with:
                - "type": "static"
                - "max_chunk_size_tokens": int (100-4096, default: 800)
                - "chunk_overlap_tokens": int (0 to max_chunk_size_tokens/2, default: 400)
        """
        results = []
        for file_id in file_ids:
            kwargs: Dict[str, Any] = {
                "vector_store_id": vector_store_id,
                "file_id": file_id,
            }
            if chunking_strategy:
                kwargs["chunking_strategy"] = chunking_strategy
            
            result = self.client.beta.vector_stores.files.create_and_poll(**kwargs)
            results.append({
                "id": result.id,
                "file_id": result.file_id,
                "status": getattr(result, "status", "completed"),
            })
        return results
    
    def add_files_to_vector_store_batch(
        self,
        vector_store_id: str,
        files: Optional[List[Dict[str, Any]]] = None,
        file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Add files to vector store using batch operations (up to 500 files).
        
        Args:
            vector_store_id: ID of the vector store
            files: List of file dicts with optional chunking/attributes:
                - "file_id": str (required)
                - "attributes": dict (optional metadata)
                - "chunking_strategy": dict (optional per-file chunking)
            file_ids: Simple list of file IDs (mutually exclusive with files)
        
        Returns:
            Batch result with status and file_counts
        """
        if files and file_ids:
            raise ValueError("files and file_ids are mutually exclusive")
        
        if file_ids:
            # Simple batch with just file IDs
            batch = self.client.beta.vector_stores.file_batches.create_and_poll(
                vector_store_id=vector_store_id,
                file_ids=file_ids,
            )
        elif files:
            # Batch with per-file configuration
            batch = self.client.beta.vector_stores.file_batches.create_and_poll(
                vector_store_id=vector_store_id,
                files=files,
            )
        else:
            raise ValueError("Either files or file_ids must be provided")
        
        return {
            "id": batch.id,
            "vector_store_id": batch.vector_store_id,
            "status": getattr(batch, "status", "completed"),
            "file_counts": getattr(batch, "file_counts", {}),
            "created_at": getattr(batch, "created_at", None),
            "expires_at": getattr(batch, "expires_at", None),
        }
    
    def get_file_batch(
        self,
        vector_store_id: str,
        batch_id: str,
    ) -> Dict[str, Any]:
        """Get status of a file batch operation."""
        batch = self.client.beta.vector_stores.file_batches.retrieve(
            vector_store_id=vector_store_id,
            batch_id=batch_id,
        )
        return {
            "id": batch.id,
            "vector_store_id": batch.vector_store_id,
            "status": getattr(batch, "status", None),
            "file_counts": getattr(batch, "file_counts", {}),
            "created_at": getattr(batch, "created_at", None),
            "expires_at": getattr(batch, "expires_at", None),
        }
    
    def list_vector_store_files(
        self,
        vector_store_id: str,
        limit: int = 100,
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """List files in a vector store."""
        result = self.client.beta.vector_stores.files.list(
            vector_store_id=vector_store_id,
            limit=limit,
            order=order,
        )
        return [
            {
                "id": f.id,
                "file_id": f.file_id,
                "created_at": f.created_at,
                "status": getattr(f, "status", None),
            }
            for f in result.data
        ]
    
    def get_vector_store_file(
        self,
        vector_store_id: str,
        file_id: str,
    ) -> Dict[str, Any]:
        """Get details of a file in a vector store."""
        f = self.client.beta.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=file_id,
        )
        return {
            "id": f.id,
            "file_id": f.file_id,
            "created_at": f.created_at,
            "status": getattr(f, "status", None),
        }
    
    def delete_vector_store_file(
        self,
        vector_store_id: str,
        file_id: str,
    ) -> bool:
        """Delete a file from a vector store."""
        result = self.client.beta.vector_stores.files.delete(
            vector_store_id=vector_store_id,
            file_id=file_id,
        )
        return getattr(result, "deleted", True)
    
    def search_vector_store(
        self,
        vector_store_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search a vector store."""
        results = self.client.vector_stores.search(
            vector_store_id=vector_store_id,
            query=query,
            limit=limit,
        )
        return [
            {
                "file_id": item.file_id,
                "score": getattr(item, "score", None),
                "content": getattr(item, "content", None),
            }
            for item in results.data
        ]


class ImageHandler:
    """Handle image inputs with detail levels."""
    
    @staticmethod
    def create_image_content(
        image_url: Optional[str] = None,
        file_id: Optional[str] = None,
        detail: str = "auto",
    ) -> Dict[str, Any]:
        """
        Create image content for Responses API.
        
        Args:
            image_url: External image URL
            file_id: File ID from uploaded image (purpose="vision")
            detail: "low", "high", or "auto"
                - low: 512x512, 85 tokens, faster
                - high: Detailed crops, more tokens
                - auto: Model decides
        
        Returns:
            Image content block for Responses API input
        """
        if image_url:
            return {
                "type": "input_image",
                "image_url": {
                    "url": image_url,
                    "detail": detail,
                },
            }
        elif file_id:
            return {
                "type": "input_image",
                "image_file": {
                    "file_id": file_id,
                    "detail": detail,
                },
            }
        else:
            raise ValueError("Either image_url or file_id must be provided")
    
    @staticmethod
    def create_multimodal_message(
        text: str,
        images: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create a message with text and images."""
        content = [{"type": "input_text", "text": text}]
        content.extend(images)
        return {
            "role": "user",
            "content": content,
        }


class ToolResourceBuilder:
    """Build tool resource configurations for Responses API."""
    
    @staticmethod
    def build_code_interpreter_resources(
        file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build code_interpreter tool resources.
        
        Supports up to 20 files attached to code_interpreter.
        """
        if not file_ids:
            return {}
        return {
            "type": "code_interpreter",
            "code_interpreter": {
                "file_ids": file_ids[:20],  # Max 20 files
            },
        }
    
    @staticmethod
    def build_file_search_resources(
        vector_store_ids: Optional[List[str]] = None,
        max_num_results: Optional[int] = None,
        ranking_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build file_search tool resources.
        
        Supports up to 10,000 files via vector stores.
        
        Args:
            vector_store_ids: List of vector store IDs
            max_num_results: Maximum number of chunks to return (default: 20 for gpt-4*, 5 for gpt-3.5)
            ranking_options: Optional ranking configuration dict with:
                - "ranker": "auto" or "default_2024_08_21" (default: "auto")
                - "score_threshold": float (0.0-1.0, default: 0.0)
                - "hybrid_search": dict with:
                    - "embedding_weight": float (rrf_embedding_weight)
                    - "text_weight": float (rrf_text_weight)
                    - At least one weight must be > 0
        """
        if not vector_store_ids:
            return {}
        
        file_search_config: Dict[str, Any] = {
            "vector_store_ids": vector_store_ids,
        }
        
        if max_num_results is not None:
            file_search_config["max_num_results"] = max_num_results
        
        if ranking_options:
            file_search_config["ranking_options"] = ranking_options
        
        return {
            "type": "file_search",
            "file_search": file_search_config,
        }
    
    @staticmethod
    def build_tools_config(
        enable_code_interpreter: bool = False,
        enable_file_search: bool = False,
        code_interpreter_file_ids: Optional[List[str]] = None,
        file_search_vector_store_ids: Optional[List[str]] = None,
        file_search_max_num_results: Optional[int] = None,
        file_search_ranking_options: Optional[Dict[str, Any]] = None,
        custom_functions: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build complete tools configuration for Responses API.
        
        Args:
            enable_code_interpreter: Enable code interpreter tool
            enable_file_search: Enable file search tool
            code_interpreter_file_ids: Files to attach to code interpreter
            file_search_vector_store_ids: Vector stores for file search
            file_search_max_num_results: Max chunks for file_search (default: 20 for gpt-4*, 5 for gpt-3.5)
            file_search_ranking_options: Ranking options for file_search (see build_file_search_resources)
            custom_functions: Custom function tools
            
        Returns:
            Tools array for Responses API
        """
        tools: List[Dict[str, Any]] = []
        
        if enable_code_interpreter:
            tool: Dict[str, Any] = {"type": "code_interpreter"}
            if code_interpreter_file_ids:
                tool["code_interpreter"] = {"file_ids": code_interpreter_file_ids[:20]}
            tools.append(tool)
        
        if enable_file_search:
            tool_config = ToolResourceBuilder.build_file_search_resources(
                vector_store_ids=file_search_vector_store_ids,
                max_num_results=file_search_max_num_results,
                ranking_options=file_search_ranking_options,
            )
            if tool_config:
                tools.append(tool_config)
        
        if custom_functions:
            for fn in custom_functions:
                if isinstance(fn, dict):
                    tools.append({"type": "function", "function": fn})
        
        return tools


class MessageAnnotationHandler:
    """Handle message annotations (file citations, file paths)."""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def process_annotations(
        self,
        message_content: Any,
        replace_annotations: bool = True,
    ) -> Tuple[str, List[str]]:
        """
        Process message annotations and replace with readable citations.
        
        Args:
            message_content: Message content object from Responses API
            replace_annotations: Whether to replace annotation markers with footnotes
            
        Returns:
            Tuple of (processed_text, citations_list)
        """
        if not hasattr(message_content, "annotations"):
            return str(message_content), []
        
        annotations = getattr(message_content, "annotations", [])
        if not annotations:
            return str(message_content), []
        
        text = getattr(message_content, "value", str(message_content))
        citations = []
        
        for index, annotation in enumerate(annotations):
            annotation_text = getattr(annotation, "text", "")
            
            # Replace annotation marker with footnote
            if replace_annotations and annotation_text:
                text = text.replace(annotation_text, f" [{index + 1}]")
            
            # Build citation
            if hasattr(annotation, "file_citation"):
                file_citation = annotation.file_citation
                file_id = file_citation.file_id
                quote = getattr(file_citation, "quote", "")
                
                try:
                    file_obj = self.client.files.retrieve(file_id)
                    citations.append(
                        f"[{index + 1}] {quote} from {file_obj.filename}"
                    )
                except Exception:
                    citations.append(f"[{index + 1}] Citation from file {file_id}")
            
            elif hasattr(annotation, "file_path"):
                file_path = annotation.file_path
                file_id = file_path.file_id
                
                try:
                    file_obj = self.client.files.retrieve(file_id)
                    citations.append(
                        f"[{index + 1}] Click <here> to download {file_obj.filename}"
                    )
                except Exception:
                    citations.append(f"[{index + 1}] File: {file_id}")
        
        return text, citations
    
    def format_message_with_citations(
        self,
        message_content: Any,
    ) -> str:
        """Format a message with citations appended."""
        text, citations = self.process_annotations(message_content)
        if citations:
            text += "\n\n" + "\n".join(citations)
        return text


class ContextManager:
    """Manage context window and truncation strategies."""
    
    @staticmethod
    def build_truncation_strategy(
        strategy_type: str = "auto",
        last_messages: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build truncation strategy for Responses API.
        
        Args:
            strategy_type: "auto" or "last_messages"
            last_messages: Number of recent messages to include (if strategy_type="last_messages")
        """
        if strategy_type == "auto":
            return {"type": "auto"}
        elif strategy_type == "last_messages":
            if last_messages is None:
                raise ValueError("last_messages required when strategy_type='last_messages'")
            return {
                "type": "last_messages",
                "last_messages": last_messages,
            }
        else:
            raise ValueError(f"Unknown strategy_type: {strategy_type}")
    
    @staticmethod
    def build_response_config(
        max_output_tokens: Optional[int] = None,
        max_prompt_tokens: Optional[int] = None,
        truncation_strategy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build response configuration with token limits and truncation.
        
        Note: For File Search, recommend max_prompt_tokens >= 20,000.
        For longer conversations, consider 50,000 or remove limit.
        """
        config: Dict[str, Any] = {}
        
        if max_output_tokens is not None:
            config["max_output_tokens"] = max_output_tokens
        
        if max_prompt_tokens is not None:
            config["max_prompt_tokens"] = max_prompt_tokens
        
        if truncation_strategy:
            config["truncation"] = truncation_strategy
        
        return config


class ResponseInspector:
    """Inspect Responses API outputs for debugging and analysis."""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    def extract_file_search_results(
        self,
        response: Any,
    ) -> List[Dict[str, Any]]:
        """
        Extract file search results from a Responses API response.
        
        Args:
            response: Response object from client.responses.create()
        
        Returns:
            List of file search result dictionaries with file_id, content, score, etc.
        """
        results = []
        output = getattr(response, "output", None) or []
        
        # Extract from response output items
        for item in output:
            item_type = getattr(item, "type", None) or (
                item.get("type") if isinstance(item, dict) else None
            )
            
            if item_type == "message":
                # Check message content for annotations (citations)
                content_list = getattr(item, "content", None) or (
                    item.get("content") if isinstance(item, dict) else []
                )
                
                for content_block in content_list:
                    if isinstance(content_block, dict):
                        block_type = content_block.get("type")
                        annotations = content_block.get("annotations", [])
                    else:
                        block_type = getattr(content_block, "type", None)
                        annotations = getattr(content_block, "annotations", [])
                    
                    if block_type == "output_text" and annotations:
                        for annotation in annotations:
                            if isinstance(annotation, dict):
                                file_citation = annotation.get("file_citation")
                            else:
                                file_citation = getattr(annotation, "file_citation", None)
                            
                            if file_citation:
                                if isinstance(file_citation, dict):
                                    file_id = file_citation.get("file_id")
                                    quote = file_citation.get("quote", "")
                                else:
                                    file_id = getattr(file_citation, "file_id", None)
                                    quote = getattr(file_citation, "quote", "")
                                
                                if file_id:
                                    results.append({
                                        "file_id": file_id,
                                        "quote": quote,
                                        "type": "citation",
                                    })
            
            elif item_type == "file_search_preview":
                # Direct file search preview results (if available)
                if isinstance(item, dict):
                    file_ids = item.get("file_ids", [])
                else:
                    file_ids = getattr(item, "file_ids", [])
                
                for file_id in file_ids:
                    results.append({
                        "file_id": file_id,
                        "type": "preview",
                    })
        
        return results
    
    def inspect_response_tool_calls(
        self,
        response: Any,
    ) -> List[Dict[str, Any]]:
        """
        Extract all tool calls from a Responses API response.
        
        Args:
            response: Response object from client.responses.create()
        
        Returns:
            List of tool call dictionaries
        """
        tool_calls = []
        output = getattr(response, "output", None) or []
        
        for item in output:
            item_type = getattr(item, "type", None) or (
                item.get("type") if isinstance(item, dict) else None
            )
            
            if item_type == "function_call":
                if isinstance(item, dict):
                    call_id = item.get("id")
                    fn = item.get("function", {})
                    fn_name = fn.get("name") if isinstance(fn, dict) else None
                    fn_args = fn.get("arguments") if isinstance(fn, dict) else None
                else:
                    call_id = getattr(item, "id", None)
                    fn = getattr(item, "function", None) or {}
                    fn_name = getattr(fn, "name", None) if hasattr(fn, "name") else (
                        fn.get("name") if isinstance(fn, dict) else None
                    )
                    fn_args = getattr(fn, "arguments", None) if hasattr(fn, "arguments") else (
                        fn.get("arguments") if isinstance(fn, dict) else None
                    )
                
                tool_calls.append({
                    "id": call_id,
                    "type": "function_call",
                    "name": fn_name,
                    "arguments": fn_args,
                })
            
            elif item_type == "file_search_preview":
                tool_calls.append({
                    "type": "file_search_preview",
                    "file_ids": (
                        item.get("file_ids") if isinstance(item, dict)
                        else getattr(item, "file_ids", [])
                    ),
                })
        
        return tool_calls
    
    def format_file_search_debug_info(
        self,
        response: Any,
    ) -> str:
        """
        Format file search debugging information from a response.
        
        Args:
            response: Response object from client.responses.create()
        
        Returns:
            Formatted string with file search debug info
        """
        file_search_results = self.extract_file_search_results(response)
        tool_calls = self.inspect_response_tool_calls(response)
        
        lines = ["File Search Debug Information", "=" * 40]
        
        # File search results
        if file_search_results:
            lines.append(f"\nFound {len(file_search_results)} file search result(s):")
            for i, result in enumerate(file_search_results, 1):
                lines.append(f"\n  [{i}] File ID: {result.get('file_id')}")
                if result.get("quote"):
                    quote = result["quote"][:100] + "..." if len(result["quote"]) > 100 else result["quote"]
                    lines.append(f"      Quote: {quote}")
                lines.append(f"      Type: {result.get('type', 'unknown')}")
        else:
            lines.append("\nNo file search results found in response.")
        
        # Tool calls
        file_search_calls = [tc for tc in tool_calls if tc.get("type") == "file_search_preview"]
        if file_search_calls:
            lines.append(f"\nFile search tool calls: {len(file_search_calls)}")
            for call in file_search_calls:
                lines.append(f"  File IDs: {call.get('file_ids', [])}")
        
        return "\n".join(lines)


def create_data_visualization_assistant(
    client: OpenAI,
    csv_file_path: Union[str, Path],
    model: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    Create a complete setup for data visualization with code interpreter.
    
    This demonstrates the pattern from the Assistants API deep dive,
    adapted for Responses API with Conversations.
    """
    file_mgr = FileManager(client)
    tool_builder = ToolResourceBuilder()
    
    # Upload CSV file
    file_info = file_mgr.upload_file(csv_file_path, purpose="assistants")
    
    # Build tools configuration
    tools = tool_builder.build_tools_config(
        enable_code_interpreter=True,
        code_interpreter_file_ids=[file_info["id"]],
    )
    
    # Create conversation with initial message
    conversation = client.conversations.create(
        items=[{
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": "Create 3 data visualizations based on the trends in this file.",
            }],
        }],
        metadata={
            "type": "data_visualization",
            "csv_file": file_info["filename"],
        },
    )
    
    return {
        "conversation_id": conversation.id,
        "tools": tools,
        "file_id": file_info["id"],
        "instructions": (
            "You are great at creating beautiful data visualizations. "
            "You analyze data present in .csv files, understand trends, "
            "and come up with data visualizations relevant to those trends. "
            "You also share a brief text summary of the trends observed."
        ),
    }

