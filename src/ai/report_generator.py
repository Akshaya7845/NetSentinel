from pathlib import Path

from src.ai.llm_service import LLMService


class ReportGenerator:
    """
    Generates and saves AI reports.
    """

    def __init__(self):

        self.llm = LLMService()

        self.output_folder = Path("monitoring/reports")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def generate_reports(self):
        """
        Generates both AI reports and saves them.
        """

        executive = self.llm.generate_executive_report()

        detailed = self.llm.generate_detailed_report()

        executive_file = self.output_folder / "executive_summary.txt"

        detailed_file = (
            self.output_folder /
            "detailed_technical_report.txt"
        )

        executive_file.write_text(
            executive,
            encoding="utf-8"
        )

        detailed_file.write_text(
            detailed,
            encoding="utf-8"
        )

        return {
            "executive_summary": executive_file,
            "detailed_report": detailed_file,
        }