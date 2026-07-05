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

    # k6 stores the HTTP failure rate (0 to 1), not the count
    failure_rate = metrics.get("http_req_failed", {}).get("value", 0)

    failed_requests = int(failure_rate * total_requests)

    return {
        "average_latency": metrics.get("http_req_duration", {}).get("avg", 0),
        "p95_latency": metrics.get("http_req_duration", {}).get("p(95)", 0),
        "total_requests": total_requests,
        "failed_requests": failed_requests,
    }


def get_smoke_summary():
    return get_k6_summary("smoke-test-results.json")


def get_latency_summary():
    return get_k6_summary("latency-test-results.json")


def get_load_summary():
    return get_k6_summary("load-test-results.json")