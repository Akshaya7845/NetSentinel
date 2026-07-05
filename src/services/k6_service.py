import json
from pathlib import Path


def read_k6_report(report_name):
    """
    Reads a k6 JSON report and returns its contents.
    """

    report_path = Path("monitoring/reports") / report_name

    if not report_path.exists():
        return None

    with open(report_path, "r") as file:
        return json.load(file)


def get_k6_summary(report_name):
    """
    Extracts important metrics from any k6 summary report.
    """

    report = read_k6_report(report_name)

    if report is None:
        return None

    metrics = report.get("metrics", {})

    total_requests = metrics.get("http_reqs", {}).get("count", 0)

    # k6 stores the failure rate (0.0 - 1.0)
    failure_rate = metrics.get("http_req_failed", {}).get("value", 0)

    failed_requests = int(failure_rate * total_requests)

    # Packet loss (%) = failed / total * 100
    packet_loss = 0
    if total_requests > 0:
        packet_loss = (failed_requests / total_requests) * 100

    # Error rate (%) = failure rate * 100
    error_rate = failure_rate * 100

    return {
        "average_latency": metrics.get("http_req_duration", {}).get("avg", 0),
        "p95_latency": metrics.get("http_req_duration", {}).get("p(95)", 0),
        "total_requests": total_requests,
        "failed_requests": failed_requests,
        "packet_loss": packet_loss,
        "error_rate": error_rate,
    }


def get_smoke_summary():
    return get_k6_summary("smoke-test-results.json")


def get_latency_summary():
    return get_k6_summary("latency-test-results.json")


def get_load_summary():
    return get_k6_summary("load-test-results.json")