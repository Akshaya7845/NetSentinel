from datetime import datetime
from pathlib import Path
import time

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.models.network_status import NetworkStatus
from src.models.performance_summary import PerformanceSummary
from src.models.postman_summary import PostmanSummary

from src.services.docker_service import get_container_status

from src.services.k6_service import (
    get_smoke_summary,
    get_latency_summary,
    get_load_summary,
)

from src.services.postman_service import get_postman_summary
from src.services.network_watcher_service import check_connectivity

from src.services.database_service import DatabaseService

from src.ai.report_generator import ReportGenerator

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


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="NetSentinel API",
    description="Backend API for the NetSentinel Intelligent Network Testing Platform",
    version="1.0.0",
)


# ============================================================
# Database Service
# ============================================================

db = DatabaseService()


# ============================================================
# Prometheus HTTP Request Middleware
# ============================================================

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):

    start_time = time.time()

    response = await call_next(request)

    elapsed_time = time.time() - start_time

    REQUEST_COUNT.inc()
    REQUEST_LATENCY.observe(elapsed_time)

    return response


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def home():

    return {
        "application": "NetSentinel",
        "message": "Welcome to NetSentinel API",
        "status": "running",
    }


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "NetSentinel API",
    }


# ============================================================
# Login Endpoint
# ============================================================

@app.get("/login")
def login():

    return {
        "service": "Login API",
        "status": "Authentication Successful",
    }


# ============================================================
# Products Endpoint
# ============================================================

@app.get("/products")
def products():

    return {
        "service": "Product API",
        "status": "Products Retrieved",
    }


# ============================================================
# Payment Endpoint
# ============================================================

@app.get("/payment")
def payment():

    return {
        "service": "Payment API",
        "status": "Payment Service Available",
    }


# ============================================================
# Prometheus Metrics Endpoint
# ============================================================

@app.get("/metrics")
def metrics():

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# ============================================================
# Database Health
# ============================================================

@app.get("/database/health")
def database_health():

    try:

        connected = db.test_connection()

        return {
            "status": "healthy" if connected else "unhealthy",
            "database": "PostgreSQL",
            "connected": connected,
        }

    except Exception as error:

        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
            "connected": False,
            "error": str(error),
        }


# ============================================================
# Database Tables
# ============================================================

@app.get("/database/tables")
def database_tables():

    try:

        tables = db.get_tables()

        return {
            "status": "success",
            "tables": tables,
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error),
        }


# ============================================================
# Network Status
# ============================================================

@app.get(
    "/network/status",
    response_model=NetworkStatus,
)
def get_network_status():

    docker_status = get_container_status()

    return NetworkStatus(
        network="Healthy",
        api="Online",
        containers_running=docker_status["containers_running"],
        containers=docker_status["container_status"],
        timestamp=datetime.now(),
    )


# ============================================================
# K6 Performance Summary
# ============================================================

@app.get(
    "/performance/summary",
    response_model=PerformanceSummary,
)
def get_performance_summary():

    # --------------------------------------------------------
    # Start test run
    # --------------------------------------------------------

    run_id = db.start_test_run(
        "k6_latency_test",
        "k6",
    )

    try:

        # ----------------------------------------------------
        # Get k6 results
        # ----------------------------------------------------

        summary = get_latency_summary()

        # ----------------------------------------------------
        # Extract metrics safely
        # ----------------------------------------------------

        average_latency = float(
            summary.get("average_latency", 0)
        )

        p95_latency = float(
            summary.get("p95_latency", 0)
        )

        total_requests = int(
            summary.get("total_requests", 0)
        )

        failed_requests = int(
            summary.get("failed_requests", 0)
        )

        packet_loss = float(
            summary.get("packet_loss", 0)
        )

        error_rate = float(
            summary.get("error_rate", 0)
        )

        # ----------------------------------------------------
        # Update Prometheus metrics
        # ----------------------------------------------------

        K6_AVERAGE_LATENCY.set(
            average_latency
        )

        K6_P95_LATENCY.set(
            p95_latency
        )

        K6_TOTAL_REQUESTS.set(
            total_requests
        )

        K6_FAILED_REQUESTS.set(
            failed_requests
        )

        K6_PACKET_LOSS.set(
            packet_loss
        )

        K6_ERROR_RATE.set(
            error_rate
        )

        # ----------------------------------------------------
        # Store performance result in PostgreSQL
        # ----------------------------------------------------

        db.insert_performance_result(
            test_type="k6",
            average_latency=average_latency,
            p95_latency=p95_latency,
            total_requests=total_requests,
            failed_requests=failed_requests,
            packet_loss=packet_loss,
            error_rate=error_rate,
        )

        # ----------------------------------------------------
        # Complete test run
        # ----------------------------------------------------

        db.complete_test_run(run_id)

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return PerformanceSummary(
            average_latency=average_latency,
            p95_latency=p95_latency,
            total_requests=total_requests,
            failed_requests=failed_requests,
            packet_loss=packet_loss,
            error_rate=error_rate,
        )

    except Exception:

        # Do not send an incorrect COMPLETED status.
        # The existing DatabaseService only exposes
        # complete_test_run(), so the failed run remains
        # available for troubleshooting.

        raise


# ============================================================
# All K6 Performance Tests
# ============================================================

@app.get("/performance/all")
def get_all_performance():

    return {
        "smoke_test": get_smoke_summary(),
        "latency_test": get_latency_summary(),
        "load_test": get_load_summary(),
    }


# ============================================================
# Postman Summary
# ============================================================

@app.get(
    "/postman/summary",
    response_model=PostmanSummary,
)
def get_postman_summary_api():

    # --------------------------------------------------------
    # Start Postman test run
    # --------------------------------------------------------

    run_id = db.start_test_run(
        "postman_api_test",
        "postman",
    )

    try:

        # ----------------------------------------------------
        # Get Postman results
        # ----------------------------------------------------

        summary = get_postman_summary()

        # ----------------------------------------------------
        # Extract metrics safely
        # ----------------------------------------------------

        total_requests = int(
            summary.get("total_requests", 0)
        )

        failed_requests = int(
            summary.get("failed_requests", 0)
        )

        total_assertions = int(
            summary.get("total_assertions", 0)
        )

        failed_assertions = int(
            summary.get("failed_assertions", 0)
        )

        average_response_time = float(
            summary.get("average_response_time", 0)
        )

        # ----------------------------------------------------
        # Update Prometheus metrics
        # ----------------------------------------------------

        POSTMAN_TOTAL_REQUESTS.set(
            total_requests
        )

        POSTMAN_FAILED_REQUESTS.set(
            failed_requests
        )

        POSTMAN_TOTAL_ASSERTIONS.set(
            total_assertions
        )

        POSTMAN_FAILED_ASSERTIONS.set(
            failed_assertions
        )

        POSTMAN_AVERAGE_RESPONSE_TIME.set(
            average_response_time
        )

        # ----------------------------------------------------
        # Store Postman result in PostgreSQL
        # ----------------------------------------------------

        db.insert_postman_result(
            total_requests=total_requests,
            failed_requests=failed_requests,
            total_assertions=total_assertions,
            failed_assertions=failed_assertions,
            average_response_time=average_response_time,
        )

        # ----------------------------------------------------
        # Complete test run
        # ----------------------------------------------------

        db.complete_test_run(run_id)

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return PostmanSummary(
            total_requests=total_requests,
            failed_requests=failed_requests,
            total_assertions=total_assertions,
            failed_assertions=failed_assertions,
            average_response_time=average_response_time,
        )

    except Exception:

        raise


# ============================================================
# Network Watcher Summary
# ============================================================

@app.get("/networkwatcher/summary")
def get_networkwatcher_summary():

    # --------------------------------------------------------
    # Start network connectivity test
    # --------------------------------------------------------

    run_id = db.start_test_run(
        "network_connectivity_test",
        "network_watcher",
    )

    try:

        # ----------------------------------------------------
        # Run connectivity checks
        # ----------------------------------------------------

        results = check_connectivity()

        # ----------------------------------------------------
        # Store each connectivity result
        # ----------------------------------------------------

        for destination, result in results.items():

            status = result.get(
                "status",
                "Unknown",
            )

            latency_ms = float(
                result.get(
                    "response_time_ms",
                    0,
                )
            )

            packet_loss = 0

            # A non-reachable endpoint is treated
            # as 100% packet loss for this check.
            if status != "Reachable":
                packet_loss = 100

            db.insert_network_connectivity(
                source="NetSentinel",
                destination=destination,
                status=status,
                latency_ms=latency_ms,
                packet_loss=packet_loss,
            )

        # ----------------------------------------------------
        # Complete test run
        # ----------------------------------------------------

        db.complete_test_run(run_id)

        # ----------------------------------------------------
        # Return results
        # ----------------------------------------------------

        return results

    except Exception:

        raise


# ============================================================
# Test Run History
# ============================================================

@app.get("/test-runs")
def get_test_runs():

    try:

        runs = db.get_test_runs()

        return {
            "test_runs": runs,
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error),
        }


# ============================================================
# AI Executive Summary
# ============================================================

@app.get("/ai/executive-summary")
def get_executive_summary():

    generator = ReportGenerator()

    reports = generator.generate_reports()

    executive_file = reports[
        "executive_summary"
    ]

    if not executive_file.exists():

        return {
            "status": "error",
            "message": "Executive Summary report was not found.",
        }

    return {
        "status": "success",
        "report_type": "executive_summary",
        "report": executive_file.read_text(
            encoding="utf-8"
        ),
    }


# ============================================================
# AI Detailed Technical Report
# ============================================================

@app.get("/ai/detailed-report")
def get_detailed_report():

    generator = ReportGenerator()

    reports = generator.generate_reports()

    detailed_file = reports[
        "detailed_report"
    ]

    if not detailed_file.exists():

        return {
            "status": "error",
            "message": "Detailed Technical Report was not found.",
        }

    return {
        "status": "success",
        "report_type": "detailed_report",
        "report": detailed_file.read_text(
            encoding="utf-8"
        ),
    }