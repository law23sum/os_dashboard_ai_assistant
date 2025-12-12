# GPT-5.1-Codex-Max Prompting Guide

## 1. Getting Started

GPT-5.1-Codex-Max advances the frontier of intelligence and efficiency while remaining API-compatible with prior Codex harnesses. It matches GPT-5.1-Codex performance on SWE-Bench Verified with roughly **30% fewer thinking tokens**—medium reasoning effort is the recommended default for interactive coding agents. High or xhigh reasoning effort unlocks longer autonomous runs for the hardest tasks. The model also introduces **first-class compaction**, enabling multi-hour sessions without rolling context, and materially improves PowerShell/Windows fluency.

To migrate existing harnesses:

- Start from the latest Codex-Max system prompt; most of the gains come from its autonomy, persistence, tool usage, and frontend quality blocks.
- Remove scripted asks for upfront plans, preambles, or streaming status messages that may interrupt long rollouts.
- Adopt the new tool policies (apply_patch, shell_command, todo/plan helpers) to keep interactions in-distribution.
- Review `codex-cli` (open-source) for a reference harness. Clone it and let Codex itself explain how pieces fit together if you prefer a guided tour.

## 2. Prompting Workflow

### 2.1 Recommended Starter Prompt

Use the standard Codex-Max prompt and layer on tactical directives only when the product requirements demand them. The critical blocks focus on:

- Autonomy and persistence (Codex should implement end-to-end)
- Tool-first execution (use git/rg/read_file/apply_patch helpers rather than raw shell)
- Frontend/UX discipline (avoid slop, keep typography + layout intentional)

Delete redundant prompts (dual planning instructions, preamble requests, etc.) to reduce the chance of the model stopping early.

### 2.2 Mid-Rollout User Updates

Codex-Max broadcasts reasoning summaries automatically. Treat them like ephemeral telemetry; do **not** prompt for explicit “status updates.” Instead, promote them in your UX the way Codex-CLI does so users can see meaningful milestones (“Found schema mismatch…”, “Refreshed dashboard copy…”).

### 2.3 Using `agents.md`

Codex-cli enumerates `AGENTS.md` files starting at `~/.codex` down to the repo leaf. Each file becomes a `# AGENTS.md instructions for <dir>` system message. This guarantees that local overrides stay in sync. Place directory-specific instructions there rather than jamming them into the main prompt.

## 3. Compaction

Compaction is baked into the Responses API for GPT-5.1-Codex-Max, enabling multi-hour trajectories without busting the context window.

- Invoke `/responses/compact` whenever the transcript nears the model limit or after major milestones.
- The endpoint returns an opaque `encrypted_content` block; feed it into subsequent `/responses` calls.
- Keep prompts identical after compaction; treat compacted items as non-inspectable.
- Limit compaction frequency to meaningful checkpoints (e.g., after finishing a subsystem) to avoid unnecessary overhead.

## 4. Tooling Essentials

### 4.1 `apply_patch`

Use the canonical Responses API apply_patch tool when possible. The model was tuned on that diff format, which yields precise patches and fewer retries. For custom harnesses, replicate the same grammar:

```
*** Begin Patch
*** Update File: path/to/file.ext
@@
-old line
+new line
*** End Patch
```

Codex is trained to emit exactly this diff. Avoid bespoke patch syntaxes unless you also retrain the model on them.

### 4.2 `shell_command`

Wrap terminal commands with the standard schema (string command, explicit `workdir`, optional `timeout_ms`). On Windows/PowerShell, call `pwsh -NoLogo -NoProfile -Command <cmd>`. Reserve shell usage for actions not covered by dedicated tools such as `git`, `rg`, `list_dir`, `read_file`, or `apply_patch`.

### 4.3 `update_plan`

Codex expects a structured TODO/plan tool. The default schema matches `codex-cli`:

```json
{
  "plan": [
    {"step": "Implement endpoint", "status": "in_progress"},
    {"step": "Add tests", "status": "pending"}
  ]
}
```

No more than one `in_progress` step at a time. Always reconcile the plan before finishing (mark each step completed/blocked/cancelled).

### 4.4 `view_image`

Use this helper to attach local screenshots or Figma exports. Pass the absolute or repo-relative path; Codex will ingest the bitmap for that turn.

## 5. Dedicated Terminal-Wrapping Tools

If you prefer specialized tools (e.g., `git(cmd: "status -sb")` instead of raw shell), mirror the underlying command semantics so the outputs stay in-distribution. Example:

```
GIT_TOOL = {
  "name": "git",
  "description": "Execute git commands in repo root",
  "parameters": {"command": "string"}
}
```

Add prompt directives such as “Strictly avoid raw `cmd` when a dedicated tool exists” to ensure adoption.

## 6. Other Custom Tools (Search, Memory, etc.)

Codex can drive semantic search, memory stores, or bespoke APIs, but give the tools precise names (`semantic_search`, `memory_retrieve`) and document how/when to use them. Provide output formats distinct from ripgrep/terminal results to avoid confusion.

## 7. Parallel Tool Calling

Enable `parallel_tool_calls` for faster workflows. Add the following exploration block (Codex-CLI already does this):

```
## Exploration and reading files
- Think first; decide all files you need.
- Batch everything; use multi_tool_use.parallel for simultaneous reads.
- Only make sequential calls if the next file can’t be known beforehand.
```

Order tool call + outputs like so:

```
function_call
function_call
function_call_output
function_call_output
```

This matches Codex’s training data and avoids misaligned responses.

## 8. Tool Response Truncation

Limit tool outputs to ~10k tokens (≈bytes/4). If truncation is required, keep the first half and the last half of the content, replacing the middle with `…<N tokens truncated>…`. This preserves context while signalling omitted sections.

## 9. Putting It Together

1. Start from the Codex-Max base prompt.
2. Layer on project-specific `AGENTS.md` instructions.
3. Use solver tools by default (`git`, `rg`, `read_file`, `apply_patch`).
4. Parallelize independent reads via `multi_tool_use.parallel`.
5. Compact conversations once context approaches the limit.
6. Keep tool responses concise and truncate safely when needed.

Following this guide keeps GPT-5.1-Codex-Max in its sweet spot: autonomous, persistent, and laser-focused on shipping working code.***
