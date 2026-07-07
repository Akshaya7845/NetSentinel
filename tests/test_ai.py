from pathlib import Path

from src.ai.llm_service import LLMService
from src.ai.report_generator import ReportGenerator


llm = LLMService()
generator = ReportGenerator()


def test_generate_executive_report():
    """
    Verify Executive Summary generation.
    """

    report = llm.generate_executive_report()

    assert isinstance(report, str)
    assert len(report) > 0


def test_generate_detailed_report():
    """
    Verify Detailed Technical Report generation.
    """

    report = llm.generate_detailed_report()

    assert isinstance(report, str)
    assert len(report) > 0


def test_report_generator():
    """
    Verify AI reports are generated and saved.
    """

    files = generator.generate_reports()

    executive = Path(files["executive_summary"])
    detailed = Path(files["detailed_report"])

    assert executive.exists()
    assert detailed.exists()

    assert executive.stat().st_size > 0
    assert detailed.stat().st_size > 0