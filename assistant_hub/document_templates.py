"""Document template catalog for governed multi-format assets.

This module captures template intents for key deliverables and provides sample
artifacts for each supported file type. The goal is to make it trivial for the
assistant or a daemon to provision starter files with baked-in governance
expectations and toolchain alignment.
"""

from dataclasses import dataclass, field
from typing import Dict, List


GOVERNANCE_CONTROLS: List[str] = [
    "every AI edit is tracked",
    "every change is diffed",
    "every document has a version history",
    "every operation has a timestamp",
    "every action is reversible",
    "every output is accountable",
]

TOOLCHAIN_ALIGNMENT: List[str] = [
    "OneNote becomes the living structured memory",
    "Word becomes the formatted deliverable engine",
    "Excel becomes the analytical substrate",
    "Git becomes the brain stem holding the lineage of every thought",
    "ChatGPT becomes the reasoning center",
    "Daemons become the continuous active cortex",
    "AIC/Sora/Aria become the interpretive personalities that guide knowledge formation",
]

DAEMON_ROLES: List[str] = [
    "notices missing documents",
    "drafts proposals",
    "updates reports",
    "summarizes notebooks",
    "analyzes spreadsheets",
    "reorganizes folders",
    "updates tasks",
    "alerts the user when something's outdated",
    "tracks version history",
    "suggests improvements",
    "predicts next steps",
    "executes workflows",
]


@dataclass
class TemplateSample:
    """A single sample artifact for a file type."""

    extension: str
    filename: str
    description: str


@dataclass
class DocumentTemplateProfile:
    """Structured definition of a deliverable template."""

    name: str
    purpose: str
    governance: List[str] = field(default_factory=list)
    toolchain_alignment: List[str] = field(default_factory=list)
    daemon_support: List[str] = field(default_factory=list)
    sample_files: List[TemplateSample] = field(default_factory=list)

    def sample_map(self) -> Dict[str, TemplateSample]:
        """Return sample files keyed by extension for quick lookup."""

        return {sample.extension: sample for sample in self.sample_files}


def _base_samples(doc_type: str) -> List[TemplateSample]:
    """Create baseline samples for all supported file types."""

    normalized = doc_type.lower()
    title = doc_type.title()
    return [
        TemplateSample(
            extension="csv",
            filename=f"{normalized.replace(' ', '_')}_template.csv",
            description=(
                f"CSV table for {title} with columns: section, owner, status, "
                "last_updated (ISO timestamp), and audit_reference. Includes rows "
                "for scope, assumptions, risks, decisions, and governance notes."
            ),
        ),
        TemplateSample(
            extension="json",
            filename=f"{normalized.replace(' ', '_')}_template.json",
            description=(
                "JSON payload capturing metadata, governance controls, and "
                f"structured sections for {title}. Includes placeholders for "
                "version_tag, source_links, and change_log entries."
            ),
        ),
        TemplateSample(
            extension="pdf",
            filename=f"{normalized.replace(' ', '_')}_template.pdf",
            description=(
                f"PDF rendering of the {title} starter content with a cover page, "
                "executive highlights, change summary, and a footer showing the "
                "latest commit hash for auditability."
            ),
        ),
        TemplateSample(
            extension="xlsx",
            filename=f"{normalized.replace(' ', '_')}_template.xlsx",
            description=(
                f"Workbook with tabs for metrics, risks, decisions, and actions for {title}. "
                "Each tab includes timestamp columns and diff-friendly change notes."
            ),
        ),
        TemplateSample(
            extension="docx",
            filename=f"{normalized.replace(' ', '_')}_template.docx",
            description=(
                f"Formatted Word starter with title page, overview, objectives, current status, "
                "open questions, and appendix that documents diffs and AI-assisted edits."
            ),
        ),
        TemplateSample(
            extension="txt",
            filename=f"{normalized.replace(' ', '_')}_template.txt",
            description=(
                f"Plain text scaffold for {title} outlining sections and governance reminders "
                "so edits remain accountable even in lightweight contexts."
            ),
        ),
        TemplateSample(
            extension="pptx",
            filename=f"{normalized.replace(' ', '_')}_template.pptx",
            description=(
                f"Slide deck with agenda, problem statement, insights, actions, and risk/mitigation slides "
                f"tailored to {title}. Notes fields remind presenters that AI edits are tracked and diffed."
            ),
        ),
    ]


document_templates: List[DocumentTemplateProfile] = []

for template_name, purpose in [
    (
        "briefs",
        "Fast, high-signal summaries that outline context, intent, and next actions.",
    ),
    (
        "proposals",
        "Persuasive narratives with problem framing, solution options, and acceptance criteria.",
    ),
    (
        "compliance reports",
        "Evidence-backed reporting aligned to regulatory controls and audit trails.",
    ),
    (
        "patient summaries",
        "Concise clinical snapshots with diagnostics, care plans, and consent provenance.",
    ),
    (
        "risk assessments",
        "Structured identification, scoring, and mitigation planning for known risks.",
    ),
    (
        "regulatory filings",
        "Formal submissions with references to statutes, controls, and supporting evidence.",
    ),
    (
        "engineering specs",
        "Technical requirements with architecture notes, interfaces, and test criteria.",
    ),
    (
        "technical documents",
        "Implementation details, runbooks, and troubleshooting guides.",
    ),
    (
        "product updates",
        "Release notes, customer impact, rollout plans, and observability checks.",
    ),
    (
        "operational manuals",
        "Step-by-step procedures with safety, rollback, and training references.",
    ),
]:
    document_templates.append(
        DocumentTemplateProfile(
            name=template_name,
            purpose=purpose,
            governance=GOVERNANCE_CONTROLS.copy(),
            toolchain_alignment=TOOLCHAIN_ALIGNMENT.copy(),
            daemon_support=DAEMON_ROLES.copy(),
            sample_files=_base_samples(template_name),
        )
    )


__all__ = [
    "DocumentTemplateProfile",
    "TemplateSample",
    "GOVERNANCE_CONTROLS",
    "TOOLCHAIN_ALIGNMENT",
    "DAEMON_ROLES",
    "document_templates",
]
