"""
Canonical Internal Representation (CIR) - Universal Document Schema
The heart of the OS Dashboard AI Assistant that enables seamless transformation
between all software types while preserving semantic meaning and audit trails.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Content types supported by the CIR system"""

    NOTE = "note"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    PDF = "pdf"
    SECTION = "section"
    SLIDE = "slide"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST = "list"
    IMAGE = "image"
    CHART = "chart"
    CODE = "code"
    FORMULA = "formula"
    COMMENT = "comment"


class SourceSystem(str, Enum):
    """Source systems that can generate CIR content"""

    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    ONENOTE = "onenote"
    PDF = "pdf"
    NOTES = "notes"
    GIT = "git"
    FILESYSTEM = "filesystem"
    OPENAI = "openai"
    SYSTEM = "system"


class AnnotationType(str, Enum):
    """Types of annotations that can be attached to content"""

    COMMENT = "comment"
    HIGHLIGHT = "highlight"
    REDLINE = "redline"
    SUGGESTION = "suggestion"
    AI_INSIGHT = "ai_insight"
    APPROVAL = "approval"
    REJECTION = "rejection"


class Provenance(BaseModel):
    """Tracks the origin and lineage of content"""

    source_system: SourceSystem
    source_id: str
    source_path: Optional[str] = None
    version_hint: Optional[str] = None  # git commit, doc revision, etc.
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_method: str = "api"  # api, file_parse, ocr, manual
    confidence: float = 1.0  # 0.0 to 1.0 confidence in extraction accuracy

    # Lineage tracking
    parent_provenance_id: Optional[str] = None
    transformation_applied: Optional[str] = None


class Annotation(BaseModel):
    """User or AI annotations on content"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author: str
    author_type: Literal["user", "ai", "system"] = "user"
    annotation_type: AnnotationType
    text: str
    anchor: Optional[str] = None  # CIR node id or text range
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Rich annotation data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None  # For AI annotations
    requires_approval: bool = False


class EmbeddingRef(BaseModel):
    """Reference to vector embeddings for semantic search"""

    model: str  # e.g., "text-embedding-ada-002"
    vector_id: str  # ID in vector database
    dimensions: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    chunk_strategy: str = "full"  # full, paragraph, sentence


class Relationship(BaseModel):
    """Relationships between CIR nodes or documents"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    relationship_type: str  # references, derives_from, updates, supersedes
    target_node_id: str
    target_document_id: Optional[str] = None
    strength: float = 1.0  # 0.0 to 1.0 relationship strength
    bidirectional: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FormattingInfo(BaseModel):
    """Rich formatting information preserved during transformations"""

    font_family: Optional[str] = None
    font_size: Optional[float] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[str] = None
    background_color: Optional[str] = None
    alignment: Optional[str] = None  # left, center, right, justify

    # Advanced formatting
    styles: Dict[str, Any] = Field(default_factory=dict)
    css_classes: List[str] = Field(default_factory=list)


class TableData(BaseModel):
    """Structured table representation"""

    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    column_types: List[str] = Field(default_factory=list)  # text, number, date, etc.

    # Table properties
    has_header_row: bool = True
    has_total_row: bool = False
    table_style: Optional[str] = None

    # Cell-level formatting
    cell_formatting: Dict[str, FormattingInfo] = Field(default_factory=dict)
    merged_cells: List[Dict[str, Any]] = Field(default_factory=list)


class ChartData(BaseModel):
    """Chart and visualization data"""

    chart_type: str = "column"  # column, line, pie, scatter, etc.
    title: str = ""

    # Data series
    datasets: List[Dict[str, Any]] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)

    # Styling
    colors: List[str] = Field(default_factory=list)
    chart_style: Dict[str, Any] = Field(default_factory=dict)

    # Axes configuration
    x_axis: Dict[str, Any] = Field(default_factory=dict)
    y_axis: Dict[str, Any] = Field(default_factory=dict)

    # Data source reference
    source_table_id: Optional[str] = None
    source_range: Optional[str] = None


class ImageData(BaseModel):
    """Image and media content"""

    url: str = ""
    alt_text: str = ""
    caption: str = ""

    # Dimensions
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None

    # File properties
    format: str = ""  # png, jpg, svg, etc.
    file_size: Optional[int] = None

    # Processing results
    thumbnail_url: Optional[str] = None
    extracted_text: Optional[str] = None  # OCR results
    image_embedding: Optional[EmbeddingRef] = None


class CIRNode(BaseModel):
    """Universal content node that can represent any type of structured content"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ContentType
    title: Optional[str] = None
    text: Optional[str] = None

    # Hierarchical structure
    children: List["CIRNode"] = Field(default_factory=list)
    parent_id: Optional[str] = None
    order: int = 0  # Position within parent
    level: int = 0  # Hierarchy depth

    # Rich content
    table: Optional[TableData] = None
    chart: Optional[ChartData] = None
    image: Optional[ImageData] = None
    formatting: Optional[FormattingInfo] = None

    # Semantic information
    semantic_role: str = "content"  # title, subtitle, body, caption, note, etc.
    importance: float = 1.0  # 0.0 to 1.0 importance score
    keywords: List[str] = Field(default_factory=list)

    # Governance and tracking
    annotations: List[Annotation] = Field(default_factory=list)
    provenance: List[Provenance] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    embedding: Optional[EmbeddingRef] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def walk(self) -> List["CIRNode"]:
        """Recursively walk all nodes in the tree"""

        nodes = [self]
        for child in self.children:
            nodes.extend(child.walk())
        return nodes

    def find_by_type(self, content_type: ContentType) -> List["CIRNode"]:
        """Find all nodes of a specific type"""

        return [node for node in self.walk() if node.type == content_type]

    def find_by_id(self, node_id: str) -> Optional["CIRNode"]:
        """Find a node by its ID"""

        for node in self.walk():
            if node.id == node_id:
                return node
        return None

    def add_annotation(self, annotation: Annotation):
        """Add an annotation to this node"""

        self.annotations.append(annotation)
        self.updated_at = datetime.utcnow()

    def add_relationship(self, relationship: Relationship):
        """Add a relationship to another node"""

        self.relationships.append(relationship)
        self.updated_at = datetime.utcnow()


class DocumentMetadata(BaseModel):
    """Rich metadata for document classification and discovery"""

    # Basic properties
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    author: str = ""
    contributors: List[str] = Field(default_factory=list)

    # Classification
    category: str = ""  # report, presentation, note, contract, etc.
    subcategory: str = ""
    priority: str = "normal"  # low, normal, high, critical
    status: str = "draft"  # draft, review, approved, archived

    # Business context
    project: Optional[str] = None
    department: Optional[str] = None
    client: Optional[str] = None
    confidentiality: str = "internal"  # public, internal, confidential, restricted

    # Technical properties
    source_format: str = ""  # docx, xlsx, pptx, pdf, md, etc.
    source_path: str = ""
    file_size: Optional[int] = None
    checksum: Optional[str] = None

    # Version information
    version: str = "1.0.0"
    revision_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Custom properties
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class CIRDocument(BaseModel):
    """Complete document representation with governance and audit trails"""

    # Core identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    document_type: SourceSystem = SourceSystem.SYSTEM

    # Content structure
    root: CIRNode
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)

    # Semantic layer
    semantic_tags: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    key_points: List[str] = Field(default_factory=list)

    # Document-level relationships
    relationships: List[Relationship] = Field(default_factory=list)

    # Governance
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Collaboration
    comments: List[Annotation] = Field(default_factory=list)
    approvals: List[Dict[str, Any]] = Field(default_factory=list)

    def get_all_text(self) -> str:
        """Extract all text content from the document"""

        text_parts = []
        for node in self.root.walk():
            if node.text:
                text_parts.append(node.text)
        return "\n".join(text_parts)

    def get_structure_summary(self) -> Dict[str, Any]:
        """Get a summary of the document structure"""

        all_nodes = self.root.walk()
        return {
            "total_nodes": len(all_nodes),
            "node_types": {
                node_type.value: len([n for n in all_nodes if n.type == node_type])
                for node_type in ContentType
            },
            "max_depth": max((node.level for node in all_nodes), default=0),
            "has_tables": any(node.table for node in all_nodes),
            "has_charts": any(node.chart for node in all_nodes),
            "has_images": any(node.image for node in all_nodes),
        }

    def add_document_annotation(self, annotation: Annotation):
        """Add a document-level annotation"""

        self.comments.append(annotation)
        self.updated_at = datetime.utcnow()

    def add_relationship(self, relationship: Relationship):
        """Add a document-level relationship"""

        self.relationships.append(relationship)
        self.updated_at = datetime.utcnow()


# Software-specific extensions
class ExcelExtension(BaseModel):
    """Excel-specific extensions to CIR"""

    worksheets: List[str] = Field(default_factory=list)
    named_ranges: Dict[str, str] = Field(default_factory=dict)
    formulas: List[Dict[str, Any]] = Field(default_factory=list)
    pivot_tables: List[Dict[str, Any]] = Field(default_factory=list)
    charts: List[ChartData] = Field(default_factory=list)


class PowerPointExtension(BaseModel):
    """PowerPoint-specific extensions"""

    slide_count: int = 0
    slide_layouts: List[str] = Field(default_factory=list)
    master_slide: Optional[str] = None
    transitions: List[Dict[str, Any]] = Field(default_factory=list)
    animations: List[Dict[str, Any]] = Field(default_factory=list)


class PDFExtension(BaseModel):
    """PDF-specific extensions"""

    page_count: int = 0
    is_searchable: bool = True
    is_form: bool = False
    bookmarks: List[Dict[str, Any]] = Field(default_factory=list)
    form_fields: List[Dict[str, Any]] = Field(default_factory=list)
    signatures: List[Dict[str, Any]] = Field(default_factory=list)
    security_settings: Dict[str, Any] = Field(default_factory=dict)
    ocr_confidence: Optional[float] = None


# Update CIRDocument to include extensions
CIRDocument.model_rebuild()
