from pathlib import Path

from src.ai.llm_service import LLMService
from src.services.database_service import DatabaseService


class ReportGenerator:
    """
    Generates AI reports using Groq.

    Reports are:
    1. Generated using LLMService.
    2. Validated.
    3. Saved as text files.
    4. Stored in PostgreSQL.

    If Groq generation fails and valid existing reports
    are available, the existing reports are reused.
    """

    def __init__(self):

        self.llm = LLMService()

        self.db = DatabaseService()

        self.output_folder = Path(
            "monitoring/reports"
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate_reports(self):
        """
        Generate Executive Summary and Detailed Technical Report.
        """

        executive_file = (
            self.output_folder
            / "executive_summary.txt"
        )

        detailed_file = (
            self.output_folder
            / "detailed_technical_report.txt"
        )

        try:

            print(
                "Generating AI reports using Groq..."
            )

            # ------------------------------------------------
            # Generate reports
            # ------------------------------------------------

            executive = (
                self.llm.generate_executive_report()
            )

            detailed = (
                self.llm.generate_detailed_report()
            )

            # ------------------------------------------------
            # Validate responses
            # ------------------------------------------------

            if not executive or not executive.strip():
                raise RuntimeError(
                    "Groq returned an empty Executive Summary."
                )

            if not detailed or not detailed.strip():
                raise RuntimeError(
                    "Groq returned an empty Detailed Technical Report."
                )

            executive = executive.strip()
            detailed = detailed.strip()

            # ------------------------------------------------
            # Save reports to files
            # ------------------------------------------------

            executive_file.write_text(
                executive,
                encoding="utf-8"
            )

            detailed_file.write_text(
                detailed,
                encoding="utf-8"
            )

            # ------------------------------------------------
            # Verify files
            # ------------------------------------------------

            if executive_file.stat().st_size == 0:
                raise RuntimeError(
                    "Executive Summary file is empty."
                )

            if detailed_file.stat().st_size == 0:
                raise RuntimeError(
                    "Detailed Technical Report file is empty."
                )

            # ------------------------------------------------
            # Store reports in PostgreSQL
            # ------------------------------------------------

            executive_id = (
                self.db.insert_ai_report(
                    report_type="executive_summary",
                    report_content=executive,
                )
            )

            detailed_id = (
                self.db.insert_ai_report(
                    report_type="detailed_report",
                    report_content=detailed,
                )
            )

            print(
                "AI reports generated successfully."
            )

            print(
                f"Executive report database ID: {executive_id}"
            )

            print(
                f"Detailed report database ID: {detailed_id}"
            )

        except Exception as error:

            print(
                "\nWARNING: AI report generation failed."
            )

            print(error)

            # ------------------------------------------------
            # Check existing reports
            # ------------------------------------------------

            executive_exists = (
                executive_file.exists()
                and executive_file.stat().st_size > 0
            )

            detailed_exists = (
                detailed_file.exists()
                and detailed_file.stat().st_size > 0
            )

            if not (
                executive_exists
                and detailed_exists
            ):
                raise RuntimeError(
                    "AI report generation failed and "
                    "no valid existing reports are available."
                ) from error

            print(
                "Using previously generated non-empty reports."
            )

        return {
            "executive_summary": executive_file,
            "detailed_report": detailed_file,
        }