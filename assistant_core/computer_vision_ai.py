"""
Computer Vision and Multimodal AI System

Advanced AI capabilities for image processing, document analysis, and multimodal understanding
"""

import asyncio
import json
import uuid
import base64
import io
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

# Computer vision libraries
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cv2
import pytesseract

# ML Libraries
import torch
import torchvision.transforms as transforms
from transformers import (
    BlipProcessor, BlipForConditionalGeneration,
    CLIPProcessor, CLIPModel,
    pipeline
)
from sentence_transformers import SentenceTransformer

from config.logging_config import setup_logger


class AnalysisType(Enum):
    OBJECT_DETECTION = "object_detection"
    TEXT_EXTRACTION = "text_extraction"
    DOCUMENT_ANALYSIS = "document_analysis"
    IMAGE_CAPTIONING = "image_captioning"
    VISUAL_QA = "visual_qa"
    SCENE_UNDERSTANDING = "scene_understanding"
    FACE_DETECTION = "face_detection"
    EMOTION_RECOGNITION = "emotion_recognition"
    CONTENT_MODERATION = "content_moderation"
    SIMILARITY_SEARCH = "similarity_search"


class DocumentType(Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    FORM = "form"
    PRESENTATION = "presentation"
    REPORT = "report"
    ID_DOCUMENT = "id_document"
    GENERAL = "general"


class ContentType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    DIAGRAM = "diagram"
    CHART = "chart"


@dataclass
class BoundingBox:
    """Bounding box coordinates"""
    x: float
    y: float
    width: float
    height: float
    confidence: float = 1.0


@dataclass
class DetectedObject:
    """Detected object information"""
    object_id: str
    label: str
    confidence: float
    bounding_box: BoundingBox
    attributes: Dict[str, Any]


@dataclass
class ExtractedText:
    """Extracted text information"""
    text: str
    confidence: float
    bounding_box: BoundingBox
    language: str = "en"
    font_size: Optional[float] = None


@dataclass
class DocumentField:
    """Extracted document field"""
    field_name: str
    field_value: str
    confidence: float
    field_type: str
    bounding_box: Optional[BoundingBox] = None


@dataclass
class AnalysisResult:
    """Computer vision analysis result"""
    analysis_id: str
    analysis_type: AnalysisType
    content_type: ContentType
    results: Dict[str, Any]
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any]
    created_at: datetime


class ComputerVisionMultimodalAI:
    """Advanced computer vision and multimodal AI system"""

    def __init__(self):
        self.logger = setup_logger("ComputerVisionAI")

        # Model storage
        self.models = {}
        self.processors = {}

        # Analysis cache
        self.analysis_cache: Dict[str, AnalysisResult] = {}
        self.image_embeddings: Dict[str, np.ndarray] = {}

        # Configuration
        self.config = {
            "max_image_size": (1920, 1080),
            "supported_formats": ["jpg", "jpeg", "png", "bmp", "tiff", "pdf"],
            "cache_enabled": True,
            "cache_ttl_hours": 24,
            "batch_processing": True,
            "gpu_enabled": torch.cuda.is_available(),
            "confidence_threshold": 0.7,
            "max_objects_per_image": 50
        }

        # Document templates
        self.document_templates = {
            DocumentType.INVOICE: {
                "fields": ["invoice_number", "date", "total_amount", "vendor", "items"],
                "patterns": {
                    "invoice_number": r"(?:invoice|inv)[\s#:]*(\w+)",
                    "total_amount": r"(?:total|amount)[\s:$]*(\d+\.?\d*)",
                    "date": r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
                }
            },
            DocumentType.RECEIPT: {
                "fields": ["merchant", "date", "total", "items", "payment_method"],
                "patterns": {
                    "total": r"(?:total|amount)[\s:$]*(\d+\.?\d*)",
                    "date": r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
                }
            }
        }

    async def initialize(self):
        """Initialize computer vision system"""
        await self._load_models()

        # Start background tasks
        asyncio.create_task(self._cache_cleanup_loop())
        asyncio.create_task(self._model_optimization_loop())

        self.logger.info("Computer Vision and Multimodal AI System initialized")

    async def _load_models(self):
        """Load computer vision models"""
        try:
            device = "cuda" if self.config["gpu_enabled"] else "cpu"

            # Image captioning model
            try:
                self.processors['blip'] = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.models['blip'] = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
            except Exception as e:
                self.logger.warning(f"BLIP model loading failed: {e}")

            # CLIP for image-text understanding
            try:
                self.processors['clip'] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                self.models['clip'] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
            except Exception as e:
                self.logger.warning(f"CLIP model loading failed: {e}")

            # Sentence transformer for embeddings
            try:
                self.models['sentence_transformer'] = SentenceTransformer('clip-ViT-B-32')
            except Exception as e:
                self.logger.warning(f"Sentence transformer loading failed: {e}")

            # Object detection pipeline
            try:
                self.models['object_detection'] = pipeline(
                    "object-detection",
                    model="facebook/detr-resnet-50",
                    device=0 if self.config["gpu_enabled"] else -1
                )
            except Exception as e:
                self.logger.warning(f"Object detection model loading failed: {e}")

            self.logger.info("Computer vision models loaded successfully")

        except Exception as e:
            self.logger.error(f"Model loading failed: {e}")
            # Initialize fallback models
            self.models = {}
            self.processors = {}

    # Core Analysis Methods

    async def analyze_image(self, image_data: Union[str, bytes, Image.Image],
                          analysis_types: List[AnalysisType],
                          options: Dict[str, Any] = None) -> AnalysisResult:
        """Comprehensive image analysis"""
        try:
            start_time = datetime.now()
            analysis_id = str(uuid.uuid4())

            # Process image
            image = await self._process_image_input(image_data)
            if image is None:
                raise Exception("Invalid image data")

            # Check cache
            cache_key = self._generate_cache_key(image, analysis_types)
            if self.config["cache_enabled"] and cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    return cached_result

            # Perform analyses
            results = {}
            overall_confidence = 0.0

            for analysis_type in analysis_types:
                try:
                    if analysis_type == AnalysisType.OBJECT_DETECTION:
                        results["objects"] = await self._detect_objects(image, options)
                    elif analysis_type == AnalysisType.TEXT_EXTRACTION:
                        results["text"] = await self._extract_text(image, options)
                    elif analysis_type == AnalysisType.IMAGE_CAPTIONING:
                        results["caption"] = await self._generate_caption(image, options)
                    elif analysis_type == AnalysisType.SCENE_UNDERSTANDING:
                        results["scene"] = await self._understand_scene(image, options)
                    elif analysis_type == AnalysisType.FACE_DETECTION:
                        results["faces"] = await self._detect_faces(image, options)
                    elif analysis_type == AnalysisType.EMOTION_RECOGNITION:
                        results["emotions"] = await self._recognize_emotions(image, options)
                    elif analysis_type == AnalysisType.CONTENT_MODERATION:
                        results["moderation"] = await self._moderate_content(image, options)
                    elif analysis_type == AnalysisType.SIMILARITY_SEARCH:
                        results["similarity"] = await self._compute_similarity(image, options)

                except Exception as e:
                    self.logger.warning(f"Analysis {analysis_type.value} failed: {e}")
                    results[analysis_type.value] = {"error": str(e)}

            # Calculate overall confidence
            confidences = []
            for result in results.values():
                if isinstance(result, dict) and "confidence" in result:
                    confidences.append(result["confidence"])
                elif isinstance(result, list):
                    for item in result:
                        if isinstance(item, dict) and "confidence" in item:
                            confidences.append(item["confidence"])

            overall_confidence = np.mean(confidences) if confidences else 0.5

            # Create result
            processing_time = (datetime.now() - start_time).total_seconds()

            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                analysis_type=analysis_types[0] if len(analysis_types) == 1 else AnalysisType.SCENE_UNDERSTANDING,
                content_type=ContentType.IMAGE,
                results=results,
                confidence_score=overall_confidence,
                processing_time=processing_time,
                metadata={
                    "image_size": image.size,
                    "analysis_types": [t.value for t in analysis_types],
                    "options": options or {}
                },
                created_at=start_time
            )

            # Cache result
            if self.config["cache_enabled"]:
                self.analysis_cache[cache_key] = analysis_result

            self.logger.info(f"Image analysis completed: {analysis_id} in {processing_time:.2f}s")
            return analysis_result

        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            raise

    async def analyze_document(self, document_data: Union[str, bytes, Image.Image],
                             document_type: DocumentType = DocumentType.GENERAL,
                             extract_fields: List[str] = None) -> AnalysisResult:
        """Comprehensive document analysis"""
        try:
            start_time = datetime.now()
            analysis_id = str(uuid.uuid4())

            # Process document
            image = await self._process_image_input(document_data)
            if image is None:
                raise Exception("Invalid document data")

            # Extract text with OCR
            extracted_text = await self._extract_text(image, {"detailed": True})

            # Analyze document structure
            document_structure = await self._analyze_document_structure(image, extracted_text)

            # Extract specific fields
            extracted_fields = {}
            if extract_fields or document_type != DocumentType.GENERAL:
                extracted_fields = await self._extract_document_fields(
                    image, extracted_text, document_type, extract_fields
                )

            # Classify document type if not specified
            if document_type == DocumentType.GENERAL:
                document_type = await self._classify_document_type(image, extracted_text)

            # Generate document summary
            summary = await self._generate_document_summary(extracted_text, extracted_fields)

            results = {
                "document_type": document_type.value,
                "extracted_text": extracted_text,
                "document_structure": document_structure,
                "extracted_fields": extracted_fields,
                "summary": summary,
                "confidence": 0.8  # Placeholder confidence
            }

            processing_time = (datetime.now() - start_time).total_seconds()

            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                analysis_type=AnalysisType.DOCUMENT_ANALYSIS,
                content_type=ContentType.DOCUMENT,
                results=results,
                confidence_score=0.8,
                processing_time=processing_time,
                metadata={
                    "document_type": document_type.value,
                    "image_size": image.size,
                    "text_length": len(extracted_text.get("text", ""))
                },
                created_at=start_time
            )

            self.logger.info(f"Document analysis completed: {analysis_id} in {processing_time:.2f}s")
            return analysis_result

        except Exception as e:
            self.logger.error(f"Document analysis failed: {e}")
            raise

    async def visual_question_answering(self, image_data: Union[str, bytes, Image.Image],
                                      question: str) -> Dict[str, Any]:
        """Answer questions about images"""
        try:
            image = await self._process_image_input(image_data)
            if image is None:
                raise Exception("Invalid image data")

            # Generate image caption first
            caption_result = await self._generate_caption(image)
            caption = caption_result.get("caption", "")

            # Extract text from image
            text_result = await self._extract_text(image)
            extracted_text = text_result.get("text", "")

            # Detect objects
            objects_result = await self._detect_objects(image)
            objects = [obj.get("label", "") for obj in objects_result.get("objects", [])]

            # Combine all information
            context = f"Image description: {caption}\n"
            if extracted_text:
                context += f"Text in image: {extracted_text}\n"
            if objects:
                context += f"Objects detected: {', '.join(objects)}\n"

            # Simple question answering (in production, use a proper VQA model)
            answer = await self._answer_visual_question(question, context, image)

            return {
                "question": question,
                "answer": answer,
                "context": context,
                "confidence": 0.7
            }

        except Exception as e:
            self.logger.error(f"Visual QA failed: {e}")
            return {"error": str(e)}

    # Individual Analysis Methods

    async def _detect_objects(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect objects in image"""
        try:
            if 'object_detection' not in self.models:
                return {"error": "Object detection model not available"}

            # Run object detection
            results = self.models['object_detection'](image)

            detected_objects = []
            for result in results:
                if result['score'] >= self.config["confidence_threshold"]:
                    bbox = result['box']
                    detected_object = DetectedObject(
                        object_id=str(uuid.uuid4()),
                        label=result['label'],
                        confidence=result['score'],
                        bounding_box=BoundingBox(
                            x=bbox['xmin'],
                            y=bbox['ymin'],
                            width=bbox['xmax'] - bbox['xmin'],
                            height=bbox['ymax'] - bbox['ymin'],
                            confidence=result['score']
                        ),
                        attributes={}
                    )
                    detected_objects.append(asdict(detected_object))

            return {
                "objects": detected_objects,
                "count": len(detected_objects),
                "confidence": np.mean([obj["confidence"] for obj in detected_objects]) if detected_objects else 0.0
            }

        except Exception as e:
            self.logger.error(f"Object detection failed: {e}")
            return {"error": str(e)}

    async def _extract_text(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocess image for better OCR
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Apply image enhancement
            enhanced = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)

            # Use Tesseract for OCR
            detailed = options.get("detailed", False) if options else False

            if detailed:
                # Get detailed information including bounding boxes
                data = pytesseract.image_to_data(enhanced, output_type=pytesseract.Output.DICT)

                extracted_texts = []
                full_text = ""

                for i in range(len(data['text'])):
                    if int(data['conf'][i]) > 30:  # Confidence threshold
                        text = data['text'][i].strip()
                        if text:
                            extracted_text = ExtractedText(
                                text=text,
                                confidence=int(data['conf'][i]) / 100.0,
                                bounding_box=BoundingBox(
                                    x=data['left'][i],
                                    y=data['top'][i],
                                    width=data['width'][i],
                                    height=data['height'][i],
                                    confidence=int(data['conf'][i]) / 100.0
                                )
                            )
                            extracted_texts.append(asdict(extracted_text))
                            full_text += text + " "

                return {
                    "text": full_text.strip(),
                    "detailed_text": extracted_texts,
                    "confidence": np.mean([t["confidence"] for t in extracted_texts]) if extracted_texts else 0.0
                }
            else:
                # Simple text extraction
                text = pytesseract.image_to_string(enhanced)
                return {
                    "text": text.strip(),
                    "confidence": 0.8  # Placeholder confidence
                }

        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return {"error": str(e)}

    async def _generate_caption(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate image caption"""
        try:
            if 'blip' not in self.models:
                return {"error": "Image captioning model not available"}

            # Process image
            inputs = self.processors['blip'](image, return_tensors="pt")

            # Generate caption
            device = next(self.models['blip'].parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                out = self.models['blip'].generate(**inputs, max_length=50)

            caption = self.processors['blip'].decode(out[0], skip_special_tokens=True)

            return {
                "caption": caption,
                "confidence": 0.8  # Placeholder confidence
            }

        except Exception as e:
            self.logger.error(f"Caption generation failed: {e}")
            return {"error": str(e)}

    async def _understand_scene(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Understand scene context"""
        try:
            # Combine multiple analyses for scene understanding
            caption_result = await self._generate_caption(image)
            objects_result = await self._detect_objects(image)

            # Analyze scene composition
            scene_analysis = {
                "description": caption_result.get("caption", ""),
                "objects": [obj["label"] for obj in objects_result.get("objects", [])],
                "object_count": objects_result.get("count", 0),
                "scene_type": self._classify_scene_type(caption_result.get("caption", "")),
                "complexity": self._assess_scene_complexity(objects_result.get("objects", [])),
                "confidence": 0.7
            }

            return scene_analysis

        except Exception as e:
            self.logger.error(f"Scene understanding failed: {e}")
            return {"error": str(e)}

    async def _detect_faces(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect faces in image"""
        try:
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            detected_faces = []
            for (x, y, w, h) in faces:
                face_data = {
                    "face_id": str(uuid.uuid4()),
                    "bounding_box": {
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                        "confidence": 0.8
                    },
                    "confidence": 0.8
                }
                detected_faces.append(face_data)

            return {
                "faces": detected_faces,
                "count": len(detected_faces),
                "confidence": 0.8
            }

        except Exception as e:
            self.logger.error(f"Face detection failed: {e}")
            return {"error": str(e)}

    async def _recognize_emotions(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Recognize emotions in image"""
        try:
            # First detect faces
            faces_result = await self._detect_faces(image)
            faces = faces_result.get("faces", [])

            if not faces:
                return {"emotions": [], "confidence": 0.0}

            emotions_data = []

            for face in faces:
                # Extract face region
                bbox = face["bounding_box"]
                face_region = image.crop((
                    bbox["x"],
                    bbox["y"],
                    bbox["x"] + bbox["width"],
                    bbox["y"] + bbox["height"]
                ))

                # Simulate emotion recognition (in production, use proper emotion model)
                emotions = {
                    "happy": np.random.uniform(0.1, 0.9),
                    "sad": np.random.uniform(0.0, 0.3),
                    "angry": np.random.uniform(0.0, 0.2),
                    "surprised": np.random.uniform(0.0, 0.4),
                    "neutral": np.random.uniform(0.2, 0.8)
                }

                # Normalize emotions
                total = sum(emotions.values())
                emotions = {k: v/total for k, v in emotions.items()}

                dominant_emotion = max(emotions.items(), key=lambda x: x[1])

                emotion_data = {
                    "face_id": face["face_id"],
                    "emotions": emotions,
                    "dominant_emotion": dominant_emotion[0],
                    "confidence": dominant_emotion[1]
                }
                emotions_data.append(emotion_data)

            return {
                "emotions": emotions_data,
                "confidence": np.mean([e["confidence"] for e in emotions_data])
            }

        except Exception as e:
            self.logger.error(f"Emotion recognition failed: {e}")
            return {"error": str(e)}

    async def _moderate_content(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Moderate image content"""
        try:
            # Simulate content moderation
            moderation_result = {
                "safe": True,
                "categories": {
                    "adult": 0.1,
                    "violence": 0.05,
                    "hate": 0.02,
                    "spam": 0.03
                },
                "confidence": 0.9
            }

            # Check if any category exceeds threshold
            threshold = 0.5
            for category, score in moderation_result["categories"].items():
                if score > threshold:
                    moderation_result["safe"] = False
                    break

            return moderation_result

        except Exception as e:
            self.logger.error(f"Content moderation failed: {e}")
            return {"error": str(e)}

    async def _compute_similarity(self, image: Image.Image, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compute image similarity embeddings"""
        try:
            if 'sentence_transformer' not in self.models:
                return {"error": "Similarity model not available"}

            # Generate image embedding
            embedding = self.models['sentence_transformer'].encode(image)

            # Store embedding for future similarity searches
            image_id = str(uuid.uuid4())
            self.image_embeddings[image_id] = embedding

            # Find similar images if requested
            similar_images = []
            if options and options.get("find_similar", False):
                similarities = {}
                for stored_id, stored_embedding in self.image_embeddings.items():
                    if stored_id != image_id:
                        similarity = np.dot(embedding, stored_embedding) / (
                            np.linalg.norm(embedding) * np.linalg.norm(stored_embedding)
                        )
                        similarities[stored_id] = similarity

                # Get top similar images
                top_similar = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
                similar_images = [{"image_id": img_id, "similarity": sim} for img_id, sim in top_similar]

            return {
                "image_id": image_id,
                "embedding_size": len(embedding),
                "similar_images": similar_images,
                "confidence": 1.0
            }

        except Exception as e:
            self.logger.error(f"Similarity computation failed: {e}")
            return {"error": str(e)}

    # Document Analysis Methods

    async def _analyze_document_structure(self, image: Image.Image,
                                        extracted_text: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document structure"""
        try:
            structure = {
                "layout": "unknown",
                "sections": [],
                "tables": [],
                "headers": [],
                "footers": []
            }

            # Analyze text layout if detailed text is available
            if "detailed_text" in extracted_text:
                detailed_texts = extracted_text["detailed_text"]

                # Group text by vertical position to identify sections
                y_positions = [t["bounding_box"]["y"] for t in detailed_texts]
                if y_positions:
                    # Simple section detection based on y-position gaps
                    sorted_texts = sorted(detailed_texts, key=lambda x: x["bounding_box"]["y"])

                    sections = []
                    current_section = []
                    last_y = 0

                    for text_item in sorted_texts:
                        y = text_item["bounding_box"]["y"]
                        if y - last_y > 50:  # Gap threshold
                            if current_section:
                                sections.append(current_section)
                                current_section = []

                        current_section.append(text_item)
                        last_y = y

                    if current_section:
                        sections.append(current_section)

                    structure["sections"] = [
                        {
                            "section_id": i,
                            "text_count": len(section),
                            "text": " ".join([t["text"] for t in section])
                        }
                        for i, section in enumerate(sections)

                    ]

            return structure

        except Exception as e:
            self.logger.error(f"Document structure analysis failed: {e}")
            return {"error": str(e)}

    async def _extract_document_fields(self, image: Image.Image,
                                     extracted_text: Dict[str, Any],
                                     document_type: DocumentType,
                                     extract_fields: List[str] = None) -> Dict[str, Any]:
        """Extract specific fields from document"""
        try:
            extracted_fields = {}

            # Get document template
            template = self.document_templates.get(document_type, {})
            patterns = template.get("patterns", {})

            # Use extracted text
            text = extracted_text.get("text", "")

            # Extract fields using patterns
            import re

            for field_name, pattern in patterns.items():
                if extract_fields and field_name not in extract_fields:
                    continue

                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    extracted_fields[field_name] = {
                        "value": matches[0] if len(matches) == 1 else matches,
                        "confidence": 0.8,
                        "pattern_used": pattern
                    }

            # Additional field extraction for specific document types
            if document_type == DocumentType.INVOICE:
                # Extract line items
                lines = text.split('\n')
                items = []
                for line in lines:
                    # Simple item detection (description + amount)
                    if re.search(r'\$?\d+\.?\d*', line) and len(line.split()) > 2:
                        items.append(line.strip())

                if items:
                    extracted_fields["items"] = {
                        "value": items,
                        "confidence": 0.6
                    }

            return extracted_fields

        except Exception as e:
            self.logger.error(f"Document field extraction failed: {e}")
            return {"error": str(e)}

    async def _classify_document_type(self, image: Image.Image,
                                    extracted_text: Dict[str, Any]) -> DocumentType:
        """Classify document type"""
        try:
            text = extracted_text.get("text", "").lower()

            # Simple keyword-based classification
            if any(word in text for word in ["invoice", "bill", "payment due"]):
                return DocumentType.INVOICE
            elif any(word in text for word in ["receipt", "purchase", "transaction"]):
                return DocumentType.RECEIPT
            elif any(word in text for word in ["contract", "agreement", "terms"]):
                return DocumentType.CONTRACT
            elif any(word in text for word in ["form", "application", "questionnaire"]):
                return DocumentType.FORM
            elif any(word in text for word in ["report", "analysis", "summary"]):
                return DocumentType.REPORT
            else:
                return DocumentType.GENERAL

        except Exception as e:
            self.logger.error(f"Document type classification failed: {e}")
            return DocumentType.GENERAL

    async def _generate_document_summary(self, extracted_text: Dict[str, Any],
                                       extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Generate document summary"""
        try:
            text = extracted_text.get("text", "")

            # Simple summary generation
            sentences = text.split('.')
            key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:3]

            summary = {
                "key_points": key_sentences,
                "word_count": len(text.split()),
                "character_count": len(text),
                "extracted_fields_count": len(extracted_fields),
                "confidence": 0.7
            }

            # Add field-based insights
            if extracted_fields:
                insights = []
                for field_name, field_data in extracted_fields.items():
                    insights.append(f"{field_name}: {field_data.get('value', 'N/A')}")
                summary["field_insights"] = insights

            return summary

        except Exception as e:
            self.logger.error(f"Document summary generation failed: {e}")
            return {"error": str(e)}

    # Utility Methods

    async def _process_image_input(self, image_data: Union[str, bytes, Image.Image]) -> Optional[Image.Image]:
        """Process various image input formats"""
        try:
            if isinstance(image_data, Image.Image):
                image = image_data
            elif isinstance(image_data, str):
                # Assume base64 encoded image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            elif isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            else:
                return None

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if too large
            max_size = self.config["max_image_size"]
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

            return image

        except Exception as e:
            self.logger.error(f"Image processing failed: {e}")
            return None

    def _generate_cache_key(self, image: Image.Image, analysis_types: List[AnalysisType]) -> str:
        """Generate cache key for analysis"""
        try:
            # Simple hash based on image size and analysis types
            import hashlib

            key_data = f"{image.size}_{sorted([t.value for t in analysis_types])}"
            return hashlib.md5(key_data.encode()).hexdigest()

        except Exception:
            return str(uuid.uuid4())

    def _is_cache_valid(self, cached_result: AnalysisResult) -> bool:
        """Check if cached result is still valid"""
        try:
            ttl_hours = self.config["cache_ttl_hours"]
            expiry_time = cached_result.created_at + timedelta(hours=ttl_hours)
            return datetime.now() < expiry_time
        except Exception:
            return False

    def _classify_scene_type(self, caption: str) -> str:
        """Classify scene type from caption"""
        caption_lower = caption.lower()

        if any(word in caption_lower for word in ["indoor", "room", "kitchen", "office"]):
            return "indoor"
        elif any(word in caption_lower for word in ["outdoor", "street", "park", "nature"]):
            return "outdoor"
        elif any(word in caption_lower for word in ["person", "people", "man", "woman"]):
            return "people"
        elif any(word in caption_lower for word in ["car", "vehicle", "transport"]):
            return "transportation"
        else:
            return "general"

    def _assess_scene_complexity(self, objects: List[Dict[str, Any]]) -> str:
        """Assess scene complexity based on objects"""
        object_count = len(objects)

        if object_count <= 2:
            return "simple"
        elif object_count <= 5:
            return "moderate"
        else:
            return "complex"

    async def _answer_visual_question(self, question: str, context: str, image: Image.Image) -> str:
        """Answer visual question using context"""
        try:
            question_lower = question.lower()
            context_lower = context.lower()

            # Simple rule-based QA (in production, use a proper VQA model)
            if "how many" in question_lower:
                # Count objects
                import re
                numbers = re.findall(r'\d+', context)
                if numbers:
                    return f"I can see {numbers[0]} items in the image."
                else:
                    return "I cannot determine the exact count from the image."

            elif "what color" in question_lower:
                # Color detection (simplified)
                return "I can see various colors in the image, but I need more specific analysis to determine exact colors."

            elif "where" in question_lower:
                # Location questions
                return "Based on the image analysis, I can see the objects and their general positions."

            elif "what is" in question_lower or "what are" in question_lower:
                # Object identification
                if "objects detected:" in context_lower:
                    objects_part = context_lower.split("objects detected:")[1].split("\n")[0]
                    return f"I can see: {objects_part}"
                else:
                    return "I can analyze the image content but need more specific information."

            else:
                # General response
                return "Based on my analysis of the image, I can provide information about the objects, text, and overall scene."

        except Exception as e:
            self.logger.error(f"Visual QA failed: {e}")
            return "I'm unable to answer that question about the image."

    # Batch Processing

    async def batch_analyze_images(self, image_list: List[Dict[str, Any]]) -> List[AnalysisResult]:
        """Batch process multiple images"""
        try:
            if not self.config["batch_processing"]:
                # Process sequentially
                results = []
                for image_data in image_list:
                    result = await self.analyze_image(
                        image_data["data"],
                        image_data["analysis_types"],
                        image_data.get("options")
                    )
                    results.append(result)
                return results

            # Process in parallel
            tasks = []
            for image_data in image_list:
                task = asyncio.create_task(
                    self.analyze_image(
                        image_data["data"],
                        image_data["analysis_types"],
                        image_data.get("options")
                    )
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch processing failed for image {i}: {result}")
                    # Create error result
                    error_result = AnalysisResult(
                        analysis_id=str(uuid.uuid4()),
                        analysis_type=AnalysisType.SCENE_UNDERSTANDING,
                        content_type=ContentType.IMAGE,
                        results={"error": str(result)},
                        confidence_score=0.0,
                        processing_time=0.0,
                        metadata={"batch_index": i},
                        created_at=datetime.now()
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)

            return processed_results

        except Exception as e:
            self.logger.error(f"Batch image analysis failed: {e}")
            return []

    # Background Tasks

    async def _cache_cleanup_loop(self):
        """Clean up expired cache entries"""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = []

                for cache_key, result in self.analysis_cache.items():
                    if not self._is_cache_valid(result):
                        expired_keys.append(cache_key)

                for key in expired_keys:
                    del self.analysis_cache[key]

                if expired_keys:
                    self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                self.logger.error(f"Cache cleanup failed: {e}")
                await asyncio.sleep(1800)

    async def _model_optimization_loop(self):
        """Optimize model performance"""
        while True:
            try:
                # Model optimization logic (e.g., memory cleanup, model switching)
                if self.config["gpu_enabled"] and torch.cuda.is_available():
                    torch.cuda.empty_cache()

                await asyncio.sleep(1800)  # Run every 30 minutes

            except Exception as e:
                self.logger.error(f"Model optimization failed: {e}")
                await asyncio.sleep(900)

    # API Methods

    async def get_analysis_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get analysis history"""
        try:
            # Sort by creation time
            sorted_results = sorted(
                self.analysis_cache.values(),
                key=lambda x: x.created_at,
                reverse=True
            )

            # Convert to dict format
            history = []
            for result in sorted_results[:limit]:
                history.append({
                    "analysis_id": result.analysis_id,
                    "analysis_type": result.analysis_type.value,
                    "content_type": result.content_type.value,
                    "confidence_score": result.confidence_score,
                    "processing_time": result.processing_time,
                    "created_at": result.created_at.isoformat()
                })

            return history

        except Exception as e:
            self.logger.error(f"Analysis history retrieval failed: {e}")
            return []

    async def get_system_status(self) -> Dict[str, Any]:
        """Get computer vision system status"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "models_loaded": len(self.models),
                "processors_loaded": len(self.processors),
                "cache_entries": len(self.analysis_cache),
                "image_embeddings": len(self.image_embeddings),
                "gpu_available": torch.cuda.is_available(),
                "gpu_enabled": self.config["gpu_enabled"],
                "supported_formats": self.config["supported_formats"],
                "max_image_size": self.config["max_image_size"],
                "confidence_threshold": self.config["confidence_threshold"]
            }

        except Exception as e:
            self.logger.error(f"System status generation failed: {e}")
            return {"error": str(e)}

    async def shutdown(self):
        """Shutdown computer vision system"""
        # Clear cache
        self.analysis_cache.clear()
        self.image_embeddings.clear()

        # Clear GPU memory
        if self.config["gpu_enabled"] and torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.logger.info("Computer Vision and Multimodal AI System shutdown complete")
