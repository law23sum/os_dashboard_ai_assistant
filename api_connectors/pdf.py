"""
PDF Connector - Advanced PDF processing with OCR and annotation support
Handles PDF reading, text extraction, OCR for scanned documents, and annotation management
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import io
import base64

from .base import BaseConnector, ConnectorConfig, OperationResult, ResourceRef, ConnectorCapability
from ..cir import (
    CIRDocument, CIRNode, ContentType, SourceSystem, Provenance, 
    DocumentMetadata, ImageData, Annotation, AnnotationType, PDFExtension
)


class PDFConnector(BaseConnector):
    """
    Connector for PDF files with OCR and annotation support
    """
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.base_path = config.settings.get('base_path', '.')
        self.ocr_engine = None
        self.pdf_processor = None
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize PDF processing engines"""
        try:
            # Initialize OCR engine if available
            import pytesseract
            self.ocr_engine = pytesseract
        except ImportError:
            self.ocr_engine = None
        
        try:
            # Initialize PDF processor
            import fitz  # PyMuPDF
            self.pdf_processor = fitz
        except ImportError:
            try:
                import PyPDF2
                self.pdf_processor = PyPDF2
            except ImportError:
                self.pdf_processor = None
    
    async def connect(self) -> OperationResult:
        """Verify PDF processing capabilities"""
        try:
            if not self.pdf_processor:
                return OperationResult(
                    success=False,
                    error="No PDF processing library available (PyMuPDF or PyPDF2 required)",
                    error_code="MISSING_DEPENDENCIES"
                )
            
            # Test basic functionality
            capabilities = []
            if self.pdf_processor:
                capabilities.append("pdf_reading")
            if self.ocr_engine:
                capabilities.append("ocr")
            
            self.is_connected = True
            return OperationResult(
                success=True,
                data={
                    "status": "connected",
                    "capabilities": capabilities,
                    "ocr_available": self.ocr_engine is not None
                }
            )
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def disconnect(self) -> OperationResult:
        """Cleanup resources"""
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})
    
    async def health_check(self) -> OperationResult:
        """Check connector health"""
        try:
            if not self.is_connected:
                return OperationResult(
                    success=False,
                    error="Not connected",
                    error_code="NOT_CONNECTED"
                )
            
            # Verify processors are still available
            if not self.pdf_processor:
                return OperationResult(
                    success=False,
                    error="PDF processor not available",
                    error_code="PROCESSOR_UNAVAILABLE"
                )
            
            self.last_health_check = datetime.utcnow()
            return OperationResult(
                success=True,
                data={"status": "healthy", "last_check": self.last_health_check}
            )
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def list_resources(self, resource_type: str = None, 
                           filters: Dict[str, Any] = None) -> OperationResult:
        """List PDF files in the specified directory"""
        try:
            import os
            
            base_path = Path(self.base_path)
            if not base_path.exists():
                return OperationResult(success=True, data=[])
            
            resources = []
            
            # Find PDF files
            for pdf_file in base_path.rglob("*.pdf"):
                if pdf_file.is_file():
                    stat = pdf_file.stat()
                    
                    # Get basic PDF info
                    pdf_info = await self._get_pdf_basic_info(str(pdf_file))
                    
                    resources.append(ResourceRef(
                        id=str(pdf_file.relative_to(base_path)),
                        name=pdf_file.name,
                        path=str(pdf_file),
                        resource_type="pdf",
                        size=stat.st_size,
                        modified_at=datetime.fromtimestamp(stat.st_mtime),
                        created_at=datetime.fromtimestamp(stat.st_ctime),
                        metadata=pdf_info
                    ))
            
            # Apply filters
            if filters:
                resources = self._apply_filters(resources, filters)
            
            return OperationResult(success=True, data=resources)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        """Get detailed PDF metadata"""
        try:
            file_path = self._get_file_path(resource_id)
            
            if not file_path.exists():
                return OperationResult(
                    success=False,
                    error="PDF file not found",
                    error_code="FILE_NOT_FOUND"
                )
            
            metadata = await self._extract_pdf_metadata(str(file_path))
            return OperationResult(success=True, data=metadata)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def read_resource(self, resource_id: str, 
                          options: Dict[str, Any] = None) -> OperationResult:
        """Read PDF and convert to CIR with OCR if needed"""
        try:
            file_path = self._get_file_path(resource_id)
            
            if not file_path.exists():
                return OperationResult(
                    success=False,
                    error="PDF file not found",
                    error_code="FILE_NOT_FOUND"
                )
            
            # Extract content based on available processors
            if hasattr(self.pdf_processor, 'open'):  # PyMuPDF
                cir_document = await self._read_pdf_with_pymupdf(str(file_path), options)
            else:  # PyPDF2
                cir_document = await self._read_pdf_with_pypdf2(str(file_path), options)
            
            return OperationResult(success=True, data=cir_document)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def write_resource(self, resource_id: str, cir_content: CIRDocument,
                           options: Dict[str, Any] = None) -> OperationResult:
        """Generate PDF from CIR content"""
        try:
            file_path = self._get_file_path(resource_id)
            
            # Generate PDF from CIR
            await self._generate_pdf_from_cir(cir_content, str(file_path), options)
            
            return OperationResult(
                success=True,
                data={"path": str(file_path), "resource_id": resource_id}
            )
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def create_resource(self, resource_type: str, cir_content: CIRDocument,
                            options: Dict[str, Any] = None) -> OperationResult:
        """Create new PDF from CIR content"""
        try:
            if resource_type != "pdf":
                return OperationResult(
                    success=False,
                    error=f"Unsupported resource type: {resource_type}",
                    error_code="UNSUPPORTED_TYPE"
                )
            
            # Generate filename
            filename = options.get('filename') or f"{cir_content.title or 'document'}.pdf"
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            file_path = self._get_file_path(filename)
            
            # Generate PDF
            await self._generate_pdf_from_cir(cir_content, str(file_path), options)
            
            return OperationResult(
                success=True,
                data={
                    "path": str(file_path),
                    "resource_id": filename,
                    "created": True
                }
            )
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def delete_resource(self, resource_id: str) -> OperationResult:
        """Delete PDF file"""
        try:
            file_path = self._get_file_path(resource_id)
            
            if not file_path.exists():
                return OperationResult(
                    success=False,
                    error="PDF file not found",
                    error_code="FILE_NOT_FOUND"
                )
            
            file_path.unlink()
            
            return OperationResult(
                success=True,
                data={"deleted_resource_id": resource_id}
            )
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def search(self, query: str, filters: Dict[str, Any] = None,
                    options: Dict[str, Any] = None) -> OperationResult:
        """Search within PDF content"""
        try:
            # List all PDFs
            list_result = await self.list_resources(filters=filters)
            if not list_result.success:
                return list_result
            
            matching_resources = []
            query_lower = query.lower()
            
            # Search within each PDF
            for resource in list_result.data:
                try:
                    # Read PDF content
                    read_result = await self.read_resource(resource.id)
                    if read_result.success:
                        cir_doc = read_result.data
                        content_text = cir_doc.get_all_text().lower()
                        
                        if query_lower in content_text:
                            # Calculate relevance score (simple implementation)
                            score = content_text.count(query_lower)
                            resource.metadata['search_score'] = score
                            resource.metadata['search_query'] = query
                            matching_resources.append(resource)
                
                except Exception:
                    # Skip files that can't be processed
                    continue
            
            # Sort by relevance
            matching_resources.sort(key=lambda x: x.metadata.get('search_score', 0), reverse=True)
            
            # Limit results
            limit = options.get('limit', 10) if options else 10
            matching_resources = matching_resources[:limit]
            
            return OperationResult(success=True, data=matching_resources)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    # Private helper methods
    def _get_file_path(self, resource_id: str):
        """Get full file path from resource ID"""
        return Path(self.base_path) / resource_id
    
    async def _get_pdf_basic_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic PDF information"""
        try:
            if hasattr(self.pdf_processor, 'open'):  # PyMuPDF
                doc = self.pdf_processor.open(file_path)
                info = {
                    "page_count": doc.page_count,
                    "metadata": doc.metadata,
                    "is_encrypted": doc.needs_pass,
                    "processor": "PyMuPDF"
                }
                doc.close()
                return info
            else:  # PyPDF2
                with open(file_path, 'rb') as file:
                    reader = self.pdf_processor.PdfReader(file)
                    return {
                        "page_count": len(reader.pages),
                        "metadata": reader.metadata,
                        "is_encrypted": reader.is_encrypted,
                        "processor": "PyPDF2"
                    }
        except Exception as e:
            return {"error": str(e), "processor": "unknown"}
    
    async def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract comprehensive PDF metadata"""
        try:
            basic_info = await self._get_pdf_basic_info(file_path)
            
            # Add file system metadata
            path = Path(file_path)
            stat = path.stat()
            
            metadata = {
                **basic_info,
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
                "file_name": path.name,
                "file_path": str(path)
            }
            
            return metadata
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _read_pdf_with_pymupdf(self, file_path: str, options: Dict[str, Any] = None) -> CIRDocument:
        """Read PDF using PyMuPDF with OCR support"""
        doc = self.pdf_processor.open(file_path)
        
        # Create root CIR document
        cir_document = CIRDocument(
            title=doc.metadata.get('title') or Path(file_path).stem,
            document_type=SourceSystem.PDF,
            root=CIRNode(
                type=ContentType.PDF,
                title=doc.metadata.get('title') or Path(file_path).stem,
                provenance=[Provenance(
                    source_system=SourceSystem.PDF,
                    source_id=file_path,
                    extraction_method="pymupdf"
                )]
            ),
            metadata=DocumentMetadata(
                source_format="pdf",
                source_path=file_path,
                author=doc.metadata.get('author', ''),
                created_at=self._parse_pdf_date(doc.metadata.get('creationDate')),
                modified_at=self._parse_pdf_date(doc.metadata.get('modDate'))
            )
        )
        
        # Add PDF extension
        pdf_extension = PDFExtension(
            page_count=doc.page_count,
            is_searchable=True,
            security_settings={"encrypted": doc.needs_pass}
        )
        
        # Process each page
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            
            # If no text found and OCR is available, try OCR
            ocr_confidence = None
            if not text.strip() and self.ocr_engine:
                text, ocr_confidence = await self._perform_ocr_on_page(page)
            
            # Extract images
            images = []
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                try:
                    # Extract image data
                    xref = img[0]
                    pix = self.pdf_processor.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        
                        images.append(ImageData(
                            url=f"embedded://page_{page_num}_img_{img_index}",
                            format="png",
                            width=pix.width,
                            height=pix.height,
                            file_size=len(img_data)
                        ))
                    
                    pix = None
                except Exception:
                    # Skip problematic images
                    continue
            
            # Create page node
            page_node = CIRNode(
                type=ContentType.SECTION,
                title=f"Page {page_num + 1}",
                text=text,
                provenance=[Provenance(
                    source_system=SourceSystem.PDF,
                    source_id=f"{file_path}#page{page_num + 1}",
                    extraction_method="pymupdf",
                    confidence=ocr_confidence or 1.0
                )],
                metadata={
                    "page_number": page_num + 1,
                    "ocr_confidence": ocr_confidence,
                    "has_images": len(images) > 0,
                    "image_count": len(images)
                }
            )
            
            # Add images as child nodes
            for img in images:
                img_node = CIRNode(
                    type=ContentType.IMAGE,
                    image=img,
                    provenance=[Provenance(
                        source_system=SourceSystem.PDF,
                        source_id=f"{file_path}#page{page_num + 1}",
                        extraction_method="pymupdf"
                    )]
                )
                page_node.children.append(img_node)
            
            cir_document.root.children.append(page_node)
        
        doc.close()
        return cir_document
    
    async def _read_pdf_with_pypdf2(self, file_path: str, options: Dict[str, Any] = None) -> CIRDocument:
        """Read PDF using PyPDF2 (text only)"""
        with open(file_path, 'rb') as file:
            reader = self.pdf_processor.PdfReader(file)
            
            # Create root CIR document
            cir_document = CIRDocument(
                title=reader.metadata.get('/Title') or Path(file_path).stem,
                document_type=SourceSystem.PDF,
                root=CIRNode(
                    type=ContentType.PDF,
                    title=reader.metadata.get('/Title') or Path(file_path).stem,
                    provenance=[Provenance(
                        source_system=SourceSystem.PDF,
                        source_id=file_path,
                        extraction_method="pypdf2"
                    )]
                ),
                metadata=DocumentMetadata(
                    source_format="pdf",
                    source_path=file_path,
                    author=reader.metadata.get('/Author', ''),
                    created_at=self._parse_pdf_date(reader.metadata.get('/CreationDate')),
                    modified_at=self._parse_pdf_date(reader.metadata.get('/ModDate'))
                )
            )
            
            # Process each page
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    
                    page_node = CIRNode(
                        type=ContentType.SECTION,
                        title=f"Page {page_num + 1}",
                        text=text,
                        provenance=[Provenance(
                            source_system=SourceSystem.PDF,
                            source_id=f"{file_path}#page{page_num + 1}",
                            extraction_method="pypdf2"
                        )],
                        metadata={"page_number": page_num + 1}
                    )
                    
                    cir_document.root.children.append(page_node)
                    
                except Exception:
                    # Skip problematic pages
                    continue
            
            return cir_document
    
    async def _perform_ocr_on_page(self, page) -> tuple[str, float]:
        """Perform OCR on a PDF page"""
        if not self.ocr_engine:
            return "", 0.0
        
        try:
            # Convert page to image
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            
            # Perform OCR
            from PIL import Image
            img = Image.open(io.BytesIO(img_data))
            
            # Get OCR result with confidence
            ocr_data = self.ocr_engine.image_to_data(img, output_type=self.ocr_engine.Output.DICT)
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            
            for i, word in enumerate(ocr_data['text']):
                if word.strip():
                    text_parts.append(word)
                    confidences.append(ocr_data['conf'][i])
            
            text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return text, avg_confidence / 100.0  # Convert to 0-1 scale
            
        except Exception:
            return "", 0.0
    
    async def _generate_pdf_from_cir(self, cir_content: CIRDocument, file_path: str, options: Dict[str, Any] = None):
        """Generate PDF from CIR content"""
        try:
            # Use reportlab for PDF generation
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            if cir_content.title:
                title = Paragraph(cir_content.title, styles['Title'])
                story.append(title)
                story.append(Spacer(1, 12))
            
            # Process content nodes
            for node in cir_content.root.walk():
                if node.text:
                    if node.type == ContentType.SECTION:
                        # Section header
                        if node.title:
                            header = Paragraph(node.title, styles['Heading1'])
                            story.append(header)
                        
                        # Section content
                        content = Paragraph(node.text, styles['Normal'])
                        story.append(content)
                        story.append(Spacer(1, 12))
                    
                    elif node.type == ContentType.PARAGRAPH:
                        para = Paragraph(node.text, styles['Normal'])
                        story.append(para)
                        story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            
        except ImportError:
            # Fallback: create simple text-based PDF
            await self._generate_simple_pdf(cir_content, file_path)
    
    async def _generate_simple_pdf(self, cir_content: CIRDocument, file_path: str):
        """Generate simple PDF without reportlab"""
        # Create a simple text representation
        text_content = f"Title: {cir_content.title}\n\n"
        text_content += cir_content.get_all_text()
        
        # Save as text file with .pdf extension (minimal fallback)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
    
    def _parse_pdf_date(self, date_str) -> Optional[datetime]:
        """Parse PDF date format"""
        if not date_str:
            return None
        
        try:
            # PDF date format: D:YYYYMMDDHHmmSSOHH'mm'
            if date_str.startswith('D:'):
                date_str = date_str[2:]
            
            # Extract date components
            if len(date_str) >= 14:
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                hour = int(date_str[8:10])
                minute = int(date_str[10:12])
                second = int(date_str[12:14])
                
                return datetime(year, month, day, hour, minute, second)
        except:
            pass
        
        return None
    
    def _apply_filters(self, resources: List[ResourceRef], filters: Dict[str, Any]) -> List[ResourceRef]:
        """Apply filters to resource list"""
        filtered = resources
        
        if 'min_pages' in filters:
            min_pages = filters['min_pages']
            filtered = [r for r in filtered 
                       if r.metadata and r.metadata.get('page_count', 0) >= min_pages]
        
        if 'max_size' in filters:
            max_size = filters['max_size']
            filtered = [r for r in filtered if r.size and r.size <= max_size]
        
        if 'created_after' in filters:
            created_after = filters['created_after']
            filtered = [r for r in filtered 
                       if r.created_at and r.created_at > created_after]
        
        return filtered
