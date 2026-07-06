import pandas as pd

from src.services.k6_service import (
    get_smoke_summary,
    get_latency_summary,
    get_load_summary,
)

from src.services.postman_service import (
    get_postman_summary,
)


class AnalysisService:
    """
    Performs analytical calculations using
    k6 and Postman performance summaries.
    """

    def get_performance_dataframe(self):
        """
        Collects performance summaries and converts them
        into a Pandas DataFrame.
        """

        smoke = get_smoke_summary()
        latency = get_latency_summary()
        load = get_load_summary()
        postman = get_postman_summary()

        data = [
            {
                "test": "Smoke Test",
                **smoke,
            },
            {
                "test": "Latency Test",
                **latency,
            },
            {
                "test": "Load Test",
                **load,
            },
        ]

        df = pd.DataFrame(data)

        return df, postman

    def calculate_summary_statistics(self):
        """
        Calculates summary statistics from the performance DataFrame.
        """

        df, postman = self.get_performance_dataframe()

        summary = {
            "average_latency": round(df["average_latency"].mean(), 2),
            "maximum_latency": round(df["average_latency"].max(), 2),
            "minimum_latency": round(df["average_latency"].min(), 2),

            "average_p95_latency": round(df["p95_latency"].mean(), 2),

            "total_requests": int(df["total_requests"].sum()),
            "failed_requests": int(df["failed_requests"].sum()),

            "average_packet_loss": round(df["packet_loss"].mean(), 2),
            "average_error_rate": round(df["error_rate"].mean(), 2),

            "postman_average_response_time":
                postman["average_response_time"],

            "postman_total_requests":
                postman["total_requests"],
        }

        return summary
    
    def calculate_rolling_average(self):
        """
        Calculates rolling average latency.
        """

        df, _ = self.get_performance_dataframe()

        df["rolling_average_latency"] = (
            df["average_latency"]
            .rolling(window=2)
            .mean()
        )

        return df

    def calculate_trend_analysis(self):
        """
        Calculates latency change between consecutive tests.
        This can later be extended to week-over-week analysis.
        """

        df = self.calculate_rolling_average()

        df["latency_change"] = (
            df["average_latency"].diff()
        )

        df["latency_change_percent"] = (
            df["average_latency"].pct_change() * 100
        )

        return df