#!/bin/bash
# deploy_ibmcloud.sh — JullBrain v0.1.0
# Despliegue en IBM Cloud Code Engine + Container Registry
# Requiere: ibmcloud CLI instalado y sesión activa (ibmcloud login)

set -euo pipefail

NAMESPACE="jullbrain"
IMAGE="us.icr.io/${NAMESPACE}/app:latest"
PROJECT="jullbrain-legal-rag"
APP_NAME="jullbrain-api"
REGION="us-south"

echo "══════════════════════════════════════════════════"
echo "  JullBrain v0.1.0 — Despliegue IBM Cloud"
echo "══════════════════════════════════════════════════"

# 1. Verificar CLI instalado
echo "[1/6] Verificando IBM Cloud CLI..."
ibmcloud version
ibmcloud plugin list | grep code-engine || {
    echo "Instalando plugin code-engine..."
    ibmcloud plugin install code-engine
}
ibmcloud plugin list | grep container-registry || {
    echo "Instalando plugin container-registry..."
    ibmcloud plugin install container-registry
}

# 2. Configurar región y Container Registry
echo "[2/6] Configurando IBM Container Registry..."
ibmcloud cr region-set ${REGION}
ibmcloud cr login
ibmcloud cr namespace-add ${NAMESPACE} 2>/dev/null || true

# 3. Construir y publicar imagen Docker
echo "[3/6] Construyendo imagen Docker..."
docker build -t ${IMAGE} -f Dockerfile .
echo "[4/6] Publicando imagen en IBM Container Registry..."
docker push ${IMAGE}

# 4. Crear o actualizar la aplicación en Code Engine
echo "[5/6] Desplegando en IBM Cloud Code Engine..."
ibmcloud ce project select --name ${PROJECT} 2>/dev/null || \
    ibmcloud ce project create --name ${PROJECT}

ibmcloud ce application create \
    --name ${APP_NAME} \
    --image ${IMAGE} \
    --port 8080 \
    --cpu 2 \
    --memory 8G \
    --min-scale 0 \
    --max-scale 3 \
    --env JULLBRAIN_ENV=ibmcloud \
    --env HF_HUB_DISABLE_XET_STORAGE=1 2>/dev/null || \
ibmcloud ce application update \
    --name ${APP_NAME} \
    --image ${IMAGE}

# 5. Obtener URL pública
echo "[6/6] Obteniendo URL del servicio..."
URL=$(ibmcloud ce application get --name ${APP_NAME} --output json | python3 -c \
    "import sys, json; d=json.load(sys.stdin); print(d.get('status',{}).get('url','(pendiente)'))")

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  JullBrain desplegado en IBM Cloud Code Engine   ║"
echo "║  URL: ${URL}                                     ║"
echo "║  Health: ${URL}/health                           ║"
echo "╚══════════════════════════════════════════════════╝"
