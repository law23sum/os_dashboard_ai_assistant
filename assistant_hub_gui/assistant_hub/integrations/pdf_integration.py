"""PDF integration wrapper for GUI."""

import os
from pathlib import Path
from typing import Dict
import sqlite3

from .base import BaseIntegration, IntegrationStatus


class PDFIntegration(BaseIntegration):
    """Integration for PDF documents."""
    
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "PDF", "pdf")
    
    def authenticate(self) -> bool:
        """Check if PDF libraries are available."""
        try:
            import PyPDF2
            self.update_status(True)
            return True
        except ImportError:
            try:
                import pdfplumber
                self.update_status(True)
                return True
            except ImportError:
                # PDF integration can still work for file discovery even without libraries
                self.update_status(True, error="PDF text extraction libraries not installed")
                return True
    
    def sync(self) -> int:
        """Scan for PDF files in common locations."""
        if not self.authenticate():
            return 0
        
        count = 0
        try:
            # Scan common document locations
            doc_paths = [
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Desktop"),
                os.path.expanduser("~/Downloads"),
            ]
            
            for base_path in doc_paths:
                if not os.path.exists(base_path):
                    continue
                
                for root, dirs, files in os.walk(base_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            file_path = os.path.join(root, file)
                            try:
                                rel_path = os.path.relpath(file_path, base_path)
                                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                                
                                # Try to extract page count if possible
                                page_count = None
                                try:
                                    import PyPDF2
                                    with open(file_path, 'rb') as f:
                                        pdf_reader = PyPDF2.PdfReader(f)
                                        page_count = len(pdf_reader.pages)
                                except Exception:
                                    try:
                                        import pdfplumber
                                        with pdfplumber.open(file_path) as pdf:
                                            page_count = len(pdf.pages)
                                    except Exception:
                                        pass
                                
                                data = {
                                    "path": file_path,
                                    "size": file_size,
                                    "extension": ".pdf"
                                }
                                if page_count:
                                    data["page_count"] = page_count
                                
                                self.record_item(
                                    external_id=rel_path,
                                    item_kind="pdf",
                                    title=Path(file).stem,
                                    data=data
                                )
                                count += 1
                            except Exception:
                                continue
            
            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            self.update_status(False, str(e))
            return 0
    
    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, '_status') or not self._status:
            self._status = IntegrationStatus()
        return self._status
    
    def extract_text(self, file_path: str) -> str:
        """Extract text content from a PDF file."""
        if not file_path or not os.path.exists(file_path):
            return ""
        
        # Try pdfplumber first (more robust with corrupted PDFs)
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    except Exception:
                        continue
            if text_parts:
                return "\n\n".join(text_parts)
        except ImportError:
            pass
        except Exception as e:
            error_msg = str(e).lower()
            # If pdfplumber fails with EOF or corruption error, try PyPDF2 with strict=False
            if "eof" in error_msg or "corrupt" in error_msg or "invalid" in error_msg:
                pass  # Will try PyPDF2 next
            else:
                # For other errors, try PyPDF2 as fallback
                pass
        
        # Fallback to PyPDF2 with strict=False for corrupted PDFs
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                # Try with strict=False first to handle corrupted PDFs
                try:
                    pdf_reader = PyPDF2.PdfReader(f, strict=False)
                except Exception:
                    # If that fails, try normal mode
                    f.seek(0)
                    pdf_reader = PyPDF2.PdfReader(f)
                
                text_parts = []
                for page in pdf_reader.pages:
                    try:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    except Exception:
                        continue
                if text_parts:
                    return "\n\n".join(text_parts)
        except ImportError:
            pass
        except Exception as e:
            error_msg = str(e).lower()
            # Handle specific EOF marker error
            if "eof marker" in error_msg:
                return f"PDF appears to be corrupted or incomplete (EOF marker not found). The file may be truncated or damaged. File: {os.path.basename(file_path)}"
            # Handle other PDF errors
            elif "corrupt" in error_msg or "invalid" in error_msg:
                return f"PDF file appears to be corrupted or invalid. File: {os.path.basename(file_path)}"
        
        # If all methods fail and no error message was returned, provide generic message
        return f"Unable to extract text from PDF. The file may be corrupted, encrypted, or contain only images. File: {os.path.basename(file_path)}"

