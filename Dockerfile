
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install CPU-only PyTorch to avoid unnecessary GPU dependencies.
RUN pip install --no-cache-dir \
    torch \
    --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -c "import fastembed; print('FastEmbed installed successfully')"

# Copy the application, knowledge base and existing FAISS index.
COPY . .

EXPOSE 10000

CMD ["sh", "-c", "uvicorn intelli_assist.api:app --host 0.0.0.0 --port ${PORT:-10000}"]
