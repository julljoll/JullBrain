# Multi-stage Dockerfile — JullBrain Enterprise Legal Platform (FastAPI + Open WebUI Backend)
# Compatible con Podman / OCI Standards

# ---------------------------------------------------------
# ETAPA 1: Builder (Compilaciones y dependencias de Python)
# ---------------------------------------------------------
FROM python:3.11-slim AS builder

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
# ETAPA 2: Runner (Entorno de Ejecución Mínimo de Producción)
# ---------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8050

# Dependencias mínimas de ejecución del sistema (Tesseract OCR en Español + libmupdf)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libmupdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar entorno virtual de Python precompilado
COPY --from=builder /opt/venv /opt/venv

# Copiar el código fuente completo de la aplicación
COPY . /app

# Crear usuario no-root por seguridad (Rootless Podman execution)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8050

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8050/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8050"]
