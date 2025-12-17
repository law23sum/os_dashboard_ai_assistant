# GPT-5.2 Prompting Guide

## 1. Introduction

GPT-5.2 is the newest flagship model for enterprise and agentic workloads. It delivers higher accuracy, stronger instruction following, and more disciplined execution across complex workflows. Building on GPT-5.1, GPT-5.2 improves token efficiency on medium-to-complex tasks, produces cleaner formatting with less unnecessary verbosity, and shows clear gains in structured reasoning, tool grounding, and multimodal understanding.

GPT-5.2 is especially well-suited for production agents that prioritize reliability, evaluability, and consistent behavior. It performs strongly across coding, document analysis, finance, and multi-tool agentic scenarios, often matching or exceeding leading models on task completion. At the same time, it remains prompt-sensitive and highly steerable in tone, verbosity, and output shape, making explicit prompting an important part of successful deployments.

While GPT-5.2 works well out of the box for many use cases, this guide focuses on prompt patterns and migration practices that maximize performance in production systems. These recommendations are drawn from internal testing and customer feedback, where small changes to prompt structure, verbosity constraints, and reasoning settings often translate into large gains in correctness, latency, and developer trust.

## 2. Key behavioral differences

Compared with GPT-5 and GPT-5.1, GPT-5.2 provides:

- **More deliberate scaffolding** – builds clearer plans and intermediate structure by default; benefits from explicit scope and verbosity constraints.
- **Lower verbosity** – more concise and task-focused, though still prompt-sensitive and responsive to user preferences.
- **Stronger instruction adherence** – improved formatting and rationale presentation with less drift from intent.
- **Tool efficiency trade-offs** – triggers additional tool actions in interactive flows; prompting can optimize this further.
- **Conservative grounding bias** – favors correctness and explicit reasoning; ambiguity handling improves with clarification prompts.

## 3. Prompting patterns

Adapt the following patterns to steer GPT-5.2 effectively.

### 3.1 Controlling verbosity and output shape

Provide concrete length constraints, especially in enterprise and coding agents.

```
<output_verbosity_spec>
- Default: 3-6 sentences or <=5 bullets for typical answers.
- For simple “yes/no + short explanation” questions: <=2 sentences.
- For complex multi-step or multi-file tasks:
  - 1 short overview paragraph
  - then <=5 bullets tagged: What changed, Where, Risks, Next steps, Open questions.
- Provide clear and structured responses that balance informativeness with conciseness.
- Avoid long narrative paragraphs; prefer compact bullets and short sections.
- Do not rephrase the user’s request unless it changes semantics.
</output_verbosity_spec>
```

### 3.2 Preventing scope drift

GPT-5.2 is strong at structured code but may produce more UI than required. Explicitly forbid extra features and uncontrolled styling.

```
<design_and_scope_constraints>
- Explore the existing design system and stay aligned to it.
- Implement EXACTLY and ONLY what the user requests.
- No extra features, no added components, no UX embellishments.
- Style must match the approved tokens.
- If an instruction is ambiguous, choose the simplest valid interpretation.
</design_and_scope_constraints>
```

### 3.3 Long-context and recall

Force summarization and re-grounding for long-context inputs to reduce “lost in the scroll” errors.

```
<long_context_handling>
- For inputs longer than ~10k tokens:
  - Produce a short internal outline of the key sections relevant to the request.
  - Restate the user’s constraints explicitly (jurisdiction, dates, product, etc.).
  - Anchor claims to sections (“In the ‘Data Retention’ section…”) rather than speaking generically.
- Quote or paraphrase fine-grained details when they matter.
</long_context_handling>
```

### 3.4 Handling ambiguity and hallucination risk

Configure prompts to reduce overconfident hallucinations.

```
<uncertainty_and_ambiguity>
- If the question is ambiguous or underspecified, call this out and:
  - Ask up to 1–3 precise clarifying questions, OR
  - Present 2–3 plausible interpretations with clearly labeled assumptions.
- When external facts may have changed recently and no tools are available:
  - Answer in general terms and mention the data may have changed.
- Never fabricate exact figures, line numbers, or references when uncertain.
- Prefer “Based on the provided context…” instead of absolute claims when unsure.
</uncertainty_and_ambiguity>
```

For high-risk contexts add a self-check:

```
<high_risk_self_check>
Before finalizing an answer in legal, financial, compliance, or safety-sensitive contexts:
- Re-scan your answer for unstated assumptions and ungrounded numbers.
- Soften or qualify overly strong language and state assumptions explicitly.
</high_risk_self_check>
```

## 4. Compaction (extending effective context)

For long-running, tool-heavy workflows that push the context window, GPT-5.2 supports response compaction via the `/responses/compact` endpoint. Compaction compresses prior conversation state and returns opaque items that preserve task-relevant information while reducing token footprint, allowing reasoning across extended workflows without hitting limits.

**When to compact**

- Multi-step agent flows with many tool calls.
- Long conversations where earlier turns must be retained.
- Iterative reasoning beyond the standard context window.

**Key properties**

- Produces opaque, encrypted items (internal format may evolve).
- Designed for continuation, not inspection.
- Compatible with GPT-5.2 and the Responses API.
- Safe to run repeatedly in long sessions.

**Endpoint**

```
POST https://api.openai.com/v1/responses/compact
```

Compaction runs a compression pass over the conversation. Pass the compacted output into the next request to continue with lower context usage.

Best practices:

- Monitor context usage and compact before hitting limits.
- Compact after major milestones, not every turn.
- Keep prompts functionally identical when resuming.
- Treat compacted items as opaque; do not parse their internals.

### Example

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": "write a very long poem about a dog.",
        },
    ],
)

output_json = [msg.model_dump() for msg in response.output]

compacted_response = client.responses.compact(
    model="gpt-5.2",
    input=[
        {
            "role": "user",
            "content": "write a very long poem about a dog.",
        },
        output_json[0],
    ],
)

print(json.dumps(compacted_response.model_dump(), indent=2))
```

## 5. Agentic steerability and user updates

GPT-5.2 excels at agentic scaffolding when prompted well. Reuse your GPT-5.1 `<user_updates_spec>` and `<solution_persistence>` blocks and tighten verbosity plus scope discipline.

```
<user_updates_spec>
- Send brief updates (1–2 sentences) only when starting a major phase or when the plan changes.
- Avoid narrating routine tool calls.
- Each update must include at least one concrete outcome (“Found X”, “Updated Y”).
- Do not expand the task beyond what the user asked; label new work as optional.
</user_updates_spec>
```

## 6. Tool-calling and parallelism

GPT-5.2 improves tool reliability and scaffolding. Reinforce best practices:

```
<tool_usage_rules>
- Prefer tools whenever you need fresh or user-specific data.
- Parallelize independent reads to reduce latency.
- After any write/update, restate what changed, where, and how it was validated.
</tool_usage_rules>
```

## 7. Structured extraction, PDF, and Office workflows

GPT-5.2 excels at structured extraction. Provide schemas and distinguish required vs. optional fields.

```
<extraction_spec>
You will extract structured data from tables/PDFs/emails into JSON.

- Follow this schema exactly (no extra fields):
  {
    "party_name": string,
    "jurisdiction": string | null,
    "effective_date": string | null,
    "termination_clause_summary": string | null
  }
- If a field is missing, set it to null rather than guessing.
- Before returning, re-scan the source for missed fields.
</extraction_spec>
```

For multi-file extraction, serialize per-document results separately and include stable IDs.

## 8. Prompt migration guide to GPT-5.2

GPT-5.2 supports a `reasoning_effort` knob (none|minimal|low|medium|high|xhigh). Use the mapping below when migrating:

| Current model | Target model | Target reasoning_effort | Notes |
| --- | --- | --- | --- |
| GPT-4o | GPT-5.2 | none | Treat 4o/4.1 migrations as fast/low-deliberation by default. |
| GPT-4.1 | GPT-5.2 | none | Same mapping as GPT-4o for parity. |
| GPT-5 | GPT-5.2 | same value except minimal -> none | Preserve existing effort unless evals regress. |
| GPT-5.1 | GPT-5.2 | same value | Keep the reasoning profile identical before tuning. |

Default reasoning is medium for GPT-5 and none for GPT-5.1/5.2.

Prompt Optimizer steps:

1. Switch models without changing prompts to isolate the model delta.
2. Pin `reasoning_effort` to preserve latency/cost.
3. Run evals for a baseline.
4. If regressions appear, tune the prompt or adjust reasoning effort incrementally.
5. Re-run evals after each change.

## 9. Web search and research

GPT-5.2 synthesizes across many sources. Establish research rules:

```
<web_search_rules>
- Act as an expert research assistant with comprehensive, well-structured answers.
- Prefer web research over assumptions when facts may be uncertain; include citations.
- Research all parts of the query and resolve contradictions.
- Do not ask clarifying questions; cover plausible intents with breadth and depth.
- Write clearly using Markdown (headers, bullets, tables when helpful).
</web_search_rules>
```

Optionally, provide a more detailed charter outlining persona, factuality, required citations, research depth, writing guidelines, value-add behavior, ambiguity handling, and partial-compliance strategies. This ensures GPT-5.2 conducts deep research, cites sources, and explains mechanisms behind key claims.

## 10. Conclusion

GPT-5.2 is a meaningful step forward for teams building production-grade agents that prioritize accuracy, reliability, and disciplined execution. It delivers stronger instruction following, cleaner output, and more consistent behavior across complex, tool-heavy workflows. Most prompts migrate cleanly when reasoning effort, verbosity, and scope constraints stay intact during the transition. Rely on evals to validate behavior before tweaking prompts, and adjust reasoning effort or constraints only when regressions appear. With explicit prompting and measured iteration, GPT-5.2 unlocks higher quality outcomes while maintaining predictable cost and latency profiles.
