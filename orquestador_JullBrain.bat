@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"
title JullBrain V3.0 - Centro de Control Legal-RAG

:: Activar entorno virtual
if exist "docling_env\Scripts\activate.bat" (
    call docling_env\Scripts\activate.bat
    chcp 65001 >nul 2>nul
) else (
    echo [ERROR] Entorno virtual 'docling_env' no encontrado.
    echo Ejecute: python -m venv docling_env
    echo Luego:   docling_env\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

:: Toda la logica vive en Python - delegar control completamente
python orquestador.py %*
exit /b %errorlevel%
