# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY app ./app

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Expose port for FastAPI
EXPOSE 8000

# Default command runs FastAPI server
# To run Celery worker instead, override with: celery -A app.celery_app worker --loglevel=info
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
