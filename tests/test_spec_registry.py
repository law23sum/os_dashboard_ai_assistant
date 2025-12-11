from pathlib import Path

import pytest

from assistant_core.spec_registry import SpecRegistry


def _make_registry() -> SpecRegistry:
    spec_path = Path(__file__).resolve().parents[1] / "OS DashboardAIAssistantTOC.txt"
    return SpecRegistry(spec_path)


def test_spec_registry_loads_known_sections() -> None:
    registry = _make_registry()
    section = registry.get_section("1.7.2")
    assert section.identifier == "1.7.2"
    assert "Interaction Modalities" in section.title


def test_spec_registry_handles_letter_suffix_sections() -> None:
    registry = _make_registry()
    section = registry.get_section("17.3.9.a")
    assert section.identifier == "17.3.9.a"
    assert "Knowledge Atlas" in section.raw


def test_require_sections_validates_and_normalizes() -> None:
    registry = _make_registry()
    normalized = registry.require_sections([" 1.7.2.", "5.3 "], feature="demo")
    assert normalized == ("1.7.2", "5.3")
    with pytest.raises(KeyError):
        registry.require_sections(["99.99"], feature="invalid")


def test_register_feature_tracks_metadata() -> None:
    registry = _make_registry()
    registration = registry.register_feature(
        "unit_test_feature",
        ["1.7.2", "6.6"],
        metadata={"module": "tests"},
    )
    assert registration.name == "unit_test_feature"
    assert ("1.7.2", "6.6") == registration.sections
    assert registry.list_registrations()[0].metadata["module"] == "tests"
