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

    return {
        "average_latency": metrics.get("http_req_duration", {}).get("avg"),
        "p95_latency": metrics.get("http_req_duration", {}).get("p(95)"),
        "total_requests": metrics.get("http_reqs", {}).get("count"),
        "failed_requests": metrics.get("http_req_failed", {}).get("fails"),
    }
def get_smoke_summary():
    return get_k6_summary("smoke-test-results.json")


def get_latency_summary():
    return get_k6_summary("latency-test-results.json")


def get_load_summary():
    return get_k6_summary("load-test-results.json")