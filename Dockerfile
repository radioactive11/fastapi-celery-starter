FROM python:3.12-slim-bullseye


RUN apt-get update -y \
    && apt-get install -y libpq-dev gcc \
    && pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./


ENV VIRTUAL_ENV=/app/.venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
RUN uv venv $VIRTUAL_ENV \
    && uv sync --locked


COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]