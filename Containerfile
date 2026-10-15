# Multi-stage Containerfile — JullBrain Enterprise Legal Platform (FastAPI + Open WebUI Backend)
# Estándar OCI nativo para Podman / Red Hat Enterprise Linux

FROM python:3.11-slim AS builder

LABEL org.opencontainers.image.title="JullBrain Enterprise Legal Platform" \
      org.opencontainers.image.description="API Backend Enterprise de Inteligencia Documental Legal para Open WebUI" \
      org.opencontainers.image.authors="Jull Ortiz <jullbrain@sha256.us>" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="2.0.0"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    git \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------
# ETAPA DE EJECUCIÓN (RUNNER)
# ---------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8050

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libmupdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY . /app

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8050

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8050/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8050"]
