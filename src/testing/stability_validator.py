import json
from pathlib import Path
from datetime import datetime


class StabilityValidator:
    """
    Week 15 infrastructure stability validator.

    Validates scale-test and stress-test results against
    predefined stability thresholds.
    """

    def __init__(
        self,
        scale_file="monitoring/reports/scale_tests/large_scale_results.json",
        stress_file="monitoring/reports/scale_tests/stress_test_results.json",
        output_file="monitoring/reports/stability/stability_report.json",
    ):
        self.scale_file = Path(scale_file)
        self.stress_file = Path(stress_file)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def validate_scale(self):
        data = self.load_json(self.scale_file)

        error_rate = data.get("overall_error_rate", 100)
        latency = data.get("avg_latency_ms", 999999)

        return {
            "scale_test_available": True,
            "error_rate_below_5_percent": error_rate < 5,
            "average_latency_below_2000_ms": latency < 2000,
            "error_rate": error_rate,
            "average_latency_ms": latency,
        }

    def validate_stress(self):
        data = self.load_json(self.stress_file)

        levels = data.get("stress_levels", [])

        stable_levels = [
            level
            for level in levels
            if level.get("verdict") == "STABLE"
        ]

        breaking_levels = [
            level
            for level in levels
            if level.get("verdict") == "BREAKING"
        ]

        return {
            "stress_test_available": True,
            "stable_levels": len(stable_levels),
            "breaking_levels": len(breaking_levels),
            "max_stable_users": data.get(
                "max_stable_users",
                0
            ),
            "breaking_point": data.get(
                "breaking_point"
            ),
            "stress_test_stable": (
                len(stable_levels) > 0
                and len(breaking_levels) == 0
            ),
        }

    def validate(self):
        issues = []

        try:
            scale = self.validate_scale()
        except Exception as error:
            scale = {
                "scale_test_available": False,
                "error": str(error),
            }
            issues.append(
                f"Scale validation failed: {error}"
            )

        try:
            stress = self.validate_stress()
        except Exception as error:
            stress = {
                "stress_test_available": False,
                "error": str(error),
            }
            issues.append(
                f"Stress validation failed: {error}"
            )

        scale_pass = (
            scale.get("scale_test_available", False)
            and scale.get(
                "error_rate_below_5_percent",
                False
            )
            and scale.get(
                "average_latency_below_2000_ms",
                False
            )
        )

        stress_pass = (
            stress.get(
                "stress_test_available",
                False
            )
            and stress.get(
                "stress_test_stable",
                False
            )
        )

        overall_status = (
            "PASS"
            if scale_pass and stress_pass
            else "REVIEW"
        )

        report = {
            "test_type": "week15_stability_validation",
            "validated_at": datetime.now().isoformat(),
            "status": overall_status,
            "scale_validation": scale,
            "stress_validation": stress,
            "issues": issues,
        }

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=2
            )

        return report


if __name__ == "__main__":
    validator = StabilityValidator()
    result = validator.validate()

    print("\n" + "=" * 60)
    print("WEEK 15 STABILITY VALIDATION")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(
        f"Report: "
        f"{validator.output_file}"
    )
