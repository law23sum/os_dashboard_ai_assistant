# Web Search Integration

Enable GPT‑5 family models to search the live web before returning an answer. With web search configured, the Responses API (and certain Chat Completions models) can pull in up‑to‑date facts, cite every source, and tailor coverage to specific domains or geographies.

---

## Search modes

1. **Non‑reasoning search** – A fast lookup where the model simply forwards the user query to web search and relays the summarized result. Ideal for low‑latency questions.
2. **Agentic search (reasoning models)** – GPT‑5 can plan a sequence of searches, open multiple pages, and decide whether to keep digging. Reasoning effort controls depth vs. latency.
3. **Deep research** – Long‑running investigations (minutes of work, hundreds of sources) via `o3-deep-research`, `o4-mini-deep-research`, or `gpt-5` with `reasoning.level = high`. Best triggered in background mode.

---

## Enabling web search via Responses API

Add the `web_search` tool to the `tools` array. The model decides when to call it unless you force usage with `tool_choice`.

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.create({
  model: "gpt-5",
  tools: [{ type: "web_search" }],
  input: "What was a positive news story from today?",
});

console.log(response.output_text);
```

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    tools=[{"type": "web_search"}],
    input="What was a positive news story from today?"
)

print(response.output_text)
```

```bash
curl "https://api.openai.com/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
        "model": "gpt-5",
        "tools": [{"type": "web_search"}],
        "input": "what was a positive news story from today?"
      }'
```

```csharp
using OpenAI.Responses;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
options.Tools.Add(ResponseTool.CreateWebSearchTool());

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart(
            "What was a positive news story from today?"
        ),
    ]),
], options);

Console.WriteLine(response.GetOutputText());
```

---

## Output format & citations

Every search-enabled response produces:

1. A `web_search_call` output item with the tool call ID and `action`:
   * `search` – issued queries (may include `query` and `domains`).
   * `open_page` / `find_in_page` – reasoning models browsing follow-ups.
2. A `message` output item with the model text plus `annotations`. Each `url_citation` contains the URL, title, and index range cited.

Inline citations must remain visible and clickable in your UI when showing any retrieved material.

---

## Domain filtering & source lists

Target specific domains with `filters.allowed_domains` (up to 100 entries). Supply bare domains (no `https://` prefix) and subdomains are included automatically.

```bash
curl "https://api.openai.com/v1/responses" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "reasoning": { "effort": "low" },
    "tools": [
      {
        "type": "web_search",
        "filters": {
          "allowed_domains": [
            "pubmed.ncbi.nlm.nih.gov",
            "clinicaltrials.gov",
            "www.who.int",
            "www.cdc.gov",
            "www.fda.gov"
          ]
        }
      }
    ],
    "tool_choice": "auto",
    "include": ["web_search_call.action.sources"],
    "input": "Please perform a web search on how semaglutide is used in the treatment of diabetes."
  }'
```

Use the `include` array with `web_search_call.action.sources` to return every URL the model consulted. Third‑party live feeds appear as `oai-sports`, `oai-weather`, or `oai-finance`.

---

## Location awareness

Improve relevance with approximate user location:

* `country`: ISO‑3166 two-letter code (e.g., `US`).
* `city` / `region`: free text.
* `timezone`: IANA strings (e.g., `America/Chicago`).

```python
response = client.responses.create(
    model="o4-mini",
    tools=[{
        "type": "web_search",
        "user_location": {
            "type": "approximate",
            "country": "GB",
            "city": "London",
            "region": "London",
        }
    }],
    input="What are the best restaurants near me?",
)
```

Deep-research models do **not** support location hints today.

---

## Controlling live internet access

* `external_web_access: true` (default) – fetches live web results.
* `external_web_access: false` – uses cached/indexed data only.

Preview variants (`web_search_preview`) always behave as if live access is enabled.

---

## API compatibility

* **Responses API:** `web_search` (current) and `web_search_preview` (legacy).
* **Chat Completions:** use dedicated models (`gpt-5-search-api`, `gpt-4o-search-preview`, `gpt-4o-mini-search-preview`).

---

## Limitations

* Unsupported in `gpt-5` when reasoning level is `minimal`, and in `gpt-4.1-nano`.
* Shares the underlying model rate limits.
* Context window limited to 128k when the tool is active.

---

## Usage notes

* Searches incur tool-call costs (see pricing).
* Always render citations alongside model text.
* Deep research is best scheduled asynchronously due to multi-minute runtimes.
* When referencing results to end users, make citations clickable and clearly visible.
