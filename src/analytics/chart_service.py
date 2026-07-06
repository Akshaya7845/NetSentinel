import matplotlib.pyplot as plt
from pathlib import Path

from src.analytics.analysis_service import AnalysisService


class ChartService:
    """
    Generates performance charts for NetSentinel.
    """

    def __init__(self):
        self.analysis = AnalysisService()

        self.output_folder = Path("monitoring/reports/charts")
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def generate_average_latency_chart(self):
        """
        Generates Average Latency chart.
        """

        df, _ = self.analysis.get_performance_dataframe()

        plt.figure(figsize=(8, 5))

        plt.bar(
            df["test"],
            df["average_latency"]
        )

        plt.title("Average Latency by Test")
        plt.xlabel("Test Type")
        plt.ylabel("Latency (ms)")

        plt.tight_layout()

        output_file = self.output_folder / "average_latency.png"

        plt.savefig(output_file)

        plt.close()

        return output_file

    def generate_chart(self, x, y, title, ylabel, filename):
        """
        Generates and saves a generic bar chart.
        """

        plt.figure(figsize=(8, 5))

        plt.bar(x, y)

        plt.title(title)
        plt.xlabel("Test Type")
        plt.ylabel(ylabel)

        plt.tight_layout()

        output_file = self.output_folder / filename

        plt.savefig(output_file)

        plt.close()

        return output_file

    def generate_all_charts(self):
        """
        Generates all Week 7 analytical charts.
        """

        df, _ = self.analysis.get_performance_dataframe()

        # Average Latency
        self.generate_chart(
            df["test"],
            df["average_latency"],
            "Average Latency by Test",
            "Latency (ms)",
            "average_latency.png",
        )

        # P95 Latency
        self.generate_chart(
            df["test"],
            df["p95_latency"],
            "P95 Latency by Test",
            "Latency (ms)",
            "p95_latency.png",
        )

        # Total Requests
        self.generate_chart(
            df["test"],
            df["total_requests"],
            "Total Requests by Test",
            "Requests",
            "total_requests.png",
        )

        # Packet Loss
        self.generate_chart(
            df["test"],
            df["packet_loss"],
            "Packet Loss by Test",
            "Packet Loss (%)",
            "packet_loss.png",
        )

        # Error Rate
        self.generate_chart(
            df["test"],
            df["error_rate"],
            "Error Rate by Test",
            "Error Rate (%)",
            "error_rate.png",
        )

        print("All charts generated successfully!")