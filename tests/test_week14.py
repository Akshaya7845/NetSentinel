import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = PROJECT_ROOT / "monitoring" / "scenarios"
REPORT_DIR = PROJECT_ROOT / "monitoring" / "reports" / "scenario_reports_v2"
QUALITY_REPORT = PROJECT_ROOT / "monitoring" / "reports" / "ai_quality_report.json"
DASHBOARD_FILE = PROJECT_ROOT / "grafana" / "dashboards" / "netsentinel-dashboard.json"


EXPECTED_SCENARIOS = {
    "healthy_network.json": "Healthy Network",
    "high_latency.json": "High Latency",
    "throughput_degradation.json": "Throughput Degradation",
    "high_error_rate.json": "High Error Rate",
    "comparative_analysis.json": "Comparative Analysis",
}


# -------------------------------------------------------------------
# 1. Scenario files
# -------------------------------------------------------------------

def test_week14_all_scenario_files_exist():
    """All five Week 14 monitoring scenario files must exist."""
    for filename in EXPECTED_SCENARIOS:
        assert (SCENARIO_DIR / filename).exists(), f"Missing scenario: {filename}"


def test_week14_scenario_json_files_are_valid():
    """All Week 14 scenario files must contain valid JSON."""
    for filename in EXPECTED_SCENARIOS:
        path = SCENARIO_DIR / filename

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        assert isinstance(data, dict)
        assert "scenario" in data
        assert data["scenario"] == EXPECTED_SCENARIOS[filename]


def test_week14_scenarios_contain_required_metrics():
    """Each scenario must contain the core network monitoring metrics."""
    required_metrics = {
        "average_latency",
        "maximum_latency",
        "minimum_latency",
        "p95_latency",
        "total_requests",
        "failed_requests",
        "error_rate",
        "postman_response_time",
    }

    for filename in EXPECTED_SCENARIOS:
        with open(SCENARIO_DIR / filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        missing = required_metrics - set(data.keys())
        assert not missing, f"{filename} is missing metrics: {missing}"


# -------------------------------------------------------------------
# 2. LangChain prompt templates
# -------------------------------------------------------------------

def test_week14_prompt_templates_load():
    """All five Week 14 scenario prompt templates must load."""
    from src.ai.prompt_templates import ScenarioPromptTemplates

    for scenario_name in EXPECTED_SCENARIOS.values():
        template = ScenarioPromptTemplates.get_template(scenario_name)

        assert template is not None
        assert hasattr(template, "format")


def test_week14_prompt_templates_contain_network_metrics():
    """Scenario prompts must reference the important monitoring metrics."""
    from src.ai.prompt_templates import ScenarioPromptTemplates

    expected_terms = [
        "latency",
        "P95",
        "error",
        "request",
    ]

    for scenario_name in EXPECTED_SCENARIOS.values():
        template = ScenarioPromptTemplates.get_template(scenario_name)
        prompt = template.format(
            average_latency=100,
            maximum_latency=200,
            minimum_latency=50,
            p95_latency=180,
            total_requests=5000,
            failed_requests=100,
            error_rate=2.0,
            postman_response_time=250,
            throughput_mbps=50,
            baseline_throughput_mbps=100,
            baseline_average_latency=30,
            baseline_p95_latency=40,
            baseline_error_rate=0,
            current_throughput_mbps=65,
        ).lower()

        for term in expected_terms:
            assert term.lower() in prompt


# -------------------------------------------------------------------
# 3. Scenario Runner V2
# -------------------------------------------------------------------

def test_week14_scenario_runner_v2_loads_scenario():
    """ScenarioRunnerV2 must load a scenario JSON file correctly."""
    from src.ai.scenario_runner_v2 import ScenarioRunnerV2

    runner = ScenarioRunnerV2()

    data = runner.load_scenario("healthy_network.json")

    assert data["scenario"] == "Healthy Network"
    assert data["average_latency"] == 28.5
    assert data["p95_latency"] == 40.1


def test_week14_scenario_runner_v2_builds_prompt():
    """ScenarioRunnerV2 must build a scenario-specific prompt."""
    from src.ai.scenario_runner_v2 import ScenarioRunnerV2

    runner = ScenarioRunnerV2()

    data = runner.load_scenario("high_latency.json")
    prompt = runner.build_prompt(data)

    assert isinstance(prompt, str)
    assert len(prompt) > 100
    assert "320.8" in prompt
    assert "650.9" in prompt


def test_week14_all_ai_reports_exist():
    """AI reports must exist for all five Week 14 scenarios."""
    expected_reports = {
        "healthy_network_report.txt",
        "high_latency_report.txt",
        "throughput_degradation_report.txt",
        "high_error_rate_report.txt",
        "comparative_analysis_report.txt",
    }

    for filename in expected_reports:
        path = REPORT_DIR / filename

        assert path.exists(), f"Missing AI report: {filename}"
        assert path.stat().st_size > 0, f"Empty AI report: {filename}"


# -------------------------------------------------------------------
# 4. AI Quality Validator
# -------------------------------------------------------------------

def test_week14_quality_validator_exists():
    """AIQualityValidator must be importable and usable."""
    from src.ai.quality_validator import AIQualityValidator

    validator = AIQualityValidator()

    assert validator is not None
    assert hasattr(validator, "validate_all")
    assert hasattr(validator, "save_quality_report")


def test_week14_quality_validation_passes():
    """All five generated reports must pass AI quality validation."""
    from src.ai.quality_validator import AIQualityValidator

    validator = AIQualityValidator()
    result = validator.validate_all()

    assert result["total_reports"] == 5
    assert result["passed"] == 5
    assert result["review"] == 0
    assert result["failed"] == 0
    assert result["average_quality_score"] >= 80

    for report in result["reports"]:
        assert report["status"] == "PASS"
        assert report["score"] >= 80
        assert report["issues"] == []


def test_week14_quality_report_file_exists():
    """The saved AI quality report must exist and contain five results."""
    assert QUALITY_REPORT.exists()
    assert QUALITY_REPORT.stat().st_size > 0

    with open(QUALITY_REPORT, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["total_reports"] == 5
    assert data["passed"] == 5
    assert data["review"] == 0
    assert data["failed"] == 0
    assert data["average_quality_score"] >= 80


# -------------------------------------------------------------------
# 5. PostgreSQL integration
# -------------------------------------------------------------------

def test_week14_database_service_has_scenario_methods():
    """DatabaseService must contain the Week 14 scenario/quality methods."""
    from src.services.database_service import DatabaseService

    assert hasattr(DatabaseService, "insert_scenario_ai_result")
    assert hasattr(DatabaseService, "get_scenario_ai_results")
    assert hasattr(DatabaseService, "get_scenario_ai_result")
    assert hasattr(DatabaseService, "insert_ai_quality_result")
    assert hasattr(DatabaseService, "get_ai_quality_results")
    assert hasattr(DatabaseService, "get_latest_ai_quality_summary")


# -------------------------------------------------------------------
# 6. Grafana dashboard integration
# -------------------------------------------------------------------

def test_week14_grafana_ai_quality_panel_exists():
    """Grafana must contain the Week 14 AI Scenario Quality panel."""
    assert DASHBOARD_FILE.exists()

    with open(DASHBOARD_FILE, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    elements = dashboard["spec"]["elements"]

    assert "panel-17" in elements

    panel = elements["panel-17"]

    assert panel["spec"]["id"] == 17
    assert panel["spec"]["title"] == "🤖 AI Scenario Quality"


def test_week14_grafana_uses_postgresql_for_quality_panel():
    """The AI quality panel must use the PostgreSQL datasource and query."""
    with open(DASHBOARD_FILE, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    panel = dashboard["spec"]["elements"]["panel-17"]

    query = (
        panel["spec"]["data"]["spec"]["queries"][0]
        ["spec"]["query"]
    )

    assert query["group"] == "grafana-postgresql-datasource"
    assert query["datasource"]["name"] == "P661532110116C186"

    raw_sql = query["spec"]["rawSql"]

    assert "ai_quality_results" in raw_sql
    assert "scenario_name" in raw_sql
    assert "status" in raw_sql
    assert "quality_score" in raw_sql


# -------------------------------------------------------------------
# 7. Week 14 FastAPI endpoints
# -------------------------------------------------------------------

def test_week14_fastapi_scenario_endpoints_exist():
    """All four required Week 14 FastAPI endpoints must exist."""
    from src.api.main import app

    routes = {
        route.path
        for route in app.routes
    }

    assert "/ai/scenarios/run-all" in routes
    assert "/ai/scenarios/validate" in routes
    assert "/ai/scenarios/list" in routes
    assert "/ai/quality-report" in routes


def test_week14_scenario_list_endpoint_returns_five_scenarios():
    """The scenario list endpoint must expose all five Week 14 scenarios."""
    from fastapi.testclient import TestClient
    from src.api.main import app

    client = TestClient(app)

    response = client.get("/ai/scenarios/list")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["total_scenarios"] == 5

    scenario_names = {
        item["scenario"]
        for item in data["scenarios"]
    }

    assert scenario_names == set(EXPECTED_SCENARIOS.values())
