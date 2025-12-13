"""Reusable AI-assisted tools for text and data transformations."""

from __future__ import annotations

from typing import Any, Dict, List

from .openai_client import chat


def summarize_text(
    text: str, style: str = "neutral", model: str = "gpt-5-mini"
) -> str:
    """Summarize text with a given tone.

    Args:
        text: Text to summarize
        style: Style preset - "neutral", "executive", or "friendly"
        model: OpenAI model to use
    """
    from .prompts import ARIA_SYSTEM_PROMPT

    style_notes = {
        "neutral": "Write in a clear, neutral tone.",
        "executive": "Write as a concise executive summary.",
        "friendly": "Write in a warm, approachable tone.",
    }
    style_note = style_notes.get(style, style_notes["neutral"])

    return chat(
        model,
        messages=[
            {"role": "system", "content": ARIA_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{style_note}\n\nSummarize the following:\n\n{text}",
            },
        ],
    )


def rewrite_html(html: str, instruction: str, model: str = "gpt-5-mini") -> str:
    """Rewrite HTML content with structure-preserving instructions."""

    return chat(
        model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant that restructures and cleans HTML."
                    " Preserve lists, equations, and headings while improving clarity."
                ),
            },
            {"role": "user", "content": f"Instruction: {instruction}\n\nHTML:\n{html}"},
        ],
    )


def excel_generate_pandas_code(
    df_sample: str, instruction: str, model: str = "gpt-5-mini"
) -> str:
    """Ask the model to generate pandas code given a DataFrame sample."""

    from .prompts import EXCEL_TRANSFORM_PROMPT

    return chat(
        model,
        messages=[
            {"role": "system", "content": EXCEL_TRANSFORM_PROMPT},
            {
                "role": "user",
                "content": f"Sample data:\n{df_sample}\n\nInstruction: {instruction}",
            },
        ],
    )
