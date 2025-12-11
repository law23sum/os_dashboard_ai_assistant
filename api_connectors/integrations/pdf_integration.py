"""
PDF Document Integration

Handles PDF file processing, text extraction, and manipulation
"""

import os
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from config.logging_config import setup_logger

logger = setup_logger(__name__)


class PDFIntegration:
    """PDF document processing integration"""

    def __init__(self):
        self.logger = setup_logger("PDFIntegration")

    def is_available(self) -> Dict[str, bool]:
        """Check which PDF libraries are available"""
        return {
            "pypdf2": PYPDF2_AVAILABLE,
            "pdfplumber": PDFPLUMBER_AVAILABLE,
            "reportlab": REPORTLAB_AVAILABLE
        }

    # PDF Reading Operations

    def read_pdf_basic(self, file_path: str) -> Dict[str, Any]:
        """Read PDF using PyPDF2 (basic text extraction)"""
        try:
            if not PYPDF2_AVAILABLE:
                return {"error": "PyPDF2 not available"}

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                content = {
                    "page_count": len(pdf_reader.pages),
                    "metadata": {},
                    "pages": []
                }

                # Extract metadata
                if pdf_reader.metadata:
                    content["metadata"] = {
                        "title": pdf_reader.metadata.title,
                        "author": pdf_reader.metadata.author,
                        "subject": pdf_reader.metadata.subject,
                        "creator": pdf_reader.metadata.creator,
                        "producer": pdf_reader.metadata.producer
                    }

                # Extract text from each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    content["pages"].append({
                        "page_number": page_num + 1,
                        "text": text,
                        "char_count": len(text)
                    })

                return content

        except Exception as e:
            self.logger.error(f"PDF reading (PyPDF2) failed: {e}")
            return {"error": str(e)}

    def read_pdf_advanced(self, file_path: str) -> Dict[str, Any]:
        """Read PDF using pdfplumber (advanced text and table extraction)"""
        try:
            if not PDFPLUMBER_AVAILABLE:
                return {"error": "pdfplumber not available"}

            content = {
                "page_count": 0,
                "pages": [],
                "tables": [],
                "metadata": {}
            }

            with pdfplumber.open(file_path) as pdf:
                content["page_count"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages):
                    page_content = {
                        "page_number": page_num + 1,
                        "text": "",
                        "char_count": 0,
                        "tables": []
                    }

                    # Extract text
                    text = page.extract_text()
                    page_content["text"] = text or ""
                    page_content["char_count"] = len(text) if text else 0

                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        page_content["tables"] = tables
                        content["tables"].extend([{
                            "page": page_num + 1,
                            "table": table
                        } for table in tables])

                    content["pages"].append(page_content)

            return content

        except Exception as e:
            self.logger.error(f"PDF reading (pdfplumber) failed: {e}")
            return {"error": str(e)}

    def extract_text_from_pdf(self, file_path: str, method: str = "auto") -> str:
        """Extract text from PDF with automatic method selection"""
        try:
            # Try advanced method first
            if method == "auto" and PDFPLUMBER_AVAILABLE:
                result = self.read_pdf_advanced(file_path)
                if "error" not in result:
                    return "\n".join([page["text"] for page in result["pages"]])

            # Fall back to basic method
            if PYPDF2_AVAILABLE:
                result = self.read_pdf_basic(file_path)
                if "error" not in result:
                    return "\n".join([page["text"] for page in result["pages"]])

            return ""

        except Exception as e:
            self.logger.error(f"PDF text extraction failed: {e}")
            return ""

    def extract_tables_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF"""
        try:
            if not PDFPLUMBER_AVAILABLE:
                return []

            tables_data = []

            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()

                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:  # Skip empty tables
                            tables_data.append({
                                "page": page_num + 1,
                                "table_index": table_idx,
                                "headers": table[0] if len(table) > 1 else [],
                                "data": table[1:] if len(table) > 1 else table,
                                "row_count": len(table),
                                "col_count": max(len(row) for row in table) if table else 0
                            })

            return tables_data

        except Exception as e:
            self.logger.error(f"PDF table extraction failed: {e}")
            return []

    # PDF Creation Operations

    def create_pdf_from_text(self, text: str, output_path: str,
                           title: str = "Generated PDF") -> bool:
        """Create PDF from text content"""
        try:
            if not REPORTLAB_AVAILABLE:
                return False

            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter

            # Add title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, height - 50, title)

            # Add text content
            c.setFont("Helvetica", 12)
            y_position = height - 80

            # Split text into lines that fit the page
            lines = text.split('\n')
            for line in lines:
                if y_position < 50:  # New page if near bottom
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = height - 50

                # Handle long lines
                if len(line) > 80:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 80:
                            current_line += word + " "
                        else:
                            c.drawString(50, y_position, current_line.strip())
                            y_position -= 15
                            current_line = word + " "

                    if current_line.strip():
                        c.drawString(50, y_position, current_line.strip())
                        y_position -= 15
                else:
                    c.drawString(50, y_position, line)
                    y_position -= 15

            c.save()
            return True

        except Exception as e:
            self.logger.error(f"PDF creation failed: {e}")
            return False

    def merge_pdfs(self, input_paths: List[str], output_path: str) -> bool:
        """Merge multiple PDFs into one"""
        try:
            if not PYPDF2_AVAILABLE:
                return False

            pdf_merger = PyPDF2.PdfMerger()

            for pdf_path in input_paths:
                if os.path.exists(pdf_path):
                    pdf_merger.append(pdf_path)

            pdf_merger.write(output_path)
            pdf_merger.close()

            return True

        except Exception as e:
            self.logger.error(f"PDF merge failed: {e}")
            return False

    def split_pdf(self, input_path: str, output_dir: str,
                 pages_per_split: int = 1) -> List[str]:
        """Split PDF into multiple files"""
        try:
            if not PYPDF2_AVAILABLE:
                return []

            with open(input_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                output_files = []
                total_pages = len(pdf_reader.pages)

                for start_page in range(0, total_pages, pages_per_split):
                    end_page = min(start_page + pages_per_split, total_pages)

                    pdf_writer = PyPDF2.PdfWriter()

                    for page_num in range(start_page, end_page):
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                    output_filename = f"{Path(input_path).stem}_pages_{start_page+1}-{end_page}.pdf"
                    output_path = os.path.join(output_dir, output_filename)

                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)

                    output_files.append(output_path)

                return output_files

        except Exception as e:
            self.logger.error(f"PDF split failed: {e}")
            return []

    # PDF Analysis Operations

    def analyze_pdf_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyze PDF document structure"""
        try:
            analysis = {
                "file_info": self.get_pdf_info(file_path),
                "content_analysis": {},
                "structure_analysis": {}
            }

            # Get content analysis
            if PDFPLUMBER_AVAILABLE:
                content = self.read_pdf_advanced(file_path)
                if "error" not in content:
                    analysis["content_analysis"] = {
                        "total_pages": content["page_count"],
                        "total_tables": len(content["tables"]),
                        "text_density": sum(len(page["text"]) for page in content["pages"]) / max(content["page_count"], 1),
                        "avg_chars_per_page": sum(page["char_count"] for page in content["pages"]) / max(content["page_count"], 1)
                    }

            # Analyze structure
            if PYPDF2_AVAILABLE:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)

                    analysis["structure_analysis"] = {
                        "page_count": len(pdf_reader.pages),
                        "is_encrypted": pdf_reader.is_encrypted,
                        "outline": len(pdf_reader.outline) if pdf_reader.outline else 0
                    }

            return analysis

        except Exception as e:
            self.logger.error(f"PDF structure analysis failed: {e}")
            return {"error": str(e)}

    def get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """Get PDF file information"""
        try:
            path = Path(file_path)
            stat = path.stat()

            info = {
                "filename": path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime
            }

            # Add PDF-specific info if available
            if PYPDF2_AVAILABLE:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    info.update({
                        "page_count": len(pdf_reader.pages),
                        "is_encrypted": pdf_reader.is_encrypted
                    })

            return info

        except Exception as e:
            return {"error": str(e)}

    def search_pdf_content(self, file_path: str, search_terms: List[str],
                          case_sensitive: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Search for terms in PDF content"""
        try:
            results = {}

            # Extract text
            text_content = self.extract_text_from_pdf(file_path)

            if not text_content:
                return {"error": "Could not extract text from PDF"}

            # Split into pages (approximate)
            if PYPDF2_AVAILABLE:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)

                    for term in search_terms:
                        term_results = []

                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()

                            if not case_sensitive:
                                page_text = page_text.lower()
                                term = term.lower()

                            if term in page_text:
                                # Find positions (simple approach)
                                positions = []
                                start = 0
                                while True:
                                    pos = page_text.find(term, start)
                                    if pos == -1:
                                        break
                                    positions.append(pos)
                                    start = pos + 1

                                term_results.append({
                                    "page": page_num + 1,
                                    "occurrences": len(positions),
                                    "positions": positions
                                })

                        if term_results:
                            results[term] = term_results

            return results

        except Exception as e:
            self.logger.error(f"PDF search failed: {e}")
            return {"error": str(e)}

    def extract_images_from_pdf(self, file_path: str, output_dir: str) -> List[str]:
        """Extract images from PDF"""
        try:
            if not PDFPLUMBER_AVAILABLE:
                return []

            extracted_images = []

            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    images = page.images

                    for img_idx, img in enumerate(images):
                        # Extract image data
                        img_data = img["stream"].get_data()

                        # Save image
                        img_filename = f"page_{page_num+1}_img_{img_idx+1}.png"
                        img_path = os.path.join(output_dir, img_filename)

                        with open(img_path, 'wb') as f:
                            f.write(img_data)

                        extracted_images.append(img_path)

            return extracted_images

        except Exception as e:
            self.logger.error(f"PDF image extraction failed: {e}")
            return []

    # Utility Methods

    def validate_pdf(self, file_path: str) -> Dict[str, Any]:
        """Validate PDF file integrity"""
        try:
            validation = {
                "is_valid": False,
                "errors": [],
                "warnings": []
            }

            if not os.path.exists(file_path):
                validation["errors"].append("File does not exist")
                return validation

            # Try to open with PyPDF2
            if PYPDF2_AVAILABLE:
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        validation["is_valid"] = True

                        # Check for encryption
                        if pdf_reader.is_encrypted:
                            validation["warnings"].append("PDF is encrypted")

                        # Check page count
                        page_count = len(pdf_reader.pages)
                        if page_count == 0:
                            validation["warnings"].append("PDF has no pages")

                except Exception as e:
                    validation["errors"].append(f"PyPDF2 validation failed: {str(e)}")

            # Try to open with pdfplumber
            if PDFPLUMBER_AVAILABLE:
                try:
                    with pdfplumber.open(file_path) as pdf:
                        if len(pdf.pages) == 0:
                            validation["warnings"].append("No pages found")
                except Exception as e:
                    validation["errors"].append(f"pdfplumber validation failed: {str(e)}")

            # If no errors, mark as valid
            if not validation["errors"]:
                validation["is_valid"] = True

            return validation

        except Exception as e:
            return {
                "is_valid": False,
                "errors": [str(e)],
                "warnings": []
            }
