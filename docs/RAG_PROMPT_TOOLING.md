# RAG + Prompt Tooling Integrations

This document describes the integrations based on [OpenAI related resources](https://cookbook.openai.com/articles/related_resources) that enhance the AI OS.

## Overview

We've integrated three tools from OpenAI's reference resources:

1. **LlamaIndex** - Enhanced RAG (Retrieval-Augmented Generation) and data augmentation
2. **Guidance** - Advanced prompt templating and control flow (Microsoft)
3. **Prompttools** - Testing and evaluating prompts, models, and vector databases

All tools are **MIT licensed** and safe for commercial use.

## License Verification

✅ **All tools verified as MIT licensed:**
- **LlamaIndex**: MIT License - [GitHub](https://github.com/run-llama/llama_index)
- **Guidance**: MIT License - [GitHub](https://github.com/microsoft/guidance)
- **Prompttools**: MIT License - [GitHub](https://github.com/hegelai/prompttools)
- **OpenAI reference guides**: MIT License - [GitHub](https://github.com/openai/openai-cookbook)

## Installation

Install the required dependencies:

```bash
pip install llama-index llama-index-embeddings-openai llama-index-llms-openai
pip install guidance
pip install prompttools
```

Or install all at once from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 1. LlamaIndex Integration

### Purpose

LlamaIndex enhances the existing semantic search capabilities with:
- Advanced document indexing and retrieval
- Better context management for RAG
- Multi-document query capabilities
- Improved chunking and embedding strategies

### Usage

```python
from assistant_core.llamaindex_integration import create_rag_engine

# Create RAG engine
rag_engine = create_rag_engine(
    storage_path="./data/llamaindex",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Add documents
documents = [
    "Document 1 text...",
    "Document 2 text...",
]

rag_engine.add_documents(documents)

# Query with context
result = rag_engine.query("What is the main topic?", similarity_top_k=5)
print(result['response'])

# Get context chunks for prompt augmentation
context = rag_engine.get_context_for_query("How does X work?", max_chunks=3)
```

### Integration Points

- **Existing semantic search**: Can be used alongside `assistant_core/search_engine.py`
- **Vector indexing**: Complements `ai_os/app/search/index.py`
- **RAG workflows**: Enhances document retrieval for AI responses

### Files

- `assistant_core/llamaindex_integration.py` - Main integration module
- `examples/use_rag_prompt_tooling.py` - Usage examples

## 2. Guidance Integration

### Purpose

Guidance provides:
- Handlebars-style templating for prompts
- Interleaved generation, prompting, and logical control
- Constrained generation
- Better prompt structure management

### Usage

```python
from assistant_core.guidance_integration import create_guidance_engine

# Create Guidance engine
guidance_engine = create_guidance_engine(
    model="gpt-4o-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Use template with variables
template = """{{#system}}You are a helpful assistant.{{/system}}
{{#user}}Explain {{topic}}.{{/user}}
{{#assistant}}{{gen 'response'}}{{/assistant}}"""

result = guidance_engine.generate_with_template(
    template,
    {"topic": "machine learning"},
)

# Create structured conversation
response = guidance_engine.create_conversation_template(
    system_prompt="You are a coding assistant.",
    conversation_history=[
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
    ],
    current_message="Tell me more.",
)
```

### Integration Points

- **Prompt management**: Can replace manual prompt construction in `assistant_hub/ai.py`
- **Conversation templates**: Enhances `assistant_core/conversation_manager.py`
- **Structured outputs**: Better control over AI responses

### Files

- `assistant_core/guidance_integration.py` - Main integration module
- `examples/use_rag_prompt_tooling.py` - Usage examples

## 3. Prompttools Integration

### Purpose

Prompttools enables:
- Testing and comparing multiple prompts
- Evaluating prompt variations
- Testing prompt robustness
- Comparing model performance

### Usage

```python
from assistant_core.prompttools_integration import create_prompt_evaluator

# Create evaluator
evaluator = create_prompt_evaluator(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Compare prompt variations
results = evaluator.compare_prompt_variations(
    base_prompt="Explain:",
    variations=[
        "Please explain in simple terms:",
        "Can you provide a detailed explanation of:",
    ],
    test_cases=[
        {"input": "machine learning", "expected_output": "..."},
    ],
    model="gpt-4o-mini",
)

# Test prompt robustness
robustness = evaluator.test_prompt_robustness(
    prompt="Explain the following:",
    test_inputs=["AI", "Python", "APIs"],
    num_runs=3,
)
```

### Integration Points

- **Prompt testing**: Test prompts before deploying to production
- **A/B testing**: Compare different prompt strategies
- **Quality assurance**: Ensure prompt consistency

### Files

- `assistant_core/prompttools_integration.py` - Main integration module
- `examples/use_rag_prompt_tooling.py` - Usage examples

## Graceful Degradation

All integrations support graceful degradation. If a library is not installed:

- Functions return `None` instead of raising errors
- Warnings are logged but the application continues
- Existing functionality remains unaffected

Example:

```python
rag_engine = create_rag_engine()
if rag_engine:
    # Use LlamaIndex
    result = rag_engine.query("...")
else:
    # Fall back to existing search
    result = existing_search_engine.search("...")
```

## Examples

See `examples/use_rag_prompt_tooling.py` for complete working examples of all three integrations.

Run examples:

```bash
export OPENAI_API_KEY=sk-...
python examples/use_rag_prompt_tooling.py
```

## Best Practices

1. **Start with LlamaIndex** for RAG if you need better document retrieval
2. **Use Guidance** for complex prompt templates and structured outputs
3. **Test prompts** with Prompttools before deploying to production
4. **Combine tools** - Use LlamaIndex for context, Guidance for prompts, Prompttools for testing

## References

- [OpenAI Related Resources](https://cookbook.openai.com/articles/related_resources)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Guidance Documentation](https://github.com/microsoft/guidance)
- [Prompttools Documentation](https://github.com/hegelai/prompttools)

## License Compliance

All integrated tools are MIT licensed, which means:
- ✅ Free to use in commercial projects
- ✅ Can modify and distribute
- ✅ Must include original license and copyright notice
- ✅ No warranty or liability

The integrations maintain this compliance by:
- Including license information in code comments
- Preserving original library functionality
- Not modifying core library code
- Providing proper attribution

## Support

For issues or questions:
1. Check the example file: `examples/use_rag_prompt_tooling.py`
2. Review library documentation (links above)
3. Check logs for graceful degradation messages
4. Ensure `OPENAI_API_KEY` is set correctly

