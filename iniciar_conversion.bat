@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion
title QUIBOR-RAG - Convertidor de Normativas y Formatos

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
echo  ████  ██  ██ ████ █████   ████  █████  
echo ██  ██ ██  ██  ██  ██  ██ ██  ██ ██  ██ 
echo ██  ██ ██  ██  ██  █████  ██  ██ █████  
echo  █████  ████  ████ ██  ██  ████  ██  ██ 
echo      █                                  
echo.
echo ██      ████  █████   ████       ██  ██ █████ ██  ██ █████ ██████ ██  ██ █████ ██     ████ 
echo ██     ██  ██ ██  ██ ██  ██      ██  ██ ████  ███ ██ ████     ██  ██  ██ ████  ██     ██  ██
echo ██     ██████ █████  ██████       ████  ████  ██ ███ ████    ██   ██  ██ ████  ██     ██████
echo █████  ██  ██ ██  ██ ██  ██        ██   █████ ██  ██ █████ ██████  ████  █████ █████  ██  ██
echo =========================================================================================
echo [SYS] QUIBOR-RAG: Convertidor Automatizado de Normativas, Leyes y Formatos Word para RAG / IA
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
echo  [>] 1. Verificación automática de requisitos locales (Python, Git, Tesseract, docling_env).
echo  [>] 2. Escaneo y análisis automático de archivos PDF/imágenes ('normativas_pdf/') y Word ('formatos_word/').
echo  [>] 3. Presentación de un informe de estado indicando qué documentos se transformarán.
echo  [>] 4. Confirmación interactiva antes de proceder con el procesamiento.
echo %COLOR_H1%=========================================================================================%COLOR_TXT%
echo.

:: Asegurar que las rutas comunes de Chocolatey, Python y Tesseract estén en el PATH de esta sesión
set "PATH=%PATH%;C:\Program Files\Tesseract-OCR;C:\ProgramData\chocolatey\bin;%USERPROFILE%\AppData\Local\Programs\Python\Python312;%USERPROFILE%\AppData\Local\Programs\Python\Python312\Scripts;C:\tools\python;C:\tools\python\Scripts"

echo %COLOR_H1%[VERIFICACION] Comprobando requisitos del sistema...%COLOR_TXT%

:: 1. Verificar si Python está instalado
where python >nul 2>&1
if %errorlevel% neq 0 goto INSTALL_PYTHON
goto CHECK_GIT

:INSTALL_PYTHON
echo [INFO] Python no está instalado. Buscando Chocolatey para instalación automática...
where choco >nul 2>&1
if %errorlevel% neq 0 goto INSTALL_CHOCO
goto DO_INSTALL_PYTHON

:INSTALL_CHOCO
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] Python no está instalado y no se puede instalar automáticamente porque no hay privilegios de Administrador para configurar Chocolatey.%COLOR_TXT%
    echo Por favor, instala Python manualmente desde: https://www.python.org/downloads/
    echo %RESET%
    pause
    exit /b 1
)
echo [INFO] Instalando Chocolatey...
powershell -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] No se pudo instalar Chocolatey automáticamente para instalar Python.%COLOR_TXT%
    echo %RESET%
    pause
    exit /b 1
)

:DO_INSTALL_PYTHON
echo [INFO] Instalando Python mediante Chocolatey...
choco install python -y
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] No se pudo instalar Python. Asegúrese de ejecutar como Administrador.%COLOR_TXT%
    echo %RESET%
    pause
    exit /b 1
)
set "PATH=%PATH%;C:\tools\python;C:\tools\python\Scripts"

:CHECK_GIT
:: 2. Verificar si Git está instalado
where git >nul 2>&1
if %errorlevel% neq 0 goto INSTALL_GIT
goto CHECK_TESSERACT

:INSTALL_GIT
where choco >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Git no está instalado. Instalando Git mediante Chocolatey...
    choco install git -y
) else (
    echo %COLOR_H1%[WARNING] Git no está instalado. Se recomienda instalarlo para control de versiones.%COLOR_TXT%
)

:CHECK_TESSERACT
:: 3. Verificar si Tesseract OCR está instalado (recomendado)
where tesseract >nul 2>&1
if %errorlevel% neq 0 goto INSTALL_TESSERACT
goto CHECK_VENV

:INSTALL_TESSERACT
where choco >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Tesseract OCR no está instalado. Instalando mediante Chocolatey...
    choco install tesseract -y
    if %errorlevel% == 0 (
        set "PATH=%PATH%;C:\Program Files\Tesseract-OCR"
    )
) else (
    echo %COLOR_H1%[WARNING] Tesseract OCR no está instalado. Se utilizará EasyOCR basado en Python por defecto.%COLOR_TXT%
)

:CHECK_VENV
:: 4. Verificar o crear entorno virtual de Python
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
echo %COLOR_H1%Seleccione el modo de operación:%COLOR_TXT%
echo  %COLOR_TXT%1.%RESET% Conversión completa (Docling + Post-Procesado + Chunks)
echo  %COLOR_TXT%2.%RESET% Solo post-procesado legal (re-estructurar .md existentes)
echo  %COLOR_TXT%3.%RESET% Forzar re-procesado (ignorar caché SHA-256)
echo  %COLOR_TXT%4.%RESET% Conversión rápida sin OCR (para PDFs nativos)
echo  %COLOR_TXT%5.%RESET% Procesar un solo archivo con OCR
echo  %COLOR_TXT%6.%RESET% Procesar un solo archivo sin OCR
echo  %COLOR_TXT%7.%RESET% Conversión completa sin chunks
echo  %COLOR_TXT%8.%RESET% Validar integridad de normativas_rag/
echo.
set /p "MODE=[>] Selecciona (1-8, Enter=1): "
if "%MODE%"=="" set MODE=1

set "EXTRA_ARGS="
if "%MODE%"=="2" set "EXTRA_ARGS=--post-process-only"
if "%MODE%"=="3" set "EXTRA_ARGS=--force-reprocess"
if "%MODE%"=="4" set "EXTRA_ARGS=--no-ocr"
if "%MODE%"=="5" (
    set /p "SEL_FILE=[>] Escribe el nombre o ruta del PDF: "
    set "EXTRA_ARGS=--file-path "!SEL_FILE!""
)
if "%MODE%"=="6" (
    set /p "SEL_FILE=[>] Escribe el nombre o ruta del PDF: "
    set "EXTRA_ARGS=--file-path "!SEL_FILE!" --no-ocr"
)
if "%MODE%"=="7" set "EXTRA_ARGS=--no-chunks"
if "%MODE%"=="8" (
    echo.
    echo %COLOR_H1%Ejecutando validador...%COLOR_TXT%
    docling_env\Scripts\python.exe validator.py normativas_rag
    goto FINISH
)

echo.
echo %COLOR_H1%Iniciando Servicio de Conversión de Normativas a RAG...%COLOR_TXT%
echo.

:: Ejecutar el script usando el Python del entorno virtual
docling_env\Scripts\python.exe convert_normativas.py %EXTRA_ARGS%

:FINISH
:: Asegurar que las secuencias siguientes usen el fondo #252525
echo %BG_COLOR%%COLOR_TXT%
echo.
echo %COLOR_H1%=========================================================================================
echo Proceso finalizado.
echo =========================================================================================%COLOR_TXT%
echo %RESET%
pause

