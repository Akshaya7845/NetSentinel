import json
from pathlib import Path

from src.ai.llm_service import LLMService


class ScenarioRunner:
    """
    Executes predefined monitoring scenarios
    and generates AI recommendations.
    """

    def __init__(self):

        self.llm = LLMService()

        self.scenario_folder = Path(
            "monitoring/scenarios"
        )

        self.output_folder = Path(
            "monitoring/reports/scenario_reports"
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def run_scenario(self, scenario_file):
        """
        Runs one monitoring scenario.
        """

        scenario_path = (
            self.scenario_folder / scenario_file
        )

        with open(
            scenario_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        prompt = f"""
You are a Senior Network Performance Engineer.

Analyze the following monitoring scenario.

Scenario:
{data["scenario"]}

Average Latency:
{data["average_latency"]} ms

Maximum Latency:
{data["maximum_latency"]} ms

Minimum Latency:
{data["minimum_latency"]} ms

P95 Latency:
{data["p95_latency"]} ms

Total Requests:
{data["total_requests"]}

Failed Requests:
{data["failed_requests"]}

Packet Loss:
{data["packet_loss"]} %

Error Rate:
{data["error_rate"]} %

Postman Response Time:
{data["postman_response_time"]} ms

Provide:

1. Overall Health

2. Root Cause

3. Performance Analysis

4. Optimization Recommendations

5. Final Conclusion
"""

        output_file = (
            self.output_folder /
            f"{scenario_path.stem}_report.txt"
        )

        try:

            print(
                f"\nGenerating AI report for "
                f"{data['scenario']}..."
            )

            report = self.llm.generate_text(prompt)

            output_file.write_text(
                report,
                encoding="utf-8"
            )

        except Exception as error:

            print("\nWARNING: Gemini quota exceeded.")
            print(error)
            print(
                "Generating fallback report instead."
            )

            report = f"""
NetSentinel Scenario Report

Scenario:
{data["scenario"]}

Status:
AI recommendation unavailable because the
Gemini API quota has been exceeded.

Scenario Metrics

Average Latency:
{data["average_latency"]} ms

Maximum Latency:
{data["maximum_latency"]} ms

Minimum Latency:
{data["minimum_latency"]} ms

P95 Latency:
{data["p95_latency"]} ms

Total Requests:
{data["total_requests"]}

Failed Requests:
{data["failed_requests"]}

Packet Loss:
{data["packet_loss"]} %

Error Rate:
{data["error_rate"]} %

Postman Response Time:
{data["postman_response_time"]} ms

Recommendation

Retry AI analysis after the Gemini
quota has been reset.
"""

            output_file.write_text(
                report,
                encoding="utf-8"
            )

        return output_file

    def run_all_scenarios(self):
        """
        Executes every predefined scenario.
        """

        generated_reports = []

        for scenario in sorted(
            self.scenario_folder.glob("*.json")
        ):

            report = self.run_scenario(
                scenario.name
            )

            generated_reports.append(report)

        return generated_reports