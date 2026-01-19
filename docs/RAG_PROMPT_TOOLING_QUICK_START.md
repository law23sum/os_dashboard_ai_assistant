# Quick Start: RAG + Prompt Tooling Integrations

This is a quick reference guide for using the RAG + prompt tooling integrations.

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
python scripts/verify_rag_prompt_tooling.py
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
status = ai_services_api.get_tooling_integrations_status()
print(status)  # {'llamaindex': True, 'guidance': True, 'prompttools': True}

# Get engines
rag = ai_services_api.get_rag_engine()
guidance = ai_services_api.get_guidance_engine()
evaluator = ai_services_api.get_prompt_evaluator()
```

## Full Examples

See `examples/use_rag_prompt_tooling.py` for complete working examples.

## Documentation

- Full docs: `docs/RAG_PROMPT_TOOLING.md`
- Summary: `docs/INTEGRATION_SUMMARY.md`

