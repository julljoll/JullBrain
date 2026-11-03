@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"
title JullBrain - Iniciar OpenSearch y OpenRAG

echo =========================================================================
echo   Iniciando Infraestructura Local Soberana: OpenSearch 2.18 + OpenRAG
echo =========================================================================

where docker >nul 2>nul
if %errorlevel% neq 0 (
    where podman >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] No se detecto Docker ni Podman instalado en el sistema.
        echo Por favor instale Docker Desktop o Podman para ejecutar OpenSearch localmente.
        pause
        exit /b 1
    ) else (
        echo [INFO] Utilizando motor Podman Compose...
        podman compose up -d
    )
) else (
    echo [INFO] Utilizando motor Docker Compose...
    docker compose up -d
)

echo.
echo [OK] Contenedores desplegados en segundo plano.
echo      - OpenSearch REST API : http://localhost:9200
echo      - OpenRAG Runtime     : http://localhost:7860
echo.
pause

