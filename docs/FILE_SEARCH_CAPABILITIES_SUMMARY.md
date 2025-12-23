# File Search Capabilities Summary

This document summarizes all File Search capabilities found in the codebase, mapped against OpenAI's Assistants API File Search documentation.

## Core Implementation Files

### 1. `assistant_core/file_tools.py`
**Main implementation file with comprehensive file search support:**

- ✅ **FileManager** - File upload and management
  - `upload_file()` - Upload files up to 512MB
  - `upload_multiple_files()` - Batch file uploads
  - `get_file()` - Retrieve file information
  - `delete_file()` - Delete files
  
- ✅ **VectorStoreManager** - Vector store operations
  - `create_vector_store()` - Create vector stores (supports up to 10,000 files)
  - `add_files_to_vector_store()` - Add files to existing stores (uses `create_and_poll`)
  - `search_vector_store()` - Direct vector store search capability

- ✅ **ToolResourceBuilder** - Tool configuration
  - `build_file_search_resources()` - Build file_search tool resources
  - `build_tools_config()` - Complete tools configuration including file_search

- ✅ **MessageAnnotationHandler** - Citation processing
  - `process_annotations()` - Process file citations from file_search
  - `format_message_with_citations()` - Format messages with citations

### 2. `assistant_core/ai.py`
**Main AI reply function with file search integration:**

- ✅ `generate_ai_reply()` function supports:
  - `enable_file_search` parameter
  - `vector_store_ids` parameter for attaching vector stores
  - Automatic tool configuration for file_search

```python
# Lines 545-550
if enable_file_search and vector_store_ids:
    tools.append({
        "type": "file_search",
        "file_search": {"vector_store_ids": vector_store_ids},
    })
```

### 3. Demo and Example Files

#### `scripts/enhanced_capabilities_demo.py`
- ✅ Complete file search demonstration
- ✅ Shows full workflow: upload → vector store → search
- ✅ Uses `FileManager` and `VectorStoreManager`

#### `scripts/assistants_demo.py`
- ✅ Assistant creation with file_search tool
- ✅ Vector store creation and file attachment
- ✅ Legacy Assistants API patterns (for reference)

#### `openai-assistants-quickstart/app/api/assistants/files/route.tsx`
- ✅ Next.js API routes for file management
- ✅ `getOrCreateVectorStore()` helper function
- ✅ File upload, list, and delete endpoints

## Implemented Features ✅

### Basic Functionality
- ✅ File upload with `purpose="assistants"`
- ✅ Vector store creation
- ✅ Adding files to vector stores
- ✅ Polling for file ingestion completion (`create_and_poll`)
- ✅ File search tool configuration
- ✅ Vector store search capability
- ✅ File citation processing and formatting

### Integration Points
- ✅ Integration with `generate_ai_reply()` function
- ✅ Tool resource building
- ✅ Message annotation handling
- ✅ Support for up to 10,000 files per vector store

### Documentation
- ✅ `docs/ENHANCED_CAPABILITIES.md` - Usage examples
- ✅ `docs/CAPABILITIES_SUMMARY.md` - Feature summary
- ✅ `docs/FILE_SEARCH.md` - File search guide

## Potential Enhancements (From OpenAI Docs)

Based on the OpenAI File Search documentation, here are features that could be added/enhanced:

### 1. File Batch Operations ⚠️
**Status:** Not currently implemented

The documentation shows support for batch operations (up to 500 files):

```python
# From docs - could be added
batch = client.beta.vector_stores.file_batches.create_and_poll(
    vector_store_id="vs_abc123",
    files=[
        {
            "file_id": "file_1",
            "attributes": {"category": "finance"}
        },
        {
            "file_id": "file_2",
            "chunking_strategy": {
                "type": "static",
                "max_chunk_size_tokens": 1000,
                "chunk_overlap_tokens": 200
            }
        }
    ]
)
```

**Current Implementation:** Uses individual `create_and_poll` calls in a loop
**Enhancement:** Add batch upload method to `VectorStoreManager`

### 2. Chunking Configuration ⚠️
**Status:** Not currently configurable

The documentation shows per-file chunking strategy:

```python
# From docs - could be added
chunking_strategy = {
    "type": "static",
    "max_chunk_size_tokens": 1000,  # Default: 800
    "chunk_overlap_tokens": 200      # Default: 400
}
```

**Current Implementation:** Uses default chunking (800 tokens, 400 overlap)
**Enhancement:** Add chunking_strategy parameter to file addition methods

### 3. Expiration Policies ⚠️
**Status:** Not currently supported

The documentation shows expiration policy support:

```python
# From docs - could be added
vector_store = client.vector_stores.create(
    name="Product Documentation",
    expires_after={
        "anchor": "last_active_at",
        "days": 7
    }
)
```

**Current Implementation:** No expiration policy support
**Enhancement:** Add `expires_after` parameter to `create_vector_store()`

### 4. Ranking Options ⚠️
**Status:** Not currently configurable

The documentation shows ranking configuration:

```python
# From docs - could be added
tool = {
    "type": "file_search",
    "file_search": {
        "vector_store_ids": [...],
        "max_num_results": 20,  # Default: 20 for gpt-4*, 5 for gpt-3.5
        "ranking_options": {
            "ranker": "auto",  # or "default_2024_08_21"
            "score_threshold": 0.0,
            "hybrid_search": {
                "embedding_weight": 0.5,
                "text_weight": 0.5
            }
        }
    }
}
```

**Current Implementation:** Uses default ranking
**Enhancement:** Add ranking options to `build_file_search_resources()` and tool configuration

### 5. Vector Store Management ⚠️
**Status:** Partial implementation

Additional management operations from docs:
- List vector stores
- Retrieve vector store details
- Update vector store (name, expiration, metadata)
- Delete vector store
- List files in vector store
- Get file batch status

**Current Implementation:** Only has create, add files, and search
**Enhancement:** Add full CRUD operations for vector stores

### 6. Message Attachments (Thread-level) ⚠️
**Status:** Not applicable (using Responses API, not Threads)

The documentation shows thread-level vector stores via message attachments. Since the codebase uses the Responses API (not deprecated Assistants API with Threads), this may not be directly applicable. However, similar patterns could be used with Conversations API.

### 7. Run Step Inspection ⚠️
**Status:** Not currently implemented

The documentation shows retrieving file search results from run steps:

```python
# From docs - could be added
run_step = client.beta.threads.runs.steps.retrieve(
    thread_id="thread_abc123",
    run_id="run_abc123",
    step_id="step_abc123",
    include=["step_details.tool_calls[*].file_search.results[*].content"]
)
```

**Current Implementation:** No step inspection capability
**Enhancement:** Add methods to inspect Responses API outputs for file search results

## Code Examples from Codebase

### Basic File Search Usage

```python
from assistant_core.file_tools import FileManager, VectorStoreManager
from assistant_core.ai import generate_ai_reply

client = get_openai_client()
file_mgr = FileManager(client)
vector_mgr = VectorStoreManager(client)

# Upload files
file_ids = []
for path in ["doc1.pdf", "doc2.pdf"]:
    file_info = file_mgr.upload_file(path, purpose="assistants")
    file_ids.append(file_info["id"])

# Create vector store
vector_store = vector_mgr.create_vector_store(
    name="knowledge-base",
    file_ids=file_ids,
)

# Use in AI reply
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="What are the key points?",
    enable_file_search=True,
    vector_store_ids=[vector_store["id"]],
)
```

### Direct Vector Store Search

```python
# Search directly
results = vector_mgr.search_vector_store(
    vector_store_id=vector_store["id"],
    query="What is machine learning?",
    limit=10
)

for result in results:
    print(f"File: {result['file_id']}, Score: {result['score']}")
```

### Tool Configuration

```python
from assistant_core.file_tools import ToolResourceBuilder

tools = ToolResourceBuilder.build_tools_config(
    enable_file_search=True,
    file_search_vector_store_ids=[vector_store["id"]],
)
```

## Supported File Formats

Based on OpenAI documentation, the following formats are supported:
- `.c`, `.cpp`, `.cs`, `.css` (text files)
- `.doc`, `.docx` (Word documents)
- `.go`, `.html`, `.java`, `.js`, `.json` (code/text)
- `.md` (Markdown)
- `.pdf` (PDF documents)
- `.php`, `.pptx` (PowerPoint), `.py`, `.rb`, `.sh`
- `.tex`, `.ts`, `.txt` (text files)

**Encoding:** For text files, must be `utf-8`, `utf-16`, or `ascii`

## Limits and Recommendations

### Current Implementation Awareness:
- ✅ Max 10,000 files per vector store (documented)
- ✅ Max 512 MB file size (implemented in FileManager)
- ✅ Max 5,000,000 tokens per file
- ⚠️ Recommended: `max_prompt_tokens >= 20,000` for file search (not automatically set)
- ⚠️ For longer conversations: Consider 50,000 or remove limit

### Default Settings (from OpenAI):
- Chunk size: 800 tokens
- Chunk overlap: 400 tokens
- Embedding model: `text-embedding-3-large` at 256 dimensions
- Max chunks: 20 for gpt-4*, 5 for gpt-3.5-turbo
- Token budget: 4,000 (gpt-3.5) or 16,000 (gpt-4*)

## Migration Notes

The codebase appears to be using the **Responses API** (not the deprecated Assistants API), which is correct per OpenAI's migration guidance. The file search capabilities work with the Responses API through the `tools` parameter.

Key differences:
- Uses `client.responses.create()` instead of `client.beta.threads.runs.create()`
- Uses `conversation_id` instead of `thread_id`
- Uses `tools` parameter directly instead of `assistant.tool_resources`

## Summary

**Strengths:**
- ✅ Solid foundation with FileManager and VectorStoreManager
- ✅ Good integration with main AI reply function
- ✅ Proper use of Responses API (not deprecated Assistants API)
- ✅ Citation handling implemented
- ✅ Polling helpers for async operations

**Potential Enhancements:**
- ⚠️ Add batch file operations
- ⚠️ Add chunking configuration options
- ⚠️ Add expiration policies
- ⚠️ Add ranking options configuration
- ⚠️ Add complete vector store CRUD operations
- ⚠️ Add run step inspection for debugging
- ⚠️ Auto-set recommended `max_prompt_tokens` for file search


