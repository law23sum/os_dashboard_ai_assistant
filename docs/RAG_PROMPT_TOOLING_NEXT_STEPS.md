# Next Steps - RAG + Prompt Tooling Integrations

This document outlines the next steps for using and maintaining the RAG + prompt tooling integrations.

## ✅ Completed Setup

1. **Integration Files**: All integration modules are in place
   - `assistant_core/llamaindex_integration.py`
   - `assistant_core/guidance_integration.py`
   - `assistant_core/prompttools_integration.py`

2. **API Router**: Registered at `/api/ai-tooling`
   - Status endpoint
   - RAG endpoints (query, documents, context)
   - Guidance template endpoint

3. **Verification Tools**: Scripts to check installation
   - `scripts/verify_rag_prompt_tooling.py`
   - `scripts/check_prompttools_update.py`

4. **Testing Tools**: Scripts to test functionality
   - `scripts/test_rag_prompt_tooling_api.py`
   - `examples/use_rag_prompt_tooling.py`

## 🚀 Next Steps

### 1. Test the API Endpoints

#### Start the Backend

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the FastAPI server
python -m uvicorn backend_api.main:app --reload
```

The server will start at `http://localhost:8000`

#### Run API Tests

```bash
# Test all endpoints
python scripts/test_rag_prompt_tooling_api.py

# Or test manually with curl
curl http://localhost:8000/api/ai-tooling/status
```

#### Expected Endpoints

- `GET /api/ai-tooling/status` - Check integration status
- `POST /api/ai-tooling/rag/query` - Query RAG engine
- `POST /api/ai-tooling/rag/documents` - Add documents
- `GET /api/ai-tooling/rag/context` - Get context chunks
- `POST /api/ai-tooling/guidance/template` - Generate with Guidance

### 2. Use the Integrations in Your Application

#### Option A: Direct Import

```python
# LlamaIndex RAG
from assistant_core.llamaindex_integration import (
    create_rag_engine,
    query_rag_engine,
    add_documents_to_rag
)

engine = create_rag_engine()
await add_documents_to_rag(engine, documents)
result = await query_rag_engine(engine, "Your query")

# Guidance
from assistant_core.guidance_integration import (
    create_guidance_engine,
    generate_with_guidance
)

engine = create_guidance_engine()
result = await generate_with_guidance(engine, template, variables)
```

#### Option B: Via API

```python
import requests

# Check status
response = requests.get("http://localhost:8000/api/ai-tooling/status")

# Query RAG
response = requests.post(
    "http://localhost:8000/api/ai-tooling/rag/query",
    json={"query": "Your question", "similarity_top_k": 5}
)
```

#### Option C: Via AI Services API

```python
from assistant_core.ai_services_api import (
    ai_services_api,
    AIServiceType,
    AIServiceRequest
)

request = AIServiceRequest(
    service_type=AIServiceType.LLAMA_INDEX_RAG,
    input_data={"query": "Your question"},
    user_id="user123"
)

response = await ai_services_api.process_request(request)
```

### 3. Monitor for Prompttools Updates

#### Check for Updates

```bash
python scripts/check_prompttools_update.py
```

This script will:
- Show installed version
- Check PyPI for latest version
- Test OpenAI compatibility
- Provide update recommendations

#### Update Prompttools

```bash
pip install --upgrade prompttools
```

#### Monitor GitHub

- Repository: https://github.com/hegelai/prompttools
- Check for issues related to OpenAI 2.x compatibility
- Watch for releases that mention OpenAI 2.x support

#### Current Status

- **Installed**: 0.0.16 (or newer if updated)
- **Latest**: 0.0.46
- **Compatibility**: Has issues with OpenAI 2.x
- **Workaround**: Integration gracefully degrades

## 📚 Documentation

- **Full Documentation**: `docs/RAG_PROMPT_TOOLING.md`
- **Quick Start**: `docs/RAG_PROMPT_TOOLING_QUICK_START.md`
- **Usage Guide**: `docs/RAG_PROMPT_TOOLING_USAGE_GUIDE.md`
- **Integration Summary**: `docs/INTEGRATION_SUMMARY.md`

## 🔧 Troubleshooting

### Backend Not Starting

```bash
# Check if port 8000 is in use
lsof -ti:8000

# Use different port
python -m uvicorn backend_api.main:app --reload --port 8001
```

### Integration Not Available

```bash
# Verify installation
python scripts/verify_rag_prompt_tooling.py

# Reinstall if needed
pip install llama-index guidance prompttools
```

### API Connection Errors

1. Ensure backend is running
2. Check CORS settings if calling from browser
3. Verify API base URL matches server

## 🎯 Example Use Cases

### 1. Document Q&A System

Use LlamaIndex RAG to build a Q&A system over your documents:

```python
# Add documents
documents = [
    {"text": "Document content...", "metadata": {"source": "doc1"}}
]
await add_documents_to_rag(engine, documents)

# Query
result = await query_rag_engine(engine, "What is X?")
```

### 2. Structured Prompt Generation

Use Guidance for structured, controlled generation:

```python
template = """
{{#system~}}You are a helpful assistant.{{~/system}}
{{#user~}}{{question}}{{~/user}}
{{#assistant~}}{{gen 'answer'}}{{~/assistant}}
"""
result = await generate_with_guidance(engine, template, {"question": "..."})
```

### 3. Multi-Modal AI Application

Combine integrations with other AI services:

```python
# Use RAG for context
rag_result = await query_rag_engine(engine, query)

# Use Guidance for structured output
guidance_result = await generate_with_guidance(
    engine, template, {"context": rag_result["response"]}
)
```

## 📊 Status Monitoring

Regular checks:

1. **Weekly**: Run `verify_rag_prompt_tooling.py`
2. **Monthly**: Check for Prompttools updates
3. **As needed**: Test API endpoints after backend updates

## 🔄 Maintenance

### Update Dependencies

```bash
# Update all RAG + prompt tooling integrations
pip install --upgrade llama-index guidance prompttools

# Verify after update
python scripts/verify_rag_prompt_tooling.py
```

### Test After Updates

```bash
# Test API endpoints
python scripts/test_rag_prompt_tooling_api.py

# Run examples
python examples/use_rag_prompt_tooling.py
```

## 📝 Notes

- All integrations use graceful degradation (work even if not installed)
- Prompttools has known compatibility issues with OpenAI 2.x
- LlamaIndex and Guidance work well with OpenAI 2.x
- All integrations are MIT licensed (safe for commercial use)

## 🎉 You're Ready!

The integrations are set up and ready to use. Start with:

1. `python scripts/verify_rag_prompt_tooling.py` - Verify setup
2. Start backend and test: `python scripts/test_rag_prompt_tooling_api.py`
3. Try examples: `python examples/use_rag_prompt_tooling.py`
4. Read the usage guide: `docs/RAG_PROMPT_TOOLING_USAGE_GUIDE.md`

Happy coding! 🚀
