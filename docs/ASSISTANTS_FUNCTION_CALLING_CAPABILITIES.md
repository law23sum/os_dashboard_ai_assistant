# Assistants API Function Calling - Code Capabilities Summary

This document summarizes all code in the codebase that implements or supports OpenAI Assistants API function calling capabilities.

## ⚠️ Important Note

The Assistants API is **deprecated** and will shut down on August 26, 2026. The codebase has been migrated to use the **Responses API** instead. However, legacy Assistants API code still exists for backward compatibility.

**Migration Guide**: https://platform.openai.com/docs/assistants/migration

---

## 1. Assistants API Implementation (Deprecated)

### 1.1 Core Assistants API Demo Script

**File**: `scripts/assistants_demo.py`

This script demonstrates the full Assistants API function calling workflow:

#### Key Features:
- ✅ **Assistant Creation with Tools**: Creates assistants with function tools defined
- ✅ **Thread Management**: Creates threads for conversations
- ✅ **Run Management**: Initiates runs and polls for completion
- ✅ **Function Call Handling**: Handles `requires_action` status and tool outputs
- ✅ **Tool Output Submission**: Submits tool outputs using `submit_tool_outputs`
- ✅ **Parallel Function Calling**: Supports multiple tool calls in parallel

#### Key Functions:

```python
# Create assistant with function tools
def create_or_update_assistant(
    client: OpenAI,
    *,
    assistant_id: Optional[str],
    name: str,
    instructions: str,
    model: str,
    enable_code: bool,
    enable_file_search: bool,
    files: Optional[List[str]],
    include_function: bool,
) -> Any:
    tools: List[Dict[str, Any]] = []
    if include_function:
        tools.append({"type": "function", "function": DISPLAY_QUIZ_SCHEMA})
    # ... creates assistant with tools
```

```python
# Handle function calls from run
def handle_function_calls(
    run,
    *,
    client: OpenAI,
    thread_id: str,
) -> Any:
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    outputs = []
    for call in tool_calls:
        if call.type != "function":
            continue
        fn_name = call.function.name
        fn_args = json.loads(call.function.arguments)
        # Execute function and collect outputs
        outputs.append({
            "tool_call_id": call.id,
            "output": json.dumps({"responses": responses}),
        })
    
    # Submit all tool outputs at once
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run.id,
        tool_outputs=outputs,
    )
    return wait_for_run(client, thread_id, run.id)
```

#### Example Function Schema:

```python
DISPLAY_QUIZ_SCHEMA = {
    "name": "display_quiz",
    "description": "Displays a quiz and returns mock responses.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "question_type": {
                            "type": "string",
                            "enum": ["MULTIPLE_CHOICE", "FREE_RESPONSE"],
                        },
                        "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["question_text"],
                },
            },
        },
        "required": ["title", "questions"],
    },
}
```

### 1.2 OpenAI Client - Assistants API Methods

**Files**: 
- `assistant_hub/ai_layer/openai_client.py`
- `assistant_core/ai_layer/openai_client.py`

#### `create_assistant()` Method:

```python
async def create_assistant(
    self, name: str, instructions: str, tools: List[str] = None
) -> Dict[str, Any]:
    """
    DEPRECATED: Create an OpenAI Assistant using the legacy Assistants API.
    
    The Assistants API is deprecated and will be shut down on August 26, 2026.
    Migrate to the Responses API using Prompts instead.
    """
    assistant_tools = []
    if tools:
        for tool in tools:
            if tool == "code_interpreter":
                assistant_tools.append({"type": "code_interpreter"})
            elif tool == "retrieval":
                assistant_tools.append({"type": "retrieval"})

    assistant = await self.client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=assistant_tools,
        model=self.config.openai_model,
    )
    return {
        "id": assistant.id,
        "name": assistant.name,
        "instructions": assistant.instructions,
    }
```

### 1.3 Frontend Quickstart Example

**File**: `openai-assistants-quickstart/app/components/chat.tsx`

This React component demonstrates streaming with function calling:

#### Key Features:
- ✅ **Streaming Support**: Uses `AssistantStream` for real-time updates
- ✅ **Event Handling**: Handles `thread.run.requires_action` events
- ✅ **Parallel Tool Calls**: Processes multiple tool calls concurrently
- ✅ **Tool Output Submission**: Submits outputs via streaming API

#### Key Code:

```typescript
// Handle requires_action event
const handleRequiresAction = async (
  event: AssistantStreamEvent.ThreadRunRequiresAction
) => {
  const runId = event.data.id;
  const toolCalls = event.data.required_action.submit_tool_outputs.tool_calls;
  
  // Process all tool calls in parallel
  const toolCallOutputs = await Promise.all(
    toolCalls.map(async (toolCall) => {
      const result = await functionCallHandler(toolCall);
      return { output: result, tool_call_id: toolCall.id };
    })
  );
  
  setInputDisabled(true);
  submitActionResult(runId, toolCallOutputs);
};
```

**File**: `openai-assistants-quickstart/app/api/assistants/route.ts`

Creates assistants with function tools:

```typescript
const assistant = await openai.beta.assistants.create({
  instructions: "You are a helpful assistant.",
  name: "Quickstart Assistant",
  model: "gpt-4o",
  tools: [
    { type: "code_interpreter" },
    {
      type: "function",
      function: {
        name: "get_weather",
        description: "Determine weather in my location",
        parameters: {
          type: "object",
          properties: {
            location: {
              type: "string",
              description: "The city and state e.g. San Francisco, CA",
            },
            unit: {
              type: "string",
              enum: ["c", "f"],
            },
          },
          required: ["location"],
        },
      },
    },
    { type: "file_search" },
  ],
});
```

**File**: `openai-assistants-quickstart/app/api/assistants/threads/[threadId]/actions/route.ts`

Submits tool outputs via streaming:

```typescript
export async function POST(request, { params: { threadId } }) {
  const { toolCallOutputs, runId } = await request.json();

  const stream = openai.beta.threads.runs.submitToolOutputsStream(
    threadId,
    runId,
    { tool_outputs: toolCallOutputs }
  );

  return new Response(stream.toReadableStream());
}
```

---

## 2. Responses API Implementation (Current/Migrated)

### 2.1 Responses API Demo Script

**File**: `scripts/responses_demo.py`

This is the migrated version using the Responses API:

#### Key Differences from Assistants API:
- ✅ **Prompts** instead of Assistants (create in dashboard)
- ✅ **Conversations** instead of Threads
- ✅ **Responses** instead of Runs
- ✅ **Direct function calling** in response output

#### Key Functions:

```python
def handle_function_calls(
    response: Any,
    *,
    client: OpenAI,
) -> Any:
    """Handle function calls from a Responses API response."""
    tool_calls = []
    output = getattr(response, "output", None) or []
    
    # Extract function calls from response output
    for item in output:
        item_type = getattr(item, "type", None)
        if item_type == "function_call":
            # Extract function call details
            tool_calls.append({
                "id": call_id,
                "name": fn_name,
                "arguments": fn_args or "{}",
            })
    
    # Execute functions and return outputs
    outputs = []
    for call in tool_calls:
        # ... execute function
        outputs.append({
            "tool_call_id": call["id"],
            "output": json.dumps({"responses": responses}),
        })
    
    return outputs
```

### 2.2 OpenAI Client - Function Calling (Responses API)

**Files**: 
- `assistant_hub/ai_layer/openai_client.py`
- `assistant_core/ai_layer/openai_client.py`

#### `function_calling()` Method:

```python
async def function_calling(
    self, message: str, functions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Use OpenAI function calling (Responses API custom tools)."""
    tools: List[Dict[str, Any]] = []
    for fn in functions or []:
        if fn.get("type") == "function" and "name" in fn:
            tools.append(fn)
        # Accept "function": {...} (Chat Completions style) too.
        inner = fn.get("function") if fn.get("type") == "function" else fn
        if isinstance(inner, dict) and inner.get("name"):
            tool = {"type": "function", **inner}
            tools.append(tool)
    
    response = await self.client.responses.create(
        model=self.config.openai_model,
        input=[{"role": "user", "content": [{"type": "input_text", "text": message}]}],
        tools=tools or None,
        tool_choice="auto" if tools else None,
        reasoning={"effort": "none"},
        text={"verbosity": "medium"},
        max_output_tokens=800,
        store=False,
    )

    calls = _extract_function_calls(response)
    return {
        "message": _extract_output_text(response),
        "function_call": calls[0] if calls else None,
    }
```

#### Advanced Features Supported:

- ✅ **Allowed Tools Constraint** (GPT-5.2 feature):
```python
# Support allowed_tools for constraining tool usage
tool_choice = "auto" if tools else None
allowed_tools_env = os.getenv("ASSISTANT_HUB_ALLOWED_TOOLS")
if allowed_tools_env and tools:
    allowed_tools_list = json.loads(allowed_tools_env)
    if isinstance(allowed_tools_list, list):
        tool_choice = {
            "type": "allowed_tools",
            "mode": os.getenv("ASSISTANT_HUB_TOOL_CHOICE_MODE", "auto"),
            "tools": allowed_tools_list,
        }
```

- ✅ **Reasoning Effort** (GPT-5.2 feature):
```python
effort = os.getenv("ASSISTANT_HUB_REASONING_EFFORT", "none")
if effort not in ("none", "low", "medium", "high", "xhigh"):
    effort = "none"
```

- ✅ **Text Verbosity** (GPT-5.2 feature):
```python
verbosity = os.getenv("ASSISTANT_HUB_TEXT_VERBOSITY", "medium")
if verbosity not in ("low", "medium", "high"):
    verbosity = "medium"
```

---

## 3. Tool Execution Handlers

### 3.1 Core Tool Execution Function

**Files**:
- `assistant_core/ai.py` (lines 603-734)
- `assistant_hub/ai.py` (lines 536-728)
- `assistant_hub_gui/assistant_hub/ai.py` (lines 651-885)

#### `execute_tool_call()` Function:

```python
def execute_tool_call(tool_call, cwd: Optional[str] = None) -> Dict:
    """Execute a tool call (shell command or file operation) and return the result."""
    
    # Support both Chat Completions tool_call objects and Responses API dict payloads
    if isinstance(tool_call, dict):
        fn_name = tool_call.get("name")
        fn_args_raw = tool_call.get("arguments", "{}")
        tool_call_id = tool_call.get("id")
    else:
        fn_name = tool_call.function.name
        fn_args_raw = tool_call.function.arguments
        tool_call_id = tool_call.id

    if fn_name == "read_file":
        # Read file implementation
        args = json.loads(fn_args_raw or "{}")
        file_path = args.get("file_path", "")
        max_lines = args.get("max_lines", 1000)
        # ... file reading logic
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": "read_file",
            "content": f"File: {file_path}\nTotal lines: {total_lines}\n\n{content}",
        }

    elif fn_name == "execute_command":
        # Execute shell command
        args = json.loads(fn_args_raw or "{}")
        command = args.get("command", "")
        work_dir = args.get("working_directory", cwd) or cwd or os.getcwd()
        result = run_bash_command(command, cwd=work_dir)
        # ... format output
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": "execute_command",
            "content": content,
        }

    return {
        "tool_call_id": tool_call_id,
        "role": "tool",
        "name": "unknown",
        "content": "Unknown tool",
    }
```

#### Supported Tools:
- ✅ **read_file**: Read file contents with line limits
- ✅ **execute_command**: Execute shell commands with working directory support
- ✅ **Extensible**: Easy to add new tool types

### 3.2 GUI Integration - Tool Call Handling

**Files**:
- `ui/gui.py` (lines 2289-2321)
- `assistant_hub/gui.py` (lines 3227-3276)
- `assistant_hub_gui/assistant_hub/gui.py` (lines 3253-3276)

#### Interactive Tool Call Loop:

```python
def worker():
    # Interactive loop: handle tool calls
    iteration = 0
    max_iterations = 10
    
    while iteration < max_iterations:
        reply, error, tool_calls = generate_ai_reply(
            # ... parameters
        )
        
        if error:
            # Handle error
            return
        
        # If there are tool calls, execute them
        if tool_calls:
            tool_results = []
            for tool_call in tool_calls:
                command_preview = None
                if tool_call.function.name == "execute_command":
                    args = json.loads(tool_call.function.arguments)
                    command_preview = args.get("command", "")
                    
                    # Request permission for potentially destructive commands
                    if command_preview and not self._request_overwrite_permission(command_preview, cwd):
                        continue

                result = execute_tool_call(tool_call, cwd=cwd)
                tool_results.append(result)
                
                # Store terminal command and result in chat immediately
                if tool_call.function.name == "execute_command":
                    # ... display command and result in UI
                    self._store_chat_message(responder, 'user', header, kind='terminal')
                    self._store_chat_message(responder, 'assistant', result["content"], kind='terminal_result')
            
            # Store tool results for next iteration
            for result in tool_results:
                self._store_chat_message(responder, "tool", result["content"], kind="tool_result")
            
            iteration += 1
            continue
        else:
            # No more tool calls, return the final reply
            return
```

---

## 4. Function Call Extraction Utilities

### 4.1 Response Parsing Functions

**Files**: 
- `assistant_hub/ai_layer/openai_client.py`
- `assistant_core/ai_layer/openai_client.py`

#### `_extract_function_calls()` Function:

```python
def _extract_function_calls(response: Any) -> Optional[List[Dict[str, Any]]]:
    """Extract custom function calls from a Responses API response."""
    calls: List[Dict[str, Any]] = []
    output = getattr(response, "output", None) or []
    
    for item in output:
        item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
        if item_type != "function_call":
            continue
        
        call_id = getattr(item, "id", None) or (item.get("id") if isinstance(item, dict) else None)
        name = getattr(item, "name", None) or (item.get("name") if isinstance(item, dict) else None)
        arguments = getattr(item, "arguments", None) or (item.get("arguments") if isinstance(item, dict) else None)
        
        if not name:
            fn = getattr(item, "function", None) or (item.get("function") if isinstance(item, dict) else None) or {}
            name = getattr(fn, "name", None) or (fn.get("name") if isinstance(fn, dict) else None)
            if not arguments:
                arguments = getattr(fn, "arguments", None) or (fn.get("arguments") if isinstance(fn, dict) else None)
        
        if name:
            calls.append({"id": call_id, "name": name, "arguments": arguments or "{}"})
    
    return calls or None
```

---

## 5. AI Reply Generation with Tool Support

### 5.1 Main AI Reply Function

**Files**:
- `assistant_core/ai.py` (lines 398-577)
- `assistant_hub/ai.py` (lines 388-531)
- `assistant_hub_gui/assistant_hub/ai.py` (lines 499-643)

#### `generate_ai_reply()` Function:

```python
def generate_ai_reply(
    history: List[ChatMessage],
    persona: str,
    prompt: Optional[str] = None,
    *,
    enable_shell: bool = True,
    custom_tools: Optional[List[Dict[str, Any]]] = None,
    # ... other parameters
) -> Tuple[str, Optional[str], Optional[List[Dict]]]:
    """Send the conversation to OpenAI and return (reply, error_message, tool_calls)."""
    
    # Prepare tools/functions for shell execution
    tools = []
    if enable_shell:
        tools.extend(get_shell_functions(cwd or os.getcwd()))
    
    # Add custom tools if provided
    if custom_tools:
        tools.extend(custom_tools)
    
    # Add apply_patch tool for code editing (GPT-5.2 feature)
    if os.getenv("ASSISTANT_HUB_ENABLE_APPLY_PATCH", "false").lower() == "true":
        tools.append({
            "type": "function",
            "function": {
                "name": "apply_patch",
                "description": "Apply a patch to create, update, or delete files in the codebase using structured diffs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file to modify"
                        },
                        "patch": {
                            "type": "string",
                            "description": "The patch to apply in unified diff format"
                        }
                    },
                    "required": ["file_path", "patch"]
                }
            }
        })
    
    # Create response with tools
    payload: Dict[str, Any] = {
        "model": model,
        "instructions": instructions,
        "input": _to_responses_input(remaining),
        "reasoning": {"effort": effort},
        "text": {"verbosity": verbosity},
        "max_output_tokens": max_tokens,
        "store": False,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    
    response = client.responses.create(**payload)
    
    # Extract tool calls
    tool_calls = _extract_function_calls(response)
    text = _extract_output_text(response)
    
    return text.strip(), None, tool_calls
```

#### Shell Functions:

The `get_shell_functions()` function (imported from shell utilities) provides:
- ✅ **execute_command**: Execute shell commands
- ✅ **read_file**: Read file contents
- ✅ **write_file**: Write file contents
- ✅ **list_directory**: List directory contents

---

## 6. Structured Outputs Support

### 6.1 Current Status

The codebase **does not currently implement** Structured Outputs with `strict: true` for Assistants API function calling. However, the Responses API implementation supports it.

### 6.2 How to Add Structured Outputs

To add Structured Outputs support, modify the function tool definition:

```python
tool = {
    "type": "function",
    "function": {
        "name": "get_current_temperature",
        "description": "Get the current temperature for a specific location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g., San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["Celsius", "Fahrenheit"],
                    "description": "The temperature unit to use."
                }
            },
            "required": ["location", "unit"],
            "additionalProperties": False  # Required for strict mode
        },
        "strict": True  # Enable structured outputs
    }
}
```

**Note**: Structured Outputs are **not supported** in the Assistants API when using vision.

---

## 7. Parallel Function Calling

### 7.1 Support Status

✅ **Fully Supported**: The codebase handles parallel function calling in both:
- Assistants API: Multiple `tool_calls` in `required_action.submit_tool_outputs.tool_calls`
- Responses API: Multiple `function_call` items in response `output`

### 7.2 Implementation Examples

#### Assistants API (Streaming):
```python
# All tool calls are processed in parallel
tool_calls = run.required_action.submit_tool_outputs.tool_calls
outputs = []
for call in tool_calls:
    # Execute each tool call
    outputs.append({
        "tool_call_id": call.id,
        "output": result,
    })

# Submit all outputs at once
run = client.beta.threads.runs.submit_tool_outputs(
    thread_id=thread_id,
    run_id=run.id,
    tool_outputs=outputs,
)
```

#### Responses API:
```python
# Extract all function calls
tool_calls = _extract_function_calls(response)

# Execute all in parallel (if needed)
for call in tool_calls:
    result = execute_function(call)
    # ... collect results
```

#### Frontend (TypeScript):
```typescript
// Process all tool calls concurrently
const toolCallOutputs = await Promise.all(
  toolCalls.map(async (toolCall) => {
    const result = await functionCallHandler(toolCall);
    return { output: result, tool_call_id: toolCall.id };
  })
);
```

---

## 8. Streaming Support

### 8.1 Assistants API Streaming

**File**: `openai-assistants-quickstart/app/components/chat.tsx`

✅ **Fully Implemented** with event handlers:

```typescript
const handleReadableStream = (stream: AssistantStream) => {
  // Text streaming
  stream.on("textCreated", handleTextCreated);
  stream.on("textDelta", handleTextDelta);
  
  // Code interpreter streaming
  stream.on("toolCallCreated", toolCallCreated);
  stream.on("toolCallDelta", toolCallDelta);
  
  // Function calling events
  stream.on("event", (event) => {
    if (event.event === "thread.run.requires_action")
      handleRequiresAction(event);
    if (event.event === "thread.run.completed") 
      handleRunCompleted();
  });
};
```

### 8.2 Responses API Streaming

The Responses API supports streaming natively. The codebase can be extended to handle streaming responses.

---

## 9. Summary of Capabilities

### ✅ Fully Implemented:

1. **Assistants API Function Calling** (deprecated but functional)
   - Assistant creation with function tools
   - Thread and run management
   - Tool call handling and output submission
   - Parallel function calling
   - Streaming support (frontend)

2. **Responses API Function Calling** (current)
   - Function tool definitions
   - Tool call extraction
   - Tool execution
   - Parallel function calling
   - Advanced features (allowed_tools, reasoning effort, verbosity)

3. **Tool Execution**
   - Shell command execution
   - File operations (read/write)
   - Extensible tool system

4. **GUI Integration**
   - Interactive tool call loops
   - Real-time command display
   - Permission requests for destructive commands

### ⚠️ Partially Implemented:

1. **Structured Outputs**: Not yet implemented for Assistants API, but can be added

2. **Streaming**: Full support in frontend, partial in backend

### ❌ Not Implemented:

1. **Structured Outputs with `strict: true`** for Assistants API function calling
2. **Event Handler Classes** for Python streaming (like the TypeScript implementation)

---

## 10. Migration Path

The codebase is actively migrating from Assistants API to Responses API:

1. **Legacy Code**: `scripts/assistants_demo.py` (marked as deprecated)
2. **Current Code**: `scripts/responses_demo.py` (migrated version)
3. **Client Methods**: `create_assistant()` marked as deprecated, `function_calling()` uses Responses API

**Recommendation**: Use the Responses API implementations going forward.

---

## 11. Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `scripts/assistants_demo.py` | Assistants API demo | ⚠️ Deprecated |
| `scripts/responses_demo.py` | Responses API demo | ✅ Current |
| `assistant_hub/ai_layer/openai_client.py` | OpenAI client with function calling | ✅ Current |
| `assistant_core/ai_layer/openai_client.py` | OpenAI client with function calling | ✅ Current |
| `assistant_core/ai.py` | Tool execution and AI reply generation | ✅ Current |
| `assistant_hub/ai.py` | Tool execution and AI reply generation | ✅ Current |
| `openai-assistants-quickstart/app/components/chat.tsx` | Frontend streaming example | ✅ Reference |
| `openai-assistants-quickstart/app/api/assistants/route.ts` | Assistant creation example | ✅ Reference |

---

## 12. Example Usage

### Using Responses API (Recommended):

```python
from assistant_hub.ai_layer.openai_client import OpenAIClient

client = OpenAIClient()
await client.initialize()

# Define function tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["C", "F"]}
                },
                "required": ["location"]
            }
        }
    }
]

# Call with function tools
result = await client.function_calling(
    message="What's the weather in San Francisco?",
    functions=tools
)

# Extract function calls
if result["function_call"]:
    # Execute function
    # ... then create follow-up response with tool outputs
```

---

## Conclusion

The codebase has comprehensive support for function calling in both the deprecated Assistants API and the current Responses API. The Responses API implementation includes advanced features like allowed tools constraints, reasoning effort control, and text verbosity settings. Tool execution is fully integrated with the GUI and supports interactive loops for multi-step operations.



