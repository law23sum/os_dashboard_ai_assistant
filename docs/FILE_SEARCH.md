# File Search Integration

Allow GPT‑4.1, GPT‑5 family, and reasoning models to search your uploaded files for relevant data before composing answers. File search is built into the Responses API (and select Chat Completions models) via the hosted `file_search` tool, giving your agents instant retrieval over curated vector stores without running your own embed + search stack.

---

## Overview

File search lets a response pull snippets from a knowledge base you maintain. Upload documents to OpenAI Files, ingest them into one or more vector stores, and pass those store IDs in `tools`. When the model decides to call the tool, it issues semantic/keyword queries, receives the best matches, and cites the originating files in its reply.

---

## Prerequisites

1. Upload files to the File API with `purpose="assistants"`.
2. Create a vector store (e.g., `knowledge_base`).
3. Attach uploaded files to the store.
4. Poll ingestion status until `completed`.

```python
import requests
from io import BytesIO
from openai import OpenAI

client = OpenAI()

def create_file(client, file_path):
    if file_path.startswith("http://") or file_path.startswith("https://"):
        response = requests.get(file_path)
        file_content = BytesIO(response.content)
        file_name = file_path.split("/")[-1]
        file_tuple = (file_name, file_content)
        result = client.files.create(file=file_tuple, purpose="assistants")
    else:
        with open(file_path, "rb") as file_content:
            result = client.files.create(file=file_content, purpose="assistants")
    print(result.id)
    return result.id

file_id = create_file(client, "https://cdn.openai.com/API/docs/deep_research_blog.pdf")
```

```javascript
import fs from "fs";
import OpenAI from "openai";
const openai = new OpenAI();

async function createFile(filePath) {
  let result;
  if (filePath.startsWith("http://") || filePath.startsWith("https://")) {
    const res = await fetch(filePath);
    const buffer = await res.arrayBuffer();
    const urlParts = filePath.split("/");
    const fileName = urlParts[urlParts.length - 1];
    const file = new File([buffer], fileName);
    result = await openai.files.create({
      file,
      purpose: "assistants",
    });
  } else {
    const fileContent = fs.createReadStream(filePath);
    result = await openai.files.create({
      file: fileContent,
      purpose: "assistants",
    });
  }
  return result.id;
}

const fileId = await createFile("https://cdn.openai.com/API/docs/deep_research_blog.pdf");
console.log(fileId);
```

```python
vector_store = client.vector_stores.create(name="knowledge_base")
print(vector_store.id)

result = client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=file_id,
)
print(result)

result = client.vector_stores.files.list(vector_store_id=vector_store.id)
print(result)
```

```javascript
const vectorStore = await openai.vectorStores.create({ name: "knowledge_base" });
console.log(vectorStore.id);

await openai.vectorStores.files.create(vectorStore.id, { file_id: fileId });

const status = await openai.vectorStores.files.list({
  vector_store_id: vectorStore.id,
});
console.log(status);
```

---

## Enabling file search in Responses API

Once a knowledge base is ready, expose it as a tool by supplying `type: "file_search"` plus the vector store IDs.

```python
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input="What is deep research by OpenAI?",
    tools=[{
        "type": "file_search",
        "vector_store_ids": ["<vector_store_id>"]
    }]
)
print(response)
```

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
  model: "gpt-5.2",
  input: "What is deep research by OpenAI?",
  tools: [
    {
      type: "file_search",
      vector_store_ids: ["<vector_store_id>"],
    },
  ],
});
console.log(response);
```

```csharp
using OpenAI.Responses;

string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!;
OpenAIResponseClient client = new(model: "gpt-5", apiKey: key);

ResponseCreationOptions options = new();
options.Tools.Add(ResponseTool.CreateFileSearchTool(["<vector_store_id>"]));

OpenAIResponse response = (OpenAIResponse)client.CreateResponse([
    ResponseItem.CreateUserMessageItem([
        ResponseContentPart.CreateInputTextPart("What is deep research by OpenAI?"),
    ]),
], options);

Console.WriteLine(response.GetOutputText());
```

When invoked, the API returns both a `file_search_call` entry (with tool call ID, issued queries, and optional results) and a `message` entry that includes citations referencing the files and indexes used.

```json
{
  "output": [
    {
      "type": "file_search_call",
      "id": "fs_67c09ccea8c48191ade9367e3ba71515",
      "status": "completed",
      "queries": ["What is deep research?"],
      "search_results": null
    },
    {
      "id": "msg_67c09cd3091c819185af2be5d13d87de",
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Deep research is a sophisticated capability ...",
          "annotations": [
            {
              "type": "file_citation",
              "index": 992,
              "file_id": "file-2dtbBZdjtDKS8eqWxqbgDi",
              "filename": "deep_research_blog.pdf"
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Retrieval customization

* **Limit results** – Set `max_num_results` to reduce tokens/latency.
* **Include raw results** – Add `include=["file_search_call.results"]` to return retrieved chunks alongside citations.
* **Metadata filters** – Supply filter expressions (e.g., `type: "in"`) that match attributes you set on vector store files.

```python
response = client.responses.create(
    model="gpt-5.2",
    input="What is deep research by OpenAI?",
    tools=[{
        "type": "file_search",
        "vector_store_ids": ["<vector_store_id>"],
        "max_num_results": 2,
        "filters": {
            "type": "in",
            "key": "category",
            "value": ["blog", "announcement"]
        }
    }],
    include=["file_search_call.results"]
)
print(response)
```

```javascript
const response = await openai.responses.create({
  model: "gpt-5.2",
  input: "What is deep research by OpenAI?",
  tools: [
    {
      type: "file_search",
      vector_store_ids: ["<vector_store_id>"],
      max_num_results: 2,
      filters: {
        type: "in",
        key: "category",
        value: ["blog", "announcement"],
      },
    },
  ],
  include: ["file_search_call.results"],
});
console.log(response);
```

---

## Supported MIME types

`text/` formats must be encoded in UTF‑8, UTF‑16, or ASCII.

| File | MIME type |
| --- | --- |
| .c | text/x-c |
| .cpp | text/x-c++ |
| .cs | text/x-csharp |
| .css | text/css |
| .doc | application/msword |
| .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document |
| .go | text/x-golang |
| .html | text/html |
| .java | text/x-java |
| .js | text/javascript |
| .json | application/json |
| .md | text/markdown |
| .pdf | application/pdf |
| .php | text/x-php |
| .pptx | application/vnd.openxmlformats-officedocument.presentationml.presentation |
| .py | text/x-python |
| .rb | text/x-ruby |
| .sh | application/x-sh |
| .tex | text/x-tex |
| .ts | application/typescript |
| .txt | text/plain |

---

## Usage notes

* File search shares Responses API rate limits for the calling model.
* Store ingestion happens asynchronously; poll status before relying on new uploads.
* Always surface file citations anywhere retrieved content is shown.
* Retrieval costs include storage, ingestion, and per-call usage—check pricing for current rates.
