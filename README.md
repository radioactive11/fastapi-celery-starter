# FastAPI Celery Starter

A basic FastAPI application with Celery integration for asynchronous task processing.

## Features

- ✅ Health check endpoint
- ✅ Celery task for adding two numbers
- ✅ Redis as message broker
- ✅ Environment-based configuration
- ✅ Python package management with uv
- ✅ Dockerized application

## Prerequisites

- Python 3.9+
- Redis server
- uv (Python package manager)
- Docker (optional, for containerized deployment)

## Installation

### 1. Install uv

```bash
pip install uv
```

### 2. Clone the repository

```bash
git clone https://github.com/radioactive11/fastapi-celery-starter.git
cd fastapi-celery-starter
```

### 3. Create and configure .env file

```bash
cp .env.example .env
```

Edit `.env` and set your Redis URL:
```
REDIS_URL=redis://localhost:6379/0
```

### 4. Install dependencies

```bash
uv pip install -r pyproject.toml
```

## Running the Application

### Start Redis

Make sure Redis is running on your system:

```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or using your system's Redis
redis-server
```

### Start FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Start Celery Worker

In a separate terminal:

```bash
celery -A app.celery_app worker --loglevel=info
```

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "message": "FastAPI is running"
}
```

### Add Numbers (Trigger Celery Task)
```bash
POST /add
Content-Type: application/json

{
  "a": 5,
  "b": 3
}
```

Response:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "submitted",
  "message": "Task to add 5 + 3 has been submitted"
}
```

The result will be printed in the Celery worker logs.

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker Deployment

### Build the Docker image

```bash
docker build -t fastapi-celery-starter .
```

### Run with Docker

You'll need to run both the FastAPI server and Celery worker:

```bash
# Run Redis
docker run -d --name redis -p 6379:6379 redis:latest

# Run FastAPI server
docker run -d --name fastapi-app \
  -p 8000:8000 \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  fastapi-celery-starter

# Run Celery worker
docker run -d --name celery-worker \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  fastapi-celery-starter \
  celery -A app.celery_app worker --loglevel=info
```

## Project Structure

```
fastapi-celery-starter/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── celery_app.py     # Celery configuration
│   ├── tasks.py          # Celery tasks
│   └── config.py         # Configuration management
├── .env.example          # Example environment variables
├── .gitignore
├── Dockerfile            # Docker configuration
├── pyproject.toml        # Project dependencies (uv)
└── README.md
```

## Development

### Testing the endpoints

```bash
# Health check
curl http://localhost:8000/health

# Trigger add task
curl -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 20}'
```

## License

MIT License