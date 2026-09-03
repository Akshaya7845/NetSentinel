import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests


class ScaleTester:
    """
    Week 15 large-scale monitoring simulation.

    Tests the currently implemented NetSentinel FastAPI
    endpoints using concurrent requests and calculates:
    - Average latency
    - P95 latency
    - P99 latency
    - Error rate
    - Requests per second
    """

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.results = []
        self.errors = []
        self.start_time = None

        os.makedirs(
            "monitoring/reports/scale_tests",
            exist_ok=True
        )

    def _single_request(self, endpoint, request_id):
        """Execute one HTTP request and capture its result."""
        try:
            start = time.time()

            response = requests.get(
                f"{self.base_url}{endpoint}",
                timeout=10
            )

            latency = (time.time() - start) * 1000

            return {
                "request_id": request_id,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "latency_ms": round(latency, 2),
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as error:
            return {
                "request_id": request_id,
                "endpoint": endpoint,
                "status_code": 0,
                "latency_ms": 9999,
                "success": False,
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
            }

    def run_concurrent_load(
        self,
        endpoint,
        concurrent_users=10,
        total_requests=50
    ):
        """
        Execute concurrent requests against one endpoint.
        """

        print("\n" + "-" * 60)
        print(f"Load Test: {endpoint}")
        print(
            f"Concurrent Users: {concurrent_users} | "
            f"Requests: {total_requests}"
        )

        self.start_time = time.time()
        results = []

        with ThreadPoolExecutor(
            max_workers=concurrent_users
        ) as executor:

            futures = [
                executor.submit(
                    self._single_request,
                    endpoint,
                    request_id
                )
                for request_id in range(total_requests)
            ]

            for future in as_completed(futures):
                results.append(future.result())

        total_time = time.time() - self.start_time

        successful = sum(
            1 for result in results
            if result["success"]
        )

        failed = total_requests - successful

        latencies = sorted(
            result["latency_ms"]
            for result in results
            if result["success"]
        )

        if latencies:
            avg_latency = sum(latencies) / len(latencies)

            p95_index = min(
                int(len(latencies) * 0.95),
                len(latencies) - 1
            )

            p99_index = min(
                int(len(latencies) * 0.99),
                len(latencies) - 1
            )

            p95_latency = latencies[p95_index]
            p99_latency = latencies[p99_index]
            min_latency = latencies[0]
            max_latency = latencies[-1]

        else:
            avg_latency = 0
            p95_latency = 0
            p99_latency = 0
            min_latency = 0
            max_latency = 0

        error_rate = (
            failed / total_requests * 100
            if total_requests
            else 0
        )

        requests_per_second = (
            total_requests / total_time
            if total_time > 0
            else 0
        )

        summary = {
            "endpoint": endpoint,
            "concurrent_users": concurrent_users,
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "error_rate_pct": round(error_rate, 2),
            "total_time_sec": round(total_time, 2),
            "req_per_sec": round(requests_per_second, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "p99_latency_ms": round(p99_latency, 2),
            "min_latency_ms": round(min_latency, 2),
            "max_latency_ms": round(max_latency, 2),
            "timestamp": datetime.now().isoformat(),
        }

        status = (
            "PASS"
            if error_rate < 5
            else "FAIL"
        )

        print(
            f"Result: {status} | "
            f"Avg: {avg_latency:.2f} ms | "
            f"P95: {p95_latency:.2f} ms | "
            f"P99: {p99_latency:.2f} ms | "
            f"Errors: {error_rate:.2f}%"
        )

        return summary

    def run_all_endpoints_scale_test(self):
        """
        Run a moderate large-scale simulation across
        the currently implemented NetSentinel endpoints.
        """

        print("\n" + "=" * 60)
        print("NETSENTINEL WEEK 15 LARGE-SCALE SIMULATION")
        print(
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        print("=" * 60)

        endpoints = [
            ("/health", 10, 50),
            ("/metrics", 10, 50),
            ("/performance/summary", 10, 50),
            ("/performance/all", 10, 50),
            ("/network/status", 10, 50),
            ("/postman/summary", 5, 25),
            ("/networkwatcher/summary", 5, 25),
            ("/ai/quality-report", 3, 10),
        ]

        endpoint_results = []

        for endpoint, users, request_count in endpoints:

            result = self.run_concurrent_load(
                endpoint,
                concurrent_users=users,
                total_requests=request_count
            )

            endpoint_results.append(result)

            time.sleep(1)

        total_requests = sum(
            result["total_requests"]
            for result in endpoint_results
        )

        total_failed = sum(
            result["failed"]
            for result in endpoint_results
        )

        overall_error_rate = (
            total_failed / total_requests * 100
            if total_requests
            else 0
        )

        avg_latency = (
            sum(
                result["avg_latency_ms"]
                for result in endpoint_results
            )
            / len(endpoint_results)
            if endpoint_results
            else 0
        )

        overall = {
            "test_type": "large_scale_simulation",
            "test_at": datetime.now().isoformat(),
            "total_endpoints": len(endpoint_results),
            "total_requests": total_requests,
            "total_failed": total_failed,
            "overall_error_rate": round(
                overall_error_rate,
                2
            ),
            "avg_latency_ms": round(
                avg_latency,
                2
            ),
            "system_verdict": (
                "STABLE"
                if overall_error_rate < 5
                else "UNSTABLE"
            ),
            "endpoint_results": endpoint_results,
        }

        output_path = (
            "monitoring/reports/scale_tests/"
            "large_scale_results.json"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                overall,
                file,
                indent=2
            )

        print("\n" + "=" * 60)
        print("SCALE TEST COMPLETE")
        print("=" * 60)
        print(
            f"Total Requests: {total_requests}"
        )
        print(
            f"Total Failed:   {total_failed}"
        )
        print(
            f"Error Rate:     "
            f"{overall['overall_error_rate']}%"
        )
        print(
            f"Average Latency:"
            f" {overall['avg_latency_ms']} ms"
        )
        print(
            f"System Verdict: "
            f"{overall['system_verdict']}"
        )
        print(
            f"Results Saved:  {output_path}"
        )

        return overall

    def run_stress_test(self):
        """
        Gradually increase concurrent users
        against the lightweight health endpoint.
        """

        print("\n" + "=" * 60)
        print("NETSENTINEL WEEK 15 STRESS TEST")
        print("=" * 60)

        stress_levels = [10, 25, 50, 75, 100]
        results = []

        for users in stress_levels:

            print(
                f"\nStress Level: "
                f"{users} concurrent users"
            )

            result = self.run_concurrent_load(
                "/health",
                concurrent_users=users,
                total_requests=users * 5
            )

            verdict = (
                "STABLE"
                if result["error_rate_pct"] < 5
                else "BREAKING"
            )

            results.append({
                "concurrent_users": users,
                "error_rate": result[
                    "error_rate_pct"
                ],
                "avg_latency": result[
                    "avg_latency_ms"
                ],
                "p95_latency": result[
                    "p95_latency_ms"
                ],
                "verdict": verdict,
            })

            if result["error_rate_pct"] > 20:
                print(
                    "System stress threshold reached."
                )
                break

        stable_levels = [
            result["concurrent_users"]
            for result in results
            if result["verdict"] == "STABLE"
        ]

        breaking_levels = [
            result["concurrent_users"]
            for result in results
            if result["verdict"] == "BREAKING"
        ]

        summary = {
            "test_type": "stress_test",
            "test_at": datetime.now().isoformat(),
            "breaking_point": (
                breaking_levels[0]
                if breaking_levels
                else None
            ),
            "max_stable_users": (
                max(stable_levels)
                if stable_levels
                else 0
            ),
            "stress_levels": results,
        }

        output_path = (
            "monitoring/reports/scale_tests/"
            "stress_test_results.json"
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                summary,
                file,
                indent=2
            )

        print("\nStress Test Complete")
        print(
            f"Maximum Stable Users: "
            f"{summary['max_stable_users']}"
        )
        print(
            f"Breaking Point: "
            f"{summary['breaking_point'] or 'Not reached'}"
        )
        print(
            f"Results Saved: {output_path}"
        )

        return summary

    def run_k6_large_scale(self):
        """
        Run a controlled k6 load test.
        """

        print("\n" + "=" * 60)
        print("NETSENTINEL WEEK 15 K6 LOAD TEST")
        print("=" * 60)

        k6_script = """
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('large_scale_errors');
const latency = new Trend('large_scale_latency');

export const options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '20s', target: 25 },
    { duration: '20s', target: 10 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<2000'],
    large_scale_errors: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:8000';

const ENDPOINTS = [
  '/health',
  '/metrics',
  '/performance/summary',
  '/network/status',
];

export default function () {
  const endpoint =
    ENDPOINTS[
      Math.floor(Math.random() * ENDPOINTS.length)
    ];

  const response = http.get(
    `${BASE_URL}${endpoint}`
  );

  latency.add(
    response.timings.duration
  );

  errorRate.add(
    response.status !== 200
  );

  check(response, {
    'status OK': (r) => r.status === 200,
    'latency < 2s':
      (r) => r.timings.duration < 2000,
  });

  sleep(0.5);
}

export function handleSummary(data) {
  return {
    'monitoring/reports/scale_tests/k6_large_scale.json':
      JSON.stringify(data, null, 2),
  };
}
"""

        script_path = (
            "monitoring/k6/"
            "large-scale-test.js"
        )

        with open(
            script_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(k6_script)

        try:
            result = subprocess.run(
                [
                    "k6",
                    "run",
                    script_path
                ],
                capture_output=True,
                text=True,
                timeout=180
            )

            print(
                "k6 execution completed."
            )

            return {
                "status": "completed",
                "success": result.returncode == 0,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-1000:],
            }

        except FileNotFoundError:

            print(
                "k6 is not installed. "
                "k6 test skipped."
            )

            return {
                "status": "skipped",
                "reason": "k6 not found",
            }

        except Exception as error:

            return {
                "status": "error",
                "error": str(error),
            }


if __name__ == "__main__":

    tester = ScaleTester()

    tester.run_all_endpoints_scale_test()

    tester.run_stress_test()

    tester.run_k6_large_scale()

    print(
        "\nWeek 15 scale testing completed."
    )
