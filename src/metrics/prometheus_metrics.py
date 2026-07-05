from prometheus_client import Counter, Histogram

# Count the total number of HTTP requests
REQUEST_COUNT = Counter(
    "netsentinel_http_requests_total",
    "Total number of HTTP requests"
)

# Measure how long requests take to process
REQUEST_LATENCY = Histogram(
    "netsentinel_http_request_duration_seconds",
    "HTTP request latency in seconds"
)
from prometheus_client import Gauge

# ==========================================
# k6 Performance Metrics
# ==========================================

K6_AVERAGE_LATENCY = Gauge(
    "netsentinel_k6_average_latency_ms",
    "Average latency from k6 report"
)

K6_P95_LATENCY = Gauge(
    "netsentinel_k6_p95_latency_ms",
    "95th percentile latency from k6 report"
)

K6_TOTAL_REQUESTS = Gauge(
    "netsentinel_k6_total_requests",
    "Total requests executed by k6"
)

K6_FAILED_REQUESTS = Gauge(
    "netsentinel_k6_failed_requests",
    "Failed requests reported by k6"
)
from prometheus_client import Gauge

POSTMAN_TOTAL_REQUESTS = Gauge(
    "netsentinel_postman_total_requests",
    "Total requests executed by Postman"
)

POSTMAN_FAILED_REQUESTS = Gauge(
    "netsentinel_postman_failed_requests",
    "Failed requests reported by Postman"
)

POSTMAN_TOTAL_ASSERTIONS = Gauge(
    "netsentinel_postman_total_assertions",
    "Total assertions executed by Postman"
)

POSTMAN_FAILED_ASSERTIONS = Gauge(
    "netsentinel_postman_failed_assertions",
    "Failed assertions reported by Postman"
)

POSTMAN_AVERAGE_RESPONSE_TIME = Gauge(
    "netsentinel_postman_average_response_time_ms",
    "Average response time from Postman"
)