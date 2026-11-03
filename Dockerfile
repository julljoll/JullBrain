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
