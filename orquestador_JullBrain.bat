@echo off
@REM ==============================================================================
@REM 🏛️ JULLBRAIN & UMIF - ENCABEZADO CANÓNICO ARCHIVO SCRIPT (.BAT)
@REM ==============================================================================
@REM Proyecto         : Jullbrain / UMIF (Unidad Móvil Informática Forense)
@REM Idea Principal   : Laboratorio Móvil con IA Local para análisis de expedientes penales,
@REM                    agilización de audiencias preliminares y descongestión judicial.
@REM Autor            : Jull Ortiz
@REM Rol Profesional  : Abogado - Diseñador UX/UI Especializado en LegalTech & Forense Digital
@REM Certificación UX : IBM Enterprise Design Thinking / IBM UX Design Professional
@REM Sitio Web        : http://www.sha256.us/
@REM Stack Tecnológico: IBM Docling (CPU), IBM Granite 3.3, Granite Embedding R2,
@REM                    IBM Granite Guardian (Ciberseguridad & Anti-Alucinaciones),
@REM                    Google OKF, Google Antigravity, Podman, Oracle Cloud, SHA-256.
@REM Leyes Nacionales : Ley Delitos Informáticos (G.O. 37.313) | Ley Mensajes de Datos y Firmas (G.O. 37.072)
@REM                    Ley de Infogobierno (G.O. 40.274) | Decreto CENIF (G.O. 39.847) | Normativas SUSCERTE
@REM                    Manual Único de Cadena de Custodia (MP/CICPC 2017) | COPP | Código Penal
@REM Estándares Int.  : ISO/IEC 27001:2022 | ISO/IEC 27002:2022 | ISO/IEC 27037:2012 | ISO/IEC 27042:2015
@REM                    UNE 197010:2015 | NIST SP 800-101 / 800-86 | ACPO v5 | RFC 3227 | SWGDE
@REM Licencia         : Apache 2.0
@REM ==============================================================================

chcp 65001 >nul 2>nul
cd /d "%~dp0"
title JullBrain ^& UMIF v0.2.0 - Centro de Control Legal-RAG (100%% IBM AI)

:: ── FASE 1: Auto-Elevación de Privilegios con Fallback Seguro ──
if not "%~1"=="" goto SKIP_ELEVATION
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/k \"\"%~f0\"\" ELEVATED' -Verb RunAs" 2>nul
    if %errorlevel% equ 0 exit /b
    echo  [AVISO] Continuando en modo usuario estandar...
)
:SKIP_ELEVATION

:: ── FASE 2: Interfaz Gráfica (Colores ANSI y Arte ASCII JullBrain) ──
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"
set "COLOR_H1=%ESC%[1;33m"
set "COLOR_TXT=%ESC%[1;32m"
set "COLOR_CYAN=%ESC%[1;36m"
set "COLOR_ERR=%ESC%[1;31m"
set "COLOR_RESET=%ESC%[0m"

echo %COLOR_H1%  =========================================================================================%COLOR_RESET%
echo %COLOR_H1%   ██╗██╗   ██╗██╗     ██╗     ██████╗ ██████╗  █████╗ ██╗███╗   ██╗%COLOR_RESET%
echo %COLOR_H1%   ██║██║   ██║██║     ██║     ██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║%COLOR_RESET%
echo %COLOR_H1%   ██║██║   ██║██║     ██║     ██████╔╝██████╔╝███████║██║██╔██╗ ██║%COLOR_RESET%
echo %COLOR_H1%   ██║██║   ██║██║     ██║     ██╔══██╗██╔══██╗██╔══██║██║██║╚██╗██║%COLOR_RESET%
echo %COLOR_H1%   ╚█████╔╝╚██████╔╝███████╗███████╗██████╔╝██║  ██║██║  ██║██║██║ ╚████║%COLOR_RESET%
echo %COLOR_H1%    ╚════╝  ╚═════╝ ╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝%COLOR_RESET%
echo %COLOR_H1%  =========================================================================================%COLOR_RESET%
echo %COLOR_TXT%   JullBrain ^& UMIF v0.2.0 - Pipeline Forense Legal-RAG (IBM Docling CPU + IBM Granite)%COLOR_RESET%
echo %COLOR_CYAN%   Analizando computadora host, procesador (CPU) y boveda de modelos en .\RAG\modelos_ia...%COLOR_RESET%
echo %COLOR_H1%  =========================================================================================%COLOR_RESET%

:: ── FASE 3: Análisis del Computador Host (CPU para Docling, RAM, Podman y Python) ──
echo.
echo %COLOR_CYAN%  [1/4] Analizando Procesador (CPU) para optimizacion nativa de IBM Docling...%COLOR_RESET%
echo         Arquitectura : %PROCESSOR_ARCHITECTURE%
echo         Procesador   : %PROCESSOR_IDENTIFIER%
echo         Hilos Logicos: %NUMBER_OF_PROCESSORS% nucleos detectados

set /a "DOCLING_THREADS=%NUMBER_OF_PROCESSORS%-1"
if %DOCLING_THREADS% LSS 2 set "DOCLING_THREADS=2"
if %DOCLING_THREADS% GTR 8 set "DOCLING_THREADS=8"

set "OMP_NUM_THREADS=%DOCLING_THREADS%"
set "MKL_NUM_THREADS=%DOCLING_THREADS%"
set "OPENBLAS_NUM_THREADS=%DOCLING_THREADS%"
set "TORCH_NUM_THREADS=%DOCLING_THREADS%"
set "DOCLING_NUM_THREADS=%DOCLING_THREADS%"

:: Variables de Ciberseguridad IBM y Boveda Local Air-Gapped en RAG\modelos_ia
set "HF_HUB_DISABLE_TELEMETRY=1"
set "HF_HUB_DISABLE_XET_STORAGE=1"
set "DO_NOT_TRACK=1"
set "ANONYMIZED_TELEMETRY=False"
set "HF_HOME=%~dp0RAG\modelos_ia\huggingface"
set "SENTENCE_TRANSFORMERS_HOME=%~dp0RAG\modelos_ia\granite_embeddings"
set "DOCLING_ARTIFACTS_PATH=%~dp0RAG\modelos_ia\docling"
set "TORCH_HOME=%~dp0RAG\modelos_ia\torch"

if not exist "RAG\datos_brutos" mkdir "RAG\datos_brutos"
if not exist "RAG\Informacion_docling_rag" mkdir "RAG\Informacion_docling_rag"
if not exist "RAG\normativas_chunks" mkdir "RAG\normativas_chunks"
if not exist "RAG\modelos_ia\docling" mkdir "RAG\modelos_ia\docling"
if not exist "RAG\modelos_ia\granite_embeddings" mkdir "RAG\modelos_ia\granite_embeddings"
if not exist "RAG\modelos_ia\huggingface" mkdir "RAG\modelos_ia\huggingface"

where podman >nul 2>&1
if %errorlevel% equ 0 (
    echo         Podman Engine: Detectado y listo para contenedores rootless.
) else (
    echo         Podman Engine: No detectado en PATH ^(Modo Local Nativo activo^).
)

:: Localizar el interprete Python mas reciente de la computadora (priorizando Python 3.14 / 3.13 / 3.12)
set "SYS_PYTHON="
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" set "SYS_PYTHON=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
if "%SYS_PYTHON%"=="" (
    for /f "delims=" %%p in ('where python 2^>nul') do (
        if "%SYS_PYTHON%"=="" set "SYS_PYTHON=%%p"
    )
)

echo %COLOR_CYAN%  [2/4] Verificando entorno virtual 'docling_env'...%COLOR_RESET%
set "VENV_VALID=0"
if exist "docling_env\Scripts\python.exe" (
    "docling_env\Scripts\python.exe" -c "import sys; print('        Python Venv activo:', sys.version.split()[0])" 2>nul
    if not errorlevel 1 set "VENV_VALID=1"
)

if "%VENV_VALID%"=="0" (
    if "%SYS_PYTHON%"=="" (
        echo %COLOR_ERR%  [ERROR] No se encontro Python instalado en el sistema.%COLOR_RESET%
        echo           Instale Python 3.12+ o 3.14 desde https://www.python.org/
        pause
        exit /b 1
    )
    echo %COLOR_H1%        Actualizando/creando entorno virtual 'docling_env' con: "%SYS_PYTHON%"...%COLOR_RESET%
    if exist "docling_env" rmdir /s /q "docling_env"
    "%SYS_PYTHON%" -m venv docling_env
    if errorlevel 1 (
        echo %COLOR_ERR%  [ERROR] Fallo al crear el entorno virtual docling_env.%COLOR_RESET%
        pause
        exit /b 1
    )
)

call "docling_env\Scripts\activate.bat"
chcp 65001 >nul 2>nul

:: ── FASE 4: Instalación de Dependencias, Modelos Locales y Ejecución ──
echo %COLOR_CYAN%  [3/4] Verificando dependencias IBM Docling y Granite...%COLOR_RESET%
"docling_env\Scripts\python.exe" -c "import docling, rich, fitz, pypdf, yaml, fastapi" 2>nul
if errorlevel 1 (
    echo %COLOR_H1%        Descargando e instalando paquetes necesarios desde requirements.txt...%COLOR_RESET%
    "docling_env\Scripts\python.exe" -m pip install --upgrade pip
    "docling_env\Scripts\python.exe" -m pip install -r requirements.txt
)

echo %COLOR_CYAN%  [4/4] Iniciando Orquestador Principal JullBrain...%COLOR_RESET%
echo.
if "%~1"=="ELEVATED" (
    "docling_env\Scripts\python.exe" orquestador.py
) else (
    "docling_env\Scripts\python.exe" orquestador.py %*
)
exit /b %errorlevel%
