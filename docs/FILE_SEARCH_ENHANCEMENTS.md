# File Search Enhancements

This document describes the newly implemented enhancements to the file search capabilities in `assistant_core/file_tools.py`.

## Overview

The following enhancements have been added to match OpenAI's full File Search API capabilities:

1. ✅ **Batch file operations** (up to 500 files at once)
2. ✅ **Per-file chunking configuration**
3. ✅ **Vector store expiration policies**
4. ✅ **Ranking options** (score thresholds, hybrid search weights)
5. ✅ **Complete CRUD operations** for vector stores
6. ✅ **Response inspection** for debugging

## 1. Batch File Operations

### Problem
Previously, files were added one at a time using a loop, which was inefficient for large batches.

### Solution
Added `add_files_to_vector_store_batch()` method that supports up to 500 files in a single batch operation.

### Usage

```python
from assistant_core.file_tools import FileManager, VectorStoreManager

file_mgr = FileManager(client)
vector_mgr = VectorStoreManager(client)

# Simple batch (just file IDs)
vector_store = vector_mgr.create_vector_store(name="my-store")
file_ids = ["file-1", "file-2", "file-3", ...]  # Up to 500 files

batch_result = vector_mgr.add_files_to_vector_store_batch(
    vector_store_id=vector_store["id"],
    file_ids=file_ids,
)
print(f"Batch status: {batch_result['status']}")

# Batch with per-file configuration
files_config = [
    {
        "file_id": "file-1",
        "attributes": {"category": "finance"},
        "chunking_strategy": {
            "type": "static",
            "max_chunk_size_tokens": 1000,
            "chunk_overlap_tokens": 200,
        },
    },
    # ... more files
]

batch_result = vector_mgr.add_files_to_vector_store_batch(
    vector_store_id=vector_store["id"],
    files=files_config,
)
```

### Benefits
- More efficient for large file sets
- Atomic batch processing
- Supports up to 500 files per batch
- Can configure chunking per file in batch

## 2. Per-File Chunking Configuration

### Problem
Previously, all files used default chunking (800 tokens, 400 overlap). Different file types may benefit from different chunk sizes.

### Solution
Added `chunking_strategy` parameter to file addition methods.

### Usage

```python
# Add file with custom chunking
chunking_strategy = {
    "type": "static",
    "max_chunk_size_tokens": 1000,  # Range: 100-4096 (default: 800)
    "chunk_overlap_tokens": 200,     # Max: max_chunk_size/2 (default: 400)
}

vector_mgr.add_files_to_vector_store(
    vector_store_id=vector_store["id"],
    file_ids=[file_id],
    chunking_strategy=chunking_strategy,
)
```

### When to Use
- **Larger chunks (1000-2000 tokens)**: Technical documents, code documentation, structured content
- **Smaller chunks (400-600 tokens)**: Chat logs, short messages, fragmented content
- **Default (800 tokens)**: General purpose documents

## 3. Vector Store Expiration Policies

### Problem
Vector stores can accumulate and incur storage costs. No way to automatically clean up unused stores.

### Solution
Added `expires_after` parameter to create/update vector store methods.

### Usage

```python
# Create with expiration policy
vector_store = vector_mgr.create_vector_store(
    name="temporary-kb",
    expires_after={
        "anchor": "last_active_at",  # Only supported value
        "days": 7,                    # Days after last active
    },
)

# Update expiration later
vector_mgr.update_vector_store(
    vector_store_id=vector_store["id"],
    expires_after={"anchor": "last_active_at", "days": 30},
)
```

### Cost Management
- First 1 GB of vector storage is free
- Additional storage: $0.10/GB/day
- Expiration policies help manage costs automatically
- Thread vector stores default to 7 days (managed by OpenAI)

## 4. Ranking Options

### Problem
File search results might include low-relevance chunks, leading to poor response quality. No way to tune ranking behavior.

### Solution
Added ranking options to `build_file_search_resources()` and `build_tools_config()`.

### Usage

```python
from assistant_core.file_tools import ToolResourceBuilder

# Basic: Score threshold (filter low-relevance results)
tools = ToolResourceBuilder.build_file_search_resources(
    vector_store_ids=[vector_store["id"]],
    max_num_results=15,
    ranking_options={
        "ranker": "auto",              # or "default_2024_08_21"
        "score_threshold": 0.5,        # Only chunks with score >= 0.5
    },
)

# Advanced: Hybrid search with custom weights
tools = ToolResourceBuilder.build_file_search_resources(
    vector_store_ids=[vector_store["id"]],
    ranking_options={
        "ranker": "auto",
        "score_threshold": 0.3,
        "hybrid_search": {
            "embedding_weight": 0.7,   # Favor semantic similarity
            "text_weight": 0.3,        # Less weight on keyword matching
        },
    },
)

# Use in tool configuration
tools = ToolResourceBuilder.build_tools_config(
    enable_file_search=True,
    file_search_vector_store_ids=[vector_store["id"]],
    file_search_max_num_results=20,
    file_search_ranking_options={
        "score_threshold": 0.4,
        "hybrid_search": {
            "embedding_weight": 0.6,
            "text_weight": 0.4,
        },
    },
)
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `ranker` | str | "auto" or "default_2024_08_21" | "auto" |
| `score_threshold` | float | Minimum relevance score (0.0-1.0) | 0.0 |
| `embedding_weight` | float | Weight for semantic similarity | - |
| `text_weight` | float | Weight for keyword matching | - |

**Note:** At least one of `embedding_weight` or `text_weight` must be > 0.

### Tuning Tips
- **Higher score_threshold (0.5-0.7)**: Stricter filtering, fewer but more relevant results
- **Lower score_threshold (0.0-0.3)**: More permissive, includes more results
- **Higher embedding_weight (0.7+)**: Better for conceptual/semantic queries
- **Higher text_weight (0.7+)**: Better for exact keyword/phrase matching

## 5. Complete CRUD Operations

### Problem
Previously, only create, add files, and search were available. No way to list, retrieve, update, or delete vector stores.

### Solution
Added full CRUD operations to `VectorStoreManager`.

### Usage

```python
vector_mgr = VectorStoreManager(client)

# CREATE
vector_store = vector_mgr.create_vector_store(name="my-store")

# READ - Get single store
store = vector_mgr.get_vector_store(vector_store["id"])
print(f"Name: {store['name']}, Files: {store['file_counts']}")

# READ - List all stores
all_stores = vector_mgr.list_vector_stores(limit=100, order="desc")
for store in all_stores:
    print(f"{store['name']}: {store['id']}")

# READ - List files in store
files = vector_mgr.list_vector_store_files(vector_store["id"])
for file in files:
    print(f"File: {file['file_id']}, Status: {file['status']}")

# READ - Get file details
file_details = vector_mgr.get_vector_store_file(
    vector_store["id"],
    file_id="file-123",
)

# READ - Get batch status
batch_status = vector_mgr.get_file_batch(
    vector_store["id"],
    batch_id="batch-123",
)

# UPDATE
updated = vector_mgr.update_vector_store(
    vector_store_id=vector_store["id"],
    name="updated-name",
    expires_after={"anchor": "last_active_at", "days": 30},
)

# DELETE - Remove file from store
vector_mgr.delete_vector_store_file(
    vector_store["id"],
    file_id="file-123",
)

# DELETE - Remove entire store
vector_mgr.delete_vector_store(vector_store["id"])
```

### Methods Added

| Method | Description |
|--------|-------------|
| `list_vector_stores()` | List all vector stores |
| `get_vector_store()` | Get vector store details |
| `update_vector_store()` | Update name or expiration |
| `delete_vector_store()` | Delete a vector store |
| `list_vector_store_files()` | List files in a store |
| `get_vector_store_file()` | Get file details in store |
| `delete_vector_store_file()` | Remove file from store |
| `get_file_batch()` | Get batch operation status |

## 6. Response Inspection

### Problem
Hard to debug what file search results were used in a response. No visibility into tool calls and retrieved chunks.

### Solution
Added `ResponseInspector` class with methods to extract and format file search information.

### Usage

```python
from assistant_core.file_tools import ResponseInspector
from assistant_core.ai import generate_ai_reply

inspector = ResponseInspector(client)

# Generate a response with file search
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="What are the key points?",
    enable_file_search=True,
    vector_store_ids=[vector_store["id"]],
)

# Extract file search results
file_search_results = inspector.extract_file_search_results(response)
for result in file_search_results:
    print(f"File: {result['file_id']}")
    print(f"Quote: {result.get('quote', 'N/A')}")

# Inspect all tool calls
all_tool_calls = inspector.inspect_response_tool_calls(response)
for call in all_tool_calls:
    print(f"Tool: {call['type']}, Name: {call.get('name', 'N/A')}")

# Get formatted debug info
debug_info = inspector.format_file_search_debug_info(response)
print(debug_info)
```

### Methods

| Method | Description |
|--------|-------------|
| `extract_file_search_results()` | Extract file citations and results from response |
| `inspect_response_tool_calls()` | Extract all tool calls from response |
| `format_file_search_debug_info()` | Format debug information as string |

### Output Example

```
File Search Debug Information
========================================

Found 3 file search result(s):

  [1] File ID: file-abc123
      Quote: The key points are...
      Type: citation

  [2] File ID: file-def456
      Quote: Another important aspect...
      Type: citation

File search tool calls: 1
  File IDs: ['file-abc123', 'file-def456']
```

## Complete Example

Putting it all together:

```python
from assistant_core.file_tools import (
    FileManager,
    VectorStoreManager,
    ToolResourceBuilder,
    ResponseInspector,
)
from assistant_core.ai import generate_ai_reply

client = get_openai_client()
file_mgr = FileManager(client)
vector_mgr = VectorStoreManager(client)
inspector = ResponseInspector(client)

# 1. Create vector store with expiration
vector_store = vector_mgr.create_vector_store(
    name="production-kb",
    expires_after={"anchor": "last_active_at", "days": 30},
)

# 2. Upload files and add via batch with custom chunking
file_ids = []
for path in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    file_info = file_mgr.upload_file(path, purpose="assistants")
    file_ids.append(file_info["id"])

files_config = [
    {
        "file_id": fid,
        "chunking_strategy": {
            "type": "static",
            "max_chunk_size_tokens": 1000,
            "chunk_overlap_tokens": 200,
        },
    }
    for fid in file_ids
]

batch_result = vector_mgr.add_files_to_vector_store_batch(
    vector_store_id=vector_store["id"],
    files=files_config,
)

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

# 4. Use in AI reply
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="What are the key points?",
    enable_file_search=True,
    vector_store_ids=[vector_store["id"]],
)

# 5. Inspect results
if response:
    debug_info = inspector.format_file_search_debug_info(response)
    print(debug_info)
```

## Migration Guide

### From Old Code

**Before:**
```python
vector_store = vector_mgr.create_vector_store(name="kb", file_ids=file_ids)
tools = ToolResourceBuilder.build_tools_config(
    enable_file_search=True,
    file_search_vector_store_ids=[vector_store["id"]],
)
```

**After (with enhancements):**
```python
vector_store = vector_mgr.create_vector_store(
    name="kb",
    expires_after={"anchor": "last_active_at", "days": 30},
)

# Use batch for many files
batch_result = vector_mgr.add_files_to_vector_store_batch(
    vector_store_id=vector_store["id"],
    file_ids=file_ids,
)

tools = ToolResourceBuilder.build_tools_config(
    enable_file_search=True,
    file_search_vector_store_ids=[vector_store["id"]],
    file_search_ranking_options={
        "score_threshold": 0.4,
    },
)
```

### Backward Compatibility

All existing code continues to work. New parameters are optional, so no breaking changes.

## See Also

- `examples/file_search_enhanced_features.py` - Complete examples
- `docs/FILE_SEARCH_CAPABILITIES_SUMMARY.md` - Overview of all capabilities
- `docs/FILE_SEARCH_QUICK_REFERENCE.md` - Quick reference guide



