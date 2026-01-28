# Conversation State Playbook

This guide covers practical patterns for persisting multi-turn conversation state when working with OpenAI’s Responses and Conversations APIs. Use it whenever you need assistants that remember prior turns or run across multiple devices/sessions.

## Manual state management with the Responses API

Every `responses.create` call is stateless, but you can emulate memory by re-sending prior dialogue turns:

```python
from openai import OpenAI

client = OpenAI()

history = [
    {"role": "user", "content": "knock knock."},
    {"role": "assistant", "content": "Who's there?"},
    {"role": "user", "content": "Orange."},
]

response = client.responses.create(
    model="gpt-4o-mini",
    input=history,
)
print(response.output_text)
```

After each response, append the model’s output back into `history` before issuing the next prompt. This makes it easy to ask “tell me another” or follow-up questions without losing context. The JavaScript equivalent is identical—send an array of alternating roles to `openai.responses.create`.

### Tracking state across requests

```python
history = [{"role": "user", "content": "tell me a joke"}]
response = client.responses.create(model="gpt-4o-mini", input=history, store=False)
history += [{"role": item.role, "content": item.content} for item in response.output]
history.append({"role": "user", "content": "tell me another"})
second = client.responses.create(model="gpt-4o-mini", input=history, store=False)
print(second.output_text)
```

Set `store=True` only if you need the response logged in the dashboard; disable it for ephemeral interactions.

## Managing state automatically

### Conversations API

Create a durable conversation object and reuse its ID across sessions:

```python
conversation = openai.conversations.create()

response = openai.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": "What are the 5 Ds of dodgeball?"}],
    conversation=conversation.id,
)
```

Conversation items (messages, tool calls, tool outputs, etc.) persist without the 30‑day TTL that responses receive, making them ideal for assistants that need long-running context.

### `previous_response_id`

Instead of replaying the entire transcript, reference the last response:

```javascript
const response = await openai.responses.create({
  model: "gpt-4o-mini",
  input: "tell me a joke",
  store: true,
});

const followUp = await openai.responses.create({
  model: "gpt-4o-mini",
  previous_response_id: response.id,
  input: [{ role: "user", content: "explain why this is funny." }],
  store: true,
});
```

This API chains responses together so the model retains context without manually stitching prior turns.

## Data retention + billing notes

- Standalone response objects remain viewable for 30 days unless `store=False`.
- Conversation objects do *not* expire automatically; anything attached to them is kept indefinitely.
- Even when you chain responses, every token from prior turns still counts toward billing and context usage.

## Context window management

Remember the model’s maximum context window (input + output +, for reasoning models, “thinking” tokens). For example, `gpt-4o-2024-08-06` allows ~128k tokens total and up to 16,384 generated tokens. Use the [tokenizer](https://platform.openai.com/tokenizer) when you’re unsure about size.

### Compaction (advanced)

If your conversation grows too large, POST the full window to `/responses/compact`. The endpoint keeps all prior user turns, replaces older assistant/tool content with an encrypted summary, and returns a smaller window you can supply on the next turn. Provide consistent `instructions` to both the Responses and Compact calls if you’re using system prompts.

## Quick reference

| Scenario | Recommended approach |
| --- | --- |
| Simple few-turn chat | Manually append inputs/outputs in memory |
| Persistent assistant across sessions | Use the Conversations API and pass `conversation=<id>` |
| Lightweight chaining | Use `previous_response_id` |
| Large/long conversations | Periodically call `/responses/compact` |

See also: [Structured outputs](./structured_outputs.md), [Function calling](./function_calling.md), and [Streaming responses](./streaming_responses.md) for adjacent patterns.
