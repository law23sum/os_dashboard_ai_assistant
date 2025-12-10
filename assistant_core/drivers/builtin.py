"""Built-in drivers that expose core assistant capabilities to the orchestrator."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import Any, Dict, List

import pandas as pd

from assistant_core.content.generators import (
    ContentConfig,
    ExcelDashboardGenerator,
    PresentationGenerator,
    WordDocumentGenerator,
)
from assistant_core.intelligence.data_collector import DataCollector, DataSource
from assistant_core.intelligence.quality_assurance import (
    AccessibilityChecker,
    BatchValidator,
    ContentValidator,
)
from assistant_core.system.operations import SystemOperationsController
from assistant_core.driver_orchestrator_architecture import (
    ActionSchema,
    BaseDriver,
    DriverManifest,
)


class IntelligenceDataDriver(BaseDriver):
    """Driver that wraps the DataCollector capabilities."""

    def __init__(self) -> None:
        actions = {
            "scrape_web_source": ActionSchema(
                name="scrape_web_source",
                description="Scrape a web source with optional CSS selectors",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "url": {"type": "string"},
                        "selectors": {"type": "object"},
                        "headers": {"type": "object"},
                        "params": {"type": "object"},
                        "rate_limit": {"type": "number"},
                    },
                    "required": ["name", "url"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Scrape news headlines"}],
            ),
            "fetch_api_source": ActionSchema(
                name="fetch_api_source",
                description="Pull data from an API endpoint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "url": {"type": "string"},
                        "headers": {"type": "object"},
                        "params": {"type": "object"},
                        "auth": {"type": "object"},
                        "rate_limit": {"type": "number"},
                    },
                    "required": ["name", "url"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Call CRM API"}],
            ),
            "batch_collect": ActionSchema(
                name="batch_collect",
                description="Collect data from multiple configured sources",
                input_schema={
                    "type": "object",
                    "properties": {
                        "sources": {"type": "array"},
                        "selectors": {"type": "object"},
                    },
                    "required": ["sources"],
                },
                output_schema={"type": "array"},
                examples=[{"description": "Gather from API + site"}],
            ),
            "cross_reference": ActionSchema(
                name="cross_reference",
                description="Cross reference results across sources",
                input_schema={
                    "type": "object",
                    "properties": {
                        "datasets": {"type": "array"},
                        "fields": {"type": "array"},
                    },
                    "required": ["datasets", "fields"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Verify pricing data"}],
            ),
            "clean_and_transform": ActionSchema(
                name="clean_and_transform",
                description="Flatten, clean, and transform structured datasets",
                input_schema={
                    "type": "object",
                    "properties": {
                        "datasets": {"type": "array"},
                        "transformations": {"type": "object"},
                    },
                    "required": ["datasets"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Prepare analytics frame"}],
            ),
        }

        manifest = DriverManifest(
            name="intelligence.data_collector.v1",
            version="1.0.0",
            vendor="OSDashboard",
            trust_level="internal",
            actions=actions,
            side_effects=["reads_external_data"],
            rate_limits={"calls_per_minute": 30},
            cost_model={"per_call": 0.0},
            latency_profile={"avg_ms": 800, "p99_ms": 3000},
            security_class="internal",
            preconditions=["network_access"],
            postconditions=["data_collected"],
            logs_schema={},
            metrics_exposed=["requests"],
            trace_points=["collector_request"],
        )
        super().__init__(manifest)
        self._collector = DataCollector()

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        if action == "scrape_web_source":
            return await self._scrape(params)
        if action == "fetch_api_source":
            return await self._fetch_api(params)
        if action == "batch_collect":
            return await self._batch(params)
        if action == "cross_reference":
            return self._cross_reference(params)
        if action == "clean_and_transform":
            return await self._clean(params)
        raise ValueError(f"Unknown intelligence action: {action}")

    async def _scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        source = self._build_source(params, "web")
        async with DataCollector(self._collector.max_concurrent) as collector:
            return await collector.scrape_webpage(source, params.get("selectors"))

    async def _fetch_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        source = self._build_source(params, "api")
        async with DataCollector(self._collector.max_concurrent) as collector:
            return await collector.fetch_api_data(source)

    async def _batch(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        sources = [self._build_source(src, src.get("source_type", "web")) for src in params["sources"]]
        selectors = params.get("selectors", {})
        async with DataCollector(self._collector.max_concurrent) as collector:
            return await collector.batch_collect(sources, selectors)

    def _cross_reference(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._collector.cross_reference_verify(params["datasets"], params["fields"])

    async def _clean(self, params: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        rows = await loop.run_in_executor(
            None,
            lambda: self._collector.clean_and_transform(
                params["datasets"], params.get("transformations")
            ).to_dict(orient="records"),
        )
        return {"rows": rows}

    def _build_source(self, params: Dict[str, Any], source_type: str) -> DataSource:
        return DataSource(
            name=params.get("name", "source"),
            url=params["url"],
            source_type=source_type,
            headers=params.get("headers"),
            params=params.get("params"),
            auth=params.get("auth"),
            rate_limit=params.get("rate_limit", 1.0),
            timeout=params.get("timeout", 30),
            retry_count=params.get("retry_count", 3),
        )


class ContentGenerationDriver(BaseDriver):
    """Driver exposing presentation, Excel, and document generation."""

    def __init__(self) -> None:
        actions = {
            "generate_presentation": ActionSchema(
                name="generate_presentation",
                description="Generate an interactive presentation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "config": {"type": "object"},
                        "slides": {"type": "array"},
                        "output_path": {"type": "string"},
                    },
                    "required": ["config", "slides"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Create exec briefing deck"}],
            ),
            "generate_excel_dashboard": ActionSchema(
                name="generate_excel_dashboard",
                description="Produce Excel dashboards with charts",
                input_schema={
                    "type": "object",
                    "properties": {
                        "config": {"type": "object"},
                        "worksheets": {"type": "array"},
                        "output_path": {"type": "string"},
                    },
                    "required": ["config", "worksheets", "output_path"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Sales KPI dashboard"}],
            ),
            "generate_word_document": ActionSchema(
                name="generate_word_document",
                description="Build Word documents with formatted sections",
                input_schema={
                    "type": "object",
                    "properties": {
                        "config": {"type": "object"},
                        "elements": {"type": "array"},
                        "output_path": {"type": "string"},
                    },
                    "required": ["config", "elements", "output_path"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Quarterly report"}],
            ),
        }

        manifest = DriverManifest(
            name="content.generator.v1",
            version="1.0.0",
            vendor="OSDashboard",
            trust_level="internal",
            actions=actions,
            side_effects=["writes_documents"],
            rate_limits={"calls_per_minute": 10},
            cost_model={"per_call": 0.0},
            latency_profile={"avg_ms": 1200, "p99_ms": 5000},
            security_class="internal",
            preconditions=["filesystem_access"],
            postconditions=["artifact_created"],
            logs_schema={},
            metrics_exposed=["artifacts_created"],
            trace_points=["content_generation"],
        )
        super().__init__(manifest)

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        if action == "generate_presentation":
            return await asyncio.to_thread(self._generate_presentation, params)
        if action == "generate_excel_dashboard":
            return await asyncio.to_thread(self._generate_excel, params)
        if action == "generate_word_document":
            return await asyncio.to_thread(self._generate_doc, params)
        raise ValueError(f"Unknown content action: {action}")

    def _generate_presentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        config = ContentConfig(**params["config"])
        generator = PresentationGenerator(config)
        for slide in params["slides"]:
            slide_type = slide.get("type", "content")
            if slide_type == "title":
                generator.add_title_slide(
                    slide.get("title", config.title),
                    slide.get("subtitle", ""),
                    slide.get("author", config.author),
                )
            elif slide_type == "chart":
                generator.add_chart_slide(
                    slide.get("title", ""),
                    slide.get("chart_type", "bar"),
                    slide.get("chart_data", {}),
                    slide.get("chart_config"),
                )
            elif slide_type == "comparison":
                generator.add_comparison_slide(
                    slide.get("title", ""),
                    slide.get("left", {}),
                    slide.get("right", {}),
                )
            else:
                generator.add_content_slide(
                    slide.get("title", ""),
                    slide.get("content", []),
                    slide.get("image_url"),
                    slide.get("chart_data"),
                )
        output_path = params.get("output_path")
        html = generator.generate_html(output_path)
        return {"output_path": output_path, "html": html}

    def _generate_excel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        config = ContentConfig(**params["config"])
        generator = ExcelDashboardGenerator(config)
        for worksheet in params["worksheets"]:
            data = pd.DataFrame(worksheet.get("data", []))
            generator.add_worksheet(
                worksheet["name"],
                data,
                worksheet.get("charts"),
            )
            for formatting in worksheet.get("conditional_formats", []):
                generator.add_conditional_formatting(
                    worksheet["name"],
                    formatting["range"],
                    formatting["type"],
                    formatting["config"],
                )
        output_path = params["output_path"]
        success = generator.generate_excel(output_path)
        return {"output_path": output_path, "success": success}

    def _generate_doc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        config = ContentConfig(**params["config"])
        generator = WordDocumentGenerator(config)
        for element in params["elements"]:
            etype = element.get("type", "paragraph")
            if etype == "heading":
                generator.add_heading(element.get("text", ""), element.get("level", 1))
            elif etype == "table":
                generator.add_table(element.get("data", []), element.get("headers"))
            elif etype == "list":
                generator.add_list(element.get("items", []), element.get("list_type", "bullet"))
            else:
                generator.add_paragraph(element.get("text", ""))
        output_path = params["output_path"]
        success = generator.generate_docx(output_path)
        return {"output_path": output_path, "success": success}


class SystemOperationsDriver(BaseDriver):
    """Driver that wraps the SystemOperationsController."""

    def __init__(self) -> None:
        actions = {
            "execute_command": ActionSchema(
                name="execute_command",
                description="Execute shell command",
                input_schema={"type": "object", "properties": {"command": {}, "cwd": {"type": "string"}}},
                output_schema={"type": "object"},
                examples=[{"description": "Run diagnostics"}],
            ),
            "get_system_info": ActionSchema(
                name="get_system_info",
                description="Retrieve system stats",
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object"},
                examples=[{"description": "Get CPU status"}],
            ),
            "install_package": ActionSchema(
                name="install_package",
                description="Install package via package manager",
                input_schema={
                    "type": "object",
                    "properties": {
                        "package": {"type": "string"},
                        "manager": {"type": "string"},
                    },
                    "required": ["package"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Install curl"}],
            ),
            "create_archive": ActionSchema(
                name="create_archive",
                description="Create compressed archive",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string"},
                        "archive_path": {"type": "string"},
                        "archive_type": {"type": "string"},
                    },
                    "required": ["source_path", "archive_path"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Zip artifacts"}],
            ),
            "extract_archive": ActionSchema(
                name="extract_archive",
                description="Extract archive",
                input_schema={
                    "type": "object",
                    "properties": {
                        "archive_path": {"type": "string"},
                        "extract_to": {"type": "string"},
                    },
                    "required": ["archive_path"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Unpack logs"}],
            ),
        }

        manifest = DriverManifest(
            name="system.operations.v1",
            version="1.0.0",
            vendor="OSDashboard",
            trust_level="internal",
            actions=actions,
            side_effects=["executes_commands"],
            rate_limits={"calls_per_minute": 20},
            cost_model={"per_call": 0.0},
            latency_profile={"avg_ms": 500, "p99_ms": 2000},
            security_class="restricted",
            preconditions=["system_policy_check"],
            postconditions=["system_state_updated"],
            logs_schema={},
            metrics_exposed=["commands_executed"],
            trace_points=["system_ops"],
        )
        super().__init__(manifest)
        self._controller = SystemOperationsController()

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        if action == "execute_command":
            return await asyncio.to_thread(
                self._controller.execute_command,
                params.get("command"),
                params.get("cwd"),
                params.get("environment"),
                params.get("timeout"),
                params.get("capture_output", True),
                params.get("shell", True),
            )
        if action == "get_system_info":
            return await asyncio.to_thread(self._controller.get_system_info)
        if action == "install_package":
            return await asyncio.to_thread(
                self._controller.install_package,
                params["package"],
                params.get("manager", "auto"),
            )
        if action == "create_archive":
            return await asyncio.to_thread(
                self._controller.create_archive,
                params["source_path"],
                params["archive_path"],
                params.get("archive_type", "zip"),
                params.get("compression_level", 6),
            )
        if action == "extract_archive":
            return await asyncio.to_thread(
                self._controller.extract_archive,
                params["archive_path"],
                params.get("extract_to"),
            )
        raise ValueError(f"Unknown system action: {action}")


class QualityAssuranceDriver(BaseDriver):
    """Driver exposing validation and accessibility checks."""

    def __init__(self) -> None:
        actions = {
            "validate_content": ActionSchema(
                name="validate_content",
                description="Run content validator rules",
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "content_type": {"type": "string"},
                        "rules": {"type": "array"},
                    },
                    "required": ["content"],
                },
                output_schema={"type": "array"},
                examples=[{"description": "Validate HTML"}],
            ),
            "batch_validate": ActionSchema(
                name="batch_validate",
                description="Validate multiple files",
                input_schema={
                    "type": "object",
                    "properties": {
                        "files": {"type": "array"},
                        "content_types": {"type": "object"},
                        "rules": {"type": "array"},
                    },
                    "required": ["files"],
                },
                output_schema={"type": "object"},
                examples=[{"description": "Validate docs"}],
            ),
            "accessibility_check": ActionSchema(
                name="accessibility_check",
                description="Run accessibility heuristics",
                input_schema={
                    "type": "object",
                    "properties": {"content": {"type": "string"}},
                    "required": ["content"],
                },
                output_schema={"type": "array"},
                examples=[{"description": "Check HTML"}],
            ),
        }

        manifest = DriverManifest(
            name="quality.assurance.v1",
            version="1.0.0",
            vendor="OSDashboard",
            trust_level="internal",
            actions=actions,
            side_effects=["reads_documents"],
            rate_limits={"calls_per_minute": 25},
            cost_model={"per_call": 0.0},
            latency_profile={"avg_ms": 600, "p99_ms": 2500},
            security_class="internal",
            preconditions=["filesystem_access"],
            postconditions=["validation_results"],
            logs_schema={},
            metrics_exposed=["validations_run"],
            trace_points=["quality_checks"],
        )
        super().__init__(manifest)
        self._validator = ContentValidator()
        self._batch_validator = BatchValidator()
        self._accessibility = AccessibilityChecker()

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        if action == "validate_content":
            results = await asyncio.to_thread(
                self._validator.validate_content,
                params["content"],
                params.get("content_type", "html"),
                params.get("rules"),
            )
            return [asdict(result) for result in results]
        if action == "batch_validate":
            results = await asyncio.to_thread(
                self._batch_validator.validate_files,
                params["files"],
                params.get("content_types"),
                params.get("rules"),
            )
            return {
                path: [asdict(result) for result in result_list]
                for path, result_list in results.items()
            }
        if action == "accessibility_check":
            results = await asyncio.to_thread(
                self._accessibility.check_accessibility,
                params["content"],
            )
            return [asdict(result) for result in results]
        raise ValueError(f"Unknown QA action: {action}")


def _driver_instances() -> List[BaseDriver]:
    return [
        IntelligenceDataDriver(),
        ContentGenerationDriver(),
        SystemOperationsDriver(),
        QualityAssuranceDriver(),
    ]


async def register_builtin_drivers(registry) -> None:
    """Register all built-in drivers with the provided registry."""
    for driver in _driver_instances():
        await registry.register_driver(driver.manifest, driver)
