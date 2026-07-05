from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
from src.models.network_status import NetworkStatus
from src.services.docker_service import get_container_status
import time
from src.models.performance_summary import PerformanceSummary
from src.services.k6_service import (
    get_smoke_summary,
    get_latency_summary,
    get_load_summary,
)
from src.models.postman_summary import PostmanSummary
from src.services.postman_service import get_postman_summary
from src.services.network_watcher_service import check_connectivity

from src.metrics.prometheus_metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,

    K6_AVERAGE_LATENCY,
    K6_P95_LATENCY,
    K6_TOTAL_REQUESTS,
    K6_FAILED_REQUESTS,
    K6_PACKET_LOSS,
    K6_ERROR_RATE,

    POSTMAN_TOTAL_REQUESTS,
    POSTMAN_FAILED_REQUESTS,
    POSTMAN_TOTAL_ASSERTIONS,
    POSTMAN_FAILED_ASSERTIONS,
    POSTMAN_AVERAGE_RESPONSE_TIME,
)
# Create the FastAPI application
app = FastAPI(
    title="NetSentinel API",
    description="Backend API for the NetSentinel Monitoring Platform",
    version="1.0.0"
)

# Middleware to collect Prometheus metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    REQUEST_COUNT.inc()
    REQUEST_LATENCY.observe(time.time() - start_time)

    return response

# Root endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to NetSentinel API"
    }

# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
@app.get("/login")
def login():
    return {
        "service": "Login API",
        "status": "Authentication Successful"
    }


@app.get("/products")
def products():
    return {
        "service": "Product API",
        "status": "Products Retrieved"
    }


@app.get("/payment")
def payment():
    return {
        "service": "Payment API",
        "status": "Payment Service Available"
    }
# ==========================================
# Prometheus Metrics Endpoint
# ==========================================
@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
# ==========================================
# Network Status API Endpoint
# ==========================================
@app.get("/network/status", response_model=NetworkStatus)
def get_network_status():

    docker_status = get_container_status()

    return NetworkStatus(
        network="Healthy",
        api="Online",
        containers_running=docker_status["containers_running"],
        containers=docker_status["container_status"],
        timestamp=datetime.now()
    )
# ==========================================
# Performance Summary API Endpoint
# ==========================================
@app.get("/performance/summary", response_model=PerformanceSummary)
def get_performance_summary():

    summary = get_latency_summary()

    K6_AVERAGE_LATENCY.set(summary["average_latency"])
    K6_P95_LATENCY.set(summary["p95_latency"])
    K6_TOTAL_REQUESTS.set(summary["total_requests"])
    K6_FAILED_REQUESTS.set(summary["failed_requests"])

# New Week 6 Metrics
    K6_PACKET_LOSS.set(summary["packet_loss"])
    K6_ERROR_RATE.set(summary["error_rate"])

    return PerformanceSummary(
    average_latency=summary["average_latency"],
    p95_latency=summary["p95_latency"],
    total_requests=summary["total_requests"],
    failed_requests=summary["failed_requests"],
    packet_loss=summary["packet_loss"],
    error_rate=summary["error_rate"],
)
@app.get("/performance/all")
def get_all_performance():

    return {
        "smoke_test": get_smoke_summary(),
        "latency_test": get_latency_summary(),
        "load_test": get_load_summary(),
    }
# ==========================================
# Postman Summary API Endpoint
# ==========================================
@app.get("/postman/summary", response_model=PostmanSummary)
def get_postman_summary_api():

    summary = get_postman_summary()
    POSTMAN_TOTAL_REQUESTS.set(summary["total_requests"])
    POSTMAN_FAILED_REQUESTS.set(summary["failed_requests"])
    POSTMAN_TOTAL_ASSERTIONS.set(summary["total_assertions"])
    POSTMAN_FAILED_ASSERTIONS.set(summary["failed_assertions"])
    POSTMAN_AVERAGE_RESPONSE_TIME.set(summary["average_response_time"])

    return PostmanSummary(
        total_requests=summary["total_requests"],
        failed_requests=summary["failed_requests"],
        total_assertions=summary["total_assertions"],
        failed_assertions=summary["failed_assertions"],
        average_response_time=summary["average_response_time"],
    )
@app.get("/networkwatcher/summary")
def get_networkwatcher_summary():
    return check_connectivity()