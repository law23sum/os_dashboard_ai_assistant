# File Search Quick Reference Guide

Quick reference for file search capabilities in the codebase with direct code locations.

## Quick Start

### 1. Upload Files and Create Vector Store

**File:** `assistant_core/file_tools.py`

```python
from assistant_core.file_tools import FileManager, VectorStoreManager

file_mgr = FileManager(client)
vector_mgr = VectorStoreManager(client)

# Upload files
file_info = file_mgr.upload_file("document.pdf", purpose="assistants")
file_ids = [file_info["id"]]

# Create vector store
vector_store = vector_mgr.create_vector_store(
    name="my-knowledge-base",
    file_ids=file_ids,
)
```

### 2. Use File Search in AI Replies

**File:** `assistant_core/ai.py` (lines 398-600)

```python
from assistant_core.ai import generate_ai_reply

response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="What does the document say?",
    enable_file_search=True,
    vector_store_ids=[vector_store["id"]],
)
```

### 3. Search Vector Store Directly

**File:** `assistant_core/file_tools.py` (lines 164-183)

```python
results = vector_mgr.search_vector_store(
    vector_store_id=vector_store["id"],
    query="your search query",
    limit=10
)
```

## Key Code Locations

### Core Implementation

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| **FileManager** | `assistant_core/file_tools.py` | 30-105 | File upload/delete |
| **VectorStoreManager** | `assistant_core/file_tools.py` | 107-183 | Vector store operations |
| **ToolResourceBuilder** | `assistant_core/file_tools.py` | 242-321 | Tool configuration |
| **MessageAnnotationHandler** | `assistant_core/file_tools.py` | 324-398 | Citation processing |
| **generate_ai_reply()** | `assistant_core/ai.py` | 398-600 | Main AI function with file_search |

### Examples and Demos

| File | Purpose |
|------|---------|
| `scripts/enhanced_capabilities_demo.py` | Complete file search demo |
| `scripts/assistants_demo.py` | Assistant creation with file_search |
| `openai-assistants-quickstart/app/api/assistants/files/route.tsx` | Next.js API routes |

### Documentation

| File | Content |
|------|---------|
| `docs/ENHANCED_CAPABILITIES.md` | Usage examples and patterns |
| `docs/CAPABILITIES_SUMMARY.md` | Feature summary |
| `docs/FILE_SEARCH.md` | File search guide |
| `docs/FILE_SEARCH_CAPABILITIES_SUMMARY.md` | Comprehensive capabilities list |

## API Reference

### FileManager Methods

```python
file_mgr.upload_file(file_path, purpose="assistants", max_size_mb=512)
file_mgr.upload_multiple_files(file_paths, purpose="assistants")
file_mgr.get_file(file_id)
file_mgr.delete_file(file_id)
```

### VectorStoreManager Methods

```python
vector_mgr.create_vector_store(name, file_ids=None, metadata=None)
vector_mgr.add_files_to_vector_store(vector_store_id, file_ids)
vector_mgr.search_vector_store(vector_store_id, query, limit=10)
```

### ToolResourceBuilder Methods

```python
ToolResourceBuilder.build_file_search_resources(vector_store_ids)
ToolResourceBuilder.build_tools_config(
    enable_file_search=False,
    file_search_vector_store_ids=None,
    ...
)
```

### generate_ai_reply Parameters

```python
generate_ai_reply(
    history,
    persona,
    prompt=None,
    enable_file_search=False,      # Enable file_search tool
    vector_store_ids=None,          # List of vector store IDs
    ...
)
```

## Supported File Formats

✅ **Supported:**
- `.pdf`, `.docx`, `.md`, `.txt`
- `.json`, `.html`, `.css`
- `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rb`, `.php`
- `.doc`, `.pptx`, `.tex`, `.sh`

⚠️ **Text encoding:** Must be `utf-8`, `utf-16`, or `ascii`

## Limits

| Limit | Value |
|-------|-------|
| Max files per vector store | 10,000 |
| Max file size | 512 MB |
| Max tokens per file | 5,000,000 |
| Max chunks returned | 20 (gpt-4*), 5 (gpt-3.5) |
| Recommended max_prompt_tokens | ≥ 20,000 for file search |

## Common Patterns

### Pattern 1: Knowledge Base Setup

```python
# Setup once
file_mgr = FileManager(client)
vector_mgr = VectorStoreManager(client)

files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
file_ids = [file_mgr.upload_file(f)["id"] for f in files]
vector_store = vector_mgr.create_vector_store("kb", file_ids)

# Use repeatedly
response, _, _ = generate_ai_reply(
    history=history,
    persona="AIC",
    prompt=user_question,
    enable_file_search=True,
    vector_store_ids=[vector_store["id"]],
)
```

### Pattern 2: Dynamic File Addition

```python
# Add new files to existing vector store
new_file = file_mgr.upload_file("new_doc.pdf")
vector_mgr.add_files_to_vector_store(
    vector_store["id"],
    [new_file["id"]]
)
```

### Pattern 3: Citation Handling

```python
from assistant_core.file_tools import MessageAnnotationHandler

handler = MessageAnnotationHandler(client)
text, citations = handler.process_annotations(message_content)
formatted = handler.format_message_with_citations(message_content)
```

## Troubleshooting

### Files not appearing in search
- ✅ Check file ingestion status (use `create_and_poll` - already implemented)
- ✅ Ensure files are in `completed` state before searching
- ✅ Verify vector_store_id is correctly passed to `generate_ai_reply`

### Poor search results
- ✅ Increase `max_prompt_tokens` to ≥ 20,000
- ✅ Consider adjusting chunking (requires enhancement)
- ✅ Check file format support

### Citations not showing
- ✅ Use `MessageAnnotationHandler` to process annotations
- ✅ Check response output format

## Next Steps (Enhancements)

See `docs/FILE_SEARCH_CAPABILITIES_SUMMARY.md` for potential enhancements:
- Batch file operations
- Chunking configuration
- Expiration policies
- Ranking options
- Vector store CRUD operations



