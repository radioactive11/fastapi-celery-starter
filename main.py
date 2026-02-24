import random
import sys

import sentry_sdk
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

from app.celery_worker import _add
from app.metrics import (
    MetricsMiddleware,
    celery_tasks_submitted_total,
    metrics_response,
    random_number_gauge,
)

_GCP_LOG_FORMAT = (
    "{level:<.1}{time:MMDD HH:mm:ss.SSSSSS} {process} {name}:{line}] {message}"
)

logger.add(sys.stdout, format=_GCP_LOG_FORMAT, colorize=True, backtrace=False)

sentry_sdk.init(
    dsn="https://1e28884b84317bfe38881a70b233adf3@sentry.k8s.radioactive11.com/1",
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

# Create FastAPI app
app = FastAPI(
    title="FastAPI Celery Starter",
    description="A basic FastAPI app with Celery integration",
    version="0.1.0",
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)


class AddRequest(BaseModel):
    """Request model for add endpoint"""

    a: int
    b: int


class TaskResponse(BaseModel):
    """Response model for task submission"""

    task_id: str
    status: str
    message: str


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "very healthy", "message": "FastAPI is running"}


@app.post("/add", response_model=TaskResponse)
def trigger_add_task(request: AddRequest):
    """
    Endpoint to trigger a Celery task that adds two numbers.

    Args:
        request: AddRequest with two integers a and b

    Returns:
        TaskResponse with task_id and status
    """
    # Trigger the Celery task asynchronously
    task = _add.delay(request.a, request.b)

    # Track task submission in metrics
    celery_tasks_submitted_total.labels(task_name="add").inc()

    return TaskResponse(
        task_id=task.id,
        status="submitted",
        message=f"Task to add {request.a} + {request.b} has been submitted",
    )


@app.get("/random")
def get_random_number():
    """Generate a random number and push it to a Prometheus gauge metric."""
    value = random.randint(1, 100)
    random_number_gauge.set(value)
    return {"random_number": value}


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return metrics_response()


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to FastAPI Celery Starter",
        "endpoints": {
            "health": "/health - Health check endpoint",
            "add": "/add - POST endpoint to trigger addition task",
            "metrics": "/metrics - Prometheus metrics endpoint",
            "docs": "/docs - API documentation",
        },
    }


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


@app.get("/log")
def _log_all_variants():
    logger.debug("Debug log message")
    logger.info("Info log message")
    logger.warning("Warning log message")
    logger.error("Error log message")

    return {"message": "Logged messages at all levels"}
