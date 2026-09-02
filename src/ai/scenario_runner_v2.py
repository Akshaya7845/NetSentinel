import json
from pathlib import Path

from src.ai.llm_service import LLMService
from src.ai.prompt_templates import ScenarioPromptTemplates


class ScenarioRunnerV2:
    """
    Week 14 multi-scenario AI runner.

    Loads monitoring scenarios, builds scenario-specific
    LangChain prompts, sends them to the existing Groq
    LLMService, and saves the generated reports.
    """

    def __init__(
        self,
        scenario_folder="monitoring/scenarios",
        output_folder="monitoring/reports/scenario_reports_v2",
    ):
        self.scenario_folder = Path(scenario_folder)
        self.output_folder = Path(output_folder)

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.llm = LLMService()

    def load_scenario(self, scenario_file):
        """
        Load a single scenario JSON file.
        """

        scenario_path = self.scenario_folder / scenario_file

        if not scenario_path.exists():
            raise FileNotFoundError(
                f"Scenario file not found: {scenario_path}"
            )

        with open(
            scenario_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def build_prompt(self, data):
        """
        Build the appropriate LangChain prompt
        for the scenario.
        """

        scenario_name = data["scenario"]

        template = ScenarioPromptTemplates.get_template(
            scenario_name
        )

        values = {
            "average_latency": data["average_latency"],
            "maximum_latency": data["maximum_latency"],
            "minimum_latency": data["minimum_latency"],
            "p95_latency": data["p95_latency"],
            "total_requests": data["total_requests"],
            "failed_requests": data["failed_requests"],
            "error_rate": data["error_rate"],
            "postman_response_time": data["postman_response_time"],
        }

        if scenario_name == "Throughput Degradation":
            values.update(
                {
                    "throughput_mbps": data["throughput_mbps"],
                    "baseline_throughput_mbps": data[
                        "baseline_throughput_mbps"
                    ],
                }
            )

        elif scenario_name == "Comparative Analysis":
            comparison = data["comparison"]

            baseline = comparison["baseline"]
            current = comparison["current"]

            values.update(
                {
                    "baseline_average_latency": baseline[
                        "average_latency"
                    ],
                    "baseline_p95_latency": baseline[
                        "p95_latency"
                    ],
                    "baseline_error_rate": baseline[
                        "error_rate"
                    ],
                    "baseline_throughput_mbps": baseline[
                        "throughput_mbps"
                    ],
                    "current_throughput_mbps": current[
                        "throughput_mbps"
                    ],
                }
            )

        return template.format(**values)

    def run_scenario(self, scenario_file):
        """
        Execute one monitoring scenario.
        """

        data = self.load_scenario(scenario_file)

        prompt = self.build_prompt(data)

        print(
            f"\nGenerating AI report for: "
            f"{data['scenario']}"
        )

        report = self.llm.generate_text(prompt)

        scenario_name = data["scenario"].lower().replace(
            " ",
            "_",
        )

        output_file = (
            self.output_folder
            / f"{scenario_name}_report.txt"
        )

        output_file.write_text(
            report,
            encoding="utf-8",
        )

        print(f"Report saved: {output_file}")

        return {
            "scenario": data["scenario"],
            "scenario_file": str(
                self.scenario_folder / scenario_file
            ),
            "report_file": str(output_file),
            "status": "success",
        }

    def run_all_scenarios(self):
        """
        Execute all monitoring scenarios.
        """

        scenario_files = sorted(
            self.scenario_folder.glob("*.json")
        )

        if not scenario_files:
            raise FileNotFoundError(
                "No scenario JSON files were found."
            )

        results = []

        for scenario_path in scenario_files:
            try:
                result = self.run_scenario(
                    scenario_path.name
                )
                results.append(result)

            except Exception as error:
                print(
                    f"\nERROR processing "
                    f"{scenario_path.name}: {error}"
                )

                results.append(
                    {
                        "scenario": scenario_path.stem,
                        "scenario_file": str(
                            scenario_path
                        ),
                        "report_file": None,
                        "status": "failed",
                        "error": str(error),
                    }
                )

        return results


if __name__ == "__main__":
    runner = ScenarioRunnerV2()

    results = runner.run_all_scenarios()

    print("\n===== WEEK 14 SCENARIO RESULTS =====")

    for result in results:
        print(
            f"{result['scenario']}: "
            f"{result['status']}"
        )
