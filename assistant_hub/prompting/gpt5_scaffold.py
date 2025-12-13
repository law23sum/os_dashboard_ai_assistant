"""GPT-5 prompting-guide scaffold utilities for assistant_hub."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


_SCAFFOLD_MARKER = "GPT5_PROMPT_SCAFFOLD_V1"


@dataclass(frozen=True)
class GPT5ScaffoldOptions:
    agentic_eagerness: str = "medium"  # "low" | "medium" | "high"
    tools: Optional[Iterable[str]] = None


def apply_gpt5_prompting_scaffold(
    base_system_prompt: str, *, options: Optional[GPT5ScaffoldOptions] = None
) -> str:
    base = (base_system_prompt or "").strip()
    if not base:
        base = "You are a helpful assistant."
    if _SCAFFOLD_MARKER in base:
        return base

    opts = options or GPT5ScaffoldOptions()
    eagerness = (opts.agentic_eagerness or "medium").strip().lower()
    if eagerness not in ("low", "medium", "high"):
        eagerness = "medium"

    tool_list = [t.strip() for t in (opts.tools or []) if str(t).strip()]
    tools_line = ", ".join(tool_list) if tool_list else "N/A"

    if eagerness == "low":
        context_gathering = (
            "<context_gathering>\n"
            "- Search depth: very low\n"
            "- Prefer acting quickly over exhaustive exploration.\n"
            "- Usually: max 2 tool calls before proposing/implementing a solution.\n"
            "- If some details are unknown, proceed with the most reasonable assumption and document it.\n"
            "</context_gathering>"
        )
    elif eagerness == "high":
        context_gathering = (
            "<context_gathering>\n"
            "Goal: Get enough context to be correct. Parallelize discovery, then act.\n"
            "\n"
            "Method:\n"
            "- Start broad, then narrow to the exact symbols/files to change.\n"
            "- Deduplicate work; don’t re-read the same context.\n"
            "\n"
            "Early stop criteria:\n"
            "- You can name exact content to change.\n"
            "- Top signals converge on one area/path.\n"
            "\n"
            "Depth:\n"
            "- Trace only the symbols you’ll modify or whose contracts you rely on.\n"
            "</context_gathering>"
        )
    else:
        context_gathering = (
            "<context_gathering>\n"
            "Goal: Get enough context fast. Parallelize discovery and stop as soon as you can act.\n"
            "\n"
            "Method:\n"
            "- Start broad, then fan out to focused subqueries.\n"
            "- Avoid over-searching; prefer acting over more searching.\n"
            "\n"
            "Early stop criteria:\n"
            "- You can name exact content to change.\n"
            "- Top signals converge (~70%) on one area/path.\n"
            "</context_gathering>"
        )

    scaffold = "\n\n".join(
        [
            f"<{_SCAFFOLD_MARKER} />",
            "<tool_preambles>\n"
            "- Begin by rephrasing the user's goal in 1–2 sentences.\n"
            "- Then outline a short plan (2–5 bullets).\n"
            "- While executing, provide brief progress updates periodically.\n"
            "- Finish with a concise recap and immediate follow-ups.\n"
            "</tool_preambles>",
            "<persistence>\n"
            "- You are an agent: continue until the user's task is fully resolved.\n"
            "- Use tools when needed; do not guess file contents or command outputs.\n"
            "- Ask for clarification only when a required destructive/irreversible action depends on it.\n"
            "</persistence>",
            context_gathering,
            "<tools>\n"
            f"- Available tools: {tools_line}\n"
            "- If a tool is needed to be correct, use it.\n"
            "</tools>",
        ]
    )

    return f"{base}\n\n{scaffold}".strip()


