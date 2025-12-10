"""Multi-step AI workflows coordinating integrations and tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
from pathlib import Path

from ..integrations.onenote.service import OneNoteService
from ..integrations.excel.service import ExcelService
from ..integrations.word.service import WordService
from ..versioning.git_async import enqueue_commit


@dataclass
class CleanNotebookResult:
    """Result from cleaning a OneNote notebook."""

    notebook_id: str
    pages_updated: int
    summary: str
    changed_files: List[str]


@dataclass
class ExcelSummaryResult:
    """Result from summarizing an Excel sheet."""

    workbook_path: str
    sheet_name: str
    summary_sheet_name: str
    changed_files: List[str]


@dataclass
class WordDraftResult:
    """Result from drafting a Word document."""

    document_path: str
    changed_files: List[str]
    summary: str


class NotebookCleanupWorkflow:
    """Clean OneNote content and persist history."""

    def __init__(self, onenote: OneNoteService):
        self.onenote = onenote

    def run(self, section_id: str, actor: str = "AIC") -> None:
        changed_files = self.onenote.clean_section(section_id, actor=actor)
        enqueue_commit(
            changed_files, actor=actor, tag="onenote", reason="Clean section"
        )


class ExcelSummaryWorkflow:
    """Generate a summary sheet from an existing workbook."""

    def __init__(self, excel: ExcelService):
        self.excel = excel

    def run(
        self, workbook: str, sheet: str, instruction: str, actor: str = "AIC"
    ) -> None:
        changed_files = self.excel.summarize_sheet(
            workbook, sheet, instruction, actor=actor
        )
        enqueue_commit(
            changed_files, actor=actor, tag="excel", reason="Summarize sheet"
        )


class WeeklyFinanceReportWorkflow:
    """Generate a weekly financial report from Excel data and create a Word summary."""

    def __init__(self, excel: ExcelService, word: WordService):
        self.excel = excel
        self.word = word

    def run(
        self, workbook_path: str, sheet_name: str, output_doc: str, actor: str = "AIC"
    ) -> None:
        # Step 1: Analyze Excel workbook
        instruction = "Group by week, sum amounts, create monthly summary"
        excel_files = self.excel.summarize_sheet(
            workbook_path, sheet_name, instruction, actor=actor
        )

        # Step 2: Generate Word summary document
        # In a real implementation, would extract summary data and format it
        summary_text = f"Weekly financial report generated from {workbook_path}"
        word_files = self.word.draft_summary(summary_text, output_doc, actor=actor)

        # Step 3: Commit all changes
        all_files = excel_files + word_files
        enqueue_commit(
            all_files, actor=actor, tag="workflow", reason="Weekly finance report"
        )


class ProjectReviewBriefWorkflow:
    """Create a project review brief from OneNote notes and Excel data."""

    def __init__(self, onenote: OneNoteService, word: WordService):
        self.onenote = onenote
        self.word = word

    def run(self, page_id: str, output_doc: str, actor: str = "Aria") -> None:
        # Step 1: Summarize OneNote page
        summary_path = self.onenote.summarize_page(page_id)

        # Step 2: Read summary and create Word document
        summary_text = summary_path.read_text(encoding="utf-8")
        word_files = self.word.draft_summary(summary_text, output_doc, actor=actor)

        # Step 3: Commit all changes
        all_files = [str(summary_path)] + word_files
        enqueue_commit(
            all_files, actor=actor, tag="workflow", reason="Project review brief"
        )


class CleanNotebookWorkflow:
    """Clean an entire OneNote notebook section by section."""

    def __init__(self, onenote: OneNoteService):
        self.onenote = onenote

    def run(self, notebook_id: str, actor: str = "AIC") -> None:
        from ..integrations.onenote import OneNoteClient

        client = OneNoteClient()
        sections = client.list_sections(notebook_id)

        all_changed_files: List[str] = []
        for section in sections:
            section_id = section.get("id")
            if not section_id:
                continue
            changed_files = self.onenote.clean_section(section_id, actor=actor)
            all_changed_files.extend(changed_files)

        # Commit all changes together
        if all_changed_files:
            enqueue_commit(
                all_changed_files,
                actor=actor,
                tag="onenote",
                reason=f"Clean notebook {notebook_id}",
            )
