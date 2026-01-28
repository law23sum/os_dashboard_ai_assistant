#!/usr/bin/env python3
"""
Examples demonstrating enhanced file search features.

This script shows how to use:
1. Batch file operations (up to 500 files)
2. Per-file chunking configuration
3. Vector store expiration policies
4. Ranking options (score thresholds, hybrid search)
5. Complete CRUD operations for vector stores
6. Response inspection for debugging
"""

from assistant_core.file_tools import (
    FileManager,
    VectorStoreManager,
    ToolResourceBuilder,
    ResponseInspector,
)
from openai import OpenAI


def example_batch_operations(client: OpenAI):
    """Example: Using batch operations to add multiple files efficiently."""
    print("\n=== Batch File Operations Example ===\n")
    
    file_mgr = FileManager(client)
    vector_mgr = VectorStoreManager(client)
    
    # Create a vector store
    vector_store = vector_mgr.create_vector_store(name="batch-example-store")
    print(f"Created vector store: {vector_store['id']}")
    
    # Upload multiple files
    file_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]  # Add your file paths
    file_ids = []
    for path in file_paths:
        try:
            file_info = file_mgr.upload_file(path, purpose="assistants")
            file_ids.append(file_info["id"])
            print(f"Uploaded: {file_info['filename']}")
        except FileNotFoundError:
            print(f"Skipping {path} (file not found)")
    
    if file_ids:
        # Add files using batch operation (more efficient for many files)
        batch_result = vector_mgr.add_files_to_vector_store_batch(
            vector_store_id=vector_store["id"],
            file_ids=file_ids,  # Simple batch with just file IDs
        )
        print(f"\nBatch status: {batch_result['status']}")
        print(f"Files processed: {batch_result['file_counts']}")


def example_chunking_configuration(client: OpenAI):
    """Example: Configuring chunking strategy for files."""
    print("\n=== Chunking Configuration Example ===\n")
    
    file_mgr = FileManager(client)
    vector_mgr = VectorStoreManager(client)
    
    # Create vector store
    vector_store = vector_mgr.create_vector_store(name="chunking-example-store")
    
    # Upload a file
    file_info = file_mgr.upload_file("large_document.pdf", purpose="assistants")
    print(f"Uploaded: {file_info['filename']}")
    
    # Add file with custom chunking strategy
    # Larger chunks for technical documents, smaller for chat-like content
    chunking_strategy = {
        "type": "static",
        "max_chunk_size_tokens": 1000,  # Default: 800, range: 100-4096
        "chunk_overlap_tokens": 200,     # Default: 400, max: max_chunk_size/2
    }
    
    result = vector_mgr.add_files_to_vector_store(
        vector_store_id=vector_store["id"],
        file_ids=[file_info["id"]],
        chunking_strategy=chunking_strategy,
    )
    print(f"File added with custom chunking: {result[0]['status']}")


def example_batch_with_per_file_chunking(client: OpenAI):
    """Example: Batch operation with per-file chunking configuration."""
    print("\n=== Batch with Per-File Chunking Example ===\n")
    
    file_mgr = FileManager(client)
    vector_mgr = VectorStoreManager(client)
    
    vector_store = vector_mgr.create_vector_store(name="per-file-chunking-store")
    
    # Upload files
    file1 = file_mgr.upload_file("technical_manual.pdf", purpose="assistants")
    file2 = file_mgr.upload_file("chat_logs.txt", purpose="assistants")
    
    # Batch with per-file configuration
    files_config = [
        {
            "file_id": file1["id"],
            "chunking_strategy": {
                "type": "static",
                "max_chunk_size_tokens": 1200,  # Larger chunks for technical docs
                "chunk_overlap_tokens": 300,
            },
            "attributes": {"category": "technical", "type": "manual"},
        },
        {
            "file_id": file2["id"],
            "chunking_strategy": {
                "type": "static",
                "max_chunk_size_tokens": 500,   # Smaller chunks for chat logs
                "chunk_overlap_tokens": 100,
            },
            "attributes": {"category": "chat", "type": "logs"},
        },
    ]
    
    batch_result = vector_mgr.add_files_to_vector_store_batch(
        vector_store_id=vector_store["id"],
        files=files_config,
    )
    print(f"Batch with per-file config: {batch_result['status']}")


def example_expiration_policies(client: OpenAI):
    """Example: Setting expiration policies for cost management."""
    print("\n=== Expiration Policies Example ===\n")
    
    vector_mgr = VectorStoreManager(client)
    
    # Create vector store with 7-day expiration after last active
    vector_store = vector_mgr.create_vector_store(
        name="temporary-knowledge-base",
        expires_after={
            "anchor": "last_active_at",
            "days": 7,
        },
    )
    print(f"Created vector store with expiration policy: {vector_store['id']}")
    print(f"Expires after: {vector_store.get('expires_after', 'N/A')} days of inactivity")
    
    # Update expiration policy later if needed
    updated = vector_mgr.update_vector_store(
        vector_store_id=vector_store["id"],
        expires_after={
            "anchor": "last_active_at",
            "days": 30,  # Extend to 30 days
        },
    )
    print(f"Updated expiration to: {updated.get('expires_after', 'N/A')}")


def example_ranking_options(client: OpenAI):
    """Example: Configuring ranking options for better search results."""
    print("\n=== Ranking Options Example ===\n")
    
    vector_mgr = VectorStoreManager(client)
    
    # Create vector store
    vector_store = vector_mgr.create_vector_store(name="ranking-example-store")
    
    # Build tools with ranking options
    # Option 1: Basic ranking with score threshold
    tools_basic = ToolResourceBuilder.build_file_search_resources(
        vector_store_ids=[vector_store["id"]],
        max_num_results=15,  # Return up to 15 chunks (default: 20 for gpt-4*)
        ranking_options={
            "ranker": "auto",  # or "default_2024_08_21"
            "score_threshold": 0.5,  # Only use chunks with relevance score >= 0.5
        },
    )
    print("Basic ranking configuration created")
    
    # Option 2: Hybrid search with custom weights
    tools_hybrid = ToolResourceBuilder.build_file_search_resources(
        vector_store_ids=[vector_store["id"]],
        ranking_options={
            "ranker": "auto",
            "score_threshold": 0.3,
            "hybrid_search": {
                "embedding_weight": 0.7,  # Favor semantic similarity
                "text_weight": 0.3,       # Less weight on keyword matching
            },
        },
    )
    print("Hybrid search configuration created (favors semantic similarity)")
    
    # Option 3: Keyword-focused hybrid search
    tools_keyword_focused = ToolResourceBuilder.build_file_search_resources(
        vector_store_ids=[vector_store["id"]],
        ranking_options={
            "hybrid_search": {
                "embedding_weight": 0.3,  # Less weight on semantic
                "text_weight": 0.7,       # Favor exact keyword matches
            },
        },
    )
    print("Keyword-focused configuration created")


def example_crud_operations(client: OpenAI):
    """Example: Complete CRUD operations for vector stores."""
    print("\n=== CRUD Operations Example ===\n")
    
    vector_mgr = VectorStoreManager(client)
    
    # CREATE
    vector_store = vector_mgr.create_vector_store(name="crud-example-store")
    print(f"Created: {vector_store['id']}")
    
    # READ - Get single vector store
    store_details = vector_mgr.get_vector_store(vector_store["id"])
    print(f"Retrieved: {store_details['name']}")
    print(f"  Files: {store_details['file_counts']}")
    print(f"  Size: {store_details.get('usage_bytes', 0)} bytes")
    
    # LIST - Get all vector stores
    all_stores = vector_mgr.list_vector_stores(limit=10)
    print(f"\nTotal vector stores: {len(all_stores)}")
    for store in all_stores[:3]:  # Show first 3
        print(f"  - {store['name']} ({store['id']})")
    
    # UPDATE
    updated = vector_mgr.update_vector_store(
        vector_store_id=vector_store["id"],
        name="crud-example-store-updated",
    )
    print(f"\nUpdated name to: {updated['name']}")
    
    # List files in vector store
    files = vector_mgr.list_vector_store_files(vector_store["id"])
    print(f"Files in store: {len(files)}")
    
    # DELETE (commented out to avoid accidental deletion)
    # vector_mgr.delete_vector_store(vector_store["id"])
    # print(f"Deleted: {vector_store['id']}")


def example_response_inspection(client: OpenAI):
    """Example: Inspecting responses to debug file search results."""
    print("\n=== Response Inspection Example ===\n")
    
    from assistant_core.ai import generate_ai_reply
    
    vector_mgr = VectorStoreManager(client)
    inspector = ResponseInspector(client)
    
    # Create vector store and add files
    vector_store = vector_mgr.create_vector_store(name="inspection-example-store")
    # ... add files to vector store ...
    
    # Generate a response with file search
    response, error, tool_calls = generate_ai_reply(
        history=[],
        persona="AIC",
        prompt="What are the key points in the documents?",
        enable_file_search=True,
        vector_store_ids=[vector_store["id"]],
    )
    
    if response:
        # Extract file search results
        file_search_results = inspector.extract_file_search_results(response)
        print(f"Found {len(file_search_results)} file search results:")
        for result in file_search_results:
            print(f"  - File ID: {result['file_id']}")
            if result.get("quote"):
                print(f"    Quote: {result['quote'][:100]}...")
        
        # Get all tool calls
        all_tool_calls = inspector.inspect_response_tool_calls(response)
        print(f"\nTool calls: {len(all_tool_calls)}")
        for call in all_tool_calls:
            print(f"  - {call['type']}: {call.get('name', 'N/A')}")
        
        # Get formatted debug info
        debug_info = inspector.format_file_search_debug_info(response)
        print(f"\n{debug_info}")


def example_complete_workflow(client: OpenAI):
    """Example: Complete workflow using all enhanced features."""
    print("\n=== Complete Workflow Example ===\n")
    
    file_mgr = FileManager(client)
    vector_mgr = VectorStoreManager(client)
    
    # 1. Create vector store with expiration policy
    vector_store = vector_mgr.create_vector_store(
        name="production-knowledge-base",
        expires_after={"anchor": "last_active_at", "days": 30},
    )
    print(f"Created vector store: {vector_store['id']}")
    
    # 2. Upload and batch add files with custom chunking
    file_paths = ["doc1.pdf", "doc2.pdf"]  # Your files
    files_config = []
    for path in file_paths:
        try:
            file_info = file_mgr.upload_file(path, purpose="assistants")
            files_config.append({
                "file_id": file_info["id"],
                "chunking_strategy": {
                    "type": "static",
                    "max_chunk_size_tokens": 1000,
                    "chunk_overlap_tokens": 200,
                },
            })
        except FileNotFoundError:
            print(f"Skipping {path}")
    
    if files_config:
        batch_result = vector_mgr.add_files_to_vector_store_batch(
            vector_store_id=vector_store["id"],
            files=files_config,
        )
        print(f"Added {len(files_config)} files via batch: {batch_result['status']}")
    
    # 3. Build tools with ranking options
    tools = ToolResourceBuilder.build_tools_config(
        enable_file_search=True,
        file_search_vector_store_ids=[vector_store["id"]],
        file_search_max_num_results=20,
        file_search_ranking_options={
            "ranker": "auto",
            "score_threshold": 0.4,
            "hybrid_search": {
                "embedding_weight": 0.6,
                "text_weight": 0.4,
            },
        },
    )
    print("Configured file search with ranking options")
    
    # 4. Use in API calls
    print("Ready to use with Responses API!")


if __name__ == "__main__":
    # Initialize OpenAI client
    import os
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("File Search Enhanced Features Examples")
    print("=" * 50)
    
    # Run examples (uncomment the ones you want to test)
    # example_batch_operations(client)
    # example_chunking_configuration(client)
    # example_batch_with_per_file_chunking(client)
    # example_expiration_policies(client)
    # example_ranking_options(client)
    # example_crud_operations(client)
    # example_response_inspection(client)
    example_complete_workflow(client)



