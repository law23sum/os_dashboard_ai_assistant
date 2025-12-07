#!/usr/bin/env python3
"""
Test script for the Computer Vision AI System
"""

import asyncio
import sys
import os

# Add current directory to path for proper imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

try:
    from assistant_core.computer_vision_ai import ComputerVisionMultimodalAI, AnalysisType, ContentType
    from PIL import Image, ImageDraw

    async def test_computer_vision():
        """Test the computer vision AI system"""
        print("🔍 Testing Computer Vision AI System...")

        # Initialize the system
        cv_ai = ComputerVisionMultimodalAI()
        await cv_ai.initialize()

        print("✅ Computer Vision AI System initialized")

        # Create a test image
        print("\n🖼️ Creating test image...")
        test_image = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(test_image)

        # Add some text
        draw.text((50, 50), "SAMPLE DOCUMENT", fill='black')
        draw.text((50, 80), "Date: 2024-01-01", fill='black')
        draw.text((50, 110), "Amount: $123.45", fill='black')

        # Add a rectangle
        draw.rectangle([200, 100, 300, 200], outline='red', width=3)

        print("✅ Test image created")

        # Test text extraction
        print("\n📝 Testing text extraction...")
        try:
            text_result = await cv_ai._extract_text(test_image)
            print("✅ Text extraction completed:")
            print(f"   Extracted text: '{text_result.get('text', '')[:50]}...'")
            print(f"   Confidence: {text_result.get('confidence', 0):.2f}")
        except Exception as e:
            print(f"❌ Text extraction failed: {e}")

        # Test image analysis
        print("\n🔬 Testing image analysis...")
        try:
            analysis_result = await cv_ai.analyze_image(
                test_image,
                [AnalysisType.TEXT_EXTRACTION, AnalysisType.SCENE_UNDERSTANDING]
            )
            print("✅ Image analysis completed:")
            print(f"   Analysis ID: {analysis_result.analysis_id}")
            print(f"   Confidence: {analysis_result.confidence_score:.2f}")
            print(f"   Processing time: {analysis_result.processing_time:.2f}s")
        except Exception as e:
            print(f"❌ Image analysis failed: {e}")

        # Test document analysis
        print("\n📄 Testing document analysis...")
        try:
            doc_result = await cv_ai.analyze_document(test_image)
            print("✅ Document analysis completed:")
            print(f"   Document type: {doc_result.results.get('document_type', 'unknown')}")
            print(f"   Analysis ID: {doc_result.analysis_id}")
        except Exception as e:
            print(f"❌ Document analysis failed: {e}")

        # Test visual QA
        print("\n❓ Testing visual question answering...")
        try:
            qa_result = await cv_ai.visual_question_answering(test_image, "What do you see in this image?")
            print("✅ Visual QA completed:")
            print(f"   Answer: {qa_result.get('answer', 'N/A')}")
        except Exception as e:
            print(f"❌ Visual QA failed: {e}")

        # Test system status
        print("\n📊 Testing system status...")
        status = await cv_ai.get_system_status()
        print("✅ System status retrieved:")
        print(f"   Models loaded: {status.get('models_loaded', 0)}")
        print(f"   Cache entries: {status.get('cache_entries', 0)}")
        print(f"   GPU available: {status.get('gpu_available', False)}")

        # Shutdown
        await cv_ai.shutdown()
        print("\n🛑 Computer Vision AI System shutdown complete")

        print("\n🎉 All computer vision tests completed!")

    if __name__ == "__main__":
        asyncio.run(test_computer_vision())

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("The computer vision AI system requires these dependencies:")
    print("  - Pillow (PIL)")
    print("  - opencv-python")
    print("  - pytesseract")
    print("  - torch")
    print("  - transformers")
    print("  - sentence-transformers")
    print("These should be installed via: pip install Pillow opencv-python pytesseract torch transformers sentence-transformers")
