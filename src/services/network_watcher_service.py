import json
import requests
import time
from pathlib import Path

SERVICES = {
    "login_api": "http://localhost:8000/login",
    "product_api": "http://localhost:8000/products",
    "payment_api": "http://localhost:8000/payment",
}


def check_connectivity():

    results = {}

    for service, url in SERVICES.items():

        start = time.time()

        try:
            response = requests.get(url, timeout=5)

            latency = round((time.time() - start) * 1000, 2)

            results[service] = {
                "status": "Reachable" if response.status_code == 200 else "Unreachable",
                "status_code": response.status_code,
                "response_time_ms": latency,
            }

        except Exception:

            results[service] = {
                "status": "Unreachable",
                "status_code": None,
                "response_time_ms": None,
            }

    report_dir = Path("monitoring/reports/networkwatcher")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / "networkwatcher-report.json"

    with open(report_file, "w") as file:
        json.dump(results, file, indent=4)

    return results