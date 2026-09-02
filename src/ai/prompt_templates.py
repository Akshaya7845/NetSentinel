from langchain_core.prompts import PromptTemplate


class ScenarioPromptTemplates:
    """
    LangChain prompt templates for NetSentinel Week 14
    multi-scenario AI analysis.
    """

    BASE_INSTRUCTIONS = """
You are a Senior Network Performance Engineer analyzing
automated NetSentinel network monitoring results.

Use only the metrics provided in the scenario.

Do not invent measurements or infrastructure details.

Focus on:
- latency
- P95 latency
- throughput when available
- error rate
- failed requests
- response time
- overall network health

Provide practical and technically reasonable recommendations.

Keep the response concise and structured.
"""

    @staticmethod
    def normal_baseline():
        return PromptTemplate.from_template(
            ScenarioPromptTemplates.BASE_INSTRUCTIONS
            + """
Scenario: Normal Baseline

Average Latency: {average_latency} ms
Maximum Latency: {maximum_latency} ms
Minimum Latency: {minimum_latency} ms
P95 Latency: {p95_latency} ms

Total Requests: {total_requests}
Failed Requests: {failed_requests}

Error Rate: {error_rate} %

Postman Response Time: {postman_response_time} ms

Analyze the baseline network condition.

Provide:

1. Overall Health
2. Performance Summary
3. Key Observations
4. Recommended Monitoring Actions
5. Final Conclusion
"""
        )

    @staticmethod
    def latency_spike():
        return PromptTemplate.from_template(
            ScenarioPromptTemplates.BASE_INSTRUCTIONS
            + """
Scenario: Latency Spike

Average Latency: {average_latency} ms
Maximum Latency: {maximum_latency} ms
Minimum Latency: {minimum_latency} ms
P95 Latency: {p95_latency} ms

Total Requests: {total_requests}
Failed Requests: {failed_requests}

Error Rate: {error_rate} %

Postman Response Time: {postman_response_time} ms

Analyze the latency degradation.

Identify:
1. Overall Health
2. Latency Impact
3. Possible Root Causes
4. Recommended Troubleshooting Actions
5. Final Conclusion

Clearly distinguish observed metrics from possible causes.
"""
        )

    @staticmethod
    def throughput_degradation():
        return PromptTemplate.from_template(
            ScenarioPromptTemplates.BASE_INSTRUCTIONS
            + """
Scenario: Throughput Degradation

Average Latency: {average_latency} ms
Maximum Latency: {maximum_latency} ms
Minimum Latency: {minimum_latency} ms
P95 Latency: {p95_latency} ms

Total Requests: {total_requests}
Failed Requests: {failed_requests}

Error Rate: {error_rate} %

Postman Response Time: {postman_response_time} ms

Current Throughput: {throughput_mbps} Mbps
Baseline Throughput: {baseline_throughput_mbps} Mbps

Analyze the throughput degradation.

Provide:

1. Overall Health
2. Throughput Analysis
3. Related Performance Indicators
4. Possible Causes
5. Optimization Recommendations
6. Final Conclusion

Do not claim a specific root cause unless the metrics support it.
"""
        )

    @staticmethod
    def high_error_rate():
        return PromptTemplate.from_template(
            ScenarioPromptTemplates.BASE_INSTRUCTIONS
            + """
Scenario: High Error Rate

Average Latency: {average_latency} ms
Maximum Latency: {maximum_latency} ms
Minimum Latency: {minimum_latency} ms
P95 Latency: {p95_latency} ms

Total Requests: {total_requests}
Failed Requests: {failed_requests}

Error Rate: {error_rate} %

Postman Response Time: {postman_response_time} ms

Analyze the high error-rate condition.

Provide:

1. Overall Health
2. Error Rate Analysis
3. Performance Impact
4. Possible Root Causes
5. Recommended Actions
6. Final Conclusion
"""
        )

    @staticmethod
    def comparative_analysis():
        return PromptTemplate.from_template(
            ScenarioPromptTemplates.BASE_INSTRUCTIONS
            + """
Scenario: Comparative Analysis

Current Metrics:

Average Latency: {average_latency} ms
Maximum Latency: {maximum_latency} ms
Minimum Latency: {minimum_latency} ms
P95 Latency: {p95_latency} ms

Total Requests: {total_requests}
Failed Requests: {failed_requests}

Error Rate: {error_rate} %

Postman Response Time: {postman_response_time} ms

Baseline Metrics:

Baseline Average Latency: {baseline_average_latency} ms
Baseline P95 Latency: {baseline_p95_latency} ms
Baseline Error Rate: {baseline_error_rate} %
Baseline Throughput: {baseline_throughput_mbps} Mbps

Current Throughput: {current_throughput_mbps} Mbps

Compare the current network performance against the baseline.

Provide:

1. Overall Health
2. Baseline vs Current Comparison
3. Major Performance Changes
4. Potential Areas of Concern
5. Recommended Actions
6. Final Conclusion

Clearly identify whether performance improved,
degraded, or remained stable.
"""
        )

    @classmethod
    def get_template(cls, scenario_name):
        """
        Return the appropriate LangChain prompt template
        for a scenario.
        """

        templates = {
            "Healthy Network": cls.normal_baseline(),
            "Normal Baseline": cls.normal_baseline(),
            "High Latency": cls.latency_spike(),
            "Latency Spike": cls.latency_spike(),
            "Throughput Degradation": cls.throughput_degradation(),
            "High Error Rate": cls.high_error_rate(),
            "Comparative Analysis": cls.comparative_analysis(),
        }

        if scenario_name not in templates:
            raise ValueError(
                f"Unsupported scenario: {scenario_name}"
            )

        return templates[scenario_name]
