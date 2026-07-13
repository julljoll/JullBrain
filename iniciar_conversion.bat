@echo off
setlocal EnableDelayedExpansion

:: Establecer codificación UTF-8 para soporte de emojis y bloques ASCII
chcp 65001 >nul

:: Asegurar que el directorio de trabajo es el del script
cd /d "%~dp0"

title JullBrain - Pipeline de Normativas RAG (Entorno Nativo)

:: 1. Auto-Elevación de Privilegios
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: 2. Declaración de Variables de Color usando powershell para generar ESC
for /f "delims=" %%a in ('powershell -Command "[char]27"') do (
    set "ESC=%%a"
)
set "BG_COLOR=%ESC%[40m"
set "COLOR_H1=%ESC%[93m"
set "COLOR_TITLE=%ESC%[96m"
set "COLOR_TXT=%ESC%[97m"
set "COLOR_GREEN=%ESC%[92m"
set "COLOR_RED=%ESC%[91m"
set "COLOR_RESET=%ESC%[0m"

:: Configurar color de fondo negro
echo %BG_COLOR%
cls

:: Imprimir logo ASCII y banner
echo %COLOR_TITLE%
echo  =========================================================================================
echo        ██╗██╗   ██╗██╗     ██╗     ██████╗ ██████╗  █████╗ ██╗███╗   ██╗
echo        ██║██║   ██║██║     ██║     ██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║
echo        ██║██║   ██║██║     ██║     ██████╔╝██████╔╝███████║██║██╔██╗ ██║
echo   ██   ██║██║   ██║██║     ██║     ██╔══██╗██╔══██╗██╔══██║██║██║╚██╗██║
echo   ╚█████╔╝╚██████╔╝███████╗███████╗██████╔╝██║  ██║██║  ██║██║██║ ╚████║
echo    ╚════╝  ╚═════╝ ╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
echo  =========================================================================================
echo %COLOR_RESET%
echo %COLOR_H1%   JullBrain RAG-Pipeline - Versión 2.0 (Entorno Local de Python)%COLOR_RESET%
echo.
echo %COLOR_TXT% Este script automatiza la conversión y validación de normativas y leyes venezolanas.%COLOR_RESET%
echo %COLOR_TXT% Autor: Jull Ortiz (Arquitecto de Información IA) ^| Licencia MIT%COLOR_RESET%
echo %COLOR_TITLE% =========================================================================================%COLOR_RESET%
echo.

set "VENV_DIR=docling_env"

echo %COLOR_H1%[FASE 3] Verificando Entorno Virtual y Dependencias...%COLOR_RESET%

:: 3. Verificación de Python y Entorno Virtual
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo   %COLOR_GREEN%[+] Entorno virtual '%VENV_DIR%': DETECTADO%COLOR_RESET%
    set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
    goto :VENV_READY
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    goto :PYTHON_NOT_FOUND
)

:: Verificar si el comando Python funciona realmente (evita el dummy alias de Microsoft Store)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    goto :PYTHON_NOT_FOUND
)

echo   %COLOR_GREEN%[+] Python global: DETECTADO%COLOR_RESET%
echo [INFO] Creando el entorno virtual '%VENV_DIR%' local...
python -m venv --system-site-packages %VENV_DIR%
if %errorlevel% neq 0 (
    echo %COLOR_RED%[ERROR] No se pudo crear el entorno virtual.%COLOR_RESET%
    pause
    exit /b 1
)
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
goto :VENV_INSTALL_DEPS

:PYTHON_NOT_FOUND
echo   %COLOR_RED%[-] Python global: NO DETECTADO o ALIAS DE MICROSOFT STORE ACTIVO%COLOR_RESET%
echo %COLOR_RED%[ERROR] Python no se encuentra instalado correctamente en el sistema.%COLOR_RESET%
echo Por favor, instale Python 3.10+ y asegúrese de agregarlo al PATH.
pause
exit /b 1

:VENV_INSTALL_DEPS
echo [INFO] Activando el entorno virtual para instalación inicial...
call "%VENV_DIR%\Scripts\activate.bat"
echo [INFO] Instalando dependencias de requirements.txt (solo primera vez)...
call python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %COLOR_RED%[ERROR] Error al instalar dependencias del sistema.%COLOR_RESET%
    pause
    exit /b 1
)
goto :RUN_PIPELINE

:VENV_READY
echo [INFO] Activando el entorno virtual...
call "%VENV_DIR%\Scripts\activate.bat"
goto :RUN_PIPELINE

:RUN_PIPELINE
echo.
echo %COLOR_TITLE% =========================================================================================%COLOR_RESET%
echo %COLOR_GREEN%[FASE 4] Iniciando el procesamiento del Pipeline RAG...%COLOR_RESET%
echo %COLOR_TITLE% =========================================================================================%COLOR_RESET%
echo.

call python convert_normativas.py

echo.
echo %COLOR_TITLE% =========================================================================================%COLOR_RESET%
echo %COLOR_GREEN%[FIN] Proceso de conversión y validación completado con éxito.%COLOR_RESET%
echo %COLOR_TITLE% =========================================================================================%COLOR_RESET%
echo.
pause
exit /b 0
