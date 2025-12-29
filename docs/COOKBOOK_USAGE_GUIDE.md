# OpenAI Cookbook Integrations - Usage Guide

This guide shows you how to use the OpenAI Cookbook integrations in your application.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Using LlamaIndex RAG](#using-llamaindex-rag)
3. [Using Guidance](#using-guidance)
4. [Using the API Endpoints](#using-the-api-endpoints)
5. [Integration via AI Services API](#integration-via-ai-services-api)
6. [Testing](#testing)

## Quick Start

### 1. Verify Installation

```bash
python scripts/verify_cookbook_integrations.py
```

### 2. Start the Backend (if using API)

```bash
python -m uvicorn backend_api.main:app --reload
```

### 3. Test the API

```bash
python scripts/test_cookbook_api.py
```

## Using LlamaIndex RAG

### Direct Import

```python
from assistant_core.llamaindex_integration import (
    create_rag_engine,
    query_rag_engine,
    add_documents_to_rag
)

# Create engine
engine = create_rag_engine()

# Add documents
documents = [
    {"text": "Your document text", "metadata": {"source": "doc1"}},
    {"text": "Another document", "metadata": {"source": "doc2"}}
]
await add_documents_to_rag(engine, documents)

# Query
result = await query_rag_engine(engine, "Your question")
print(result["response"])
```

### Via API

```python
import requests

# Add documents
response = requests.post(
    "http://localhost:8000/api/cookbook/rag/documents",
    json={
        "documents": ["Document 1", "Document 2"],
        "metadata": {"source": "test"}
    }
)

# Query
response = requests.post(
    "http://localhost:8000/api/cookbook/rag/query",
    json={
        "query": "Your question",
        "similarity_top_k": 5,
        "response_mode": "compact"
    }
)
result = response.json()
print(result["response"])
```

## Using Guidance

### Direct Import

```python
from assistant_core.guidance_integration import (
    create_guidance_engine,
    generate_with_guidance
)

# Create engine
engine = create_guidance_engine()

# Define template (Handlebars syntax)
template = """
{{#system~}}
You are a helpful assistant.
{{~/system}}

{{#user~}}
Write a greeting for {{name}}.
{{~/user}}

{{#assistant~}}
{{gen 'greeting' max_tokens=50}}
{{~/assistant}}
"""

# Generate
variables = {"name": "Alice"}
result = await generate_with_guidance(engine, template, variables)
print(result["generated_text"])
```

### Via API

```python
import requests

response = requests.post(
    "http://localhost:8000/api/cookbook/guidance/template",
    json={
        "template": "Hello {{name}}!",
        "variables": {"name": "World"}
    }
)
result = response.json()
print(result["generated_text"])
```

## Using the API Endpoints

All endpoints are available at `/api/cookbook/`:

### Status Endpoint

```bash
curl http://localhost:8000/api/cookbook/status
```

Returns:
```json
{
  "llamaindex": true,
  "guidance": true,
  "prompttools": false,
  "openai_api_key_set": true
}
```

### RAG Endpoints

- `POST /api/cookbook/rag/documents` - Add documents
- `POST /api/cookbook/rag/query` - Query RAG engine
- `GET /api/cookbook/rag/context` - Get context chunks

### Guidance Endpoint

- `POST /api/cookbook/guidance/template` - Generate with template

## Integration via AI Services API

You can also use the unified AI Services API:

```python
from assistant_core.ai_services_api import (
    ai_services_api,
    AIServiceType,
    AIServiceRequest
)

# Initialize (usually done at startup)
await ai_services_api.initialize()

# Make a request
request = AIServiceRequest(
    service_type=AIServiceType.LLAMA_INDEX_RAG,
    input_data={
        "query": "Your question",
        "similarity_top_k": 5
    },
    user_id="user123"
)

response = await ai_services_api.process_request(request)
print(response.result)
```

## Testing

### Test Scripts

1. **Verification Script**: Check if integrations are installed
   ```bash
   python scripts/verify_cookbook_integrations.py
   ```

2. **API Test Script**: Test all API endpoints
   ```bash
   python scripts/test_cookbook_api.py
   ```

3. **Usage Examples**: See example code
   ```bash
   python examples/use_cookbook_integrations.py
   ```

### Manual Testing

1. Start the backend:
   ```bash
   python -m uvicorn backend_api.main:app --reload
   ```

2. Check status:
   ```bash
   curl http://localhost:8000/api/cookbook/status
   ```

3. Test RAG query:
   ```bash
   curl -X POST http://localhost:8000/api/cookbook/rag/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is Python?", "similarity_top_k": 3}'
   ```

## Troubleshooting

### Integration Not Available

If an integration shows as not available:

1. Check installation:
   ```bash
   pip install llama-index guidance prompttools
   ```

2. Check OpenAI API key:
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

3. Verify with script:
   ```bash
   python scripts/verify_cookbook_integrations.py
   ```

### Prompttools Compatibility

Prompttools currently has compatibility issues with OpenAI 2.x. The integration will gracefully degrade. To use Prompttools:

1. Downgrade OpenAI to 1.x (not recommended for production)
2. Wait for Prompttools update
3. Use alternative prompt evaluation tools

### API Connection Errors

If you get connection errors:

1. Ensure backend is running:
   ```bash
   python -m uvicorn backend_api.main:app --reload
   ```

2. Check the port (default: 8000)

3. Verify CORS settings if calling from browser

## Next Steps

- Read the [Full Documentation](OPENAI_COOKBOOK_INTEGRATIONS.md)
- Check [Quick Start Guide](QUICK_START_COOKBOOK.md)
- See [Integration Summary](INTEGRATION_SUMMARY.md)
- Review [Example Code](../examples/openai_cookbook_integrations.py)

## Support

For issues or questions:
- Check the documentation in `docs/`
- Review example code in `examples/`
- Run verification scripts to diagnose issues

