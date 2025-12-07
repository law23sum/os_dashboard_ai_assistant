"""Multi-step AI workflows coordinating integrations and tools."""

from __future__ import annotations

from typing import Iterable

from ..integrations.onenote.service import OneNoteService
from ..integrations.excel.service import ExcelService
from ..versioning.git_async import enqueue_commit


class NotebookCleanupWorkflow:
    """Example workflow to clean OneNote content and persist history."""

    def __init__(self, onenote: OneNoteService):
        self.onenote = onenote

    def run(self, section_id: str, actor: str = "AIC") -> None:
        changed_files = self.onenote.clean_section(section_id, actor=actor)
        enqueue_commit(changed_files, actor=actor, tag="onenote", reason="Clean section")


class ExcelSummaryWorkflow:
    """Generate a summary sheet from an existing workbook."""

    def __init__(self, excel: ExcelService):
        self.excel = excel

    def run(self, workbook: str, sheet: str, instruction: str, actor: str = "AIC") -> None:
        changed_files = self.excel.summarize_sheet(workbook, sheet, instruction, actor=actor)
        enqueue_commit(changed_files, actor=actor, tag="excel", reason="Summarize sheet")
