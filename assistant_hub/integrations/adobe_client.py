"""
Adobe API Client for PDF services and Creative Cloud integration
"""
import asyncio
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from adobe.pdfservices.operation.auth.credentials import Credentials
    from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
    from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
    from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
    from adobe.pdfservices.operation.execution_context import ExecutionContext
    from adobe.pdfservices.operation.io.file_ref import FileRef
    from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
    from adobe.pdfservices.operation.pdfops.create_pdf_operation import CreatePDFOperation
    from adobe.pdfservices.operation.pdfops.combine_pdf_operation import CombinePDFOperation
    from adobe.pdfservices.operation.pdfops.split_pdf_operation import SplitPDFOperation
    from adobe.pdfservices.operation.pdfops.options.splitpdf.split_pdf_options import SplitPDFOptions
    from adobe.pdfservices.operation.pdfops.options.splitpdf.page_ranges import PageRanges
    ADOBE_SDK_AVAILABLE = True
except ImportError:
    ADOBE_SDK_AVAILABLE = False

from config import get_api_config
from ..logging_config import setup_logger


class AdobeClient:
    """Adobe API client for PDF services and Creative Cloud"""

    def __init__(self):
        self.config = get_api_config()
        self.logger = setup_logger("AdobeClient")
        self.credentials = None
        self.execution_context = None

    async def initialize(self) -> bool:
        """Initialize Adobe client"""
        try:
            if not ADOBE_SDK_AVAILABLE:
                self.logger.warning("Adobe PDF Services SDK not available. Install with: pip install adobe-pdfservices-sdk")
                return False

            # Create credentials
            self.credentials = Credentials.service_account_credentials_builder() \
                .from_file(self.config.adobe_private_key_file) \
                .build()

            # Create execution context
            self.execution_context = ExecutionContext.create(self.credentials)

            self.logger.info("Adobe client initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Adobe client: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Adobe services are accessible"""
        try:
            if not ADOBE_SDK_AVAILABLE:
                return False

            # Simple test - this would require a test file
            return self.credentials is not None and self.execution_context is not None

        except Exception as e:
            self.logger.error(f"Adobe health check failed: {e}")
            return False

    # PDF Operations
    async def extract_text_from_pdf(self, input_file_path: str, output_dir: str = "output") -> Dict[str, Any]:
        """Extract text from PDF"""
        try:
            if not ADOBE_SDK_AVAILABLE:
                raise Exception("Adobe PDF Services SDK not available")

            # Create FileRef instance
            source_file_ref = FileRef.create_from_local_file(input_file_path)

            # Create operation
            extract_pdf_operation = ExtractPDFOperation.create_new()
            extract_pdf_operation.set_input(source_file_ref)

            # Set options
            extract_pdf_options = ExtractPDFOptions.builder() \
                .add_element_to_extract(ExtractElementType.TEXT) \
                .build()
            extract_pdf_operation.set_options(extract_pdf_options)

            # Execute operation
            result = extract_pdf_operation.execute(self.execution_context)

            # Save result
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            result.save_as(output_file_path)

            return {
                'input_file': input_file_path,
                'output_file': output_file_path,
                'operation': 'extract_text',
                'status': 'completed'
            }

        except Exception as e:
            self.logger.error(f"PDF text extraction failed: {e}")
            raise

    async def create_pdf_from_docx(self, input_file_path: str, output_dir: str = "output") -> Dict[str, Any]:
        """Create PDF from DOCX file"""
        try:
            if not ADOBE_SDK_AVAILABLE:
                raise Exception("Adobe PDF Services SDK not available")

            # Create FileRef instance
            source_file_ref = FileRef.create_from_local_file(input_file_path)

            # Create operation
            create_pdf_operation = CreatePDFOperation.create_new()
            create_pdf_operation.set_input(source_file_ref)

            # Execute operation
            result = create_pdf_operation.execute(self.execution_context)

            # Save result
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, f"created_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            result.save_as(output_file_path)

            return {
                'input_file': input_file_path,
                'output_file': output_file_path,
                'operation': 'create_pdf',
                'status': 'completed'
            }

        except Exception as e:
            self.logger.error(f"PDF creation failed: {e}")
            raise

    async def combine_pdfs(self, input_files: List[str], output_dir: str = "output") -> Dict[str, Any]:
        """Combine multiple PDFs into one"""
        try:
            if not ADOBE_SDK_AVAILABLE:
                raise Exception("Adobe PDF Services SDK not available")

            # Create operation
            combine_pdf_operation = CombinePDFOperation.create_new()

            # Add input files
            for file_path in input_files:
                source_file_ref = FileRef.create_from_local_file(file_path)
                combine_pdf_operation.add_input(source_file_ref)

            # Execute operation
            result = combine_pdf_operation.execute(self.execution_context)

            # Save result
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, f"combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            result.save_as(output_file_path)

            return {
                'input_files': input_files,
                'output_file': output_file_path,
                'operation': 'combine_pdfs',
                'status': 'completed'
            }

        except Exception as e:
            self.logger.error(f"PDF combination failed: {e}")
            raise

    async def split_pdf(self, input_file_path: str, page_ranges: List[tuple],
                       output_dir: str = "output") -> Dict[str, Any]:
        """Split PDF into multiple files"""
        try:
            if not ADOBE_SDK_AVAILABLE:
                raise Exception("Adobe PDF Services SDK not available")

            # Create FileRef instance
            source_file_ref = FileRef.create_from_local_file(input_file_path)

            # Create page ranges
            ranges = PageRanges()
            for start, end in page_ranges:
                ranges.add_range(start, end)

            # Create options
            split_pdf_options = SplitPDFOptions.page_ranges_builder() \
                .add_page_ranges(ranges) \
                .build()

            # Create operation
            split_pdf_operation = SplitPDFOperation.create_new()
            split_pdf_operation.set_input(source_file_ref)
            split_pdf_operation.set_options(split_pdf_options)

            # Execute operation
            result = split_pdf_operation.execute(self.execution_context)

            # Save results
            os.makedirs(output_dir, exist_ok=True)
            output_files = []

            for i, file_ref in enumerate(result.get_result()):
                output_file_path = os.path.join(output_dir, f"split_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                file_ref.save_as(output_file_path)
                output_files.append(output_file_path)

            return {
                'input_file': input_file_path,
                'output_files': output_files,
                'operation': 'split_pdf',
                'status': 'completed'
            }

        except Exception as e:
            self.logger.error(f"PDF splitting failed: {e}")
            raise

    async def extract_pdf_elements(self, input_file_path: str, elements: List[str],
                                 output_dir: str = "output") -> Dict[str, Any]:
        """Extract specific elements from PDF"""
        try:
            if not ADOBE_SDK_AVAILABLE:
                raise Exception("Adobe PDF Services SDK not available")

            # Create FileRef instance
            source_file_ref = FileRef.create_from_local_file(input_file_path)

            # Create operation
            extract_pdf_operation = ExtractPDFOperation.create_new()
            extract_pdf_operation.set_input(source_file_ref)

            # Set options based on requested elements
            options_builder = ExtractPDFOptions.builder()

            element_mapping = {
                'text': ExtractElementType.TEXT,
                'tables': ExtractElementType.TABLES,
                'text_properties': ExtractElementType.TEXT_PROPERTIES
            }

            for element in elements:
                if element.lower() in element_mapping:
                    options_builder.add_element_to_extract(element_mapping[element.lower()])

            extract_pdf_options = options_builder.build()
            extract_pdf_operation.set_options(extract_pdf_options)

            # Execute operation
            result = extract_pdf_operation.execute(self.execution_context)

            # Save result
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, f"extracted_elements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            result.save_as(output_file_path)

            return {
                'input_file': input_file_path,
                'output_file': output_file_path,
                'extracted_elements': elements,
                'operation': 'extract_elements',
                'status': 'completed'
            }

        except Exception as e:
            self.logger.error(f"PDF element extraction failed: {e}")
            raise

    # Creative Cloud API Operations (placeholder for future implementation)
    async def get_creative_cloud_assets(self) -> List[Dict[str, Any]]:
        """Get Creative Cloud assets (placeholder)"""
        try:
            # This would require Creative Cloud API integration
            # Currently returning placeholder data
            self.logger.warning("Creative Cloud API integration not yet implemented")

            return [
                {
                    'id': 'placeholder_1',
                    'name': 'Sample Asset',
                    'type': 'image',
                    'created_date': datetime.now().isoformat(),
                    'status': 'placeholder'
                }
            ]

        except Exception as e:
            self.logger.error(f"Failed to get Creative Cloud assets: {e}")
            raise

    async def upload_to_creative_cloud(self, file_path: str, asset_type: str = "image") -> Dict[str, Any]:
        """Upload asset to Creative Cloud (placeholder)"""
        try:
            # This would require Creative Cloud API integration
            self.logger.warning("Creative Cloud upload not yet implemented")

            return {
                'file_path': file_path,
                'asset_type': asset_type,
                'upload_status': 'placeholder',
                'message': 'Creative Cloud API integration pending'
            }

        except Exception as e:
            self.logger.error(f"Failed to upload to Creative Cloud: {e}")
            raise

    # Unified PDF processing method
    async def process_pdf(self, file_path: str, operation: str = "extract_text", **kwargs) -> Any:
        """Process PDF with specified operation"""
        operations = {
            'extract_text': self.extract_text_from_pdf,
            'create_from_docx': self.create_pdf_from_docx,
            'combine': self.combine_pdfs,
            'split': self.split_pdf,
            'extract_elements': self.extract_pdf_elements
        }

        if operation not in operations:
            raise ValueError(f"Unknown PDF operation: {operation}")

        if operation == 'combine':
            return await operations[operation](kwargs.get('input_files', [file_path]), **kwargs)
        elif operation == 'split':
            return await operations[operation](file_path, kwargs.get('page_ranges', [(1, 1)]), **kwargs)
        elif operation == 'extract_elements':
            return await operations[operation](file_path, kwargs.get('elements', ['text']), **kwargs)
        else:
            return await operations[operation](file_path, **kwargs)

    async def shutdown(self):
        """Shutdown Adobe client"""
        self.credentials = None
        self.execution_context = None
        self.logger.info("Adobe client shutdown complete")
