
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY intelli_assist ./intelli_assist
COPY evals ./evals
COPY data ./data

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn intelli_assist.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
