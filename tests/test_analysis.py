from src.analytics.analysis_service import AnalysisService
from src.analytics.chart_service import ChartService


analysis = AnalysisService()
charts = ChartService()


def test_performance_dataframe():
    """
    Verify the performance DataFrame is created correctly.
    """

    df, postman = analysis.get_performance_dataframe()

    assert not df.empty
    assert len(df) == 3
    assert "average_latency" in df.columns
    assert isinstance(postman, dict)


def test_summary_statistics():
    """
    Verify summary statistics are generated.
    """

    summary = analysis.calculate_summary_statistics()

    assert summary["average_latency"] > 0
    assert summary["total_requests"] > 0
    assert summary["failed_requests"] >= 0


def test_rolling_average():
    """
    Verify rolling average calculation.
    """

    df = analysis.calculate_rolling_average()

    assert "rolling_average_latency" in df.columns


def test_trend_analysis():
    """
    Verify trend analysis calculation.
    """

    df = analysis.calculate_trend_analysis()

    assert "latency_change" in df.columns
    assert "latency_change_percent" in df.columns


def test_chart_generation():
    """
    Verify all charts are generated.
    """

    charts.generate_all_charts()