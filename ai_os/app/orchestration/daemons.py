"""Example daemon flows for the AI OS."""
from __future__ import annotations

from ai_os.app.connectors.base import Connector
from ai_os.app.orchestration.events import Event
from ai_os.app.search.index import InMemoryVectorIndex
from ai_os.app.governance.audit import AuditLog


class RegulationIngestDaemon:
    """Placeholder daemon for ingesting regulations and proposing updates."""

    name = "regulation_ingest"

    def __init__(
        self,
        pdf_connector: Connector,
        word_connector: Connector,
        index: InMemoryVectorIndex,
        audit: AuditLog,
    ):
        self.pdf = pdf_connector
        self.word = word_connector
        self.index = index
        self.audit = audit

    def handle_event(self, event: Event):
        pdf_id = event.payload["resource_id"]

        operation = self.audit.start(
            actor=f"daemon:{self.name}",
            intent="ingest_regulation_and_prepare_policy_update",
            triggered_by="event",
            metadata={"event": event.name},
        )

        pdf_cir = self.pdf.read(pdf_id)
        self.audit.add_touch(operation.id, self.pdf.system_name, pdf_id, "read")

        self.index.upsert_document(pdf_cir, payload={"system": self.pdf.system_name, "resource_id": pdf_id})

        draft_root = pdf_cir.root.model_copy(deep=True)
        draft_root.type = "document"
        draft_root.title = f"Policy update draft based on {pdf_cir.root.title or 'regulation'}"
        draft_root.text = (
            "DRAFT POLICY UPDATE\n\n"
            "This is a placeholder draft generated from the regulation.\n"
            "Replace with LLM-driven comparison output."
        )

        draft_cir = pdf_cir.model_copy()
        draft_cir.root = draft_root
        draft_cir.doc_type = "word"

        created = self.word.write(resource_id="new", cir=draft_cir)
        self.audit.add_touch(operation.id, self.word.system_name, created.id, "write")

        diff = self.word.diff(before=pdf_cir, after=draft_cir)
        self.audit.add_diff(operation.id, diff)

        self.audit.finish(operation.id)
