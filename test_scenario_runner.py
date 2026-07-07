from src.ai.scenario_runner import ScenarioRunner


runner = ScenarioRunner()

reports = runner.run_all_scenarios()

print("\nScenario Reports Generated:\n")

for report in reports:
    print(report)