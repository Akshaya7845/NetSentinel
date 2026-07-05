from pydantic import BaseModel


class PostmanSummary(BaseModel):
    total_requests: int
    failed_requests: int
    total_assertions: int
    failed_assertions: int
    average_response_time: float