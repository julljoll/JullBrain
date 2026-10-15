#!/usr/bin/env bash
set -e

# import_image.sh — Importación de Imagen TAR en Linux para Podman
# JullBrain Enterprise Legal Platform

PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]')

echo "========================================================================================="
echo "  JullBrain Enterprise Legal Platform — Importación TAR (Linux)"
echo "  Proyecto Detectado: ${PROJECT_NAME}"
echo "========================================================================================="
echo ""

if ! command -v podman &> /dev/null; then
    echo "[ERROR CRÍTICO] Podman CLI no se encuentra instalado."
    exit 1
fi

if [ ! -f "${PROJECT_NAME}.tar" ]; then
    echo "[ERROR CRÍTICO] No se encontró el archivo ${PROJECT_NAME}.tar."
    echo "Verifica que el archivo TAR se encuentre en el directorio actual: $(pwd)"
    exit 1
fi

echo "[1/1] Cargando imagen OCI desde ${PROJECT_NAME}.tar..."
echo "-----------------------------------------------------------------------------------------"
podman load -i "${PROJECT_NAME}.tar"

echo ""
echo "========================================================================================="
echo "  ÉXITO: La imagen ${PROJECT_NAME}:latest ha sido importada correctamente en Podman."
echo "  Ejecutar contenedor: podman run -d -p 8050:8050 ${PROJECT_NAME}:latest"
echo "========================================================================================="
