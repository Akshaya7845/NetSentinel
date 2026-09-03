import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.testing.scale_tester import ScaleTester
from src.testing.stability_validator import StabilityValidator


# =========================================================
# Week 15 - Scale Tester Tests
# =========================================================

def test_week15_scale_tester_initialization():
    tester = ScaleTester()

    assert tester.base_url == "http://localhost:8000"
    assert tester.results == []
    assert tester.errors == []


def test_week15_single_request_success():
    tester = ScaleTester()

    class MockResponse:
        status_code = 200

    with patch(
        "src.testing.scale_tester.requests.get",
        return_value=MockResponse()
    ):
        result = tester._single_request("/health", 1)

    assert result["request_id"] == 1
    assert result["endpoint"] == "/health"
    assert result["status_code"] == 200
    assert result["success"] is True
    assert result["latency_ms"] >= 0


def test_week15_single_request_failure():
    tester = ScaleTester()

    with patch(
        "src.testing.scale_tester.requests.get",
        side_effect=Exception("Connection failed")
    ):
        result = tester._single_request("/health", 1)

    assert result["request_id"] == 1
    assert result["status_code"] == 0
    assert result["success"] is False
    assert result["latency_ms"] == 9999
    assert "error" in result


def test_week15_concurrent_load_pass():
    tester = ScaleTester()

    class MockResponse:
        status_code = 200

    with patch(
        "src.testing.scale_tester.requests.get",
        return_value=MockResponse()
    ):
        result = tester.run_concurrent_load(
            "/health",
            concurrent_users=2,
            total_requests=5
        )

    assert result["endpoint"] == "/health"
    assert result["total_requests"] == 5
    assert result["successful"] == 5
    assert result["failed"] == 0
    assert result["error_rate_pct"] == 0
    assert result["p95_latency_ms"] >= 0
    assert result["p99_latency_ms"] >= 0


def test_week15_concurrent_load_failure():
    tester = ScaleTester()

    with patch(
        "src.testing.scale_tester.requests.get",
        side_effect=Exception("Connection failed")
    ):
        result = tester.run_concurrent_load(
            "/health",
            concurrent_users=2,
            total_requests=5
        )

    assert result["total_requests"] == 5
    assert result["successful"] == 0
    assert result["failed"] == 5
    assert result["error_rate_pct"] == 100
    assert result["avg_latency_ms"] == 0


def test_week15_zero_request_load():
    tester = ScaleTester()

    result = tester.run_concurrent_load(
        "/health",
        concurrent_users=2,
        total_requests=0
    )

    assert result["total_requests"] == 0
    assert result["failed"] == 0
    assert result["error_rate_pct"] == 0


# =========================================================
# Week 15 - Stability Validator Tests
# =========================================================

def test_week15_stability_validator_initialization():
    validator = StabilityValidator()

    assert validator.scale_file.exists()
    assert validator.stress_file.exists()
    assert validator.output_file.parent.exists()


def test_week15_load_json():
    validator = StabilityValidator()

    data = validator.load_json(validator.scale_file)

    assert isinstance(data, dict)
    assert data["test_type"] == "large_scale_simulation"


def test_week15_validate_scale():
    validator = StabilityValidator()

    result = validator.validate_scale()

    assert result["scale_test_available"] is True
    assert result["error_rate_below_5_percent"] is True
    assert result["average_latency_below_2000_ms"] is True
    assert result["error_rate"] == 0.0
    assert result["average_latency_ms"] < 2000
    assert result["average_latency_ms"] >= 0


def test_week15_validate_stress():
    validator = StabilityValidator()

    result = validator.validate_stress()

    assert result["stress_test_available"] is True
    assert result["stable_levels"] == 5
    assert result["breaking_levels"] == 0
    assert result["max_stable_users"] == 100
    assert result["breaking_point"] is None
    assert result["stress_test_stable"] is True


def test_week15_stability_validation_passes():
    validator = StabilityValidator()

    result = validator.validate()

    assert result["status"] == "PASS"
    assert result["issues"] == []


def test_week15_stability_report_exists():
    report_file = Path(
        "monitoring/reports/stability/stability_report.json"
    )

    assert report_file.exists()

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    assert report["status"] == "PASS"
    assert report["scale_validation"]["scale_test_available"] is True
    assert report["stress_validation"]["stress_test_available"] is True


# =========================================================
# Week 15 - Existing Evidence Tests
# =========================================================

def test_week15_large_scale_report_exists():
    report_file = Path(
        "monitoring/reports/scale_tests/large_scale_results.json"
    )

    assert report_file.exists()

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    assert report["total_endpoints"] == 8
    assert report["total_requests"] == 310
    assert report["total_failed"] == 0
    assert report["system_verdict"] == "STABLE"


def test_week15_stress_report_exists():
    report_file = Path(
        "monitoring/reports/scale_tests/stress_test_results.json"
    )

    assert report_file.exists()

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    assert report["max_stable_users"] == 100
    assert report["breaking_point"] is None
    assert len(report["stress_levels"]) == 5


def test_week15_k6_report_exists():
    report_file = Path(
        "monitoring/reports/scale_tests/k6_large_scale.json"
    )

    assert report_file.exists()

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    assert "metrics" in report
    assert "http_req_duration" in report["metrics"]
    assert "large_scale_errors" in report["metrics"]


def test_week15_k6_threshold_passed():
    report_file = Path(
        "monitoring/reports/scale_tests/k6_large_scale.json"
    )

    with open(
        report_file,
        "r",
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    threshold = report["metrics"]["http_req_duration"]["thresholds"]

    assert threshold["p(99)<2000"]["ok"] is True

    error_threshold = report["metrics"][
        "large_scale_errors"
    ]["thresholds"]

    assert error_threshold["rate<0.1"]["ok"] is True


# =========================================================
# Additional Coverage Tests
#
# IMPORTANT:
# These tests mock file writing so the real Week 15
# evidence reports are NEVER modified.
# =========================================================

def test_run_all_endpoints_scale_test():
    tester = ScaleTester()

    fake_result = {
        "total_requests": 10,
        "failed": 0,
        "error_rate_pct": 0.0,
        "avg_latency_ms": 100.0,
        "p95_latency_ms": 150.0,
        "p99_latency_ms": 180.0,
    }

    with patch.object(
        tester,
        "run_concurrent_load",
        return_value=fake_result
    ), patch(
        "src.testing.scale_tester.time.sleep"
    ), patch(
        "src.testing.scale_tester.json.dump"
    ) as mock_dump, patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_all_endpoints_scale_test()

    assert result["test_type"] == "large_scale_simulation"
    assert result["total_endpoints"] == 8
    assert result["total_requests"] == 80
    assert result["total_failed"] == 0
    assert result["overall_error_rate"] == 0.0
    assert result["avg_latency_ms"] == 100.0
    assert result["system_verdict"] == "STABLE"

    assert mock_dump.called


def test_run_all_endpoints_scale_test_with_failures():
    tester = ScaleTester()

    fake_result = {
        "total_requests": 10,
        "failed": 1,
        "error_rate_pct": 10.0,
        "avg_latency_ms": 100.0,
        "p95_latency_ms": 150.0,
        "p99_latency_ms": 180.0,
    }

    with patch.object(
        tester,
        "run_concurrent_load",
        return_value=fake_result
    ), patch(
        "src.testing.scale_tester.time.sleep"
    ), patch(
        "src.testing.scale_tester.json.dump"
    ) as mock_dump, patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_all_endpoints_scale_test()

    assert result["total_failed"] == 8
    assert result["overall_error_rate"] == 10.0
    assert result["system_verdict"] == "UNSTABLE"

    assert mock_dump.called


def test_run_stress_test_all_stable():
    tester = ScaleTester()

    fake_result = {
        "error_rate_pct": 0.0,
        "avg_latency_ms": 100.0,
        "p95_latency_ms": 150.0,
    }

    with patch.object(
        tester,
        "run_concurrent_load",
        return_value=fake_result
    ), patch(
        "src.testing.scale_tester.time.sleep"
    ), patch(
        "src.testing.scale_tester.json.dump"
    ) as mock_dump, patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_stress_test()

    assert result["test_type"] == "stress_test"
    assert result["max_stable_users"] == 100
    assert result["breaking_point"] is None
    assert len(result["stress_levels"]) == 5

    for level in result["stress_levels"]:
        assert level["verdict"] == "STABLE"

    assert mock_dump.called


def test_run_stress_test_breaking_threshold():
    tester = ScaleTester()

    def fake_load(
        endpoint,
        concurrent_users,
        total_requests
    ):
        if concurrent_users == 25:
            return {
                "error_rate_pct": 25.0,
                "avg_latency_ms": 500.0,
                "p95_latency_ms": 800.0,
            }

        return {
            "error_rate_pct": 0.0,
            "avg_latency_ms": 100.0,
            "p95_latency_ms": 150.0,
        }

    with patch.object(
        tester,
        "run_concurrent_load",
        side_effect=fake_load
    ), patch(
        "src.testing.scale_tester.time.sleep"
    ), patch(
        "src.testing.scale_tester.json.dump"
    ) as mock_dump, patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_stress_test()

    assert result["breaking_point"] == 25
    assert result["max_stable_users"] == 10
    assert len(result["stress_levels"]) == 2
    assert result["stress_levels"][1]["verdict"] == "BREAKING"

    assert mock_dump.called


def test_stress_test_breaking_verdict_without_early_break():
    tester = ScaleTester()

    fake_result = {
        "error_rate_pct": 10.0,
        "avg_latency_ms": 300.0,
        "p95_latency_ms": 500.0,
    }

    with patch.object(
        tester,
        "run_concurrent_load",
        return_value=fake_result
    ), patch(
        "src.testing.scale_tester.time.sleep"
    ), patch(
        "src.testing.scale_tester.json.dump"
    ) as mock_dump, patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_stress_test()

    assert result["breaking_point"] == 10
    assert result["max_stable_users"] == 0
    assert len(result["stress_levels"]) == 5

    for level in result["stress_levels"]:
        assert level["verdict"] == "BREAKING"

    assert mock_dump.called


# =========================================================
# k6 Coverage Tests
# =========================================================

def test_k6_file_not_found():
    tester = ScaleTester()

    with patch(
        "src.testing.scale_tester.subprocess.run",
        side_effect=FileNotFoundError
    ), patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_k6_large_scale()

    assert result["status"] == "skipped"
    assert result["reason"] == "k6 not found"


def test_k6_subprocess_failure():
    tester = ScaleTester()

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = "k6 failed"
    mock_result.stderr = "error"

    with patch(
        "src.testing.scale_tester.subprocess.run",
        return_value=mock_result
    ), patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_k6_large_scale()

    assert result["status"] == "completed"
    assert result["success"] is False
    assert result["stdout"] == "k6 failed"
    assert result["stderr"] == "error"


def test_k6_subprocess_success():
    tester = ScaleTester()

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "k6 success"
    mock_result.stderr = ""

    with patch(
        "src.testing.scale_tester.subprocess.run",
        return_value=mock_result
    ), patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_k6_large_scale()

    assert result["status"] == "completed"
    assert result["success"] is True


def test_k6_unexpected_exception():
    tester = ScaleTester()

    with patch(
        "src.testing.scale_tester.subprocess.run",
        side_effect=RuntimeError("unexpected error")
    ), patch(
        "builtins.open",
        MagicMock()
    ):

        result = tester.run_k6_large_scale()

    assert result["status"] == "error"
    assert "unexpected error" in result["error"]


# =========================================================
# Stability Validator Exception Coverage
# =========================================================

def test_stability_validate_scale_exception():
    validator = StabilityValidator()

    with patch.object(
        validator,
        "validate_scale",
        side_effect=RuntimeError("scale failure")
    ):

        result = validator.validate()

    assert result["status"] == "REVIEW"

    assert (
        result["scale_validation"][
            "scale_test_available"
        ]
        is False
    )

    assert (
        "scale failure"
        in result["scale_validation"]["error"]
    )

    assert any(
        "Scale validation failed" in issue
        for issue in result["issues"]
    )


def test_stability_validate_stress_exception():
    validator = StabilityValidator()

    with patch.object(
        validator,
        "validate_scale",
        return_value={
            "scale_test_available": True,
            "error_rate_below_5_percent": True,
            "average_latency_below_2000_ms": True,
        }
    ), patch.object(
        validator,
        "validate_stress",
        side_effect=RuntimeError("stress failure")
    ):

        result = validator.validate()

    assert result["status"] == "REVIEW"

    assert (
        result["stress_validation"][
            "stress_test_available"
        ]
        is False
    )

    assert (
        "stress failure"
        in result["stress_validation"]["error"]
    )

    assert any(
        "Stress validation failed" in issue
        for issue in result["issues"]
    )


def test_stability_validate_both_fail():
    validator = StabilityValidator()

    with patch.object(
        validator,
        "validate_scale",
        side_effect=RuntimeError("scale failure")
    ), patch.object(
        validator,
        "validate_stress",
        side_effect=RuntimeError("stress failure")
    ):

        result = validator.validate()

    assert result["status"] == "REVIEW"
    assert len(result["issues"]) == 2

    assert (
        result["scale_validation"][
            "scale_test_available"
        ]
        is False
    )

    assert (
        result["stress_validation"][
            "stress_test_available"
        ]
        is False
    )


def test_stability_validate_pass():
    validator = StabilityValidator()

    with patch.object(
        validator,
        "validate_scale",
        return_value={
            "scale_test_available": True,
            "error_rate_below_5_percent": True,
            "average_latency_below_2000_ms": True,
        }
    ), patch.object(
        validator,
        "validate_stress",
        return_value={
            "stress_test_available": True,
            "stress_test_stable": True,
        }
    ):

        result = validator.validate()

    assert result["status"] == "PASS"
    assert result["issues"] == []