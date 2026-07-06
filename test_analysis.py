from src.analytics.analysis_service import AnalysisService

analysis = AnalysisService()

df, postman = analysis.get_performance_dataframe()

print(df)

print("\nPostman Summary")
print(postman)

print("\nPerformance Statistics")
print(analysis.calculate_summary_statistics())

print("\nRolling Average")
print(analysis.calculate_rolling_average())

print("\nTrend Analysis")
print(analysis.calculate_trend_analysis())