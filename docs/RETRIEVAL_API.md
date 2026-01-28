Retrieval
=========

Search your data using semantic similarity.

The **Retrieval API** allows you to perform [**semantic search**](/docs/guides/retrieval#semantic-search) over your data, which is a technique that surfaces semantically similar results — even when they match few or no keywords. Retrieval is useful on its own, but is especially powerful when combined with our models to synthesize responses.

![Retrieval depiction](https://cdn.openai.com/API/docs/images/retrieval-depiction.png)

The Retrieval API is powered by [**vector stores**](/docs/guides/retrieval#vector-stores), which serve as indices for your data. This guide will cover how to perform semantic search, and go into the details of vector stores.

Quickstart
----------

* **Create vector store** and upload files.

Create vector store with files

```python
from openai import OpenAI
client = OpenAI()

vector_store = client.vector_stores.create(        # Create vector store
    name="Support FAQ",
)

client.vector_stores.files.upload_and_poll(        # Upload file
    vector_store_id=vector_store.id,
    file=open("customer_policies.txt", "rb")
)
```

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const vector_store = await client.vectorStores.create({   // Create vector store
    name: "Support FAQ",
});

await client.vector_stores.files.upload_and_poll({         // Upload file
    vector_store_id: vector_store.id,
    file: fs.createReadStream("customer_policies.txt"),
});
```

* **Send search query** to get relevant results.

Search query

```python
user_query = "What is the return policy?"

results = client.vector_stores.search(
    vector_store_id=vector_store.id,
    query=user_query,
)
```

```javascript
const userQuery = "What is the return policy?";

const results = await client.vectorStores.search({
    vector_store_id: vector_store.id,
    query: userQuery,
});
```

To learn how to use the results with our models, check out the [synthesizing responses](/docs/guides/retrieval#synthesizing-responses) section.

Semantic search
---------------

**Semantic search** is a technique that leverages [vector embeddings](/docs/guides/embeddings) to surface semantically relevant results. Importantly, this includes results with few or no shared keywords, which classical search techniques might miss.

For example, let's look at potential results for `"When did we go to the moon?"`:

|Text|Keyword Similarity|Semantic Similarity|
|---|---|---|
|The first lunar landing occurred in July of 1969.|0%|65%|
|The first man on the moon was Neil Armstrong.|27%|43%|
|When I ate the moon cake, it was delicious.|40%|28%|

_([Jaccard](https://en.wikipedia.org/wiki/Jaccard_index) used for keyword, [cosine](https://en.wikipedia.org/wiki/Cosine_similarity) with `text-embedding-3-small` used for semantic.)_

Notice how the most relevant result contains none of the words in the search query. This flexibility makes semantic search a very powerful technique for querying knowledge bases of any size.

Semantic search is powered by [vector stores](/docs/guides/retrieval#vector-stores), which we cover in detail later in the guide. This section will focus on the mechanics of semantic search.

### Performing semantic search

You can query a vector store using the `search` function and specifying a `query` in natural language. This will return a list of results, each with the relevant chunks, similarity scores, and file of origin.

Search query

```python
results = client.vector_stores.search(
    vector_store_id=vector_store.id,
    query="How many woodchucks are allowed per passenger?",
)
```

```javascript
const results = await client.vectorStores.search({
    vector_store_id: vector_store.id,
    query: "How many woodchucks are allowed per passenger?",
});
```

Results

```json
{
  "object": "vector_store.search_results.page",
  "search_query": "How many woodchucks are allowed per passenger?",
  "data": [
    {
      "file_id": "file-12345",
      "filename": "woodchuck_policy.txt",
      "score": 0.85,
      "attributes": {
        "region": "North America",
        "author": "Wildlife Department"
      },
      "content": [
        {
          "type": "text",
          "text": "According to the latest regulations, each passenger is allowed to carry up to two woodchucks."
        },
        {
          "type": "text",
          "text": "Ensure that the woodchucks are properly contained during transport."
        }
      ]
    },
    {
      "file_id": "file-67890",
      "filename": "transport_guidelines.txt",
      "score": 0.75,
      "attributes": {
        "region": "North America",
        "author": "Transport Authority"
      },
      "content": [
        {
          "type": "text",
          "text": "Passengers must adhere to the guidelines set forth by the Transport Authority regarding the transport of woodchucks."
        }
      ]
    }
  ],
  "has_more": false,
  "next_page": null
}
```

A response will contain 10 results maximum by default, but you can set up to 50 using the `max_num_results` param.

### Query rewriting

Certain query styles yield better results, so we've provided a setting to automatically rewrite your queries for optimal performance. Enable this feature by setting `rewrite_query=true` when performing a `search`.

The rewritten query will be available in the result's `search_query` field.

|Original|Rewritten|
|---|---|
|I'd like to know the height of the main office building.|primary office building height|
|What are the safety regulations for transporting hazardous materials?|safety regulations for hazardous materials|
|How do I file a complaint about a service issue?|service complaint filing process|

### Attribute filtering

Attribute filtering helps narrow down results by applying criteria, such as restricting searches to a specific date range. You can define and combine criteria in `attribute_filter` to target files based on their attributes before performing semantic search.

Use **comparison filters** to compare a specific `key` in a file's `attributes` with a given `value`, and **compound filters** to combine multiple filters using `and` and `or`.

Comparison filter

```json
{
  "type": "eq" | "ne" | "gt" | "gte" | "lt" | "lte" | "in" | "nin",
  "key": "attributes_key",
  "value": "target_value"
}
```

Compound filter

```json
{
  "type": "and" | "or",
  "filters": [...]
}
```

Examples:

Region filter

```json
{
  "type": "eq",
  "key": "region",
  "value": "us"
}
```

Date range filter

```json
{
  "type": "and",
  "filters": [
    {
      "type": "gte",
      "key": "date",
      "value": 1704067200
    },
    {
      "type": "lte",
      "key": "date",
      "value": 1710892800
    }
  ]
}
```

Filename include/exclude

```json
{
  "type": "in",
  "property": "filename",
  "value": ["example.txt", "example2.txt"]
}
```

```json
{
  "type": "nin",
  "property": "filename",
  "value": ["draft.txt", "internal_notes.md"]
}
```

Complex filter

```json
{
  "type": "or",
  "filters": [
    {
      "type": "and",
      "filters": [
        {
          "type": "or",
          "filters": [
            { "type": "eq", "key": "project_code", "value": "X123" },
            { "type": "eq", "key": "project_code", "value": "X999" }
          ]
        },
        { "type": "eq", "key": "confidentiality", "value": "top_secret" }
      ]
    },
    { "type": "eq", "key": "language", "value": "en" }
  ]
}
```

### Ranking

If you find that your file search results are not sufficiently relevant, you can adjust the `ranking_options` to improve the quality of responses. This includes specifying a `ranker`, such as `auto` or `default-2024-08-21`, and setting a `score_threshold` between 0.0 and 1.0. A higher `score_threshold` will limit the results to more relevant chunks, though it may exclude some potentially useful ones. When `ranking_options.hybrid_search` is provided you can also tune `hybrid_search.embedding_weight` (`rrf_embedding_weight`) and `hybrid_search.text_weight` (`rrf_text_weight`) to control how reciprocal rank fusion balances semantic embedding matches vs. sparse keyword matches.

Vector stores
-------------

Vector stores are the containers that power semantic search for the Retrieval API and the [file search](/docs/guides/tools-file-search) tool. When you add a file to a vector store it will be automatically chunked, embedded, and indexed.

Vector stores contain `vector_store_file` objects, which are backed by a `file` object.

|Object type|Description|
|---|---|
|file|Represents content uploaded through the Files API.|
|vector_store|Container for searchable files.|
|vector_store.file|Wrapper type representing a file chunked and embedded with filterable attributes.|

### Pricing

You will be charged based on the total storage used across all your vector stores, determined by the size of parsed chunks and their corresponding embeddings.

|Storage|Cost|
|---|---|
|Up to 1 GB|Free|
|Beyond 1 GB|$0.10/GB/day|

See [expiration policies](/docs/guides/retrieval#expiration-policies) for options to minimize costs.

### Vector store operations

Create vector store

```python
client.vector_stores.create(
    name="Support FAQ",
    file_ids=["file_123"]
)
```

```javascript
await client.vector_stores.create({
    name: "Support FAQ",
    file_ids: ["file_123"]
});
```

Retrieve vector store

```python
client.vector_stores.retrieve(vector_store_id="vs_123")
```

```javascript
await client.vector_stores.retrieve({ vector_store_id: "vs_123" });
```

Update vector store

```python
client.vector_stores.update(vector_store_id="vs_123", name="Support FAQ Updated")
```

```javascript
await client.vector_stores.update({
    vector_store_id: "vs_123",
    name: "Support FAQ Updated"
});
```

Delete vector store

```python
client.vector_stores.delete(vector_store_id="vs_123")
```

```javascript
await client.vector_stores.delete({ vector_store_id: "vs_123" });
```

List vector stores

```python
client.vector_stores.list()
```

```javascript
await client.vector_stores.list();
```

### Vector store file operations

Create vector store file

```python
client.vector_stores.files.create_and_poll(
    vector_store_id="vs_123",
    file_id="file_123"
)
```

```javascript
await client.vector_stores.files.create_and_poll({
    vector_store_id: "vs_123",
    file_id: "file_123"
});
```

Upload vector store file

```python
client.vector_stores.files.upload_and_poll(
    vector_store_id="vs_123",
    file=open("customer_policies.txt", "rb")
)
```

```javascript
await client.vector_stores.files.upload_and_poll({
    vector_store_id: "vs_123",
    file: fs.createReadStream("customer_policies.txt"),
});
```

Retrieve vector store file

```python
client.vector_stores.files.retrieve(
    vector_store_id="vs_123",
    file_id="file_123"
)
```

```javascript
await client.vector_stores.files.retrieve({
    vector_store_id: "vs_123",
    file_id: "file_123"
});
```

Update vector store file

```python
client.vector_stores.files.update(
    vector_store_id="vs_123",
    file_id="file_123",
    attributes={"key": "value"}
)
```

```javascript
await client.vector_stores.files.update({
    vector_store_id: "vs_123",
    file_id: "file_123",
    attributes: { key: "value" }
});
```

Delete vector store file

```python
client.vector_stores.files.delete(
    vector_store_id="vs_123",
    file_id="file_123"
)
```

```javascript
await client.vector_stores.files.delete({
    vector_store_id: "vs_123",
    file_id: "file_123"
});
```

List vector store files

```python
client.vector_stores.files.list(vector_store_id="vs_123")
```

```javascript
await client.vector_stores.files.list({ vector_store_id: "vs_123" });
```javascript
await client.vector_stores.files.list({ vector_store_id: "vs_123" });
```

### Batch operations

Batch create

```python
client.vector_stores.file_batches.create_and_poll(
    vector_store_id="vs_123",
    files=[
        {
            "file_id": "file_123",
            "attributes": {"department": "finance"}
        },
        {
            "file_id": "file_456",
            "chunking_strategy": {
                "type": "static",
                "max_chunk_size_tokens": 1200,
                "chunk_overlap_tokens": 200
            }
        }
    ]
)
```

```javascript
await client.vector_stores.file_batches.create_and_poll({
    vector_store_id: "vs_123",
    files: [
        {
            file_id: "file_123",
            attributes: { department: "finance" }
        },
        {
            file_id: "file_456",
            chunking_strategy: {
                type: "static",
                max_chunk_size_tokens: 1200,
                chunk_overlap_tokens: 200
            }
        }
    ]
});
```

Batch retrieve

```python
client.vector_stores.file_batches.retrieve(
    vector_store_id="vs_123",
    batch_id="vsfb_123"
)
```

```javascript
await client.vector_stores.file_batches.retrieve({
    vector_store_id: "vs_123",
    batch_id: "vsfb_123"
});
```

Batch cancel

```python
client.vector_stores.file_batches.cancel(
    vector_store_id="vs_123",
    batch_id="vsfb_123"
)
```

```javascript
await client.vector_stores.file_batches.cancel({
    vector_store_id: "vs_123",
    batch_id: "vsfb_123"
});
```

Batch list

```python
client.vector_stores.file_batches.list(vector_store_id="vs_123")
```

```javascript
await client.vector_stores.file_batches.list({ vector_store_id: "vs_123" });
```

When creating a batch you can either provide `file_ids` with optional `attributes` and/or `chunking_strategy`, or use the `files` array to pass objects that include a `file_id` plus optional per-file overrides.

### Attributes

Each `vector_store.file` can have associated `attributes`, a dictionary of values that can be referenced when performing semantic search with attribute filtering (max 16 keys, 256 chars each).

```python
client.vector_stores.files.create(
    vector_store_id="<vector_store_id>",
    file_id="file_123",
    attributes={
        "region": "US",
        "category": "Marketing",
        "date": 1672531200
    }
)
```

### Expiration policies

Set `expires_after` on a vector store to clean up storage automatically.

```python
client.vector_stores.update(
    vector_store_id="vs_123",
    expires_after={
        "anchor": "last_active_at",
        "days": 7
    }
)
```

### Limits & chunking

* Max file size: 512 MB
* Max tokens per file: 5,000,000
* Default chunking: 800-token chunks with 400-token overlap
* `max_chunk_size_tokens` must be between 100 and 4096 and `chunk_overlap_tokens` should not exceed half the chunk size.

Supported file types include `.txt`, `.md`, `.json`, `.pdf`, `.py`, `.ts`, `.docx`, `.pptx`, `.html`, `.css`, `.js`, `.c`, `.cpp`, `.java`, `.rb`, `.sh`, `.tex`, and more (UTF-8/UTF-16/ascii for `text/*`).

Synthesizing responses
----------------------

After performing a query you may want to synthesize a response based on the results.

```python
from openai import OpenAI

client = OpenAI()

user_query = "What is the return policy?"

results = client.vector_stores.search(
    vector_store_id=vector_store.id,
    query=user_query,
)

completion = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "developer",
            "content": "Produce a concise answer to the query based on the provided sources."
        },
        {
            "role": "user",
            "content": f"Sources: {format_results(results)}\n\nQuery: '{user_query}'"
        }
    ],
)
```

```javascript
const userQuery = "What is the return policy?";
const results = await client.vectorStores.search({
    vector_store_id: vector_store.id,
    query: userQuery,
});

const completion = await client.chat.completions.create({
    model: "gpt-4.1",
    messages: [
        {
            role: "developer",
            content: "Produce a concise answer to the query based on the provided sources."
        },
        {
            role: "user",
            content: `Sources: ${formatResults(results)}\n\nQuery: '${userQuery}'`
        }
    ],
});
```

Sample formatter

```python
def format_results(results):
    formatted_results = ''
    for result in results.data:
        formatted_result = f"<result file_id='{result.file_id}' file_name='{result.file_name}'>"
        for part in result.content:
            formatted_result += f"<content>{part.text}</content>"
        formatted_results += formatted_result + "</result>"
    return f"<sources>{formatted_results}</sources>"
```

```javascript
function formatResults(results) {
    let formattedResults = '';
    for (const result of results.data) {
        let formattedResult = `<result file_id='${result.file_id}' file_name='${result.file_name}'>`;
        for (const part of result.content) {
            formattedResult += `<content>${part.text}</content>`;
        }
        formattedResults += formattedResult + "</result>";
    }
    return `<sources>${formattedResults}</sources>`;
}
```

Was this page useful? Let us know what Retrieval API features you still need so we can continue to include them in future releases.
