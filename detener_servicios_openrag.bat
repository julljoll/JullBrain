@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"
title JullBrain - Detener OpenSearch y OpenRAG

echo =========================================================================
echo   Deteniendo Contenedores de OpenSearch y OpenRAG...
echo =========================================================================

where docker >nul 2>nul
if %errorlevel% neq 0 (
    where podman >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] No se detecto Docker ni Podman.
        pause
        exit /b 1
    ) else (
        podman compose down
    )
) else (
    docker compose down
)

echo.
echo [OK] Servicios detenidos y recursos liberados.
echo.
pause

