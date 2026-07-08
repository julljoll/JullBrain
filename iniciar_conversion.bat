@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion
title JullBrain - Convertidor de Normativas y Formatos

:: Get the ESC character for custom colors
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"

:: Define colors: Background #252525 (Dark Grey), H1 #FECF06 (Yellow/Gold), Text #00FF41 (Green), Error #FF5555 (Light Red)
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
echo [SYS] JullBrain: Convertidor Automatizado de Normativas, Leyes y Formatos Word para RAG / IA
echo =========================================================================================%COLOR_TXT%
echo.
echo Este proyecto proporciona una solución automatizada de alta fidelidad para escanear y 
echo convertir archivos PDF y documentos Word (como leyes, decretos, normativas y formatos) 
echo en documentos de texto estructurados en Markdown. Está especialmente optimizado para que 
echo motores de Inteligencia Artificial (IA) y sistemas RAG (Generación Aumentada por Recuperación) 
echo puedan consumir y analizar la información con la máxima precisión y sin pérdida de datos.
echo.
echo [+] Información del Desarrollador:
echo     [-] Nombre: Jull Ortiz
echo     [-] Correo: julljoll@gmail.com
echo     [-] Web: sha256.us
echo     [-] Instagram: @sha256.us
echo [+] Propósito: Avanzar en la transformación tecnológica del sistema de justicia venezolano.
echo [+] Licencia: MIT (Derechos de Autor (C) 2026 Jull Ortiz).
echo =========================================================================================
echo.
echo %COLOR_H1%[i] PROCESO DE EJECUCIÓN DEL SCRIPT:%COLOR_TXT%
echo  [>] 1. Verificación automática de requisitos locales (Python, Tesseract, docling_env).
echo  [>] 2. Escaneo y conversión automática de todos los archivos PDF/imágenes ('normativas_pdf/') y Word ('formatos_word/').
echo  [>] 3. Aplicación del pipeline de post-procesado legal (legalizer + metadata + validador + chunks) para RAG/DB vectoriales.
echo %COLOR_H1%=========================================================================================%COLOR_TXT%
echo.

:: Asegurar rutas comunes en el PATH de esta sesión
set "PATH=%PATH%;C:\Program Files\Tesseract-OCR;%USERPROFILE%\AppData\Local\Programs\Python\Python312;%USERPROFILE%\AppData\Local\Programs\Python\Python312\Scripts"

echo %COLOR_H1%[VERIFICACION] Comprobando requisitos del sistema...%COLOR_TXT%

:: 1. Verificar si Python está instalado
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] Python no está instalado.%COLOR_TXT%
    echo.
    echo %COLOR_ERR%  Descárgalo manualmente desde: https://www.python.org/downloads/%COLOR_TXT%
    echo %COLOR_ERR%  Asegúrate de marcar "Add Python to PATH" durante la instalación.%COLOR_TXT%
    echo %RESET%
    pause
    exit /b 1
)

:: 2. Verificar Tesseract OCR (opcional, Docling usa EasyOCR como fallback)
where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo %COLOR_H1%[WARNING] Tesseract OCR no está instalado.%COLOR_TXT%
    echo  Se usara EasyOCR ^(Python^) como alternativa. La conversion puede ser mas lenta.
    echo  Para mejor rendimiento, instala Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki
)

:CHECK_VENV
:: 3. Verificar o crear entorno virtual de Python
cd /d "%~dp0"
if exist docling_env goto CHECK_DEPS
echo [INFO] Creando entorno virtual 'docling_env'...
python -m venv docling_env
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] No se pudo crear el entorno virtual.%COLOR_TXT%
    echo %RESET%
    pause
    exit /b 1
)

:CHECK_DEPS
:: 5. Verificar y/o instalar dependencias de Python en el entorno virtual
echo [INFO] Verificando dependencias de Python en docling_env...
docling_env\Scripts\python.exe -c "import docling, fitz, pypdf, rich" >nul 2>&1
if %errorlevel% == 0 goto RUN_SCRIPT
echo [INFO] Instalando/Actualizando dependencias requeridas (docling, PyMuPDF, pypdf, rich)...
docling_env\Scripts\python.exe -m pip install --upgrade pip
docling_env\Scripts\python.exe -m pip install docling PyMuPDF pypdf rich
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] Error al instalar las dependencias de Python.%COLOR_TXT%
    echo %RESET%
    pause
    exit /b 1
)

:RUN_SCRIPT
echo %COLOR_H1%[OK] Todos los requisitos verificados y listos.%COLOR_TXT%

echo.
echo %COLOR_H1%Iniciando conversión automática de todos los archivos...%COLOR_TXT%
echo.

:: Ejecutar la conversión completa con pipeline legal (Docling + Post-Procesado + Chunks)
docling_env\Scripts\python.exe convert_normativas.py

:FINISH
:: Asegurar que las secuencias siguientes usen el fondo #252525
echo %BG_COLOR%%COLOR_TXT%
echo.
echo %COLOR_H1%=========================================================================================
echo Proceso finalizado.
echo =========================================================================================%COLOR_TXT%
echo %RESET%
pause

