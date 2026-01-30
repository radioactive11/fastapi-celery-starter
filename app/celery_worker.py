from celery import Celery
import time

from app.config import REDIS_URL
from app.metrics import (
    celery_tasks_completed_total,
    celery_task_duration_seconds,
    celery_queue_size
)

# Create Celery instance
celery_worker = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


@celery_worker.task(name="add")
def _add(x: int, y: int) -> int:
    """
    Add two numbers together.
    Tracks execution time and completion metrics.
    """
    task_name = "add"
    start_time = time.time()

    try:
        # Simulate some processing time for demo purposes
        time.sleep(0.1)

        result = x + y
        print(f"Adding {x} + {y} = {result}")

        # Record successful completion
        celery_tasks_completed_total.labels(
            task_name=task_name,
            status="success"
        ).inc()

        return result

    except Exception as e:
        # Record failed completion
        celery_tasks_completed_total.labels(
            task_name=task_name,
            status="failed"
        ).inc()
        raise

    finally:
        # Record task duration
        duration = time.time() - start_time
        celery_task_duration_seconds.labels(task_name=task_name).observe(duration)
