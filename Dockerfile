<<<<<<< HEAD
# ==============================================================================
# JullBrain v0.2.0 — Dockerfile / Containerfile Nativo para Podman (Windows & Linux)
# Stack Exclusivo IBM (Docling CPU + Granite 3.3 + Granite Embedding R2 + Guardian)
# ==============================================================================
FROM docker.io/library/python:3.12-slim

LABEL maintainer="Jullierms (Jull) — JullBrain Legal-RAG"
LABEL org.opencontainers.image.title="JullBrain Legal-RAG (IBM Stack)"
LABEL org.opencontainers.image.version="0.2.0"
LABEL org.opencontainers.image.vendor="JullBrain"
LABEL io.containers.autoupdate="local"

# 1. Variables de Entorno Zero-Trust y Bóveda Local de Modelos IA
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    JULLBRAIN_ENV=podman \
    JULLBRAIN_PORT=8080 \
    JULLBRAIN_MODEL_VAULT=/app/RAG/modelos_ia \
    DOCLING_ARTIFACTS_PATH=/app/RAG/modelos_ia/docling \
    HF_HOME=/app/RAG/modelos_ia/huggingface \
    TORCH_HOME=/app/RAG/modelos_ia/torch \
    OLLAMA_MODELS=/app/RAG/modelos_ia/ollama \
    HF_HUB_DISABLE_TELEMETRY=1 \
    DO_NOT_TRACK=1 \
    ANONYMIZED_TELEMETRY=False \
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4

# 2. Dependencias del sistema para IBM Docling (CPU) y PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 3. Usuario no privilegiado compatible con Podman Rootless (--userns=keep-id)
RUN groupadd -g 10001 jullbrain && \
    useradd -u 10001 -g jullbrain -m -s /bin/bash jullbrain

WORKDIR /app

# 4. Instalación de dependencias Python (Stack IBM)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# 5. Copia del código fuente y estructura del núcleo RAG/
COPY --chown=jullbrain:jullbrain . /app

# Asegurar estructura de directorios del núcleo RAG y permisos para Podman rootless
RUN mkdir -p \
    /app/RAG/datos_brutos \
    /app/RAG/Informacion_docling_rag \
    /app/RAG/normativas_chunks \
    /app/RAG/modelos_ia/docling \
    /app/RAG/modelos_ia/granite_embeddings \
    /app/RAG/modelos_ia/granite_llm \
    /app/RAG/modelos_ia/granite_guardian \
    /app/RAG/modelos_ia/huggingface \
    /app/RAG/modelos_ia/torch \
    /app/RAG/modelos_ia/ollama \
    /app/RAG/notebooks_db \
    /app/RAG/lightrag_db \
    /app/logs && \
    chown -R jullbrain:jullbrain /app && \
    chmod -R g+rwX /app/RAG /app/logs

USER jullbrain

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8080/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
=======
# Dockerfile — JullBrain Legal-RAG Pipeline (Terminal Mode)
FROM python:3.11-slim

LABEL maintainer="JullBrain Team"
LABEL description="JullBrain Legal-RAG Pipeline — IBM Docling + Granite"
LABEL version="0.1.0"

WORKDIR /app

# Instalar dependencias del sistema para procesamiento de PDF y OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código del pipeline
COPY common_utils.py .
COPY orquestador.py .
COPY convert_normativas.py .
COPY legalizer.py .
COPY metadata_extractor.py .
COPY validator.py .
COPY granite_embedder.py .
COPY granite_guardian_guardrail.py .
COPY audit_logger.py .
COPY notebook_manager.py .
COPY opensearch_indexer.py .
COPY gpu_detector.py .
COPY cleanup.py .
COPY version.py .
COPY pipeline_config.json .
COPY gpu_config.json .

# Crear directorios de trabajo
RUN mkdir -p RAG/datos_brutos RAG/Informacion_docling_rag \
    RAG/notebooks_db normativas_chunks normativas_rag \
    .conversion_cache

# Variables de entorno
ENV JULLBRAIN_ENV=local
ENV HF_HUB_DISABLE_XET_STORAGE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "orquestador.py", "--qa"]
>>>>>>> 9dc0729da20b5212662bb449cb68c84c940431b8
