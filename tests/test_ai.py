from pathlib import Path

from src.ai.report_generator import ReportGenerator


generator = ReportGenerator()


def test_report_generator():
    """
    Verify AI reports are generated or existing reports are reused.
    """

    files = generator.generate_reports()

    executive = Path(files["executive_summary"])
    detailed = Path(files["detailed_report"])

    assert executive.exists()
    assert detailed.exists()

    assert executive.stat().st_size > 0
    assert detailed.stat().st_size > 0


def test_executive_report_exists():
    """
    Verify Executive Summary exists and is not empty.
    """

    report = Path("monitoring/reports/executive_summary.txt")

    assert report.exists()

    assert report.read_text(
        encoding="utf-8"
    ).strip() != ""


def test_detailed_report_exists():
    """
    Verify Detailed Technical Report exists and is not empty.
    """

    report = Path(
        "monitoring/reports/detailed_technical_report.txt"
    )

    assert report.exists()

    assert report.read_text(
        encoding="utf-8"
    ).strip() != ""