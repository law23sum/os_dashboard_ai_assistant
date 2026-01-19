"""Meeting journal helpers for IPM."""

from __future__ import annotations

from typing import Dict, List
from datetime import datetime, timezone

SECTION_TYPES = [
    "Comments",
    "KnowledgeTransfer",
    "DisputableDebate",
    "ChallengesRisks",
    "SolutionsMitigations",
    "ProposalRaised",
    "MisunderstandingClarification",
    "TechnicalDesign",
    "CommonDiscussions",
    "Questions",
    "NextSteps",
]

KEYWORD_MAP = [
    ("NextSteps", ["next step", "action item", "follow up", "todo"]),
    ("ChallengesRisks", ["risk", "challenge", "blocker", "issue"]),
    ("SolutionsMitigations", ["solution", "mitigation", "fix", "resolve"]),
    ("ProposalRaised", ["proposal", "suggest", "raise", "pitch"]),
    ("TechnicalDesign", ["design", "architecture", "spec", "implementation"]),
    ("MisunderstandingClarification", ["clarify", "misunderstanding", "confusion"]),
    ("DisputableDebate", ["debate", "disagree", "counter"]),
    ("KnowledgeTransfer", ["handoff", "knowledge", "context", "background"]),
    ("Questions", ["?", "question", "ask"]),
]


def _infer_section(text: str) -> str:
    lowered = text.lower()
    for section, keywords in KEYWORD_MAP:
        for keyword in keywords:
            if keyword in lowered:
                return section
    return "Comments"


def generate_journal_blocks(segments: List[dict]) -> List[dict]:
    blocks: List[dict] = []
    now = datetime.now(timezone.utc).isoformat()
    for segment in segments:
        text = segment.get("text_original") or ""
        section = _infer_section(text)
        blocks.append(
            {
                "meeting_id": segment.get("meeting_id"),
                "ts_start": segment.get("ts_start", 0),
                "ts_end": segment.get("ts_end", 0),
                "section_type": section,
                "speaker_label": segment.get("speaker_label"),
                "content": text,
                "references": {},
                "created_at": now,
            }
        )
    return blocks
