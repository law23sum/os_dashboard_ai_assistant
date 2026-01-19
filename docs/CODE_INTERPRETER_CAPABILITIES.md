# Code Interpreter Capabilities in AI OS

This document summarizes all code interpreter implementations and capabilities found in the codebase, based on OpenAI's Code Interpreter documentation.

## Overview

The codebase has comprehensive support for OpenAI's Code Interpreter tool, allowing assistants to write and run Python code in a sandboxed execution environment. Code Interpreter can process files with diverse data formats and generate files with data and images of graphs.

## Key Implementation Files

### 1. Core AI Integration (`assistant_core/ai.py`)

**Location:** Lines 416-543

**Key Features:**
- `enable_code_interpreter` parameter in `generate_ai_reply()` function
- Supports up to 20 files attached to code interpreter
- Integrated with Responses API

**Code Snippet:**
```python
# Add code_interpreter tool if enabled
if enable_code_interpreter:
    code_tool: Dict[str, Any] = {"type": "code_interpreter"}
    if uploaded_file_ids:
        code_tool["code_interpreter"] = {"file_ids": uploaded_file_ids[:20]}  # Max 20 files
    tools.append(code_tool)
```

**Function Signature:**
```python
def generate_ai_reply(
    history: List[ChatMessage],
    persona: str,
    prompt: Optional[str] = None,
    *,
    enable_code_interpreter: bool = False,
    uploaded_file_ids: Optional[List[str]] = None,
    # ... other parameters
) -> Tuple[str, Optional[str], Optional[List[Dict]]]:
```

### 2. File Tools Module (`assistant_core/file_tools.py`)

**Location:** Lines 242-321

**Key Classes:**
- `ToolResourceBuilder`: Builds tool resource configurations for Responses API
- `MessageAnnotationHandler`: Handles file citations and file paths from code interpreter

**Methods:**

#### `build_code_interpreter_resources()`
```python
@staticmethod
def build_code_interpreter_resources(
    file_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build code_interpreter tool resources.
    Supports up to 20 files attached to code_interpreter.
    """
```

#### `build_tools_config()`
```python
@staticmethod
def build_tools_config(
    enable_code_interpreter: bool = False,
    enable_file_search: bool = False,
    code_interpreter_file_ids: Optional[List[str]] = None,
    file_search_vector_store_ids: Optional[List[str]] = None,
    custom_functions: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Build complete tools configuration for Responses API.
    """
```

### 3. CLI Tool (`scripts/ai_code_interpreter.py`)

**Location:** Complete file (175 lines)

**Features:**
- Lightweight CLI for invoking OpenAI's Code Interpreter via Responses API
- Supports memory tiers: 1g, 4g, 16g, 64g
- Container reuse with `--container-id` option
- File upload support with multiple files
- Renders code interpreter outputs and generated files

**Usage Examples:**
```bash
# Basic usage
python scripts/ai_code_interpreter.py "Plot sin(x) for x∈[-2π, 2π]"

# With file upload
python scripts/ai_code_interpreter.py --file data/sample.csv "Summarize uploads"

# With memory configuration
python scripts/ai_code_interpreter.py --memory 4g "Process large dataset"

# With container reuse
python scripts/ai_code_interpreter.py --container-id <container_id> "Continue analysis"
```

**Key Functions:**
- `upload_files()`: Upload files to OpenAI Files API
- `build_tool_config()`: Build tool configuration with container settings
- `render_response()`: Display code interpreter outputs, logs, and generated files

**Container Configuration:**
```python
container: Dict[str, Any] = {
    "type": "auto",  # or specific container_id
    "memory_limit": args.memory,  # "1g", "4g", "16g", "64g"
}
if file_ids:
    container["file_ids"] = file_ids

return {
    "type": "code_interpreter",
    "container": container,
}
```

### 4. Assistants Demo (`scripts/assistants_demo.py`)

**Location:** Lines 145-192

**Features:**
- Demonstrates code interpreter with assistant creation
- File upload and attachment to code interpreter
- Integration with tool resources

**Code Snippet:**
```python
if enable_code or files:
    tools.append({"type": "code_interpreter"})
    tool_resources["code_interpreter"] = {"file_ids": []}

if files:
    for raw_path in files:
        upload = client.files.create(
            file=(Path(raw_path).name, data),
            purpose="assistants",
        )
        if "code_interpreter" in tool_resources:
            tool_resources["code_interpreter"]["file_ids"].append(upload.id)
```

### 5. Enhanced Capabilities Demo (`scripts/enhanced_capabilities_demo.py`)

**Location:** Lines 112-170

**Features:**
- Comprehensive demo of code interpreter with file attachments
- Integration with FileManager and ToolResourceBuilder
- Conversation-based workflow

**Example Usage:**
```python
def demo_code_interpreter(
    client: OpenAI, files: List[str], question: str, model: str
) -> None:
    """Demonstrate code interpreter with file attachments."""
    file_mgr = FileManager(client)
    tool_builder = ToolResourceBuilder()
    
    # Upload files
    file_ids = []
    for file_path in files:
        file_info = file_mgr.upload_file(file_path, purpose="assistants")
        file_ids.append(file_info["id"])
    
    # Build tools with code interpreter
    tools = tool_builder.build_tools_config(
        enable_code_interpreter=True,
        code_interpreter_file_ids=file_ids,
    )
    
    # Create response
    response = client.responses.create(
        model=model,
        conversation=conversation.id,
        tools=tools,
        # ...
    )
```

## Container Files and Generated Files

### Handling Generated Files

The codebase includes support for downloading files generated by code interpreter:

**From `scripts/ai_code_interpreter.py` (Lines 111-151):**
```python
def render_response(response) -> None:
    container_refs: List[Dict[str, str]] = []
    for entry in getattr(response, "output", []) or []:
        # ... process annotations
        for annotation in chunk.get("annotations", []) or []:
            if annotation.get("type") == "container_file_citation":
                container_refs.append({
                    "container_id": annotation.get("container_id", ""),
                    "file_id": annotation.get("file_id", ""),
                    "filename": annotation.get("filename", ""),
                })
    
    # Display generated files
    if container_refs:
        print("\nGenerated files:")
        for ref in container_refs:
            print(f"  - {ref['filename']} (container={ref['container_id']}, file_id={ref['file_id']})")
        print(
            "Download files using `client.container_files.content(container_id, file_id)` "
            "or the /v1/container-files endpoints."
        )
```

**Example from Reference Implementation:**
```python
# Download files from container (from the OpenAI reference archive)
if container_id:
    url = f"https://api.openai.com/v1/containers/{container_id}/files"
    resp_files = requests.get(url, headers=headers)
    files = resp_files.json().get("data", [])
    for f in files:
        if f["source"] != "user":  # Only download generated files
            url_download = f"https://api.openai.com/v1/containers/{container_id}/files/{cfile_id}/content"
            # Download file...
```

## File Support

### Supported File Formats

Based on OpenAI documentation, code interpreter supports:
- **Data files**: `.csv`, `.json`, `.xlsx`, `.xml`
- **Documents**: `.pdf`, `.docx`, `.pptx`, `.txt`, `.md`, `.html`
- **Code**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.rb`, `.php`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif` (for analysis, not generation in older API)
- **Archives**: `.zip`, `.tar`

### File Limits

- **Max file size**: 512 MB
- **Max files per code_interpreter**: 20 files
- **Max tokens per file**: 5,000,000
- **Project limit**: 100 GB (contact support to increase)

### File Purpose

Files must be uploaded with `purpose="assistants"`:
```python
file_info = file_mgr.upload_file("data.csv", purpose="assistants")
```

## Memory Tiers

The CLI tool supports container memory tiers:
- `1g`: 1 GB (default)
- `4g`: 4 GB
- `16g`: 16 GB
- `64g`: 64 GB

```python
MEMORY_CHOICES = {"1g", "4g", "16g", "64g"}

container: Dict[str, Any] = {
    "type": "auto",
    "memory_limit": args.memory,  # One of MEMORY_CHOICES
}
```

## Integration Points

### 1. Assistant Core AI Layer

**File:** `assistant_core/ai_layer/openai_client.py` (Lines 279-330)

```python
async def create_assistant(
    self, name: str, instructions: str, tools: List[str] = None
) -> Dict[str, Any]:
    assistant_tools = []
    if tools:
        for tool in tools:
            if tool == "code_interpreter":
                assistant_tools.append({"type": "code_interpreter"})
```

### 2. Assistant Hub

**File:** `assistant_hub/ai_layer/openai_client.py` (Lines 292-293)

Similar implementation for assistant creation with code interpreter support.

## Usage Examples

### Basic Usage

```python
from assistant_core.ai import generate_ai_reply
from assistant_core.file_tools import FileManager

client = get_openai_client()
file_mgr = FileManager(client)

# Upload file
file_info = file_mgr.upload_file("data.csv", purpose="assistants")

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
    custom_functions=[...]  # Optional custom functions
)

# Use with Responses API
response = client.responses.create(
    model="gpt-5.2",
    tools=tools,
    input=[...],
)
```

### With Container Configuration

```python
# Using CLI tool
python scripts/ai_code_interpreter.py \
    --memory 4g \
    --file data1.csv \
    --file data2.csv \
    "Analyze trends and create visualizations"

# Programmatically
tool_config = {
    "type": "code_interpreter",
    "container": {
        "type": "auto",
        "memory_limit": "4g",
        "file_ids": ["file-123", "file-456"]
    }
}
```

## Response Processing

### Code Interpreter Outputs

The codebase handles code interpreter outputs in multiple formats:

1. **Message outputs**: Text responses from the model
2. **Code interpreter calls**: Python code executed and outputs
3. **File annotations**: References to generated files

**Example from `scripts/ai_code_interpreter.py`:**
```python
elif entry_type == "code_interpreter_call":
    print("```python")
    logs = payload.get("code", "") or payload.get("input", "")
    if logs:
        print(logs.strip())
    print("```")
    for out in payload.get("outputs", []) or []:
        text = out.get("logs") or out.get("text")
        if text:
            print(text.strip())
```

## Best Practices

1. **File Organization**: Use vector stores for knowledge bases, code_interpreter for data analysis
2. **Memory Selection**: Use appropriate memory tier based on dataset size
3. **File Limits**: Remember max 20 files per code_interpreter tool
4. **Error Handling**: Check file upload sizes and handle errors gracefully
5. **Cleanup**: Delete unused files to manage costs

## Documentation References

- **Main Documentation**: `docs/ENHANCED_CAPABILITIES.md`
- **OpenAI Reference**: `reference/openai-reference/examples/data/oai_docs/tool-code-interpreter.txt`
- **Migration Guide**: `docs/ASSISTANTS_MIGRATION.md`

## Related Capabilities

- **File Search**: Vector store integration for semantic search (complementary to code interpreter)
- **Message Annotations**: Handle file citations and file paths
- **Container Files API**: Download files generated by code interpreter

## API Compatibility

The codebase uses the **Responses API** (newer API) rather than the legacy Assistants API:

- ✅ Uses `client.responses.create()` instead of `client.beta.assistants.create()`
- ✅ Tools configured in `tools` array directly
- ✅ Container configuration in tool definition
- ✅ File IDs passed in container configuration

## Demo Scripts

Run comprehensive demos:

```bash
# Code interpreter demo
python scripts/enhanced_capabilities_demo.py \
    --demo code_interpreter \
    --file data.csv \
    --question "Analyze trends and create visualizations"

# Direct CLI usage
python scripts/ai_code_interpreter.py \
    --file data.csv \
    --memory 4g \
    "Create visualizations"
```

## Summary

The codebase has comprehensive, production-ready support for OpenAI's Code Interpreter with:
- ✅ Core integration in `assistant_core/ai.py`
- ✅ Dedicated CLI tool in `scripts/ai_code_interpreter.py`
- ✅ File management utilities in `assistant_core/file_tools.py`
- ✅ Multiple demo implementations
- ✅ Container configuration with memory tiers
- ✅ Generated file handling
- ✅ Annotation processing

All implementations follow OpenAI's latest Responses API patterns and support advanced features like container reuse and memory tier selection.

