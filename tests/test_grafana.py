import json
from pathlib import Path

import requests


GRAFANA_URL = "http://localhost:3000"
PROMETHEUS_URL = "http://localhost:9090"

DASHBOARD_FILE = (
    Path(__file__).resolve().parent.parent
    / "grafana"
    / "dashboards"
    / "netsentinel-dashboard.json"
)


def test_grafana_health():
    """
    Verify that Grafana is running and healthy.
    """

    response = requests.get(
        f"{GRAFANA_URL}/api/health",
        timeout=10
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("database") == "ok"


def test_prometheus_health():
    """
    Verify that Prometheus is running and reachable.
    """

    response = requests.get(
        f"{PROMETHEUS_URL}/-/healthy",
        timeout=10
    )

    assert response.status_code == 200


def test_grafana_dashboard_file_exists():
    """
    Verify that the NetSentinel Grafana dashboard JSON exists.
    """

    assert DASHBOARD_FILE.exists()
    assert DASHBOARD_FILE.is_file()


def test_grafana_dashboard_json_valid():
    """
    Verify that the NetSentinel Grafana dashboard JSON
    is valid and uses the expected Grafana Dashboard v2 structure.
    """

    with open(DASHBOARD_FILE, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    assert isinstance(dashboard, dict)

    assert dashboard.get("apiVersion") == "dashboard.grafana.app/v2"
    assert dashboard.get("kind") == "Dashboard"

    assert "spec" in dashboard
    assert isinstance(dashboard["spec"], dict)

    assert "elements" in dashboard["spec"]
    assert isinstance(dashboard["spec"]["elements"], dict)

    assert len(dashboard["spec"]["elements"]) > 0

def test_grafana_dashboard_contains_required_panels():
    """
    Verify that the NetSentinel Grafana dashboard contains
    all required Week 11 monitoring panels.
    """

    with open(DASHBOARD_FILE, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    elements = dashboard["spec"]["elements"]

    panel_titles = []

    for element in elements.values():

        if element.get("kind") != "Panel":
            continue

        panel_spec = element.get("spec", {})
        title = panel_spec.get("title")

        if title:
            panel_titles.append(title)

    required_panels = [
        "Average Latency",
        "P95 Latency",
        "Connectivity Status",
        "Total Request",
        "Failed Request",
        "Error Rate",
        "Packet Loss %",
        "Throughput",
    ]

    for required_panel in required_panels:
        assert required_panel in panel_titles, (
            f"Required Grafana panel not found: {required_panel}"
        )

def test_prometheus_latency_metric():
    """
    Verify that the NetSentinel latency metric
    is available from Prometheus.
    """

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={
            "query": "netsentinel_k6_average_latency_ms"
        },
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("status") == "success"

    result = data.get("data", {}).get("result", [])

    assert len(result) > 0, (
        "netsentinel_k6_average_latency_ms metric "
        "was not found in Prometheus"
    )


def test_prometheus_failed_requests_metric():
    """
    Verify that the NetSentinel failed-request metric
    is available from Prometheus.
    """

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={
            "query": "netsentinel_k6_failed_requests"
        },
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data.get("status") == "success"

    result = data.get("data", {}).get("result", [])

    assert len(result) > 0, (
        "netsentinel_k6_failed_requests metric "
        "was not found in Prometheus"
    )
