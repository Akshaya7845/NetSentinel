import requests

BASE_URL = "http://localhost:8000"


def test_health_endpoint():
    """Verify the Health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"


def test_metrics_endpoint():
    """Verify the Prometheus metrics endpoint."""
    response = requests.get(f"{BASE_URL}/metrics")
    assert response.status_code == 200

    assert "netsentinel_http_requests_total" in response.text
    assert "netsentinel_http_request_duration_seconds" in response.text


def test_performance_summary():
    """Verify the k6 Performance Summary endpoint."""
    response = requests.get(f"{BASE_URL}/performance/summary")
    assert response.status_code == 200

    data = response.json()

    assert "average_latency" in data
    assert "p95_latency" in data
    assert "total_requests" in data
    assert "failed_requests" in data
    assert "packet_loss" in data
    assert "error_rate" in data


def test_postman_summary():
    """Verify the Postman Summary endpoint."""
    response = requests.get(f"{BASE_URL}/postman/summary")
    assert response.status_code == 200

    data = response.json()

    assert "total_requests" in data
    assert "failed_requests" in data
    assert "average_response_time" in data


def test_network_status():
    """Verify Network Status endpoint."""
    response = requests.get(f"{BASE_URL}/network/status")
    assert response.status_code == 200

    data = response.json()

    assert "network" in data
    assert "api" in data
    assert "containers_running" in data


def test_networkwatcher_summary():
    """Verify Azure Network Watcher Summary endpoint."""
    response = requests.get(f"{BASE_URL}/networkwatcher/summary")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)


def test_all_performance():
    """Verify Combined Performance endpoint."""
    response = requests.get(f"{BASE_URL}/performance/all")
    assert response.status_code == 200

    data = response.json()

    assert "smoke_test" in data
    assert "latency_test" in data
    assert "load_test" in data