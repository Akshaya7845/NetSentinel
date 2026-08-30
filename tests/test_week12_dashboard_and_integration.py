import json
import os
import subprocess

import requests


# ============================================================
# NetSentinel Week 12
# Dashboard and Integration Tests
# ============================================================

GRAFANA_URL = "http://localhost:3000"
PROMETHEUS_URL = "http://localhost:9090"
FASTAPI_URL = "http://localhost:8000"

GRAFANA_AUTH = ("admin", "admin")

DASHBOARD_JSON = "grafana/dashboards/netsentinel-dashboard.json"


# ============================================================
# Docker Infrastructure Tests
# ============================================================

def test_postgres_container_running():
    """Verify PostgreSQL container is running."""

    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            "name=netsentinel-db",
            "--format",
            "{{.Status}}",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Up" in result.stdout

    print("✅ PostgreSQL container is running")


def test_prometheus_container_running():
    """Verify Prometheus container is running."""

    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            "name=netsentinel-prometheus",
            "--format",
            "{{.Status}}",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Up" in result.stdout

    print("✅ Prometheus container is running")


def test_grafana_container_running():
    """Verify Grafana container is running."""

    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            "name=netsentinel-grafana",
            "--format",
            "{{.Status}}",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Up" in result.stdout

    print("✅ Grafana container is running")


def test_docker_volumes_exist():
    """Verify NetSentinel Docker volumes exist."""

    result = subprocess.run(
        [
            "docker",
            "volume",
            "ls",
        ],
        capture_output=True,
        text=True,
    )

    assert "netsentinel_grafana_data" in result.stdout
    assert "netsentinel_postgres_data" in result.stdout
    assert "netsentinel_prometheus_data" in result.stdout

    print("✅ Required Docker volumes exist")


# ============================================================
# PostgreSQL Tests
# ============================================================

def test_postgres_tables_exist():
    """Verify the current NetSentinel PostgreSQL tables exist."""

    result = subprocess.run(
        [
            "docker",
            "exec",
            "netsentinel-db",
            "psql",
            "-U",
            "admin",
            "-d",
            "netsentinel",
            "-c",
            "\\dt",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    expected_tables = [
        "ai_reports",
        "network_connectivity",
        "performance_results",
        "postman_results",
        "test_runs",
    ]

    for table in expected_tables:
        assert table in result.stdout, (
            f"Expected PostgreSQL table '{table}' was not found"
        )

    print("✅ All current NetSentinel PostgreSQL tables exist")


def test_database_health_endpoint():
    """Verify FastAPI PostgreSQL health endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/database/health",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["database"] == "PostgreSQL"
    assert data["connected"] is True

    print("✅ PostgreSQL database health endpoint is working")


# ============================================================
# FastAPI Tests
# ============================================================

def test_fastapi_health():
    """Verify FastAPI health endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/health",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "NetSentinel API"

    print("✅ FastAPI health endpoint is working")


def test_fastapi_metrics_endpoint():
    """Verify Prometheus metrics endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/metrics",
        timeout=10,
    )

    assert response.status_code == 200

    metrics_text = response.text

    assert "netsentinel_http_requests_total" in metrics_text
    assert "netsentinel_k6_average_latency_ms" in metrics_text
    assert "netsentinel_k6_p95_latency_ms" in metrics_text
    assert "netsentinel_k6_total_requests" in metrics_text
    assert "netsentinel_k6_packet_loss_percent" in metrics_text
    assert "netsentinel_k6_error_rate_percent" in metrics_text
    assert "netsentinel_postman_total_requests" in metrics_text
    assert "netsentinel_postman_average_response_time_ms" in metrics_text

    print("✅ FastAPI Prometheus metrics endpoint is working")


# ============================================================
# Prometheus Tests
# ============================================================

def test_prometheus_health():
    """Verify Prometheus is responding."""

    response = requests.get(
        f"{PROMETHEUS_URL}/-/healthy",
        timeout=10,
    )

    assert response.status_code == 200

    print("✅ Prometheus is healthy")


def test_prometheus_targets():
    """Verify Prometheus has active scrape targets."""

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/targets",
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"

    active_targets = data["data"]["activeTargets"]

    assert len(active_targets) >= 1

    print("✅ Prometheus scrape target is configured")


def test_prometheus_netsentinel_metrics():
    """Verify NetSentinel metrics are available in Prometheus."""

    metrics = [
        "netsentinel_k6_average_latency_ms",
        "netsentinel_k6_p95_latency_ms",
        "netsentinel_k6_total_requests",
        "netsentinel_k6_failed_requests",
        "netsentinel_k6_packet_loss_percent",
        "netsentinel_k6_error_rate_percent",
        "netsentinel_postman_total_requests",
        "netsentinel_postman_failed_requests",
        "netsentinel_postman_average_response_time_ms",
    ]

    for metric in metrics:

        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": metric},
            timeout=10,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "success"

        result = data["data"]["result"]

        assert len(result) >= 1, (
            f"Prometheus metric '{metric}' has no data"
        )

        print(f"✅ Prometheus metric available: {metric}")


# ============================================================
# Grafana Tests
# ============================================================

def test_grafana_health():
    """Verify Grafana health."""

    response = requests.get(
        f"{GRAFANA_URL}/api/health",
        auth=GRAFANA_AUTH,
        timeout=10,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["database"] == "ok"

    print("✅ Grafana is healthy")


def test_grafana_prometheus_datasource():
    """Verify Prometheus datasource is configured in Grafana."""

    response = requests.get(
        f"{GRAFANA_URL}/api/datasources",
        auth=GRAFANA_AUTH,
        timeout=10,
    )

    assert response.status_code == 200

    datasources = response.json()

    prometheus_datasources = [
        datasource
        for datasource in datasources
        if datasource.get("type") == "prometheus"
    ]

    assert len(prometheus_datasources) >= 1

    print("✅ Grafana Prometheus datasource is configured")


def test_dashboard_json_exists():
    """Verify the NetSentinel dashboard JSON exists."""

    assert os.path.exists(DASHBOARD_JSON), (
        f"Dashboard JSON not found: {DASHBOARD_JSON}"
    )

    print("✅ NetSentinel dashboard JSON exists")


def test_dashboard_json_is_valid():
    """Verify dashboard JSON is valid."""

    with open(DASHBOARD_JSON, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    assert isinstance(dashboard, dict)

    print("✅ Dashboard JSON is valid")


def get_dashboard_panels():
    """
    Return panels from the current Grafana dashboard schema.

    NetSentinel currently uses Grafana's newer dashboard format:

        spec
          └── elements
                └── panel-x
                      ├── kind = Panel
                      └── spec
                            └── title

    This helper converts those elements into a simple list
    for the tests below.
    """

    with open(DASHBOARD_JSON, "r", encoding="utf-8") as file:
        dashboard = json.load(file)

    elements = dashboard.get("spec", {}).get("elements", {})

    panels = []

    if isinstance(elements, dict):

        for element in elements.values():

            if not isinstance(element, dict):
                continue

            if element.get("kind") != "Panel":
                continue

            panel_spec = element.get("spec", {})

            if not isinstance(panel_spec, dict):
                panel_spec = {}

            panels.append(
                {
                    "id": panel_spec.get("id"),
                    "title": panel_spec.get("title", ""),
                    "raw": element,
                }
            )

    return panels


def test_dashboard_has_required_panels():
    """Verify dashboard contains at least four panels."""

    panels = get_dashboard_panels()

    assert len(panels) >= 4, (
        f"Dashboard contains only {len(panels)} panels"
    )

    panel_titles = [
        panel["title"]
        for panel in panels
    ]

    print(
        f"✅ Dashboard contains {len(panels)} panels: "
        f"{panel_titles}"
    )


def test_dashboard_contains_connectivity_panel():
    """Verify the existing Connectivity Status panel is present."""

    panels = get_dashboard_panels()

    panel_titles = [
        panel["title"]
        for panel in panels
    ]

    connectivity_found = any(
        "Connectivity" in title
        for title in panel_titles
    )

    assert connectivity_found, (
        "Existing Connectivity Status panel was not found. "
        f"Available panels: {panel_titles}"
    )

    print("✅ Existing Connectivity Status panel is present")


# ============================================================
# AI Report Tests
# ============================================================

def test_ai_executive_summary():
    """Verify AI Executive Summary endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/ai/executive-summary",
        timeout=60,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["report_type"] == "executive_summary"
    assert data["report"]

    print("✅ AI Executive Summary is working")


def test_ai_detailed_report():
    """Verify AI Detailed Technical Report endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/ai/detailed-report",
        timeout=60,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["report_type"] == "detailed_report"
    assert data["report"]

    print("✅ AI Detailed Technical Report is working")


# ============================================================
# Network Connectivity Test
# ============================================================

def test_networkwatcher_summary():
    """Verify Network Watcher connectivity endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/networkwatcher/summary",
        timeout=60,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    print("✅ Network Watcher connectivity endpoint is working")


# ============================================================
# Postman Test
# ============================================================

def test_postman_summary():
    """Verify Postman summary endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/postman/summary",
        timeout=60,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_requests" in data
    assert "failed_requests" in data
    assert "average_response_time" in data

    print("✅ Postman summary endpoint is working")


# ============================================================
# K6 Performance Test
# ============================================================

def test_performance_summary():
    """Verify K6 performance summary endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/performance/all",
        timeout=60,
    )

    assert response.status_code == 200

    data = response.json()

    assert "smoke_test" in data
    assert "latency_test" in data
    assert "load_test" in data

    print("✅ K6 performance summary endpoint is working")


# ============================================================
# Test Run History
# ============================================================

def test_test_run_history():
    """Verify test run history endpoint."""

    response = requests.get(
        f"{FASTAPI_URL}/test-runs",
        timeout=30,
    )

    assert response.status_code == 200

    data = response.json()

    assert "test_runs" in data

    print("✅ Test run history endpoint is working")