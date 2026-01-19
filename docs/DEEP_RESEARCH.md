# Deep Research Integration

Use OpenAI’s `o3-deep-research` or `o4-mini-deep-research` models when a task demands multi-source analysis, synthesis, and inline citations that mirror the output of a human research analyst. These models orchestrate web search, vector-store lookups, remote MCP servers, and optional code execution to produce data-backed reports.

## Triggering a research run

```python
from openai import OpenAI

client = OpenAI(timeout=3600)

prompt = """
Research the economic impact of semaglutide on global healthcare systems.
Do:
- Include specific figures, trends, statistics, and measurable outcomes.
- Prioritize reliable, up-to-date sources (WHO, CDC, regulators, pharma earnings).
- Include inline citations and return all source metadata.
"""

response = client.responses.create(
    model="o3-deep-research",
    input=prompt,
    background=True,
    tools=[
        {"type": "web_search_preview"},
        {
            "type": "file_search",
            "vector_store_ids": [
                "vs_68870b8868b88191894165101435eef6",
                "vs_12345abcde6789fghijk101112131415",
            ],
        },
        {"type": "code_interpreter", "container": {"type": "auto"}},
    ],
)

print(response.output_text)
```

**Key parameters**

- `background=True` keeps long-running jobs alive (≈10 minutes of retention) so polling/webhooks don’t time out.
- You must provide at least one data source: `web_search_preview`, `file_search`, or remote MCP (plus optional connectors/code interpreter).
- Set generous client timeouts (these calls can run for minutes) or rely on background mode.

## Output anatomy

The `response.output` array contains the entire trace: `web_search_call`, `file_search_call`, `code_interpreter_call`, `mcp_tool_call`, and the final `message`. Render inline citations (`annotations`) as clickable links in the UI.

```json
{
  "type": "web_search_call",
  "status": "completed",
  "action": { "type": "search", "query": "positive news story today" }
}
```

```json
{
  "type": "message",
  "content": [
    {
      "type": "output_text",
      "text": "Semaglutide ... [1]",
      "annotations": [{ "url": "...", "title": "WHO", "start_index": 42, "end_index": 46 }]
    }
  ]
}
```

## Prompt preparation

Deep research models start working immediately; they do **not** ask clarifying questions like ChatGPT. Consider adding a preprocessing step with a faster model (e.g. `gpt-4.1`) to gather user preferences or rewrite prompts before sending them to `o3-deep-research`.

Example clarifier:

```python
clarifier = client.responses.create(
    model="gpt-4.1",
    input="Research surfboards for me...",
    instructions="Gather missing details, ask concise follow-ups.",
)
```

## Private data sources

Attach internal context via:

- `file_search` (vector stores; deep research supports up to two stores per call)
- Remote MCP servers that implement the **search + fetch** contract (`require_approval` must be `never`)
- Connectors (Dropbox, Gmail, etc.) configured through MCP

Example MCP tool config:

```python
tools=[
    {
        "type": "mcp",
        "server_label": "mycompany_mcp",
        "server_url": "https://mycompany.com/mcp",
        "require_approval": "never",
    }
]
```

For sensitive pipelines, run research in stages (public web first, private MCP second) to minimize exposure.

## Safety + monitoring

- Log every research run (`store=true`) or maintain your own audit trail of tool calls.
- Restrict MCP servers to trusted hosts; untrusted servers can inject malicious instructions.
- Validate tool-call arguments (schema/regex) before forwarding to external systems.
- Consider an LLM-based monitor that blocks suspicious calls (e.g., leaking CRM data in a query string).
- Follow [background mode](./BACKGROUND.md) guidance and configure [webhooks](./WEBHOOKS.md) for completion notifications.

## When to use code interpreter

Attach `code_interpreter` whenever you expect the model to:

- Perform statistical analysis or regression
- Generate charts/tables from combined datasets
- Run quick simulations

The container runs in isolated “auto” mode; no custom image is required.

## Supported tools recap

| Tool | Use case |
| --- | --- |
| `web_search_preview` | Public internet browsing/search |
| `file_search` | Internal vector stores (max 2 IDs) |
| `mcp` | Remote data sources implementing search + fetch |
| `code_interpreter` | Analysis/visualization |

Function calling is not supported inside deep research flows.

## Additional resources

- [Model reference](https://platform.openai.com/docs/models/o3-deep-research)
- [Web search tool](https://platform.openai.com/docs/guides/tools-web-search)
- [Remote MCP guide](https://platform.openai.com/docs/guides/tools-remote-mcp)
- [OpenAI deep research examples](https://cookbook.openai.com/examples/deep_research_api)
