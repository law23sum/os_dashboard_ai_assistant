# GPT-5.2 Features Implementation

This document describes the GPT-5.2 features implemented in the AI OS.

## Overview

GPT-5.2 is OpenAI's best general-purpose model, part of the GPT-5 flagship model family. It shows improvements over GPT-5.1 in:
- General intelligence
- Instruction following
- Accuracy and token efficiency
- Multimodality—especially vision
- Code generation—especially front-end UI creation
- Tool calling and context management in the API
- Spreadsheet understanding and creation

## Model Variants

| Variant | Best For | Use Case |
|---------|----------|----------|
| `gpt-5.2` | Complex reasoning, broad world knowledge, code-heavy or multi-step agentic tasks | Default for most complex tasks |
| `gpt-5.2-pro` | Tough problems requiring harder thinking | When you need maximum reasoning power |
| `gpt-5.1-codex-max` | Interactive coding products; full spectrum of coding tasks | Coding-specific applications |
| `gpt-5-mini` | Cost-optimized reasoning and chat; balances speed, cost, and capability | General chat and cost-sensitive use cases |
| `gpt-5-nano` | High-throughput tasks, especially simple instruction-following or classification | Simple, high-volume tasks |

## Key Features Implemented

### 1. Reasoning Effort Levels

GPT-5.2 supports multiple reasoning effort levels to control how much the model "thinks" before responding:

- **`none`** (default): Lower-latency interactions, minimal reasoning tokens
- **`low`**: Light reasoning for faster responses
- **`medium`**: Balanced reasoning for most tasks
- **`high`**: Thorough reasoning for complex problems
- **`xhigh`**: Maximum reasoning effort (new in GPT-5.2)

**Usage:**
```python
# Set via environment variable
export ASSISTANT_HUB_REASONING_EFFORT=medium

# Or in code
response = generate_ai_reply(
    history, persona, prompt,
    # ... other params
)
# Uses ASSISTANT_HUB_REASONING_EFFORT env var
```

**Note:** `temperature`, `top_p`, and `logprobs` are only supported when `reasoning.effort == "none"`.

### 2. Verbosity Control

Control output token generation:

- **`low`**: Concise answers, minimal commentary
- **`medium`** (default): Balanced output
- **`high`**: Thorough explanations, structured code with inline comments

**Usage:**
```python
export ASSISTANT_HUB_TEXT_VERBOSITY=low
```

### 3. Custom Tools

GPT-5.2 supports custom tools with freeform text inputs (not limited to JSON):

```python
from assistant_hub.ai import create_custom_tool

# Create a custom tool
code_exec_tool = create_custom_tool(
    name="code_exec",
    description="Executes arbitrary python code",
)

# Use with custom_tools parameter
response, error, tool_calls = generate_ai_reply(
    history, persona, prompt,
    custom_tools=[code_exec_tool]
)
```

**Custom tools with CFG (Context-Free Grammar):**
```python
sql_tool = create_custom_tool(
    name="sql_query",
    description="Execute SQL queries",
    grammar="""
        start: SELECT column_list FROM table_name [WHERE condition]
        column_list: column ("," column)*
        ...
    """
)
```

### 4. Allowed Tools

Constrain which tools can be used from a larger toolkit:

```python
# Set via environment variable (JSON array of tool names)
export ASSISTANT_HUB_ALLOWED_TOOLS='["execute_command", "read_file"]'
export ASSISTANT_HUB_TOOL_CHOICE_MODE=auto  # or "required"
```

**Modes:**
- `auto`: Model may pick any of the allowed tools
- `required`: Model must invoke one of the allowed tools

### 5. Previous Response ID (Chain of Thought)

Pass chain of thought between turns for improved intelligence and lower latency:

```python
response, error, tool_calls = generate_ai_reply(
    history, persona, prompt,
    previous_response_id=previous_response.id  # From previous API call
)
```

This enables:
- Fewer generated reasoning tokens
- Higher cache hit rates
- Lower latency
- Better multi-turn conversations

### 6. Apply Patch Tool

GPT-5.2's `apply_patch` tool enables structured code editing:

```python
# Enable via environment variable
export ASSISTANT_HUB_ENABLE_APPLY_PATCH=true
```

The tool allows the model to create, update, and delete files using structured diffs, enabling iterative, multistep code editing workflows.

### 7. Preambles

Enable tool call explanations for better transparency:

```python
response, error, tool_calls = generate_ai_reply(
    history, persona, prompt,
    enable_preambles=True
)
```

When enabled, GPT-5.2 will explain why it's calling a tool before each tool invocation, improving debuggability and user confidence.

## Migration Guidance

### From GPT-5.1
- **Drop-in replacement**: `gpt-5.2` with default settings should work as-is
- Consider enabling `previous_response_id` for multi-turn conversations

### From o3
- Use `gpt-5.2` with `medium` or `high` reasoning effort
- Start with `medium` and increase if needed

### From GPT-4.1
- Use `gpt-5.2` with `none` reasoning effort
- Tune prompts for best results
- Increase reasoning effort if needed

### From o4-mini or GPT-4.1-mini
- Use `gpt-5-mini` with prompt tuning

### From GPT-4.1-nano
- Use `gpt-5-nano` with prompt tuning

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASSISTANT_HUB_REASONING_EFFORT` | `none` | Reasoning effort: none, low, medium, high, xhigh |
| `ASSISTANT_HUB_TEXT_VERBOSITY` | `medium` | Output verbosity: low, medium, high |
| `ASSISTANT_HUB_ALLOWED_TOOLS` | - | JSON array of allowed tool names |
| `ASSISTANT_HUB_TOOL_CHOICE_MODE` | `auto` | Tool choice mode: auto, required |
| `ASSISTANT_HUB_ENABLE_APPLY_PATCH` | `false` | Enable apply_patch tool |
| `ASSISTANT_HUB_OPENAI_MODEL` | `gpt-5-mini` | Default model |

## Code Examples

### Basic Usage with GPT-5.2

```python
from assistant_hub.ai import generate_ai_reply, ChatMessage

history = [ChatMessage(role="user", content="Hello!")]
response, error, tool_calls = generate_ai_reply(
    history=history,
    persona="Sora",  # Uses gpt-5.2
    prompt="What is the capital of France?",
)
```

### Using Custom Tools

```python
from assistant_hub.ai import generate_ai_reply, create_custom_tool

# Define custom tool
sql_tool = create_custom_tool(
    name="execute_sql",
    description="Execute SQL queries on the database",
)

response, error, tool_calls = generate_ai_reply(
    history=history,
    persona="AIC",
    prompt="Query the users table",
    custom_tools=[sql_tool],
)
```

### Multi-turn with Previous Response ID

```python
# First turn
response1, error1, tool_calls1 = generate_ai_reply(
    history, persona, "What is 2+2?"
)

# Second turn - pass previous response ID
response2, error2, tool_calls2 = generate_ai_reply(
    history, persona, "What about 3+3?",
    previous_response_id=response1.id,  # Pass CoT from previous turn
)
```

## Best Practices

1. **Start with defaults**: Use `none` reasoning effort and `medium` verbosity initially
2. **Use preambles for debugging**: Enable when you need to understand tool call reasoning
3. **Leverage previous_response_id**: Always pass it in multi-turn conversations
4. **Constrain tools when needed**: Use `allowed_tools` to prevent unintended tool usage
5. **Validate custom tool outputs**: Always validate freeform inputs on the server side
6. **Write concise tool descriptions**: The model chooses tools based on descriptions

## References

- [GPT-5.2 Documentation](https://platform.openai.com/docs/guides/gpt-5-2)
- [Responses API Guide](https://platform.openai.com/docs/guides/responses-api)
- [OpenAI GPT-5.2 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5-2_prompting_guide)










