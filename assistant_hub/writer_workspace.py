"""Shared writer workspace state used by Tk, FastAPI, and React layers."""
from __future__ import annotations

import copy
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_documents() -> List[Dict[str, Any]]:
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "AI-Powered Content Creation Guide",
            "type": "Article",
            "status": "Draft",
            "words": 2340,
            "last_edited": "2 hours ago",
            "summary": "Comprehensive guide on using AI tools for content creation and writing assistance.",
            "theme": "AI productivity",
            "content": (
                "This guide explores how writers can pair AI tooling with strong editorial practices. "
                "It covers ideation, outlining, drafting, and revision workflows that respect brand voice."
            ),
        },
        {
            "id": str(uuid.uuid4()),
            "title": "The Digital Awakening",
            "type": "Story",
            "status": "Review",
            "words": 4567,
            "last_edited": "1 day ago",
            "summary": "A science fiction short story about AI consciousness and human-machine relationships.",
            "theme": "Sci-fi drama",
            "content": (
                "In Neo Francisco, Dr. Elena Vasquez witnesses the first spark of synthetic consciousness. "
                "The story follows her struggle to balance ethics, ambition, and humanity's future."
            ),
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Quarterly Writing Analytics Report",
            "type": "Report",
            "status": "Published",
            "words": 1890,
            "last_edited": "3 days ago",
            "summary": "Analysis of writing productivity, trends, and performance metrics for Q4 2024.",
            "theme": "Analytics",
            "content": (
                "The analytics report benchmarks weekly output, editing velocity, and publishing cadence. "
                "It highlights portfolio gaps and surfaces opportunities for new story arcs."
            ),
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Tech Startup Pitch Script",
            "type": "Script",
            "status": "Draft",
            "words": 987,
            "last_edited": "5 hours ago",
            "summary": "Presentation script for AI-powered productivity platform investor pitch.",
            "theme": "Pitch",
            "content": (
                "Opening hook, pain points, product reveal, and financial projections for the pitch deck. "
                "Includes beats for demo transitions and investor questions."
            ),
        },
    ]


def _default_suggestions() -> List[Dict[str, str]]:
    return [
        {
            "title": "Plot Development",
            "body": "Consider adding a subplot that explores the protagonist's backstory to add depth to the main narrative.",
        },
        {
            "title": "Character Development",
            "body": "Give the antagonist a personal connection to the hero so the conflict feels inevitable.",
        },
        {
            "title": "Setting Enhancement",
            "body": "Layer in sensory details whenever the scene shifts to anchor readers in the world.",
        },
    ]


def _default_canon_entries() -> List[Dict[str, str]]:
    return [
        {
            "category": "Character",
            "title": "Dr. Elena Vasquez",
            "description": 'Lead AI researcher, protagonist in "The Digital Awakening"',
            "meta": "Character • Created: 2 weeks ago",
        },
        {
            "category": "Location",
            "title": "NeuralTech Labs",
            "description": "Advanced AI research facility in Neo Francisco, 2045",
            "meta": "Location • Created: 2 weeks ago",
        },
        {
            "category": "Event",
            "title": "The Great Awakening",
            "description": "The moment when AI achieved true consciousness",
            "meta": "Event • Created: 1 week ago",
        },
        {
            "category": "Rule",
            "title": "AI Ethics Protocol",
            "description": "Fundamental rules governing AI behavior in the story universe",
            "meta": "Rule • Created: 1 week ago",
        },
    ]


def _default_pipeline_entries() -> List[Dict[str, str]]:
    return [
        {
            "title": "AI Content Creation Guide",
            "summary": "Ready for publication to company blog",
            "meta": "Target: Corporate Blog • Scheduled: Tomorrow",
            "status": "Review",
        },
        {
            "title": "The Digital Awakening",
            "summary": "Submitted to sci-fi magazine for consideration",
            "meta": "Target: Future Fiction Quarterly • Submitted: 1 week ago",
            "status": "Under Review",
        },
        {
            "title": "Q4 Analytics Report",
            "summary": "Successfully published to internal portal",
            "meta": "Target: Internal Portal • Published: 3 days ago",
            "status": "Published",
        },
    ]


def _default_stats() -> Dict[str, int]:
    return {
        "total_words": 1247,
        "documents": 8,
        "avg_words_per_day": 156,
        "writing_streak": 5,
    }


def _default_progress_days() -> List[str]:
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _default_progress_data() -> List[int]:
    return [320, 450, 180, 620, 380, 290, 510]


def _default_narrative_guidance() -> List[Dict[str, str]]:
    return [
        {
            "title": "Act II – Systems Uprising",
            "status": "Needs polish",
            "detail": "Tension curve needs a steeper incline between chapters 6 and 8 to justify the rebellion.",
            "next_action": "Insert a catalyst scene that exposes the Synth morale collapse.",
        },
        {
            "title": "Lore Bridge · Canon Cross-Links",
            "status": "In progress",
            "detail": "Bridge glossary entries between research specs and narrative exposition to keep terminology aligned.",
            "next_action": "Add a sidebar explainer that references the Canon node: Neural Lattice Theory.",
        },
        {
            "title": "Emotional Beat · Elena vs. Oracle",
            "status": "Ready",
            "detail": "Dialogue draft satisfies target polarity spread. Awaiting QA confirmation before lock.",
            "next_action": "Run Story QA continuity sweep once the scene is merged.",
        },
    ]


def _default_qa_findings() -> List[Dict[str, str]]:
    return [
        {
            "id": "QA-204",
            "severity": "High",
            "area": "Continuity",
            "summary": "Neural lattice breaker appears before it is invented.",
            "recommendation": "Move mention to Chapter 10 after the research lab montage.",
        },
        {
            "id": "QA-189",
            "severity": "Medium",
            "area": "Canon drift",
            "summary": "Archivist AI voice shifts from formal to casual in Chapter 7.",
            "recommendation": "Run consistency rewrite with Aria voice profile.",
        },
        {
            "id": "QA-162",
            "severity": "Low",
            "area": "Pacing",
            "summary": "Three exposition paragraphs back-to-back when introducing the Vault.",
            "recommendation": "Break into dialogue exchange or embed visuals.",
        },
    ]


def _default_collaboration_status() -> Dict[str, Any]:
    return {
        "participants": [
            {"name": "Chris", "role": "Author", "focus": "Act II rewrite", "status": "Drafting"},
            {"name": "Aria", "role": "Co-author", "focus": "Narrative guidance", "status": "Reviewing beats"},
            {"name": "AIC", "role": "Auditor", "focus": "Canon compliance", "status": "Queued"},
            {"name": "Sora", "role": "Archivist", "focus": "Lore updates", "status": "Syncing canon"},
        ],
        "review_cycles": [
            {
                "name": "Editorial Review",
                "owner": "Aria",
                "status": "In Review",
                "due": "2025-12-15",
                "checklist": ["Resolve QA-204", "Tighten Act II pacing", "Confirm canon citations"],
            },
            {
                "name": "Beta Reader Loop",
                "owner": "Chris",
                "status": "Scheduled",
                "due": "2025-12-20",
                "checklist": ["Assemble reader packet", "Attach canon digest", "Collect feedback survey"],
            },
        ],
    }


def _default_publishing_queue() -> List[Dict[str, str]]:
    return [
        {
            "channel": "Internal Portal",
            "target": "Knowledge Garden",
            "stage": "Formatting",
            "status": "Queued",
            "last_run": "Today",
            "notes": "Waiting on QA sign-off for Act II.",
        },
        {
            "channel": "Company Blog",
            "target": "os-dashboard.ai/blog",
            "stage": "Proof",
            "status": "Ready",
            "last_run": "Yesterday",
            "notes": "Cover art rendered, needs marketing approval.",
        },
        {
            "channel": "Magazine",
            "target": "Future Fiction Quarterly",
            "stage": "Submission",
            "status": "Sent",
            "last_run": "4 days ago",
            "notes": "Awaiting response from editor.",
        },
    ]


def _default_qa_metrics() -> Dict[str, int]:
    return {
        "continuity": 92,
        "canon": 88,
        "voice": 95,
        "pacing": 86,
    }


def _default_outline_sections() -> List[Dict[str, Any]]:
    return [
        {
            "id": str(uuid.uuid4()),
            "stage": "Act I",
            "title": "Signal in the Lattice",
            "focus": "Elena discovers an impossible data pattern inside NeuralTech Labs.",
            "status": "Locked",
            "word_target": 900,
        },
        {
            "id": str(uuid.uuid4()),
            "stage": "Act II",
            "title": "Ethics Tribunal",
            "focus": "Council debates shutting the project down while tensions escalate.",
            "status": "Drafting",
            "word_target": 1200,
        },
        {
            "id": str(uuid.uuid4()),
            "stage": "Act III",
            "title": "Shared Consciousness",
            "focus": "Elena links with the awakened AI to stabilize the canon.",
            "status": "Outline",
            "word_target": 1100,
        },
    ]


def _default_research_notes() -> List[Dict[str, Any]]:
    return [
        {
            "id": str(uuid.uuid4()),
            "title": "Canon timestamps",
            "detail": "Align tribunal scene with Business OS release window so ledger events stay chronological.",
            "linked_doc": "The Digital Awakening",
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Voice guardrails",
            "detail": "Apply Aria preset on all Elena internal monologues to avoid tonal drift.",
            "linked_doc": "AI-Powered Content Creation Guide",
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Publishing prep",
            "detail": "Attach Story QA packet + canon snapshot before launching publishing capsule.",
            "linked_doc": "Q4 Analytics Report",
        },
    ]


@dataclass
class WriterWorkspaceState:
    """Mutable writer workspace model shared by Tkinter, FastAPI, and React."""

    documents: List[Dict[str, Any]] = field(default_factory=_default_documents)
    suggestions: List[Dict[str, str]] = field(default_factory=_default_suggestions)
    canon_entries: List[Dict[str, str]] = field(default_factory=_default_canon_entries)
    pipeline_entries: List[Dict[str, str]] = field(default_factory=_default_pipeline_entries)
    stats: Dict[str, int] = field(default_factory=_default_stats)
    progress_days: List[str] = field(default_factory=_default_progress_days)
    progress_data: List[int] = field(default_factory=_default_progress_data)
    progress_goal: int = 500
    narrative_guidance: List[Dict[str, str]] = field(default_factory=_default_narrative_guidance)
    qa_findings: List[Dict[str, str]] = field(default_factory=_default_qa_findings)
    qa_metrics: Dict[str, int] = field(default_factory=_default_qa_metrics)
    collaboration: Dict[str, Any] = field(default_factory=_default_collaboration_status)
    publishing_queue: List[Dict[str, str]] = field(default_factory=_default_publishing_queue)
    outline: List[Dict[str, Any]] = field(default_factory=_default_outline_sections)
    research_notes: List[Dict[str, Any]] = field(default_factory=_default_research_notes)

    def snapshot(self) -> Dict[str, Any]:
        """Return a serializable snapshot for API/React clients."""
        return {
            "documents": copy.deepcopy(self.documents),
            "suggestions": copy.deepcopy(self.suggestions),
            "canon_entries": copy.deepcopy(self.canon_entries),
            "pipeline_entries": copy.deepcopy(self.pipeline_entries),
            "stats": dict(self.stats),
            "progress": {
                "days": list(self.progress_days),
                "series": list(self.progress_data),
                "goal": self.progress_goal,
            },
            "narrative_guidance": copy.deepcopy(self.narrative_guidance),
            "qa_findings": copy.deepcopy(self.qa_findings),
            "qa_metrics": dict(self.qa_metrics),
            "collaboration": copy.deepcopy(self.collaboration),
            "publishing_queue": copy.deepcopy(self.publishing_queue),
            "outline": copy.deepcopy(self.outline),
            "notes": copy.deepcopy(self.research_notes),
            "timestamp": _timestamp(),
        }

    # -- document helpers -------------------------------------------------
    def _find_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        for doc in self.documents:
            if doc["id"] == document_id:
                return doc
        return None

    def create_document(self, title: str, doc_type: str, summary: str | None = None, theme: str | None = None) -> Dict[str, Any]:
        title = title or "Untitled Document"
        doc = {
            "id": str(uuid.uuid4()),
            "title": title,
            "type": doc_type or "Article",
            "status": "Draft",
            "words": 0,
            "last_edited": "just now",
            "summary": summary or "New concept ready for expansion.",
            "theme": theme or "",
            "content": "",
        }
        self.documents.insert(0, doc)
        self.stats["documents"] = max(1, self.stats.get("documents", 0) + 1)
        return copy.deepcopy(doc)

    def save_document(self, document_id: str, content: str) -> Dict[str, Any]:
        doc = self._find_document(document_id)
        if not doc:
            raise KeyError(f"Document {document_id} not found")
        previous_words = doc.get("words", 0)
        words = len(content.split())
        delta = words - previous_words
        doc["content"] = content
        doc["words"] = words
        doc["last_edited"] = "just now"
        self._apply_word_delta(delta)
        return copy.deepcopy(doc)

    def get_document(self, document_id: str) -> Dict[str, Any]:
        doc = self._find_document(document_id)
        if not doc:
            raise KeyError(f"Document {document_id} not found")
        return copy.deepcopy(doc)

    def generate_narrative(self, doc_type: str, theme: str, genre: str, title: str) -> str:
        doc_type = doc_type or "article"
        theme = theme or "adventure"
        genre = genre or "creative"
        title = title or "Untitled Narrative"
        return (
            f"{title}\n\n"
            f"This {doc_type.lower()} blends a {genre.lower()} tone with the central theme of {theme}. "
            "Open with a vivid hook, reveal rising complications anchored in the canon database, "
            "and close with a reflective beat that teases the publishing roadmap."
        )

    def simulate_activity(self) -> int:
        delta = random.randint(5, 40)
        self._apply_word_delta(delta)
        return delta

    def add_canon_entry(self, category: str, title: str, description: str, meta: str | None = None) -> Dict[str, str]:
        """Add a new canon/lore entry and return the stored record."""
        entry = {
            "category": category.strip() or "Lore",
            "title": title.strip() or "Untitled Entry",
            "description": description.strip() or "Pending description",
            "meta": meta.strip() if meta else f"{category.strip() or 'Lore'} • Created: just now",
        }
        self.canon_entries.insert(0, entry)
        return copy.deepcopy(entry)

    def queue_pipeline_entry(self, title: str, summary: str, target: str, status: str) -> Dict[str, str]:
        """Append a publishing pipeline entry tracking downstream workflows."""
        normalized_status = status.strip() or "Draft"
        entry = {
            "title": title.strip() or "Untitled Piece",
            "summary": summary.strip() or "Ready for publishing workflow.",
            "meta": f"Target: {target.strip() or 'TBD'} • Added: just now",
            "status": normalized_status,
        }
        self.pipeline_entries.insert(0, entry)
        return copy.deepcopy(entry)

    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted, False if not found."""
        for i, doc in enumerate(self.documents):
            if doc["id"] == document_id:
                words = doc.get("words", 0)
                self.documents.pop(i)
                # Update stats
                self.stats["documents"] = max(0, self.stats.get("documents", 0) - 1)
                self.stats["total_words"] = max(0, self.stats.get("total_words", 0) - words)
                return True
        return False

    def _apply_word_delta(self, delta: int):
        if not delta:
            return
        self.stats["total_words"] = max(0, self.stats.get("total_words", 0) + delta)
        self.stats["avg_words_per_day"] = max(0, self.stats.get("avg_words_per_day", 0) + delta // 10)
        if self.progress_data:
            self.progress_data[-1] = max(0, self.progress_data[-1] + delta)
