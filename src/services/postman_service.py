import json
from pathlib import Path


def read_postman_report():
    """
    Reads the Newman JSON report.
    """

    report_path = Path("monitoring/reports/postman/postman-report.json")

    if not report_path.exists():
        return None

    with open(report_path, "r") as file:
        return json.load(file)


def get_postman_summary():
    """
    Extracts useful metrics from the Newman report.
    """

    report = read_postman_report()

    if report is None:
        return None

    run = report.get("run", {})

    stats = run.get("stats", {})
    timings = run.get("timings", {})

    return {
        "total_requests": stats.get("requests", {}).get("total", 0),
        "failed_requests": stats.get("requests", {}).get("failed", 0),
        "total_assertions": stats.get("assertions", {}).get("total", 0),
        "failed_assertions": stats.get("assertions", {}).get("failed", 0),
        "average_response_time": timings.get("responseAverage", 0),
    }