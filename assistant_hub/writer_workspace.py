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

    def _apply_word_delta(self, delta: int):
        if not delta:
            return
        self.stats["total_words"] = max(0, self.stats.get("total_words", 0) + delta)
        self.stats["avg_words_per_day"] = max(0, self.stats.get("avg_words_per_day", 0) + delta // 10)
        if self.progress_data:
            self.progress_data[-1] = max(0, self.progress_data[-1] + delta)
