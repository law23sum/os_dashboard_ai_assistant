"""Minimal FastAPI entrypoint showcasing the architecture skeleton."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI

from ai_os.app.cir import CIRDocument, CIRNode
from ai_os.app.connectors.notes import NotesConnector
from ai_os.app.connectors.word import WordConnector
from ai_os.app.connectors.pdf import PDFConnector
from ai_os.app.orchestration.daemons import RegulationIngestDaemon
from ai_os.app.orchestration.events import EventBus
from ai_os.app.orchestration.runner import Orchestrator
from ai_os.app.search.index import InMemoryVectorIndex
from ai_os.app.governance.audit import AuditLog


class DummyStorage:
    """Simple storage adapter for demonstrating connector wiring."""

    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}

    def list(self, folder=None):
        return list(self.data.values())

    def meta(self, resource_id):
        return self.data.get(resource_id, {})

    def get(self, resource_id):
        return self.data[resource_id]

    def upsert(self, resource_id, title: str, text: str = "", table=None, metadata=None):
        if resource_id == "new":
            resource_id = str(len(self.data) + 1)
        self.data[resource_id] = {
            "id": resource_id,
            "title": title,
            "text": text,
            "table": table,
            "metadata": metadata or {},
        }
        return self.data[resource_id]

    def search(self, query, limit: int = 10):
        matches = []
        for record in self.data.values():
            haystack = f"{record.get('title', '')} {record.get('text', '')}".lower()
            if query.lower() in haystack:
                matches.append(record)
        return matches[:limit]


app = FastAPI(title="AI OS Dashboard Skeleton")

bus = EventBus()
orch = Orchestrator(bus)
index = InMemoryVectorIndex()
audit = AuditLog()

notes_storage = DummyStorage()
word_storage = DummyStorage()
pdf_storage = DummyStorage()

notes = NotesConnector(notes_storage)
word = WordConnector(word_storage)
pdf = PDFConnector(pdf_storage)

reg_daemon = RegulationIngestDaemon(pdf_connector=pdf, word_connector=word, index=index, audit=audit)
orch.register_daemon("pdf.added.regulations", reg_daemon)


@app.post("/notes")
def create_note(payload: Dict[str, Any]):
    title = payload.get("title", "Untitled Note")
    text = payload.get("text", "")
    cir = CIRDocument(root=CIRNode(type="note", title=title, text=text), doc_type="note")
    ref = notes.write("new", cir)

    index.upsert_document(cir, payload={"system": notes.system_name, "resource_id": ref.id})
    return {"id": ref.id, "title": ref.name}


@app.post("/pdfs/regulations")
def add_regulation_pdf(payload: Dict[str, Any]):
    title = payload.get("title", "New Regulation")
    text = payload.get("text", "")
    cir = CIRDocument(root=CIRNode(type="pdf", title=title, text=text), doc_type="pdf")
    ref = pdf.write("new", cir)
    orch.emit("pdf.added.regulations", {"resource_id": ref.id})
    return {"pdf_id": ref.id, "status": "ingested_event_emitted"}


@app.get("/search")
def unified_search(q: str):
    results = index.search(q, limit=10)
    return [{"score": score, **payload} for score, payload in results]


@app.get("/audit/{op_id}")
def get_audit(op_id: str):
    record = audit.get(op_id)
    return {
        "id": record.id,
        "actor": record.actor,
        "intent": record.intent,
        "triggered_by": record.triggered_by,
        "started_at": record.started_at,
        "finished_at": record.finished_at,
        "touched": record.touched,
        "diffs": record.diffs,
        "metadata": record.metadata,
    }
