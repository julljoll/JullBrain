#!/usr/bin/env bash
# ==============================================================================
# JullBrain v0.2.0 — Script de Despliegue Oficial en Oracle Cloud (OCI)
# Configurado nativamente con Podman Rootless y Bóveda Local de Modelos IBM
# ==============================================================================
set -euo pipefail

APP_DIR="/opt/jullbrain"
RAG_DIR="${APP_DIR}/RAG"
MODEL_VAULT="${RAG_DIR}/modelos_ia"
PORT="${JULLBRAIN_PORT:-8080}"

echo "======================================================================"
echo "  JullBrain v0.2.0 — Despliegue Soberano en Oracle Cloud (OCI)"
echo "  Stack Exclusivo IBM (Docling CPU + Granite 3.3 + Embedding R2 + Guardian)"
echo "  Motor de Contenedores: Podman Nativo (Rootless)"
echo "======================================================================"

# 1. Detectar arquitectura y sistema operativo en OCI
ARCH=$(uname -m)
CORES=$(nproc || echo 4)
echo "[INFO] Arquitectura detectada: ${ARCH} | Núcleos CPU para IBM Docling: ${CORES}"

# 2. Instalar Podman y dependencias base según distribución (Oracle Linux / Ubuntu)
if command -v dnf >/dev/null 2>&1; then
    echo "[1/5] Instalando Podman y herramientas en Oracle Linux / RHEL..."
    sudo dnf install -y podman podman-compose git curl python3.12 python3.12-pip
elif command -v apt-get >/dev/null 2>&1; then
    echo "[1/5] Instalando Podman y herramientas en Ubuntu (OCI)..."
    sudo apt-get update -y
    sudo apt-get install -y podman podman-compose git curl python3 python3-venv python3-pip
fi

# 3. Preparar estructura del Núcleo RAG y Bóveda Local de Modelos IA
echo "[2/5] Inicializando núcleo RAG y bóveda criptográfica de modelos en ${RAG_DIR}..."
sudo mkdir -p \
    "${RAG_DIR}/datos_brutos" \
    "${RAG_DIR}/Informacion_docling_rag" \
    "${RAG_DIR}/normativas_chunks" \
    "${MODEL_VAULT}/docling" \
    "${MODEL_VAULT}/granite_embeddings" \
    "${MODEL_VAULT}/granite_llm" \
    "${MODEL_VAULT}/granite_guardian" \
    "${MODEL_VAULT}/huggingface" \
    "${MODEL_VAULT}/torch" \
    "${MODEL_VAULT}/ollama" \
    "${RAG_DIR}/notebooks_db" \
    "${RAG_DIR}/lightrag_db" \
    "${APP_DIR}/logs"

sudo chown -R "$(id -u):$(id -g)" "${APP_DIR}"

# 4. Construir imagen nativa con Podman usando Containerfile
echo "[3/5] Construyendo imagen JullBrain con Podman (Containerfile)..."
cd "${APP_DIR}"
podman build -f Containerfile -t localhost/jullbrain-ibm:0.2.0 .

# 5. Desplegar servicios con Podman Compose o Podman Run Rootless
echo "[4/5] Iniciando enclave Podman Rootless..."
if command -v podman-compose >/dev/null 2>&1; then
    podman-compose -f podman-compose.yml up -d
else
    podman run -d \
        --name jullbrain-core \
        --replace \
        --security-opt=no-new-privileges \
        --userns=keep-id \
        -p "${PORT}:8080" \
        -e JULLBRAIN_ENV=oracle \
        -e OMP_NUM_THREADS="${CORES}" \
        -e MKL_NUM_THREADS="${CORES}" \
        -e JULLBRAIN_MODEL_VAULT=/app/RAG/modelos_ia \
        -e DOCLING_ARTIFACTS_PATH=/app/RAG/modelos_ia/docling \
        -e HF_HOME=/app/RAG/modelos_ia/huggingface \
        -e TORCH_HOME=/app/RAG/modelos_ia/torch \
        -v "${RAG_DIR}:/app/RAG:Z" \
        -v "${APP_DIR}/logs:/app/logs:Z" \
        localhost/jullbrain-ibm:0.2.0
fi

# 6. Descargar modelos IBM Granite en la bóveda local del contenedor Ollama (si está activo)
if podman ps --format "{{.Names}}" | grep -q "jullbrain-ollama"; then
    echo "[5/5] Aprovisionando modelos IBM Granite en bóveda local (${MODEL_VAULT}/ollama)..."
    podman exec jullbrain-ollama ollama pull granite3.3:8b || true
    podman exec jullbrain-ollama ollama pull granite-guardian:3.2 || true
fi

echo "======================================================================"
echo "  [OK] Despliegue en Oracle Cloud completado con éxito."
echo "  - Endpoint local/OCI : http://localhost:${PORT}/health"
echo "  - Bóveda de Modelos  : ${MODEL_VAULT}"
echo "  - Estado Podman      : podman ps"
echo "======================================================================"
