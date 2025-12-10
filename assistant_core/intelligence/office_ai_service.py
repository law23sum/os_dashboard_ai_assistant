"""Office AI processing helpers inspired by the AI Office Agent architecture guide."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd

from assistant_core.content.generators import (
    ContentConfig,
    ExcelDashboardGenerator,
    PresentationGenerator,
    WordDocumentGenerator,
)
from assistant_core.integrations.office_realtime import (
    AIOfficeMessage,
    ApplicationType,
    MessageType,
)
from assistant_core.intelligence.quality_assurance import (
    AccessibilityChecker,
    ContentValidator,
    ValidationResult,
)


@dataclass
class OfficeAIResult:
    """Container for AI responses returned to the realtime router."""

    status: str
    message_type: str
    document_id: str
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "message_type": self.message_type,
            "document_id": self.document_id,
            "output_path": self.output_path,
            "metadata": self.metadata or {},
        }


class OfficeAIProcessingService:
    """Local AI processing pipeline for Office documents."""

    def __init__(
        self,
        workspace_dir: str = "./workspace",
        *,
        validator: Optional[ContentValidator] = None,
        accessibility_checker: Optional[AccessibilityChecker] = None,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.validator = validator or ContentValidator()
        self.accessibility_checker = accessibility_checker or AccessibilityChecker()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process_message(self, message: AIOfficeMessage | Dict[str, Any]) -> Dict[str, Any]:
        """Process an AIOfficeMessage or dict payload into a structured response."""
        if isinstance(message, dict):
            message = self._dict_to_message(message)

        handler_map = {
            MessageType.AI_ANALYZE_REQUEST: self._handle_analyze,
            MessageType.AI_GENERATE_REQUEST: self._handle_generate,
            MessageType.AI_SUGGEST_REQUEST: self._handle_suggest,
        }

        handler = handler_map.get(message.type)
        if not handler:
            return {
                "status": "unsupported",
                "message_type": message.type.value,
                "document_id": message.document_id or "unspecified",
                "detail": f"Operation {message.type.value} is not handled locally.",
            }

        return handler(message)

    # ------------------------------------------------------------------
    # Operation handlers
    # ------------------------------------------------------------------
    def _handle_analyze(self, message: AIOfficeMessage) -> Dict[str, Any]:
        payload = message.payload or {}
        document_type = payload.get("document_type") or message.target.value
        text = self._extract_text(payload)
        content_type = payload.get("content_type", "text")

        validation_results = self.validator.validate_content(text, content_type=content_type)
        accessibility_results: List[ValidationResult] = []
        if content_type.lower() == "html":
            accessibility_results = self.accessibility_checker.check_accessibility(text)

        analysis = {
            "document_type": document_type,
            "summary": self._summarize_text(text),
            "quality": self._serialize_validation_results(validation_results),
            "accessibility": self._serialize_validation_results(accessibility_results),
            "score": self._score_validation(validation_results + accessibility_results),
        }

        recommendations = self._build_recommendations(validation_results, accessibility_results)
        return {
            "status": "analyzed",
            "message_type": message.type.value,
            "document_id": message.document_id or "unspecified",
            "analysis": analysis,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _handle_generate(self, message: AIOfficeMessage) -> Dict[str, Any]:
        payload = message.payload or {}
        document_type = (payload.get("document_type") or message.target.value).lower()

        try:
            if document_type in ("powerpoint", "presentation", ApplicationType.POWERPOINT.value):
                meta = self._generate_presentation(payload)
            elif document_type in ("excel", ApplicationType.EXCEL.value):
                meta = self._generate_excel(payload)
            else:
                meta = self._generate_word(payload)
            status = "generated"
        except Exception as exc:  # pragma: no cover - defensive catch for optional deps
            self.logger.error("Content generation failed: %s", exc)
            meta = {"error": str(exc)}
            status = "error"

        return {
            "status": status,
            "message_type": message.type.value,
            "document_id": message.document_id or "unspecified",
            "output": meta,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def _handle_suggest(self, message: AIOfficeMessage) -> Dict[str, Any]:
        payload = message.payload or {}
        text = self._extract_text(payload)
        content_type = payload.get("content_type", "text")
        validation_results = self.validator.validate_content(text, content_type=content_type)

        suggestions = [
            {
                "title": result.rule_name.replace("_", " ").title(),
                "detail": result.message,
                "severity": result.severity,
                "passed": result.passed,
                "suggestion": result.suggestion,
            }
            for result in validation_results
        ]

        if not suggestions:
            suggestions.append(
                {
                    "title": "Content Review",
                    "detail": "No validation feedback generated.",
                    "severity": "info",
                    "passed": True,
                }
            )

        return {
            "status": "suggestions",
            "message_type": message.type.value,
            "document_id": message.document_id or "unspecified",
            "suggestions": suggestions,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # ------------------------------------------------------------------
    # Generation helpers
    # ------------------------------------------------------------------
    def _generate_presentation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        config = ContentConfig(
            title=payload.get("title", "AI Generated Presentation"),
            author=payload.get("author", "AI Assistant"),
            theme=payload.get("theme", "professional"),
        )
        generator = PresentationGenerator(config)
        sections = payload.get("sections") or payload.get("slides") or self._default_sections(payload)

        generator.add_title_slide(
            payload.get("title", "Executive Summary"),
            subtitle=payload.get("subtitle", "Automated content"),
            author=config.author,
        )
        for section in sections:
            generator.add_content_slide(
                section.get("title", "Details"),
                section.get("bullets") or section.get("content") or section.get("points", []),
                image_url=section.get("image"),
                chart_data=section.get("chart"),
            )

        output_path = self._workspace_file("presentation", "html")
        html_content = generator.generate_html(output_path)
        return {
            "output_path": str(output_path),
            "slide_count": len(generator.slides),
            "preview": html_content[:5000],
        }

    def _generate_word(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        config = ContentConfig(
            title=payload.get("title", "AI Generated Report"),
            author=payload.get("author", "AI Assistant"),
        )
        generator = WordDocumentGenerator(config)
        sections = payload.get("sections") or self._default_sections(payload)

        for idx, section in enumerate(sections, start=1):
            generator.add_heading(section.get("title", f"Section {idx}"), level=2)
            for paragraph in section.get("paragraphs") or section.get("bullets") or []:
                generator.add_paragraph(paragraph)
            if section.get("table"):
                table = section["table"]
                generator.add_table(table.get("rows", []), headers=table.get("headers"))

        output_path = self._workspace_file("report", "docx")
        success = generator.generate_docx(str(output_path))
        return {
            "output_path": str(output_path) if success else None,
            "section_count": len(sections),
            "success": success,
        }

    def _generate_excel(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        config = ContentConfig(
            title=payload.get("title", "AI Dashboard"),
            author=payload.get("author", "AI Assistant"),
        )
        generator = ExcelDashboardGenerator(config)

        sheets = payload.get("sheets") or self._default_sheet_payload(payload)
        for sheet in sheets:
            data = pd.DataFrame(sheet.get("data", []))
            if data.empty:
                continue
            worksheet_id = generator.add_worksheet(sheet.get("name", "Sheet"), data)
            for chart in sheet.get("charts", []):
                generator.add_chart(sheet.get("name", "Sheet"), chart.get("type", "bar"), chart.get("data_range", "A1:B5"), chart)
            for fmt in sheet.get("conditional_formats", []):
                generator.add_conditional_formatting(sheet.get("name", "Sheet"), fmt.get("range", "A2:A10"), fmt.get("type", "color_scale"), fmt.get("config", {}))

        output_path = self._workspace_file("dashboard", "xlsx")
        success = generator.generate_excel(str(output_path))
        return {
            "output_path": str(output_path) if success else None,
            "sheet_count": len(generator.workbook_data),
            "success": success,
        }

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _dict_to_message(self, payload: Dict[str, Any]) -> AIOfficeMessage:
        return AIOfficeMessage(
            type=payload.get("type", MessageType.AI_ANALYZE_REQUEST),
            source=payload.get("source", ApplicationType.WEB_DASHBOARD),
            target=payload.get("target", ApplicationType.WEB_DASHBOARD),
            payload=payload.get("payload", {}),
            session_id=payload.get("session_id", "local"),
            document_id=payload.get("document_id"),
        )

    def _extract_text(self, payload: Dict[str, Any]) -> str:
        text = payload.get("text") or payload.get("content") or payload.get("prompt")
        if isinstance(text, (dict, list)):
            text = json.dumps(text)
        return str(text or "")

    def _workspace_file(self, prefix: str, extension: str) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_{self._slugify(prefix)}_{timestamp}.{extension}"
        return self.workspace_dir / filename

    def _slugify(self, value: str) -> str:
        value = value or "output"
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower() or "output"

    def _summarize_text(self, text: str, max_len: int = 320) -> str:
        plain = re.sub(r"\s+", " ", text).strip()
        if len(plain) <= max_len:
            return plain
        return plain[: max_len - 3] + "..."

    def _serialize_validation_results(self, results: Sequence[ValidationResult]) -> List[Dict[str, Any]]:
        serialized = []
        for result in results:
            serialized.append(
                {
                    "rule": result.rule_name,
                    "passed": result.passed,
                    "message": result.message,
                    "severity": result.severity,
                    "suggestion": result.suggestion,
                    "line": result.line_number,
                }
            )
        return serialized

    def _score_validation(self, results: Sequence[ValidationResult]) -> float:
        if not results:
            return 1.0
        passed = len([r for r in results if r.passed])
        return round(passed / len(results), 3)

    def _build_recommendations(
        self,
        validation_results: Sequence[ValidationResult],
        accessibility_results: Sequence[ValidationResult],
    ) -> List[Dict[str, Any]]:
        recs: List[Dict[str, Any]] = []
        combined = list(validation_results) + list(accessibility_results)
        combined = [r for r in combined if not r.passed]
        for result in combined[:10]:
            recs.append(
                {
                    "title": result.rule_name.replace("_", " ").title(),
                    "detail": result.message,
                    "severity": result.severity,
                    "suggestion": result.suggestion,
                }
            )
        if not recs:
            recs.append(
                {
                    "title": "Content Health",
                    "detail": "All automated checks passed.",
                    "severity": "info",
                }
            )
        return recs

    def _default_sections(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = payload.get("prompt", "Key updates")
        return [
            {
                "title": "Overview",
                "bullets": [prompt, "Goals", "KPIs"],
            },
            {
                "title": "Highlights",
                "bullets": ["Revenue growth", "Customer wins", "Next steps"],
            },
        ]

    def _default_sheet_payload(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        sample_rows = payload.get("data") or [
            {"Metric": "Revenue", "Value": 120000, "Target": 100000},
            {"Metric": "Customers", "Value": 240, "Target": 230},
            {"Metric": "NPS", "Value": 68, "Target": 60},
        ]
        return [
            {
                "name": "Summary",
                "data": sample_rows,
                "charts": [
                    {
                        "type": "bar",
                        "title": "Metric vs Target",
                        "data_range": "A1:C4",
                        "position": "E2",
                    }
                ],
            }
        ]


__all__ = ["OfficeAIProcessingService", "OfficeAIResult"]
