from pathlib import Path

from src.ai.llm_service import LLMService


class ReportGenerator:
    """
    Generates and saves AI reports.

    If Gemini is unavailable (quota exceeded, network issue, etc.),
    existing reports will be used instead of failing.
    """

    def __init__(self):

        self.llm = LLMService()

        self.output_folder = Path("monitoring/reports")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def generate_reports(self):
        """
        Generates Executive Summary and Detailed Technical Report.

        If Gemini fails, existing reports are returned.
        """

        executive_file = (
            self.output_folder / "executive_summary.txt"
        )

        detailed_file = (
            self.output_folder /
            "detailed_technical_report.txt"
        )

        try:

            print("Generating AI reports using Gemini...")

            executive = self.llm.generate_executive_report()

            detailed = self.llm.generate_detailed_report()

            executive_file.write_text(
                executive,
                encoding="utf-8"
            )

            detailed_file.write_text(
                detailed,
                encoding="utf-8"
            )

            print("AI reports generated successfully.")

        except Exception as error:

            print("\nWARNING: Gemini report generation failed.")
            print(error)

            if executive_file.exists() and detailed_file.exists():

                print(
                    "Using previously generated AI reports."
                )

            else:

                raise RuntimeError(
                    "No existing AI reports found and "
                    "Gemini generation failed."
                ) from error

        return {
            "executive_summary": executive_file,
            "detailed_report": detailed_file,
        }