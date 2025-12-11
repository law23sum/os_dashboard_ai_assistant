# Canonical Internal Representation (CIR) Schema Design

## 1. Core Philosophy & Design Principles

The CIR schema serves as the universal document format that enables seamless transformation between all software types while preserving semantic meaning, structure, and metadata.

### Design Principles:
1. **Lossless Transformation**: Preserve all meaningful information during format conversions
2. **Semantic Richness**: Capture intent and meaning, not just formatting
3. **Extensibility**: Support new document types and features without breaking existing code
4. **Composability**: Allow complex documents to be built from simpler components
5. **Provenance Tracking**: Maintain complete audit trail of changes and sources

## 2. CIR Schema Architecture

### 2.1 Document Structure Hierarchy

```python
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass
class CIRDocument:
    """
    Root document container - represents any document type
    """
    # Core Identity
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    document_type: str = "generic"  # word, excel, powerpoint, pdf, note, etc.
    
    # Content Structure
    metadata: 'DocumentMetadata' = field(default_factory=lambda: DocumentMetadata())
    sections: List['Section'] = field(default_factory=list)
    attachments: List['Attachment'] = field(default_factory=list)
    
    # Semantic Layer
    semantic_tags: List[str] = field(default_factory=list)
    embeddings: Optional[Dict[str, List[float]]] = None
    relationships: List['DocumentRelationship'] = field(default_factory=list)
    
    # Provenance & Governance
    provenance: 'ProvenanceChain' = field(default_factory=lambda: ProvenanceChain())
    version: str = "1.0.0"
    
    # Collaboration
    comments: List['Comment'] = field(default_factory=list)
    annotations: List['Annotation'] = field(default_factory=list)

@dataclass
class DocumentMetadata:
    """
    Rich metadata for document classification and discovery
    """
    # Basic Properties
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
    author: str = ""
    contributors: List[str] = field(default_factory=list)
    
    # Classification
    category: str = ""  # report, presentation, note, contract, etc.
    subcategory: str = ""
    priority: str = "normal"  # low, normal, high, critical
    status: str = "draft"  # draft, review, approved, archived
    
    # Business Context
    project: Optional[str] = None
    department: Optional[str] = None
    client: Optional[str] = None
    confidentiality: str = "internal"  # public, internal, confidential, restricted
    
    # Technical Properties
    source_format: str = ""  # docx, xlsx, pptx, pdf, md, etc.
    source_path: str = ""
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    
    # Custom Properties
    custom_fields: Dict[str, Any] = field(default_factory=dict)
```

### 2.2 Content Structure Components

```python
@dataclass
class Section:
    """
    Hierarchical content section - can represent chapters, slides, sheets, etc.
    """
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    section_type: str = "content"  # content, header, footer, sidebar, etc.
    level: int = 1  # hierarchy level (1=top, 2=sub, etc.)
    order: int = 0  # position within parent
    
    # Content
    content_blocks: List['ContentBlock'] = field(default_factory=list)
    subsections: List['Section'] = field(default_factory=list)
    
    # Layout & Styling
    layout_hints: Dict[str, Any] = field(default_factory=dict)
    style_properties: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

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

@dataclass
class ContentBlock:
    """
    Atomic content unit - text, table, image, chart, etc.
    """
    id: UUID = field(default_factory=uuid4)
    block_type: ContentBlockType = ContentBlockType.TEXT
    content: Union[str, Dict, List] = ""
    
    # Formatting
    formatting: 'TextFormatting' = field(default_factory=lambda: TextFormatting())
    layout: 'LayoutProperties' = field(default_factory=lambda: LayoutProperties())
    
    # Semantic Information
    semantic_role: str = "body"  # title, subtitle, body, caption, note, etc.
    importance: float = 1.0  # 0.0 to 1.0 importance score
    
    # References & Links
    references: List['Reference'] = field(default_factory=list)
    hyperlinks: List['Hyperlink'] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 2.3 Rich Content Types

```python
@dataclass
class TextFormatting:
    """
    Comprehensive text formatting information
    """
    # Font Properties
    font_family: Optional[str] = None
    font_size: Optional[float] = None
    font_weight: Optional[str] = None  # normal, bold, etc.
    font_style: Optional[str] = None   # normal, italic, etc.
    
    # Text Properties
    color: Optional[str] = None
    background_color: Optional[str] = None
    text_decoration: List[str] = field(default_factory=list)  # underline, strikethrough
    
    # Paragraph Properties
    alignment: Optional[str] = None  # left, center, right, justify
    line_height: Optional[float] = None
    paragraph_spacing: Optional[float] = None
    indent: Optional[float] = None
    
    # Advanced Properties
    language: Optional[str] = None
    direction: str = "ltr"  # ltr, rtl
    
@dataclass
class TableData:
    """
    Structured table representation
    """
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    column_types: List[str] = field(default_factory=list)  # text, number, date, etc.
    
    # Table Properties
    has_header_row: bool = True
    has_total_row: bool = False
    table_style: Optional[str] = None
    
    # Cell Formatting
    cell_formatting: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    merged_cells: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ChartData:
    """
    Chart and visualization data
    """
    chart_type: str = "column"  # column, line, pie, scatter, etc.
    title: str = ""
    
    # Data
    datasets: List[Dict[str, Any]] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Styling
    colors: List[str] = field(default_factory=list)
    chart_style: Dict[str, Any] = field(default_factory=dict)
    
    # Axes
    x_axis: Dict[str, Any] = field(default_factory=dict)
    y_axis: Dict[str, Any] = field(default_factory=dict)
    
    # Source Data Reference
    data_source: Optional['Reference'] = None

@dataclass
class ImageData:
    """
    Image and media content
    """
    # Image Properties
    url: str = ""
    alt_text: str = ""
    caption: str = ""
    
    # Dimensions
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    
    # File Properties
    format: str = ""  # png, jpg, svg, etc.
    file_size: Optional[int] = None
    
    # Processing
    thumbnail_url: Optional[str] = None
    embeddings: Optional[List[float]] = None
    extracted_text: Optional[str] = None  # OCR results
```

### 2.4 Semantic & Relationship Layer

```python
@dataclass
class DocumentRelationship:
    """
    Relationships between documents and content
    """
    id: UUID = field(default_factory=uuid4)
    relationship_type: str = ""  # references, derives_from, updates, supersedes
    target_document_id: UUID = field(default_factory=uuid4)
    target_section_id: Optional[UUID] = None
    
    # Relationship Properties
    strength: float = 1.0  # 0.0 to 1.0 relationship strength
    bidirectional: bool = False
    
    # Context
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""

@dataclass
class Reference:
    """
    References to external content or data sources
    """
    id: UUID = field(default_factory=uuid4)
    reference_type: str = ""  # citation, data_source, hyperlink, etc.
    
    # Target Information
    target_uri: str = ""
    target_title: str = ""
    target_description: str = ""
    
    # Reference Properties
    access_date: Optional[datetime] = None
    is_active: bool = True
    
    # Citation Information
    authors: List[str] = field(default_factory=list)
    publication_date: Optional[datetime] = None
    publisher: str = ""

@dataclass
class Annotation:
    """
    User annotations and AI-generated insights
    """
    id: UUID = field(default_factory=uuid4)
    annotation_type: str = "comment"  # comment, highlight, suggestion, insight
    
    # Target
    target_section_id: Optional[UUID] = None
    target_block_id: Optional[UUID] = None
    target_text_range: Optional[Dict[str, int]] = None  # start, end positions
    
    # Content
    content: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Properties
    is_resolved: bool = False
    priority: str = "normal"
    tags: List[str] = field(default_factory=list)
```

### 2.5 Provenance & Governance

```python
@dataclass
class ProvenanceChain:
    """
    Complete audit trail of document changes
    """
    creation_event: 'ProvenanceEvent' = field(default_factory=lambda: ProvenanceEvent())
    events: List['ProvenanceEvent'] = field(default_factory=list)
    
    def add_event(self, event: 'ProvenanceEvent'):
        """Add new provenance event"""
        self.events.append(event)
        
    def get_lineage(self) -> List['ProvenanceEvent']:
        """Get complete lineage of changes"""
        return [self.creation_event] + self.events

@dataclass
class ProvenanceEvent:
    """
    Single change event in document history
    """
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Event Details
    event_type: str = ""  # create, update, transform, merge, split, etc.
    description: str = ""
    
    # Actor Information
    actor_type: str = "user"  # user, daemon, system, api
    actor_id: str = ""
    actor_name: str = ""
    
    # Change Details
    changes: List['ChangeRecord'] = field(default_factory=list)
    
    # Context
    operation_id: Optional[UUID] = None  # Groups related changes
    parent_event_id: Optional[UUID] = None
    
    # Verification
    checksum_before: Optional[str] = None
    checksum_after: Optional[str] = None

@dataclass
class ChangeRecord:
    """
    Specific change within a provenance event
    """
    change_type: str = ""  # add, remove, modify, move
    target_path: str = ""  # JSONPath to changed element
    
    # Change Data
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    # Metadata
    confidence: float = 1.0  # For AI-generated changes
    requires_approval: bool = False
```

## 3. Software-Specific Extensions

### 3.1 Excel/Spreadsheet Extensions

```python
@dataclass
class SpreadsheetExtension:
    """
    Excel-specific extensions to CIR
    """
    worksheets: List['Worksheet'] = field(default_factory=list)
    named_ranges: Dict[str, str] = field(default_factory=dict)
    formulas: List['Formula'] = field(default_factory=list)
    pivot_tables: List['PivotTable'] = field(default_factory=list)
    charts: List['ChartData'] = field(default_factory=list)

@dataclass
class Worksheet:
    """
    Individual worksheet representation
    """
    name: str = ""
    cells: Dict[str, 'Cell'] = field(default_factory=dict)  # A1: Cell
    dimensions: Dict[str, int] = field(default_factory=dict)  # rows, cols
    
@dataclass
class Cell:
    """
    Individual cell with formula and formatting
    """
    value: Any = None
    formula: Optional[str] = None
    data_type: str = "text"  # text, number, date, boolean, formula
    formatting: TextFormatting = field(default_factory=lambda: TextFormatting())

@dataclass
class Formula:
    """
    Excel formula with dependencies
    """
    cell_address: str = ""
    formula_text: str = ""
    dependencies: List[str] = field(default_factory=list)
    result: Any = None
```

### 3.2 PowerPoint/Presentation Extensions

```python
@dataclass
class PresentationExtension:
    """
    PowerPoint-specific extensions
    """
    slides: List['Slide'] = field(default_factory=list)
    slide_master: Optional['SlideMaster'] = None
    transitions: List['Transition'] = field(default_factory=list)
    animations: List['Animation'] = field(default_factory=list)

@dataclass
class Slide:
    """
    Individual slide representation
    """
    slide_number: int = 1
    layout_type: str = "content"  # title, content, comparison, etc.
    background: Optional['Background'] = None
    elements: List['SlideElement'] = field(default_factory=list)
    
    # Timing
    duration: Optional[float] = None
    auto_advance: bool = False

@dataclass
class SlideElement:
    """
    Elements on a slide (text boxes, images, shapes)
    """
    element_type: str = "textbox"  # textbox, image, shape, chart
    position: Dict[str, float] = field(default_factory=dict)  # x, y, width, height
    content: Union[str, 'ImageData', 'ChartData'] = ""
    formatting: Dict[str, Any] = field(default_factory=dict)
```

### 3.3 PDF Extensions

```python
@dataclass
class PDFExtension:
    """
    PDF-specific extensions
    """
    pages: List['PDFPage'] = field(default_factory=list)
    bookmarks: List['Bookmark'] = field(default_factory=list)
    forms: List['FormField'] = field(default_factory=list)
    signatures: List['DigitalSignature'] = field(default_factory=list)
    
    # PDF Properties
    is_searchable: bool = True
    is_form: bool = False
    security_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PDFPage:
    """
    Individual PDF page
    """
    page_number: int = 1
    dimensions: Dict[str, float] = field(default_factory=dict)  # width, height
    text_blocks: List['TextBlock'] = field(default_factory=list)
    images: List['ImageData'] = field(default_factory=list)
    
    # OCR Results
    ocr_confidence: Optional[float] = None
    extracted_text: Optional[str] = None

@dataclass
class FormField:
    """
    PDF form field
    """
    field_name: str = ""
    field_type: str = "text"  # text, checkbox, radio, dropdown
    value: Any = None
    position: Dict[str, float] = field(default_factory=dict)
    is_required: bool = False
```

## 4. Transformation Patterns

### 4.1 Format Conversion Rules

```python
class CIRTransformer:
    """
    Handles transformations between CIR and specific formats
    """
    
    def __init__(self):
        self.transformation_rules = self.load_transformation_rules()
        self.format_handlers = self.register_format_handlers()
    
    async def to_cir(self, source_data: Any, source_format: str) -> CIRDocument:
        """
        Convert from any format to CIR
        """
        handler = self.format_handlers.get(source_format)
        if not handler:
            raise UnsupportedFormatException(f"No handler for {source_format}")
        
        return await handler.parse_to_cir(source_data)
    
    async def from_cir(self, cir_doc: CIRDocument, target_format: str) -> Any:
        """
        Convert from CIR to any format
        """
        handler = self.format_handlers.get(target_format)
        if not handler:
            raise UnsupportedFormatException(f"No handler for {target_format}")
        
        return await handler.generate_from_cir(cir_doc)
    
    async def transform(self, source_data: Any, source_format: str, 
                       target_format: str) -> Any:
        """
        Direct transformation between formats via CIR
        """
        # Source → CIR
        cir_doc = await self.to_cir(source_data, source_format)
        
        # Apply transformation rules
        transformed_cir = await self.apply_transformation_rules(
            cir_doc, source_format, target_format
        )
        
        # CIR → Target
        return await self.from_cir(transformed_cir, target_format)
```

### 4.2 Semantic Preservation Rules

```python
@dataclass
class TransformationRule:
    """
    Rules for preserving semantics during format conversion
    """
    source_format: str = ""
    target_format: str = ""
    rule_type: str = "mapping"  # mapping, enhancement, reduction
    
    # Mapping Rules
    element_mappings: Dict[str, str] = field(default_factory=dict)
    style_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Semantic Rules
    preserve_hierarchy: bool = True
    preserve_formatting: bool = True
    preserve_relationships: bool = True
    
    # Custom Logic
    custom_transformer: Optional[str] = None  # Function name for complex transformations

class SemanticPreserver:
    """
    Ensures semantic meaning is preserved during transformations
    """
    
    async def preserve_document_structure(self, cir_doc: CIRDocument, 
                                        target_format: str) -> CIRDocument:
        """
        Adapt document structure for target format while preserving meaning
        """
        if target_format == "powerpoint":
            return await self.adapt_for_presentation(cir_doc)
        elif target_format == "excel":
            return await self.adapt_for_spreadsheet(cir_doc)
        elif target_format == "pdf":
            return await self.adapt_for_pdf(cir_doc)
        
        return cir_doc
    
    async def adapt_for_presentation(self, cir_doc: CIRDocument) -> CIRDocument:
        """
        Convert document structure to slide-appropriate format
        """
        # Convert sections to slides
        # Summarize long text blocks
        # Extract key points as bullet lists
        # Convert tables to charts where appropriate
        pass
```

This CIR schema provides a robust foundation for unified document handling across all software types while maintaining semantic richness and complete audit trails. The extensible design allows for software-specific features while ensuring consistent transformation patterns.
