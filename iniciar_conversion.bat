@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion
title JullBrain - Convertidor de Normativas (Python Nativo)

:: Get the ESC character for custom colors
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"

:: Define colors
set "BG_COLOR=%ESC%[48;2;37;37;37m"
set "COLOR_H1=%ESC%[38;2;254;207;6m"
set "COLOR_TXT=%ESC%[38;2;0;255;65m"
set "COLOR_ERR=%ESC%[38;2;255;85;85m"
set "RESET=%ESC%[0m"

:: Apply custom background and text colors to the entire console
echo %BG_COLOR%%COLOR_TXT%
cls

echo %COLOR_H1%=========================================================================================
echo    ████ ██   ██ ██      ██      ██████  ██████   █████  ███████ ██   ██
echo      ██ ██   ██ ██      ██      ██   ██ ██   ██ ██   ██   ██    ███  ██
echo      ██ ██   ██ ██      ██      ██████  ██████  ███████   ██    ██ ██ ██
echo  ██   ██ ██   ██ ██      ██      ██   ██ ██  ██  ██   ██   ██    ██  ███
echo   █████   █████  ███████ ███████ ██████  ██   ██ ██   ██ ███████ ██   ██
echo.
echo                        ---  M I   C E R E B R O   P E R S O N A L  ---
echo =========================================================================================
echo [SYS] JullBrain V-2.0: Convertidor Automatizado de Normativas, Leyes y Formatos Word para RAG / IA
echo =========================================================================================%COLOR_TXT%
echo.
echo Este proyecto proporciona una solución automatizada de alta fidelidad para escanear y 
echo convertir archivos PDF y documentos Word en documentos de texto estructurados en Markdown 
echo y JSON (Hierarchical Chunking). Optimizado para motores de IA.
echo.
echo [+] Ejecución: Entorno Python Nativo (Entorno Virtual).
echo =========================================================================================
echo.

:: ===========================================================================
:: 1. VERIFICACION DE PYTHON
:: ===========================================================================
echo %COLOR_H1%[ESTADO] Analizando dependencias del sistema...%COLOR_TXT%
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   [-] Python: %COLOR_ERR%NO INSTALADO (Requisito indispensable)%COLOR_TXT%
    echo %COLOR_ERR%Por favor instala Python 3.10+ desde python.org y agregalo al PATH.%COLOR_TXT%
    pause
    exit /b 1
) else (
    echo   [+] Python: %COLOR_TXT%INSTALADO%COLOR_TXT%
)

:: ===========================================================================
:: 2. VERIFICACION / CREACION DEL ENTORNO VIRTUAL
:: ===========================================================================
cd /d "%~dp0"
set "VENV_DIR=docling_env"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo.
    echo %COLOR_H1%[INFO] Creando entorno virtual local '%VENV_DIR%'...%COLOR_TXT%
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo %COLOR_ERR%[ERROR] No se pudo crear el entorno virtual.%COLOR_TXT%
        pause
        exit /b 1
    )
)

echo %COLOR_H1%[INFO] Activando entorno virtual e instalando dependencias...%COLOR_TXT%
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] Hubo un problema instalando los requirements.%COLOR_TXT%
    pause
    exit /b 1
)

:: ===========================================================================
:: 3. EJECUCION DE CONVERSION
:: ===========================================================================
echo.
echo %COLOR_H1%=========================================================================================
echo [INICIO] Ejecutando el orquestador principal de JullBrain...
echo          Se analizaran las carpetas normativas_pdf y se procesaran hacia normativas_rag.
echo =========================================================================================%COLOR_TXT%
echo.

python convert_normativas.py

echo.
echo %COLOR_H1%=========================================================================================
echo [FIN] Proceso de conversion finalizado.
echo =========================================================================================%COLOR_TXT%
echo %RESET%
pause
exit /b 0
