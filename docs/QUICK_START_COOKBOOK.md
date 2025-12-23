# Quick Start: OpenAI Cookbook Integrations

This is a quick reference guide for using the OpenAI Cookbook integrations.

## Installation

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install llama-index llama-index-embeddings-openai llama-index-llms-openai
pip install guidance
pip install prompttools
```

## Verify Installation

```bash
python scripts/verify_cookbook_integrations.py
```

This will check if all integrations are installed and working.

## Quick Examples

### 1. LlamaIndex - Enhanced RAG

```python
from assistant_core.llamaindex_integration import create_rag_engine

# Create engine
rag = create_rag_engine()

# Add documents
rag.add_documents([
    "Document 1 text...",
    "Document 2 text...",
])

# Query
result = rag.query("What is the main topic?")
print(result['response'])
```

### 2. Guidance - Structured Prompts

```python
from assistant_core.guidance_integration import create_guidance_engine

# Create engine
guidance = create_guidance_engine()

# Use template
template = """{{#system}}You are helpful.{{/system}}
{{#user}}Explain {{topic}}.{{/user}}
{{#assistant}}{{gen 'response'}}{{/assistant}}"""

result = guidance.generate_with_template(template, {"topic": "AI"})
print(result['output'])
```

### 3. Prompttools - Test Prompts

```python
from assistant_core.prompttools_integration import create_prompt_evaluator

# Create evaluator
evaluator = create_prompt_evaluator()

# Compare prompts
results = evaluator.compare_prompt_variations(
    base_prompt="Explain:",
    variations=["Please explain:", "Can you explain:"],
    test_cases=[{"input": "AI", "expected_output": "..."}],
)
```

## Using in AI Services API

```python
from assistant_core.ai_services_api import ai_services_api

# Check availability
status = ai_services_api.get_cookbook_integrations_status()
print(status)  # {'llamaindex': True, 'guidance': True, 'prompttools': True}

# Get engines
rag = ai_services_api.get_rag_engine()
guidance = ai_services_api.get_guidance_engine()
evaluator = ai_services_api.get_prompt_evaluator()
```

## Full Examples

See `examples/openai_cookbook_integrations.py` for complete working examples.

## Documentation

- Full docs: `docs/OPENAI_COOKBOOK_INTEGRATIONS.md`
- Summary: `docs/INTEGRATION_SUMMARY.md`


