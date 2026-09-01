import json
from pathlib import Path

import requests


BASE_URL = "http://localhost:8000"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_azure_network_watcher_module_exists():
    """Verify Azure Network Watcher integration module exists."""
    module_path = (
        PROJECT_ROOT
        / "src"
        / "network"
        / "azure_network_watcher.py"
    )

    assert module_path.exists(), (
        "Azure Network Watcher module not found: "
        "src/network/azure_network_watcher.py"
    )


def test_networkwatcher_summary():
    """Verify Network Watcher summary endpoint is available."""
    response = requests.get(
        f"{BASE_URL}/networkwatcher/summary",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert "login_api" in data
    assert "product_api" in data
    assert "payment_api" in data


def test_networkwatcher_paths():
    """Verify all required network paths return status and latency."""
    response = requests.get(
        f"{BASE_URL}/networkwatcher/summary",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    required_paths = [
        "login_api",
        "product_api",
        "payment_api",
    ]

    for path in required_paths:
        assert path in data
        assert "status" in data[path]
        assert "response_time_ms" in data[path]


def test_groq_benchmark_exists():
    """Verify Groq benchmark script exists."""
    benchmark_path = (
        PROJECT_ROOT
        / "src"
        / "ai"
        / "benchmark.py"
    )

    assert benchmark_path.exists(), (
        "Groq benchmark file not found: "
        "src/ai/benchmark.py"
    )


def test_benchmark_results_exist():
    """Verify Groq benchmark results JSON was generated."""
    result_path = (
        PROJECT_ROOT
        / "monitoring"
        / "reports"
        / "benchmark_results.json"
    )

    assert result_path.exists(), (
        "Benchmark results not found: "
        "monitoring/reports/benchmark_results.json"
    )

    with open(result_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert isinstance(data, dict)


def test_grafana_dashboard_exists():
    """Verify the NetSentinel Grafana dashboard exists."""
    dashboard_path = (
        PROJECT_ROOT
        / "grafana"
        / "dashboards"
        / "netsentinel-dashboard.json"
    )

    assert dashboard_path.exists(), (
        "Grafana dashboard JSON not found."
    )

    with open(dashboard_path, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    assert isinstance(dashboard, dict)


def test_grafana_networkwatcher_panel():
    """
    Verify Azure Network Watcher content exists
    in the exported Grafana dashboard.
    """
    dashboard_path = (
        PROJECT_ROOT
        / "grafana"
        / "dashboards"
        / "netsentinel-dashboard.json"
    )

    with open(dashboard_path, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    dashboard_text = json.dumps(
        dashboard,
        ensure_ascii=False
    ).lower()

    assert "azure network watcher" in dashboard_text, (
        "Azure Network Watcher content not found "
        "in Grafana dashboard."
    )


def test_week13_integration():
    """Final Week 13 integration validation."""
    response = requests.get(
        f"{BASE_URL}/networkwatcher/summary",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    required_paths = [
        "login_api",
        "product_api",
        "payment_api",
    ]

    assert len(data) >= 3

    for path in required_paths:
        assert path in data
        assert data[path]["status"] == "Reachable"
        assert "response_time_ms" in data[path]