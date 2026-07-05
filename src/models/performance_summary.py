from pydantic import BaseModel


class PerformanceSummary(BaseModel):
    average_latency: float
    p95_latency: float
    total_requests: int
    failed_requests: int