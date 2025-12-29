# Assistants API Migration Guide

This document outlines the migration from the deprecated Assistants API to the Responses API.

## Overview

OpenAI has deprecated the Assistants API in favor of the Responses API. The Assistants API will shut down on **August 26, 2026**. This codebase has been updated to support both patterns during the transition period.

**Migration Guide**: https://platform.openai.com/docs/assistants/migration

## Key Changes

| Before (Assistants API) | Now (Responses API) | Why? |
|---|---|---|
| **Assistants** | **Prompts** | Prompts hold configuration (model, tools, instructions) and are easier to version and update |
| **Threads** | **Conversations** | Streams of items instead of just messages |
| **Runs** | **Responses** | Responses send input items or use a conversation object and receive output items; tool call loops are explicitly managed |
| **Run steps** | **Items** | Generalized objects—can be messages, tool calls, outputs, and more |

## What's Changed in This Codebase

### 1. Deprecated Methods

The following methods now emit deprecation warnings:

- `OpenAIClient.create_assistant()` - Use Prompts created in the dashboard instead
- `scripts/assistants_demo.py` - Use `scripts/responses_demo.py` instead

### 2. New Features Added

#### Conversations API Support

Conversations replace Threads and provide better state management:

```python
from assistant_core.ai_layer.openai_client import OpenAIClient

client = OpenAIClient()
await client.initialize()

# Create a conversation
conversation = await client.create_conversation(
    items=[{"role": "user", "content": [{"type": "input_text", "text": "Hello"}]}],
    metadata={"user_id": "user123"}
)

# Use conversation in responses
response = await client.responses.create(
    model="gpt-4o-mini",
    input=[{"role": "user", "content": [{"type": "input_text", "text": "What are the 5 Ds of dodgeball?"}]}],
    conversation=conversation["id"],
    store=True
)
```

#### Helper Functions

New helper module: `assistant_core/conversation_helpers.py`

- `create_conversation_from_history()` - Convert messages to a conversation
- `migrate_thread_to_conversation()` - Migrate old threads to conversations
- `use_conversation_for_chat()` - Simplified chat interface using conversations

### 3. Updated Functions

#### `generate_ai_reply()`

Now supports both `conversation_id` and `previous_response_id`:

```python
# Using Conversations (recommended)
response, error, tool_calls = generate_ai_reply(
    history=history,
    persona="AIC",
    prompt="What are the 5 Ds of dodgeball?",
    conversation_id="conv_123"  # Persistent state
)

# Using previous_response_id (backward compatible)
response, error, tool_calls = generate_ai_reply(
    history=history,
    persona="AIC",
    prompt="What are the 5 Ds of dodgeball?",
    previous_response_id="resp_456"  # Legacy pattern
)
```

## Migration Steps

### Step 1: Create Prompts in Dashboard

1. Go to OpenAI Dashboard → Prompts
2. Create a prompt for each assistant you use
3. Store the prompt ID in your configuration

### Step 2: Replace Threads with Conversations

**Before (Assistants API):**
```python
thread = client.beta.threads.create()
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

**After (Responses API):**
```python
conversation = client.conversations.create()
response = client.responses.create(
    prompt={"id": "prompt_123"},
    input=[{"role": "user", "content": [{"type": "input_text", "text": "Hello"}]}],
    conversation=conversation.id
)
```

### Step 3: Update Tool Handling

**Before:**
```python
run = wait_for_run(client, thread_id, run.id)
if run.status == "requires_action":
    tool_outputs = handle_tool_calls(run)
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )
```

**After:**
```python
response = client.responses.create(...)
tool_calls = extract_function_calls(response)
if tool_calls:
    tool_outputs = handle_tool_calls(tool_calls)
    response = client.responses.create(
        conversation=conversation.id,
        input=[{
            "role": "tool",
            "content": [{
                "type": "tool_output",
                "tool_call_id": output["tool_call_id"],
                "output": output["output"]
            } for output in tool_outputs]
        }]
    )
```

### Step 4: Migrate Existing Threads

Use the helper function to migrate existing threads:

```python
from assistant_core.conversation_helpers import migrate_thread_to_conversation

conversation = migrate_thread_to_conversation(
    client=client,
    thread_id="thread_123",
    metadata={"migrated_from": "thread_123"}
)
```

## Benefits of Migration

1. **Simpler API**: Direct request/response pattern instead of async polling
2. **Better State Management**: Conversations store items server-side without expiration
3. **Version Control**: Prompts can be versioned and managed in dashboard
4. **New Features**: Access to deep research, MCP, computer use, and more
5. **Performance**: Better performance and lower latency

## Backward Compatibility

The codebase maintains backward compatibility during the transition:

- `create_assistant()` still works but emits deprecation warnings
- `previous_response_id` pattern still supported
- Old `assistants_demo.py` script still functional

## Examples

### New Demo Script

See `scripts/responses_demo.py` for a complete example using the Responses API:

```bash
# Create a conversation and use it
python scripts/responses_demo.py \
    --create-conversation \
    --question "What are the 5 Ds of dodgeball?" \
    --question "Explain why this is funny."

# Use a prompt from dashboard
python scripts/responses_demo.py \
    --prompt-id prompt_123 \
    --conversation-id conv_456 \
    --question "Solve 3x + 11 = 14"
```

### Using Conversations in Code

```python
from assistant_core.ai import generate_ai_reply
from assistant_core.ai_layer.openai_client import OpenAIClient

# Initialize client
client = OpenAIClient()
await client.initialize()

# Create conversation
conversation = await client.create_conversation(
    metadata={"session_id": "session_123"}
)

# Use in generate_ai_reply
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="Hello!",
    conversation_id=conversation["id"]
)
```

## Enhanced Capabilities

The codebase now includes comprehensive file and tool management capabilities inspired by the Assistants API deep dive:

- **File Management**: Upload, manage, and attach files to conversations
- **Code Interpreter**: Execute code with file attachments (up to 20 files)
- **File Search**: Vector store integration for semantic search (up to 10,000 files)
- **Image Handling**: Multimodal inputs with detail level control (low/high/auto)
- **Message Annotations**: Process file citations and file paths
- **Context Management**: Token limits and truncation strategies

See `docs/ENHANCED_CAPABILITIES.md` for complete documentation.

### Quick Example

```python
from assistant_core.file_tools import FileManager, VectorStoreManager
from assistant_core.ai import generate_ai_reply

client = get_openai_client()
file_mgr = FileManager(client)

# Upload file
file_info = file_mgr.upload_file("data.csv", purpose="assistants")

# Use with code interpreter
response, error, tool_calls = generate_ai_reply(
    history=[],
    persona="AIC",
    prompt="Analyze this data and create visualizations",
    enable_code_interpreter=True,
    uploaded_file_ids=[file_info["id"]],
)
```

## Resources

- [Official Migration Guide](https://platform.openai.com/docs/assistants/migration)
- [Assistants API Deep Dive](https://platform.openai.com/docs/assistants/how-it-works) (for reference)
- [Responses API Documentation](https://platform.openai.com/docs/api-reference/responses)
- [Conversations API Documentation](https://platform.openai.com/docs/api-reference/conversations)
- [Prompts in Dashboard](https://platform.openai.com/prompts)
- [Enhanced Capabilities Guide](ENHANCED_CAPABILITIES.md)

## Timeline

- **Now**: Both APIs supported, deprecation warnings active
- **August 26, 2026**: Assistants API shutdown
- **Recommendation**: Migrate before Q2 2026 to allow time for testing

