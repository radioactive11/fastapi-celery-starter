from prometheus_client import Counter, Gauge, Histogram, Summary, Info, Enum, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

# Counter: Monotonically increasing counter
# Example: Count total HTTP requests
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

# Counter: Count Celery tasks submitted
celery_tasks_submitted_total = Counter(
    'celery_tasks_submitted_total',
    'Total number of Celery tasks submitted',
    ['task_name']
)

# Counter: Count Celery tasks completed
celery_tasks_completed_total = Counter(
    'celery_tasks_completed_total',
    'Total number of Celery tasks completed',
    ['task_name', 'status']
)

# Gauge: Last generated random number (for testing metric collection)
random_number_gauge = Gauge(
    'random_number_value',
    'Last generated random number'
)

# Gauge: Current active requests
active_requests = Gauge(
    'active_requests',
    'Number of active HTTP requests being processed'
)

# Gauge: Current queue size (simulated for demo)
celery_queue_size = Gauge(
    'celery_queue_size',
    'Current number of tasks in Celery queue',
    ['queue_name']
)

# Gauge: Active Celery workers
active_celery_workers = Gauge(
    'active_celery_workers',
    'Number of active Celery workers'
)

# Histogram: Request duration in seconds
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# Histogram: Task execution duration
celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task execution duration in seconds',
    ['task_name'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0)
)

# Summary: Request size in bytes
http_request_size_bytes = Summary(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

# Summary: Response size in bytes
http_response_size_bytes = Summary(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint']
)

# Info: Application information
app_info = Info(
    'app_info',
    'Application information'
)

# Set application info (call this once during startup)
app_info.info({
    'version': '0.1.0',
    'name': 'FastAPI Celery Starter',
    'environment': 'development'
})

# Enum: Application state
app_state = Enum(
    'app_state',
    'Current application state',
    states=['starting', 'running', 'degraded', 'maintenance']
)

# Set initial state
app_state.state('running')


# Helper function to generate metrics response
def metrics_response() -> Response:
    """Generate Prometheus metrics response"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Middleware helper to track request metrics
class MetricsMiddleware:
    """Middleware to automatically track HTTP request metrics"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Skip metrics endpoint to avoid recursion
        if scope["path"] == "/metrics":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        # Track active requests
        active_requests.inc()

        # Start timing
        start_time = time.time()

        # Track request size
        content_length = 0
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"content-length":
                content_length = int(header_value.decode())
                break

        if content_length > 0:
            http_request_size_bytes.labels(method=method, endpoint=path).observe(content_length)

        # Variables to capture response info
        status_code = 500  # Default to error
        response_size = 0

        async def send_wrapper(message):
            nonlocal status_code, response_size

            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                response_size += len(message.get("body", b""))

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            duration = time.time() - start_time

            # Decrement active requests
            active_requests.dec()

            # Record request count
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status=status_code
            ).inc()

            # Record request duration
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)

            # Record response size
            if response_size > 0:
                http_response_size_bytes.labels(
                    method=method,
                    endpoint=path
                ).observe(response_size)
