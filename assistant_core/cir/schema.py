"""Canonical Internal Representation (CIR) schema definitions.

This module provides a lossless, extensible data model that sits between
source document formats (Word, Excel, PowerPoint, PDF, Markdown, etc.) and
application logic that needs to transform or analyze content. The schema
captures semantics, structure, provenance, and collaboration metadata to
support reliable round-trip conversions and auditability.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4


# --- Core Document Model ----------------------------------------------------

@dataclass
class DocumentMetadata:
    """Rich metadata for document classification and discovery."""

    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
    author: str = ""
    contributors: List[str] = field(default_factory=list)

    # Classification
    category: str = ""
    subcategory: str = ""
    priority: str = "normal"  # low, normal, high, critical
    status: str = "draft"  # draft, review, approved, archived

    # Business context
    project: Optional[str] = None
    department: Optional[str] = None
    client: Optional[str] = None
    confidentiality: str = "internal"  # public, internal, confidential, restricted

    # Technical properties
    source_format: str = ""
    source_path: str = ""
    file_size: Optional[int] = None
    checksum: Optional[str] = None

    # Custom properties
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CIRDocument:
    """Root document container that represents any document type."""

    id: UUID = field(default_factory=uuid4)
    title: str = ""
    document_type: str = "generic"  # word, excel, powerpoint, pdf, note, etc.

    metadata: DocumentMetadata = field(default_factory=lambda: DocumentMetadata())
    sections: List[Section] = field(default_factory=list)  # type: ignore[name-defined]
    attachments: List[Attachment] = field(default_factory=list)  # type: ignore[name-defined]

    # Semantic layer
    semantic_tags: List[str] = field(default_factory=list)
    embeddings: Optional[Dict[str, List[float]]] = None
    relationships: List[DocumentRelationship] = field(default_factory=list)  # type: ignore[name-defined]

    # Provenance & governance
    provenance: ProvenanceChain = field(default_factory=lambda: ProvenanceChain())  # type: ignore[name-defined]
    version: str = "1.0.0"

    # Collaboration
    comments: List[Comment] = field(default_factory=list)  # type: ignore[name-defined]
    annotations: List[Annotation] = field(default_factory=list)  # type: ignore[name-defined]

    def get_all_text(self) -> str:
        """Extract all text content from the document"""
        text_parts = []

        # Add title
        if self.title:
            text_parts.append(self.title)

        # Extract text from all sections and content blocks
        for section in self.sections:
            text_parts.extend(self._extract_section_text(section))

        # Add attachment descriptions
        for attachment in self.attachments:
            if attachment.description:
                text_parts.append(attachment.description)

        return "\n".join(text_parts)

    def _extract_section_text(self, section: Section) -> List[str]:
        """Extract text from a section recursively"""
        text_parts = []

        # Add section title
        if section.title:
            text_parts.append(section.title)

        # Extract text from content blocks
        for block in section.content_blocks:
            text_parts.extend(self._extract_block_text(block))

        # Process subsections recursively
        for subsection in section.subsections:
            text_parts.extend(self._extract_section_text(subsection))

        return text_parts

    def _extract_block_text(self, block: ContentBlock) -> List[str]:
        """Extract text from a content block"""
        text_parts = []

        if block.content:
            if isinstance(block.content, str):
                text_parts.append(block.content)
            elif isinstance(block.content, dict):
                # Handle structured content like tables
                if "text" in block.content:
                    text_parts.append(str(block.content["text"]))
                elif "rows" in block.content:
                    # Extract text from table rows
                    for row in block.content.get("rows", []):
                        if isinstance(row, list):
                            text_parts.extend([str(cell) for cell in row])

        return text_parts


# --- Content Structure ------------------------------------------------------


class ContentBlockType(Enum):
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    CHART = "chart"
    CODE = "code"
    FORMULA = "formula"
    LIST = "list"
    QUOTE = "quote"
    MEDIA = "media"
    EMBED = "embed"
    CUSTOM = "custom"


class ContentType(Enum):
    """High-level content type classification for search and filtering."""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    NOTE = "note"
    EMAIL = "email"
    CALENDAR = "calendar"
    CONTACT = "contact"
    TASK = "task"
    WEBPAGE = "webpage"
    CODE = "code"
    DATABASE = "database"
    ARCHIVE = "archive"
    OTHER = "other"


class SourceSystem(Enum):
    """Source system classification for content provenance."""
    ONEDRIVE = "onedrive"
    SHAREPOINT = "sharepoint"
    OUTLOOK = "outlook"
    TEAMS = "teams"
    AZURE_DEVOPS = "azure_devops"
    GITHUB = "github"
    GITLAB = "gitlab"
    GOOGLE_DRIVE = "google_drive"
    GOOGLE_MAIL = "google_mail"
    GOOGLE_CALENDAR = "google_calendar"
    DROPBOX = "dropbox"
    BOX = "box"
    SLACK = "slack"
    DISCORD = "discord"
    LOCAL_FILESYSTEM = "local_filesystem"
    DATABASE = "database"
    WEB_SCRAPER = "web_scraper"
    API_INTEGRATION = "api_integration"
    MANUAL_UPLOAD = "manual_upload"
    OTHER = "other"


@dataclass
class TextFormatting:
    """Comprehensive text formatting information."""

    font_family: Optional[str] = None
    font_size: Optional[float] = None
    font_weight: Optional[str] = None
    font_style: Optional[str] = None

    color: Optional[str] = None
    background_color: Optional[str] = None
    text_decoration: List[str] = field(default_factory=list)

    alignment: Optional[str] = None
    line_height: Optional[float] = None
    paragraph_spacing: Optional[float] = None
    indent: Optional[float] = None

    language: Optional[str] = None
    direction: str = "ltr"


@dataclass
class LayoutProperties:
    """Basic layout hints for content blocks."""

    position: Dict[str, float] = field(default_factory=dict)
    size: Dict[str, float] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Reference:
    """References to external content or data sources."""

    id: UUID = field(default_factory=uuid4)
    reference_type: str = ""
    target_uri: str = ""
    target_title: str = ""
    target_description: str = ""
    access_date: Optional[datetime] = None
    is_active: bool = True
    authors: List[str] = field(default_factory=list)
    publication_date: Optional[datetime] = None
    publisher: str = ""


@dataclass
class Hyperlink:
    """Inline hyperlink metadata."""

    url: str = ""
    display_text: str = ""
    tooltip: Optional[str] = None


@dataclass
class ContentBlock:
    """Atomic content unit (text, table, image, chart, etc.)."""

    id: UUID = field(default_factory=uuid4)
    block_type: ContentBlockType = ContentBlockType.TEXT
    content: Union[str, Dict[str, Any], List[Any]] = ""

    formatting: TextFormatting = field(default_factory=lambda: TextFormatting())
    layout: LayoutProperties = field(default_factory=lambda: LayoutProperties())

    semantic_role: str = "body"
    importance: float = 1.0

    references: List[Reference] = field(default_factory=list)
    hyperlinks: List[Hyperlink] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Section:
    """Hierarchical content section (chapters, slides, sheets, etc.)."""

    id: UUID = field(default_factory=uuid4)
    title: str = ""
    section_type: str = "content"
    level: int = 1
    order: int = 0

    content_blocks: List[ContentBlock] = field(default_factory=list)
    subsections: List[Section] = field(default_factory=list)  # type: ignore[name-defined]

    layout_hints: Dict[str, Any] = field(default_factory=dict)
    style_properties: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


# --- Rich Content Types -----------------------------------------------------


@dataclass
class TableData:
    """Structured table representation."""

    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    column_types: List[str] = field(default_factory=list)

    has_header_row: bool = True
    has_total_row: bool = False
    table_style: Optional[str] = None

    cell_formatting: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    merged_cells: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ChartData:
    """Chart and visualization data."""

    chart_type: str = "column"
    title: str = ""

    datasets: List[Dict[str, Any]] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)

    colors: List[str] = field(default_factory=list)
    chart_style: Dict[str, Any] = field(default_factory=dict)

    x_axis: Dict[str, Any] = field(default_factory=dict)
    y_axis: Dict[str, Any] = field(default_factory=dict)

    data_source: Optional[Reference] = None


@dataclass
class ImageData:
    """Image and media content."""

    url: str = ""
    alt_text: str = ""
    caption: str = ""

    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None

    format: str = ""
    file_size: Optional[int] = None

    thumbnail_url: Optional[str] = None
    embeddings: Optional[List[float]] = None
    extracted_text: Optional[str] = None


@dataclass
class DocumentRelationship:
    """Relationships between documents and content."""

    id: UUID = field(default_factory=uuid4)
    relationship_type: str = ""
    target_document_id: UUID = field(default_factory=uuid4)
    target_section_id: Optional[UUID] = None

    strength: float = 1.0
    bidirectional: bool = False

    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""


@dataclass
class Annotation:
    """User annotations and AI-generated insights."""

    id: UUID = field(default_factory=uuid4)
    annotation_type: str = "comment"
    target_section_id: Optional[UUID] = None
    target_block_id: Optional[UUID] = None
    target_text_range: Optional[Dict[str, int]] = None

    content: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    is_resolved: bool = False
    priority: str = "normal"
    tags: List[str] = field(default_factory=list)


@dataclass
class Comment(Annotation):
    """Alias for backwards compatibility with legacy comment storage."""


@dataclass
class Attachment:
    """Binary or external attachment associated with a document."""

    id: UUID = field(default_factory=uuid4)
    filename: str = ""
    uri: str = ""
    description: str = ""
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# --- Provenance & Governance ------------------------------------------------


@dataclass
class ChangeRecord:
    """Specific change within a provenance event."""

    change_type: str = ""
    target_path: str = ""
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    confidence: float = 1.0
    requires_approval: bool = False


@dataclass
class ProvenanceEvent:
    """Single change event in document history."""

    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = ""
    description: str = ""
    actor_type: str = "user"
    actor_id: str = ""
    actor_name: str = ""
    changes: List[ChangeRecord] = field(default_factory=list)
    operation_id: Optional[UUID] = None
    parent_event_id: Optional[UUID] = None
    checksum_before: Optional[str] = None
    checksum_after: Optional[str] = None


@dataclass
class ProvenanceChain:
    """Complete audit trail of document changes."""

    creation_event: ProvenanceEvent = field(default_factory=lambda: ProvenanceEvent(event_type="create"))
    events: List[ProvenanceEvent] = field(default_factory=list)

    def add_event(self, event: ProvenanceEvent) -> None:
        self.events.append(event)

    def get_lineage(self) -> List[ProvenanceEvent]:
        return [self.creation_event] + self.events


# --- Domain Extensions ------------------------------------------------------


@dataclass
class Cell:
    """Individual cell with formula and formatting."""

    value: Any = None
    formula: Optional[str] = None
    data_type: str = "text"
    formatting: TextFormatting = field(default_factory=lambda: TextFormatting())


@dataclass
class Worksheet:
    """Individual worksheet representation."""

    name: str = ""
    cells: Dict[str, Cell] = field(default_factory=dict)
    dimensions: Dict[str, int] = field(default_factory=dict)


@dataclass
class Formula:
    """Excel formula with dependencies."""

    cell_address: str = ""
    formula_text: str = ""
    dependencies: List[str] = field(default_factory=list)
    result: Any = None


@dataclass
class PivotTable:
    """Placeholder for pivot table metadata."""

    name: str = ""
    source_range: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpreadsheetExtension:
    """Excel-specific extensions to CIR."""

    worksheets: List[Worksheet] = field(default_factory=list)
    named_ranges: Dict[str, str] = field(default_factory=dict)
    formulas: List[Formula] = field(default_factory=list)
    pivot_tables: List[PivotTable] = field(default_factory=list)
    charts: List[ChartData] = field(default_factory=list)


@dataclass
class SlideElement:
    """Elements on a slide (text boxes, images, shapes)."""

    element_type: str = "textbox"
    position: Dict[str, float] = field(default_factory=dict)
    content: Union[str, ImageData, ChartData, ContentBlock] = ""
    formatting: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Background:
    """Slide background properties."""

    fill: Dict[str, Any] = field(default_factory=dict)
    image: Optional[ImageData] = None


@dataclass
class Slide:
    """Individual slide representation."""

    slide_number: int = 1
    layout_type: str = "content"
    background: Optional[Background] = None
    elements: List[SlideElement] = field(default_factory=list)
    duration: Optional[float] = None
    auto_advance: bool = False


@dataclass
class Transition:
    """Slide transition metadata."""

    type: str = "fade"
    duration: float = 0.0


@dataclass
class Animation:
    """Slide animation metadata."""

    target_element_index: int = 0
    effect: str = ""
    duration: float = 0.0
    trigger: str = "on_click"


@dataclass
class SlideMaster:
    """Global slide styling and placeholders."""

    layouts: Dict[str, Any] = field(default_factory=dict)
    theme: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PresentationExtension:
    """PowerPoint-specific extensions."""

    slides: List[Slide] = field(default_factory=list)
    slide_master: Optional[SlideMaster] = None
    transitions: List[Transition] = field(default_factory=list)
    animations: List[Animation] = field(default_factory=list)


@dataclass
class TextBlock:
    """PDF text block representation."""

    text: str = ""
    bounding_box: Dict[str, float] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Bookmark:
    """PDF bookmark data."""

    title: str = ""
    page_number: int = 1
    destination: Optional[str] = None


@dataclass
class DigitalSignature:
    """PDF digital signature metadata."""

    signer: str = ""
    signed_at: Optional[datetime] = None
    certificate_serial: Optional[str] = None


@dataclass
class FormField:
    """PDF form field."""

    field_name: str = ""
    field_type: str = "text"
    value: Any = None
    position: Dict[str, float] = field(default_factory=dict)
    is_required: bool = False


@dataclass
class PDFPage:
    """Individual PDF page."""

    page_number: int = 1
    dimensions: Dict[str, float] = field(default_factory=dict)
    text_blocks: List[TextBlock] = field(default_factory=list)
    images: List[ImageData] = field(default_factory=list)
    ocr_confidence: Optional[float] = None
    extracted_text: Optional[str] = None


@dataclass
class PDFExtension:
    """PDF-specific extensions."""

    pages: List[PDFPage] = field(default_factory=list)
    bookmarks: List[Bookmark] = field(default_factory=list)
    forms: List[FormField] = field(default_factory=list)
    signatures: List[DigitalSignature] = field(default_factory=list)
    is_searchable: bool = True
    is_form: bool = False
    security_settings: Dict[str, Any] = field(default_factory=dict)


# --- Transformation Layer ---------------------------------------------------


@dataclass
class TransformationRule:
    """Rules for preserving semantics during format conversion."""

    source_format: str = ""
    target_format: str = ""
    rule_type: str = "mapping"  # mapping, enhancement, reduction
    element_mappings: Dict[str, str] = field(default_factory=dict)
    style_mappings: Dict[str, str] = field(default_factory=dict)
    preserve_hierarchy: bool = True
    preserve_formatting: bool = True
    preserve_relationships: bool = True
    custom_transformer: Optional[str] = None


class UnsupportedFormatException(Exception):
    """Raised when a transformer cannot handle the requested format."""


class CIRTransformer:
    """Handles transformations between CIR and specific formats."""

    def __init__(self) -> None:
        self.transformation_rules = self.load_transformation_rules()
        self.format_handlers = self.register_format_handlers()

    async def to_cir(self, source_data: Any, source_format: str) -> CIRDocument:
        handler = self.format_handlers.get(source_format)
        if not handler:
            raise UnsupportedFormatException(f"No handler for {source_format}")
        return await handler.parse_to_cir(source_data)

    async def from_cir(self, cir_doc: CIRDocument, target_format: str) -> Any:
        handler = self.format_handlers.get(target_format)
        if not handler:
            raise UnsupportedFormatException(f"No handler for {target_format}")
        return await handler.generate_from_cir(cir_doc)

    async def transform(self, source_data: Any, source_format: str, target_format: str) -> Any:
        cir_doc = await self.to_cir(source_data, source_format)
        transformed_cir = await self.apply_transformation_rules(cir_doc, source_format, target_format)
        return await self.from_cir(transformed_cir, target_format)

    def load_transformation_rules(self) -> List[TransformationRule]:
        return []

    def register_format_handlers(self) -> Dict[str, Any]:
        return {}

    async def apply_transformation_rules(self, cir_doc: CIRDocument, source_format: str, target_format: str) -> CIRDocument:
        return cir_doc


class SemanticPreserver:
    """Ensures semantic meaning is preserved during transformations."""

    async def preserve_document_structure(self, cir_doc: CIRDocument, target_format: str) -> CIRDocument:
        if target_format == "powerpoint":
            return await self.adapt_for_presentation(cir_doc)
        if target_format == "excel":
            return await self.adapt_for_spreadsheet(cir_doc)
        if target_format == "pdf":
            return await self.adapt_for_pdf(cir_doc)
        return cir_doc

    async def adapt_for_presentation(self, cir_doc: CIRDocument) -> CIRDocument:
        # Convert sections to slides, summarize long text blocks, and adapt layout hints.
        return cir_doc

    async def adapt_for_spreadsheet(self, cir_doc: CIRDocument) -> CIRDocument:
        # Extract structured data into worksheet-friendly formats and preserve formulas.
        return cir_doc

    async def adapt_for_pdf(self, cir_doc: CIRDocument) -> CIRDocument:
        # Flatten layout while retaining searchable text and annotations.
        return cir_doc


__all__ = [
    "Annotation",
    "Attachment",
    "Background",
    "CIRDocument",
    "CIRTransformer",
    "Cell",
    "ChangeRecord",
    "ChartData",
    "Comment",
    "ContentBlock",
    "ContentBlockType",
    "ContentType",
    "DigitalSignature",
    "DocumentMetadata",
    "DocumentRelationship",
    "FormField",
    "Formula",
    "Hyperlink",
    "ImageData",
    "LayoutProperties",
    "PDFExtension",
    "PDFPage",
    "PivotTable",
    "PresentationExtension",
    "ProvenanceChain",
    "ProvenanceEvent",
    "Reference",
    "Section",
    "SemanticPreserver",
    "Slide",
    "SlideElement",
    "SlideMaster",
    "SourceSystem",
    "SpreadsheetExtension",
    "TableData",
    "TextBlock",
    "TextFormatting",
    "TransformationRule",
    "Transition",
    "UnsupportedFormatException",
    "Worksheet",
]
