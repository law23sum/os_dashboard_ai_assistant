import pytest

from assistant_core.driver_orchestrator_architecture import DriverRegistry
from assistant_core.drivers import (
    ContentGenerationDriver,
    QualityAssuranceDriver,
    SystemOperationsDriver,
    register_builtin_drivers,
)


@pytest.mark.asyncio
async def test_register_builtin_drivers_populates_registry():
    registry = DriverRegistry()
    await register_builtin_drivers(registry)
    assert {
        "intelligence.data_collector.v1",
        "content.generator.v1",
        "system.operations.v1",
        "quality.assurance.v1",
    }.issubset(registry.manifests.keys())


@pytest.mark.asyncio
async def test_quality_assurance_driver_validate_basic_html():
    driver = QualityAssuranceDriver()
    html = """<!DOCTYPE html><html><head><title>x</title></head><body><h1>Title</h1></body></html>"""
    results = await driver.execute_action(
        "validate_content",
        {"content": html, "content_type": "html"},
    )
    assert results, "Expected validation results"
    assert any(isinstance(item, dict) for item in results)


@pytest.mark.asyncio
async def test_content_generation_driver_creates_presentation(tmp_path):
    driver = ContentGenerationDriver()
    output_path = tmp_path / "deck.html"
    config = {"title": "Demo", "author": "tester"}
    slides = [
        {"type": "title", "title": "Hello", "subtitle": "World"},
        {"type": "content", "title": "Agenda", "content": ["Item 1", "Item 2"]},
    ]
    result = await driver.execute_action(
        "generate_presentation",
        {"config": config, "slides": slides, "output_path": str(output_path)},
    )
    assert output_path.exists()
    assert "html" in result


@pytest.mark.asyncio
async def test_system_operations_driver_executes_command():
    driver = SystemOperationsDriver()
    result = await driver.execute_action("execute_command", {"command": "echo driver_test"})
    assert result["success"]
    assert "driver_test" in result["stdout"]
