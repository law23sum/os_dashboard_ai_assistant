# Enhanced Capabilities Guide

This guide covers advanced features inspired by the Assistants API deep dive, now available through the Responses API.

## Overview

The `assistant_core/file_tools.py` module provides comprehensive file and tool management capabilities:

- **File Management**: Upload, retrieve, and delete files
- **Code Interpreter**: Execute code with file attachments
- **File Search**: Vector store integration for semantic search
- **Image Handling**: Multimodal inputs with detail level control
- **Message Annotations**: Process file citations and file paths
- **Context Management**: Token limits and truncation strategies

## File Management

### Upload Files

```python
from assistant_core.file_tools import FileManager
from assistant_core.ai import get_openai_client

client = get_openai_client()
file_mgr = FileManager(client)

# Upload a single file
file_info = file_mgr.upload_file("data.csv", purpose="assistants")
print(f"Uploaded: {file_info['id']}")

# Upload multiple files
files = file_mgr.upload_multiple_files(
    ["data1.csv", "data2.csv", "report.pdf"],
    purpose="assistants"
)
```

**File Limits:**
- Max file size: 512 MB
- Max tokens per file: 5,000,000
- Project limit: 100 GB (contact support to increase)

**File Purposes:**
- `"assistants"`: For use with code_interpreter and file_search tools
- `"vision"`: For image input content (downloadable)

## Code Interpreter

### Basic Usage

```python
from assistant_core.file_tools import FileManager, ToolResourceBuilder
from assistant_core.ai import generate_ai_reply

client = get_openai_client()
file_mgr = FileManager(client)

# Upload CSV file
file_info = file_mgr.upload_file("revenue-forecast.csv", purpose="assistants")

# Generate reply with code interpreter
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="Create 3 data visualizations based on trends in this file.",
    enable_code_interpreter=True,
    uploaded_file_ids=[file_info["id"]],
)
```

### Advanced Configuration

```python
from assistant_core.file_tools import ToolResourceBuilder

# Build complete tools configuration
tools = ToolResourceBuilder.build_tools_config(
    enable_code_interpreter=True,
    code_interpreter_file_ids=["file-123", "file-456"],  # Max 20 files
    custom_functions=[
        {
            "name": "custom_function",
            "description": "A custom function",
            "parameters": {...}
        }
    ]
)
```

**Code Interpreter Limits:**
- Max 20 files per code_interpreter tool
- Files must be uploaded with `purpose="assistants"`

## File Search (Vector Stores)

### Create Vector Store

```python
from assistant_core.file_tools import FileManager, VectorStoreManager

client = get_openai_client()
file_mgr = FileManager(client)
vector_mgr = VectorStoreManager(client)

# Upload files
file_ids = []
for path in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    file_info = file_mgr.upload_file(path, purpose="assistants")
    file_ids.append(file_info["id"])

# Create vector store
vector_store = vector_mgr.create_vector_store(
    name="knowledge-base",
    file_ids=file_ids,
)

# Use in responses
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="What are the key points in these documents?",
    enable_file_search=True,
    vector_store_ids=[vector_store["id"]],
)
```

### Search Vector Store

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

**File Search Limits:**
- Max 10,000 files per vector store
- Recommended: Set `max_prompt_tokens >= 20,000` for file search
- For longer conversations: Consider 50,000 or remove limit

## Image Handling

### Image URLs

```python
from assistant_core.ai import generate_ai_reply

response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="What is the difference between these images?",
    image_urls=[
        "https://example.com/image1.png",
        "https://example.com/image2.png",
    ],
    image_detail="high",  # "low", "high", or "auto"
)
```

### Image File IDs

```python
from assistant_core.file_tools import FileManager, ImageHandler

client = get_openai_client()
file_mgr = FileManager(client)

# Upload image
image_info = file_mgr.upload_file("myimage.png", purpose="vision")

# Use in response
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="What is this an image of?",
    image_file_ids=[image_info["id"]],
    image_detail="high",
)
```

### Image Detail Levels

- **`"low"`**: 512x512 resolution, ~85 tokens, faster responses
- **`"high"`**: Detailed crops based on image size, more tokens
- **`"auto"`**: Model decides the appropriate detail level

**Supported Formats:**
- PNG, JPG, GIF, WEBP
- Max 100 GB per project for vision files

## Message Annotations

### Process Annotations

When the model uses file_search or code_interpreter, responses may contain annotations:

```python
from assistant_core.file_tools import MessageAnnotationHandler

client = get_openai_client()
annotation_handler = MessageAnnotationHandler(client)

# Process message with annotations
text, citations = annotation_handler.process_annotations(
    message_content=response.output[0].content[0],
    replace_annotations=True
)

# Display with citations
formatted_text = annotation_handler.format_message_with_citations(
    message_content=response.output[0].content[0]
)
print(formatted_text)
```

**Annotation Types:**
1. **`file_citation`**: References from file_search tool
2. **`file_path`**: Files generated by code_interpreter

## Context Window Management

### Truncation Strategies

```python
from assistant_core.file_tools import ContextManager

# Auto truncation (default)
truncation = ContextManager.build_truncation_strategy("auto")

# Keep last N messages
truncation = ContextManager.build_truncation_strategy(
    "last_messages",
    last_messages=50
)

# Build complete response config
config = ContextManager.build_response_config(
    max_output_tokens=4000,
    max_prompt_tokens=50000,  # Recommended for file_search
    truncation_strategy=truncation,
)
```

### Token Limits

**Recommendations:**
- **File Search**: `max_prompt_tokens >= 20,000`
- **Long conversations**: `max_prompt_tokens >= 50,000` or remove limit
- **Code Interpreter**: Default limits usually sufficient

## Complete Example: Data Visualization

```python
from assistant_core.file_tools import create_data_visualization_assistant
from assistant_core.ai import get_openai_client

client = get_openai_client()

# Create complete setup
setup = create_data_visualization_assistant(
    client=client,
    csv_file_path="revenue-forecast.csv",
    model="gpt-4o",
)

# Use the setup
from openai import OpenAI
response = client.responses.create(
    model="gpt-4o",
    conversation=setup["conversation_id"],
    instructions=setup["instructions"],
    tools=setup["tools"],
    input=[{
        "role": "user",
        "content": [{
            "type": "input_text",
            "text": "Create 3 data visualizations based on trends.",
        }],
    }],
    store=True,
)
```

## Integration with generate_ai_reply

All capabilities are integrated into `generate_ai_reply()`:

```python
from assistant_core.ai import generate_ai_reply

response, error, tool_calls = generate_ai_reply(
    history=history,
    persona="AIC",
    prompt="Analyze this data and create visualizations",
    
    # File support
    uploaded_file_ids=["file-123"],
    vector_store_ids=["vs-456"],
    
    # Tool support
    enable_code_interpreter=True,
    enable_file_search=True,
    
    # Image support
    image_urls=["https://example.com/chart.png"],
    image_detail="high",
    
    # Context management
    max_tokens=4000,
    conversation_id="conv-789",
)
```

## Demo Script

Run the comprehensive demo:

```bash
# File upload
python scripts/enhanced_capabilities_demo.py \
    --demo file_upload \
    --file data.csv --file report.pdf

# Code interpreter
python scripts/enhanced_capabilities_demo.py \
    --demo code_interpreter \
    --file data.csv \
    --question "Analyze trends and create visualizations"

# File search
python scripts/enhanced_capabilities_demo.py \
    --demo file_search \
    --file doc1.pdf --file doc2.pdf \
    --question "What are the key points?"

# Image analysis
python scripts/enhanced_capabilities_demo.py \
    --demo image_analysis \
    --image https://example.com/image.png \
    --image-detail high \
    --question "What is in this image?"

# Data visualization
python scripts/enhanced_capabilities_demo.py \
    --demo data_viz \
    --file revenue.csv

# Run all demos
python scripts/enhanced_capabilities_demo.py --demo all
```

## Best Practices

1. **File Organization**: Use vector stores for knowledge bases, code_interpreter for data analysis
2. **Image Detail**: Use "low" for quick previews, "high" for detailed analysis
3. **Token Management**: Set appropriate limits based on tool usage
4. **Error Handling**: Always check file upload sizes and handle errors gracefully
5. **Cleanup**: Delete unused files and vector stores to manage costs

## Migration from Assistants API

These capabilities replace the following Assistants API patterns:

| Assistants API | Responses API |
|---|---|
| `assistant.tool_resources` | `tools` array with resource configs |
| `thread.messages` with attachments | `conversation.items` with file references |
| `run` with tool calls | `response` with tool calls in output |
| Message annotations | Same format, use `MessageAnnotationHandler` |

See `docs/ASSISTANTS_MIGRATION.md` for complete migration guide.









