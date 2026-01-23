from fastapi import FastAPI
from pydantic import BaseModel
from app.tasks import add_numbers

# Create FastAPI app
app = FastAPI(
    title="FastAPI Celery Starter",
    description="A basic FastAPI app with Celery integration",
    version="0.1.0"
)


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
    return {
        "status": "healthy",
        "message": "FastAPI is running"
    }


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
    task = add_numbers.delay(request.a, request.b)
    
    return TaskResponse(
        task_id=task.id,
        status="submitted",
        message=f"Task to add {request.a} + {request.b} has been submitted"
    )


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to FastAPI Celery Starter",
        "endpoints": {
            "health": "/health - Health check endpoint",
            "add": "/add - POST endpoint to trigger addition task",
            "docs": "/docs - API documentation"
        }
    }
