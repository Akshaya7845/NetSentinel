from src.analytics.analysis_service import AnalysisService


class PromptBuilder:
    """
    Builds prompts for Gemini AI using
    NetSentinel performance analytics.
    """

    def __init__(self):
        self.analysis = AnalysisService()

    def build_executive_prompt(self):
        """
        Builds a short executive summary prompt.
        """

        summary = self.analysis.calculate_summary_statistics()

        return f"""
You are a Senior Network Performance Engineer.

Analyze the following NetSentinel network performance metrics.

Average Latency: {summary['average_latency']} ms
Maximum Latency: {summary['maximum_latency']} ms
Minimum Latency: {summary['minimum_latency']} ms
Average P95 Latency: {summary['average_p95_latency']} ms

Total Requests: {summary['total_requests']}
Failed Requests: {summary['failed_requests']}

Average Packet Loss: {summary['average_packet_loss']} %
Average Error Rate: {summary['average_error_rate']} %

Postman Average Response Time:
{summary['postman_average_response_time']} ms

Generate an Executive Performance Summary.

Requirements:
- Maximum 8 bullet points.
- Under 200 words.
- Mention overall health.
- Mention important observations.
- Mention issues only if they exist.
- Provide 3 recommendations.
- Finish with one conclusion sentence.
"""

    def build_detailed_prompt(self):
        """
        Builds a detailed technical report prompt.
        """

        summary = self.analysis.calculate_summary_statistics()

        return f"""
You are an expert Network Performance Engineer.

Analyze the following NetSentinel performance metrics.

Average Latency: {summary['average_latency']} ms
Maximum Latency: {summary['maximum_latency']} ms
Minimum Latency: {summary['minimum_latency']} ms
Average P95 Latency: {summary['average_p95_latency']} ms

Total Requests: {summary['total_requests']}
Failed Requests: {summary['failed_requests']}

Average Packet Loss: {summary['average_packet_loss']} %
Average Error Rate: {summary['average_error_rate']} %

Postman Average Response Time:
{summary['postman_average_response_time']} ms

Provide a detailed engineering report containing:

1. Overall Network Health
2. Performance Observations
3. Potential Issues
4. Root Cause Analysis
5. Optimization Recommendations
6. Final Technical Conclusion

Explain your reasoning clearly using the metrics provided.
"""