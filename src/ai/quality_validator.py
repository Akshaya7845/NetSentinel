from pathlib import Path
import json
import re


class AIQualityValidator:
    """
    Week 14 deterministic validator for generated AI scenario reports.
    """

    REQUIRED_SCENARIOS = {
        "comparative_analysis_report.txt": "Comparative Analysis",
        "healthy_network_report.txt": "Healthy Network",
        "high_error_rate_report.txt": "High Error Rate",
        "high_latency_report.txt": "High Latency",
        "throughput_degradation_report.txt": "Throughput Degradation",
    }

    QUALITY_CHECKS = {
        "minimum_length": 200,
        "minimum_metric_matches": 3,
    }

    def __init__(
        self,
        report_folder="monitoring/reports/scenario_reports_v2",
    ):
        self.report_folder = Path(report_folder)

    def _check_report(self, report_path, scenario_name):
        """
        Validate a single AI-generated report.
        """

        result = {
            "scenario": scenario_name,
            "report_file": str(report_path),
            "status": "PASS",
            "score": 0,
            "checks": {},
            "issues": [],
        }

        if not report_path.exists():
            result["status"] = "FAIL"
            result["issues"].append("Report file does not exist.")
            return result

        text = report_path.read_text(
            encoding="utf-8",
            errors="replace",
        ).strip()

        checks = result["checks"]

        checks["file_exists"] = True

        checks["not_empty"] = bool(text)

        checks["minimum_length"] = (
            len(text) >= self.QUALITY_CHECKS["minimum_length"]
        )

        scenario_terms = {
            "Healthy Network": [
                "healthy",
                "baseline",
                "stable",
                "zero failures",
            ],
            "Comparative Analysis": [
                "baseline",
                "current",
                "comparison",
                "degraded",
            ],
            "High Error Rate": [
                "high error",
                "error rate",
                "failed requests",
            ],
            "High Latency": [
                "high latency",
                "latency spike",
                "latency",
            ],
            "Throughput Degradation": [
                "throughput",
                "degradation",
                "baseline",
            ],
        }

        expected_terms = scenario_terms.get(
            scenario_name,
            [scenario_name.lower()],
        )

        checks["scenario_mentioned"] = any(
            term.lower() in text.lower()
            for term in expected_terms
        )

        metric_keywords = [
            "latency",
            "p95",
            "error rate",
            "failed requests",
            "response time",
            "throughput",
        ]

        metric_matches = sum(
            1
            for keyword in metric_keywords
            if keyword.lower() in text.lower()
        )

        checks["metric_coverage"] = (
            metric_matches
            >= self.QUALITY_CHECKS["minimum_metric_matches"]
        )

        section_keywords = [
            "health",
            "analysis",
            "recommend",
            "conclusion",
        ]

        section_matches = sum(
            1
            for keyword in section_keywords
            if keyword.lower() in text.lower()
        )

        checks["structured_analysis"] = section_matches >= 3

        failure_patterns = [
            "api quota exceeded",
            "quota has been exceeded",
            "ai recommendation unavailable",
            "gemini quota",
            "error generating",
        ]

        checks["no_api_failure_message"] = not any(
            pattern in text.lower()
            for pattern in failure_patterns
        )

        suspicious_patterns = [
            r"\bI cannot\b",
            r"\bI don't have access\b",
            r"\bunable to analyze\b",
        ]

        checks["no_obvious_failure_text"] = not any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in suspicious_patterns
        )

        passed_checks = sum(
            1 for value in checks.values() if value
        )

        total_checks = len(checks)

        result["score"] = round(
            (passed_checks / total_checks) * 100,
            2,
        )

        if not checks["not_empty"]:
            result["issues"].append("Report is empty.")

        if not checks["minimum_length"]:
            result["issues"].append(
                "Report is shorter than the minimum expected length."
            )

        if not checks["scenario_mentioned"]:
            result["issues"].append(
                "Scenario name is not clearly mentioned."
            )

        if not checks["metric_coverage"]:
            result["issues"].append(
                "Insufficient network metric coverage."
            )

        if not checks["structured_analysis"]:
            result["issues"].append(
                "Report does not contain enough analytical sections."
            )

        if not checks["no_api_failure_message"]:
            result["issues"].append(
                "Report contains an API failure or quota message."
            )

        if not checks["no_obvious_failure_text"]:
            result["issues"].append(
                "Report contains an obvious AI failure message."
            )

        if result["score"] >= 80 and not result["issues"]:
            result["status"] = "PASS"
        else:
            result["status"] = "REVIEW"

        return result

    def validate_all(self):
        """
        Validate all expected Week 14 scenario reports.
        """

        results = []

        for filename, scenario_name in self.REQUIRED_SCENARIOS.items():
            report_path = self.report_folder / filename

            result = self._check_report(
                report_path,
                scenario_name,
            )

            results.append(result)

        passed = sum(
            1 for result in results
            if result["status"] == "PASS"
        )

        review = sum(
            1 for result in results
            if result["status"] == "REVIEW"
        )

        failed = sum(
            1 for result in results
            if result["status"] == "FAIL"
        )

        average_score = round(
            sum(result["score"] for result in results)
            / len(results),
            2,
        ) if results else 0

        return {
            "total_reports": len(results),
            "passed": passed,
            "review": review,
            "failed": failed,
            "average_quality_score": average_score,
            "reports": results,
        }

    def save_quality_report(
        self,
        output_file="monitoring/reports/ai_quality_report.json",
    ):
        """
        Validate all reports and save the quality report.
        """

        validation = self.validate_all()

        output_path = Path(output_file)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                validation,
                indent=4,
            ),
            encoding="utf-8",
        )

        return output_path, validation


if __name__ == "__main__":
    validator = AIQualityValidator()

    output_path, validation = (
        validator.save_quality_report()
    )

    print("===== WEEK 14 AI QUALITY VALIDATION =====")

    for report in validation["reports"]:
        print(
            f"{report['scenario']}: "
            f"{report['status']} "
            f"({report['score']}%)"
        )

    print()
    print(
        f"Total Reports: "
        f"{validation['total_reports']}"
    )
    print(
        f"Passed: "
        f"{validation['passed']}"
    )
    print(
        f"Review: "
        f"{validation['review']}"
    )
    print(
        f"Failed: "
        f"{validation['failed']}"
    )
    print(
        f"Average Quality Score: "
        f"{validation['average_quality_score']}%"
    )

    print(
        f"\nQuality report saved: "
        f"{output_path}"
    )
