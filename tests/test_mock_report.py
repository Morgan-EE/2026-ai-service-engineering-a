import pytest

from src.mock_report import generate_mock_report
from src.models import ResearchReport


def test_generates_report_with_input_topic() -> None:
    report = generate_mock_report("  파일 업로드 기능 설계  ")

    assert isinstance(report, ResearchReport)
    assert report.topic == "파일 업로드 기능 설계"


def test_required_sections_are_populated() -> None:
    report = generate_mock_report("알림 시스템")

    for section in (
        report.requirements_summary,
        report.approaches,
        report.comparison,
        report.risks,
        report.checklist,
    ):
        assert section
        assert all(item.strip() for item in section)


def test_sources_are_clearly_mock() -> None:
    report = generate_mock_report("알림 시스템")

    assert report.sources
    assert all(source.startswith("Mock Source") for source in report.sources)


def test_output_is_deterministic() -> None:
    assert generate_mock_report("알림 시스템") == generate_mock_report("알림 시스템")


def test_blank_topic_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        generate_mock_report("  \n  ")
