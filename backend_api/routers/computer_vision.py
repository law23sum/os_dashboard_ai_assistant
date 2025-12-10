"""Computer Vision router that mirrors Tkinter tab actions for shared UI."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter()


class CVBase(BaseModel):
    """Allow model_* field names without warnings."""

    model_config = ConfigDict(protected_namespaces=())


class ImagePayload(CVBase):
    filename: str
    content_type: Optional[str] = None
    data_url: Optional[str] = None


class AnalysisResult(CVBase):
    summary: str
    labels: List[str]
    confidence: float
    metadata: Dict[str, Any]
    highlights: List[str]
    generated_at: str


class OCRResult(CVBase):
    text: str
    word_count: int
    language: str
    sections: List[str]


class Detection(CVBase):
    label: str
    confidence: float
    bounding_box: Dict[str, int]


class DetectionResult(CVBase):
    objects: List[Detection]
    detected_at: str
    model_version: str


class VisionStats(CVBase):
    documents_processed_today: int
    avg_latency_ms: int
    last_model_update: str
    active_models: List[str]


SAMPLE_LABELS = [
    "architecture",
    "whiteboard",
    "diagram",
    "document",
    "meeting-notes",
]


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


@router.get("/stats", response_model=VisionStats)
async def get_stats() -> VisionStats:
    """Return synthetic stats for the UI header."""
    return VisionStats(
        documents_processed_today=42,
        avg_latency_ms=480,
        last_model_update="2025-01-12T09:30:00Z",
        active_models=["clip-vit-base", "yolo-v8-small", "tesseract-ocr"],
    )


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_image(payload: ImagePayload) -> AnalysisResult:
    """Analyze an uploaded/sampled image."""
    labels = SAMPLE_LABELS[:3]
    summary = (
        f"Detected {', '.join(labels)} in {payload.filename or 'uploaded asset'}. "
        "Layout suggests a planning diagram with handwritten annotations."
    )
    highlights = [
        "Identified two layers of architecture sketches",
        "Found annotated region referencing 'Edge Nodes'",
        "Detected light mode UI mockups near the bottom third",
    ]
    metadata = {
        "filename": payload.filename,
        "content_type": payload.content_type,
        "hash_preview": hash(payload.data_url or payload.filename or "cv") & 0xFFFF,
    }
    return AnalysisResult(
        summary=summary,
        labels=labels,
        confidence=0.87,
        metadata=metadata,
        highlights=highlights,
        generated_at=_timestamp(),
    )


@router.post("/ocr", response_model=OCRResult)
async def run_ocr(payload: ImagePayload) -> OCRResult:
    """Return pseudo OCR output."""
    lines = [
        "Edge cluster telemetry → security pipeline",
        "Human-in-loop review before auto deployment",
        "Sync narrative to Writer Workspace",
    ]
    text = "\n".join(lines)
    return OCRResult(
        text=text,
        word_count=len(text.split()),
        language="en",
        sections=lines,
    )


@router.post("/detect", response_model=DetectionResult)
async def detect_objects(payload: ImagePayload) -> DetectionResult:
    """Return pseudo object detection boxes."""
    detections = [
        Detection(label="whiteboard", confidence=0.96, bounding_box={"x": 48, "y": 32, "w": 620, "h": 380}),
        Detection(label="diagram-node", confidence=0.82, bounding_box={"x": 160, "y": 140, "w": 220, "h": 140}),
        Detection(label="note", confidence=0.78, bounding_box={"x": 420, "y": 210, "w": 180, "h": 120}),
    ]
    return DetectionResult(
        objects=detections,
        detected_at=_timestamp(),
        model_version="yolo-v8-small",
    )
