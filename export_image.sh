#!/usr/bin/env bash
set -e

# export_image.sh — Exportación de Imagen TAR en Linux para Podman
# JullBrain Enterprise Legal Platform

PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]')

echo "========================================================================================="
echo "  JullBrain Enterprise Legal Platform — Exportación TAR (Linux)"
echo "  Proyecto Detectado: ${PROJECT_NAME}"
echo "========================================================================================="
echo ""

if ! command -v podman &> /dev/null; then
    echo "[ERROR CRÍTICO] Podman CLI no se encuentra instalado."
    exit 1
fi

if ! podman image inspect "${PROJECT_NAME}:latest" &> /dev/null; then
    echo "[ADVERTENCIA] La imagen ${PROJECT_NAME}:latest no existe. Construyéndola..."
    ./build_podman.sh
fi

echo ""
echo "[1/1] Exportando imagen a paquete comprimido TAR (${PROJECT_NAME}.tar)..."
echo "-----------------------------------------------------------------------------------------"
rm -f "${PROJECT_NAME}.tar"
podman save -o "${PROJECT_NAME}.tar" "${PROJECT_NAME}:latest"

echo ""
echo "========================================================================================="
echo "  ÉXITO: Paquete TAR generado correctamente: ${PROJECT_NAME}.tar"
echo "========================================================================================="
