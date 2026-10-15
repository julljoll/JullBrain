#!/usr/bin/env bash
set -e

# build_podman.sh — Script de Construcción OCI para Linux en Podman
# JullBrain Enterprise Legal Platform

PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]')

echo "========================================================================================="
echo "  JullBrain Enterprise Legal Platform — Construcción Podman (Linux)"
echo "  Proyecto Detectado: ${PROJECT_NAME}"
echo "========================================================================================="
echo ""

if ! command -v podman &> /dev/null; then
    echo "[ERROR CRÍTICO] Podman no está instalado o no se encuentra en el PATH."
    echo "Instálalo mediante el gestor de paquetes de tu distribución (apt, dnf, pacman)."
    exit 1
fi

echo "[1/2] Verificando instalación de Podman..."
podman --version
echo ""

echo "[2/2] Construyendo la imagen OCI (${PROJECT_NAME}:latest)..."
echo "-----------------------------------------------------------------------------------------"
podman build -t "${PROJECT_NAME}:latest" -f Containerfile .

echo ""
echo "========================================================================================="
echo "  ÉXITO: La imagen ${PROJECT_NAME}:latest ha sido construida correctamente."
echo "========================================================================================="
