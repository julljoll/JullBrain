# Dockerfile — JullBrain v0.1.0
# Imagen base: Python 3.11 slim (compatible IBM Code Engine)
FROM python:3.11-slim

# Metadata
LABEL maintainer="JullBrain Team"
LABEL description="JullBrain Legal-RAG Pipeline API — IBM Docling + Granite"
LABEL version="0.1.0"

WORKDIR /app

# Instalar dependencias del sistema para Docling (OCR y PDF)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar (capa cacheable)
COPY requirements_ibmcloud.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_ibmcloud.txt

# Copiar código fuente del proyecto
# NOTA: RAG/datos_brutos/ NO se incluye en la imagen (datos sensibles en COS)
COPY app.py .
COPY audit_logger.py .
COPY notebook_manager.py .
COPY opensearch_indexer.py .
COPY granite_guardian_guardrail.py .
COPY convert_normativas.py .
COPY legalizer.py .
COPY metadata_extractor.py .
COPY validator.py .
COPY granite_embedder.py .
COPY cleanup.py .
COPY pipeline_config.json .
COPY ibmcloud_config.json .
COPY gpu_config.json .
COPY gpu_detector.py .

# Crear directorios RAG vacíos (se montan desde COS en runtime)
RUN mkdir -p RAG/datos_brutos RAG/Informacion_docling_rag \
    RAG/notebooks_db RAG/lightrag_db \
    .conversion_cache

# Variables de entorno base
ENV JULLBRAIN_ENV=ibmcloud
ENV HF_HUB_DISABLE_XET_STORAGE=1
ENV PYTHONUNBUFFERED=1

# IBM Code Engine usa puerto 8080 por convención
EXPOSE 8080

# Servidor de producción
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", \
     "--workers", "2", "--timeout-keep-alive", "300"]
