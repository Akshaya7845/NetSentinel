from pathlib import Path

from src.ai.scenario_runner import ScenarioRunner


def test_run_all_scenarios():
    """
    Verify all predefined monitoring scenarios
    execute successfully.
    """

    runner = ScenarioRunner()

    reports = runner.run_all_scenarios()

    assert len(reports) == 3

    for report in reports:

        report_path = Path(report)

        assert report_path.exists()

        assert report_path.stat().st_size > 0