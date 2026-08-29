# from pathlib import Path

# from src.ai.llm_service import LLMService


# class ReportGenerator:
#     """
#     Generates and saves AI reports.

#     If Gemini/Groq is unavailable (quota exceeded, network issue, etc.),
#     existing reports will be used instead of failing.
#     """

#     def __init__(self):

#         self.llm = LLMService()

#         self.output_folder = Path("monitoring/reports")
#         self.output_folder.mkdir(parents=True, exist_ok=True)

#     def generate_reports(self):
#         """
#         Generates Executive Summary and Detailed Technical Report.

#         If Gemini fails, existing reports are returned.
#         """

#         executive_file = (
#             self.output_folder / "executive_summary.txt"
#         )

#         detailed_file = (
#             self.output_folder /
#             "detailed_technical_report.txt"
#         )

#         try:

#             print("Generating AI reports using Groq...")

#             executive = self.llm.generate_executive_report()

#             detailed = self.llm.generate_detailed_report()

#             executive_file.write_text(
#                 executive,
#                 encoding="utf-8"
#             )

#             detailed_file.write_text(
#                 detailed,
#                 encoding="utf-8"
#             )

#             print("AI reports generated successfully.")

#         except Exception as error:

#             print("\nWARNING: Gemini report generation failed.")
#             print(error)

#             if executive_file.exists() and detailed_file.exists():

#                 print(
#                     "Using previously generated AI reports."
#                 )

#             else:

#                 raise RuntimeError(
#                     "No existing AI reports found and "
#                     "Gemini generation failed."
#                 ) from error

#         return {
#             "executive_summary": executive_file,
#             "detailed_report": detailed_file,
#         }

from pathlib import Path

from src.ai.llm_service import LLMService


class ReportGenerator:
    """
    Generates and saves AI reports using Groq.

    If Groq is unavailable or returns invalid/empty content,
    existing non-empty reports will be reused.
    """

    def __init__(self):

        self.llm = LLMService()

        self.output_folder = Path("monitoring/reports")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def generate_reports(self):
        """
        Generates Executive Summary and Detailed Technical Report.

        If Groq generation fails, existing non-empty reports
        are reused instead of failing.
        """

        executive_file = (
            self.output_folder / "executive_summary.txt"
        )

        detailed_file = (
            self.output_folder / "detailed_technical_report.txt"
        )

        try:

            print("Generating AI reports using Groq...")

            executive = self.llm.generate_executive_report()
            detailed = self.llm.generate_detailed_report()

            # ------------------------------------------
            # Validate Groq responses
            # ------------------------------------------

            if not executive or not executive.strip():
                raise RuntimeError(
                    "Groq returned an empty Executive Summary."
                )

            if not detailed or not detailed.strip():
                raise RuntimeError(
                    "Groq returned an empty Detailed Technical Report."
                )

            # ------------------------------------------
            # Save reports
            # ------------------------------------------

            executive_file.write_text(
                executive.strip(),
                encoding="utf-8"
            )

            detailed_file.write_text(
                detailed.strip(),
                encoding="utf-8"
            )

            # ------------------------------------------
            # Verify files were actually written
            # ------------------------------------------

            if executive_file.stat().st_size == 0:
                raise RuntimeError(
                    "Executive Summary file was created but is empty."
                )

            if detailed_file.stat().st_size == 0:
                raise RuntimeError(
                    "Detailed Technical Report file was created but is empty."
                )

            print("AI reports generated successfully.")

        except Exception as error:

            print("\nWARNING: Groq report generation failed.")
            print(error)

            # ------------------------------------------
            # Reuse existing non-empty reports
            # ------------------------------------------

            executive_exists = (
                executive_file.exists()
                and executive_file.stat().st_size > 0
            )

            detailed_exists = (
                detailed_file.exists()
                and detailed_file.stat().st_size > 0
            )

            if executive_exists and detailed_exists:

                print(
                    "Using previously generated non-empty AI reports."
                )

            else:

                raise RuntimeError(
                    "Groq report generation failed and "
                    "no valid existing AI reports are available."
                ) from error

        return {
            "executive_summary": executive_file,
            "detailed_report": detailed_file,
        }