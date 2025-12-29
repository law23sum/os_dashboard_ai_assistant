# OpenAI Responses API Reference

Authoritative summary of the `/v1/responses` suite that powers GPT-4.1, GPT-5, reasoning, and tool-calling models. Use these endpoints when you need stateful interactions, computer use, web/file search, or background jobs.

---

## Endpoint overview

- `POST /v1/responses` – Create a model response (text, JSON, or tool calls).
- `GET /v1/responses/{response_id}` – Retrieve a previously created response.
- `DELETE /v1/responses/{response_id}` – Permanently delete a stored response.
- `POST /v1/responses/{response_id}/cancel` – Cancel a background response.
- `POST /v1/responses/compact` – Compact (summarize) long conversations.
- `GET /v1/responses/{response_id}/input_items` – List all input items for a response.
- `POST /v1/responses/input_tokens` – Estimate input token counts before sending.

Unless otherwise noted, pass your API key via `Authorization: Bearer $OPENAI_API_KEY` and set `Content-Type: application/json`.

---

## Create a model response

`POST https://api.openai.com/v1/responses`

```bash
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4.1",
    "input": "Tell me a three sentence bedtime story about a unicorn."
  }'
```

Key body fields:

| Field | Type | Description |
| --- | --- | --- |
| `model` | string | Model ID (for example `gpt-4o`, `gpt-5.1`, `o3-mini`). |
| `input` | string or array | User text, images, or tool inputs for this turn. |
| `instructions` | string | Optional system/developer message. |
| `conversation` | string or object | Attach to a stored conversation to keep state. |
| `previous_response_id` | string | Alternate way to keep state by referencing the prior response. |
| `tools` | array | Built-in tools (`web_search`, `file_search`, `code_interpreter`, `shell`, etc.) or custom function calls. |
| `tool_choice` | string or object | Force a tool or allow auto-selection (default). |
| `max_output_tokens` | integer | Hard limit for generated tokens (visible + reasoning). |
| `max_tool_calls` | integer | Limit how many tool invocations the model can emit. |
| `parallel_tool_calls` | boolean | Allow parallel tool calls (default `true`). |
| `temperature` / `top_p` | number | Sampling controls. Prefer editing only one of them. |
| `reasoning` | object | gpt-5 / o-series reasoning controls (effort, budget, etc.). |
| `background` | boolean | Run in the background (poll or cancel later). |
| `include` | array | Request extra data such as tool call sources or logprobs. |
| `store` | boolean | Whether to persist the response for later retrieval (default `true`). |
| `metadata` | map | Up to 16 key/value tags for auditing or querying. |

Successful calls return a `response` object (defined later). Responses with `background: true` will surface `status: queued` or `in_progress`; poll or subscribe to webhooks until completion.

---

## Retrieve a model response

`GET https://api.openai.com/v1/responses/{response_id}`

Use to fetch the latest status, streamed tool outputs, or regenerated text. Optional `include` flags mirror the create endpoint.

```bash
curl https://api.openai.com/v1/responses/resp_123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## Delete a response

`DELETE https://api.openai.com/v1/responses/{response_id}`

Removes the stored record. Returns `{ "id": "...", "object": "response", "deleted": true }`.

---

## Cancel a background response

`POST https://api.openai.com/v1/responses/{response_id}/cancel`

Only valid for responses created with `background: true`. Returns the final `response` object (status will be `cancelled`).

---

## Compact a conversation

`POST https://api.openai.com/v1/responses/compact`

Use when long-running conversations exceed the model’s context window. Compaction keeps all user turns, replaces older assistant/tool turns with encrypted summaries, and returns a shortened window you can pass back to `/responses`.

```bash
curl -X POST https://api.openai.com/v1/responses/compact \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5.1-codex-max",
    "input": [
      {
        "role": "user",
        "content": "Create a simple landing page for a dog petting café."
      },
      {
        "id": "msg_001",
        "type": "message",
        "status": "completed",
        "role": "assistant",
        "content": [{ "type": "output_text", "text": "Below is a single file ..." }]
      }
    ]
  }'
```

Response type: `response.compaction` with compacted `output` plus token usage.

---

## List input items

`GET https://api.openai.com/v1/responses/{response_id}/input_items`

Parameters:

- `limit` (1–100, default 20)
- `order` (`asc` or `desc`, default `desc`)
- `after` (pagination cursor)
- `include` (additional data such as logprobs)

Returns a standard paginated list containing each `message`, `input_image`, or `tool` item that fed into the response.

---

## Estimate input token counts

`POST https://api.openai.com/v1/responses/input_tokens`

Mirrors the create payload but only returns `{ "object": "response.input_tokens", "input_tokens": <int> }`. Supply the same `model`, `input`, `instructions`, `conversation`, `tools`, etc., to plan budgets before sending the full request.

---

## Response object schema

Key fields returned by create/retrieve/cancel operations:

- `id` – Unique response ID (string).
- `object` – Always `response`.
- `created_at` – Unix timestamp.
- `status` – `queued`, `in_progress`, `completed`, `failed`, `cancelled`, or `incomplete`.
- `model` – Model ID used.
- `output` – Array of content items, e.g. `message`, `output_text`, `code_interpreter_call`, `shell_call`, etc.
- `parallel_tool_calls` – Whether parallel tool calls were allowed.
- `previous_response_id` – Pointer to the prior response when chaining state.
- `instructions` – System/developer message for this turn.
- `max_output_tokens`, `max_tool_calls`, `temperature`, `top_p`, `tool_choice`, `tools`, `reasoning`.
- `background`, `store`, `metadata`.
- `prompt_cache_key` / `prompt_cache_retention` – Hints used to reuse cached prefixes (`24h` retention optional).
- `safety_identifier` – Pseudonymous end-user ID for abuse monitoring.
- `usage` – Token accounting with `input_tokens`, `output_tokens`, `output_tokens_details.reasoning_tokens`, and `total_tokens`.
- `error` / `incomplete_details` – Present when failures occur.

SDKs expose `output_text` as a convenience field that concatenates all `output_text` chunks, but you can always inspect the structured `output` array directly.

---

## Input item list object

`GET /responses/{id}/input_items` returns:

```json
{
  "object": "list",
  "data": [
    {
      "id": "msg_abc123",
      "type": "message",
      "role": "user",
      "content": [
        { "type": "input_text", "text": "Tell me a three sentence bedtime story about a unicorn." }
      ]
    }
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc123",
  "has_more": false
}
```

Use pagination to traverse large histories or to replay specific turns into a new response.

---

## Compacted response object

`response.compaction` payloads contain:

- `id` – Compaction job ID.
- `object` – `response.compaction`.
- `created_at` – Unix timestamp.
- `output` – The compacted conversation, combining preserved user turns with encrypted assistant/tool summaries (`type: "compaction"` with `encrypted_content`).
- `usage` – Input/output token totals for the compaction run.

Example:

```json
{
  "id": "resp_001",
  "object": "response.compaction",
  "output": [
    {
      "type": "message",
      "role": "user",
      "content": [{ "type": "input_text", "text": "Summarize our launch checklist from last week." }]
    },
    {
      "type": "message",
      "role": "user",
      "content": [{ "type": "input_text", "text": "You are performing a CONTEXT CHECKPOINT COMPACTION..." }]
    },
    {
      "type": "compaction",
      "id": "cmp_001",
      "encrypted_content": "encrypted-summary"
    }
  ],
  "usage": {
    "input_tokens": 42897,
    "output_tokens": 12000,
    "total_tokens": 54912
  }
}
```

---

## Example Response objects

### Completed response

```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon..."
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 36,
    "output_tokens": 87,
    "total_tokens": 123
  }
}
```

### Response with tool output

```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "status": "completed",
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape..."
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 328,
    "output_tokens": 52,
    "total_tokens": 380
  }
}
```

Use the combination of `status`, `output`, `usage`, and `error` fields to drive UI updates, enforce quotas, and debug tool interactions across both desktop and web clients.

