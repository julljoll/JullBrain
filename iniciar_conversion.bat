@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion
title JullBrain - Convertidor de Normativas (Docker)

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
echo    â–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ      â–ˆâ–ˆ      â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ
echo      â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ      â–ˆâ–ˆ      â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ   â–ˆâ–ˆ    â–ˆâ–ˆâ–ˆ  â–ˆâ–ˆ
echo      â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ      â–ˆâ–ˆ      â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆ    â–ˆâ–ˆ â–ˆâ–ˆ â–ˆâ–ˆ
echo  â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ      â–ˆâ–ˆ      â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ  â–ˆâ–ˆ  â–ˆâ–ˆ   â–ˆâ–ˆ   â–ˆâ–ˆ    â–ˆâ–ˆ  â–ˆâ–ˆâ–ˆ
echo   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ   â–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ  â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ â–ˆâ–ˆ   â–ˆâ–ˆ
echo.
echo                        ---  M I   C E R E B R O   P E R S O N A L  ---
echo =========================================================================================
echo [SYS] JullBrain V-2.0: Convertidor Automatizado de Normativas, Leyes y Formatos Word para RAG / IA
echo =========================================================================================%COLOR_TXT%
echo.
echo Este proyecto proporciona una soluciÃ³n automatizada de alta fidelidad para escanear y 
echo convertir archivos PDF y documentos Word en documentos de texto estructurados en Markdown 
echo y JSON (Hierarchical Chunking). Optimizado para que motores de Inteligencia Artificial (IA) 
echo y sistemas RAG consuman la informaciÃ³n con la mÃ¡xima precisiÃ³n y sin pÃ©rdida de datos.
echo.
echo [+] InformaciÃ³n del Desarrollador:
echo     [-] Nombre: Jull Ortiz
echo     [-] Correo: julljoll@gmail.com
echo     [-] Web: sha256.us
echo     [-] Instagram: @sha256.us
echo [+] PropÃ³sito: Avanzar en la transformaciÃ³n tecnolÃ³gica del sistema de justicia venezolano.
echo [+] EjecuciÃ³n: Entorno Dockerizado y Aislado.
echo =========================================================================================
echo.

:: ===========================================================================
:: 1. ANALISIS DE ESTADO DEL SISTEMA
:: ===========================================================================
echo %COLOR_H1%[ESTADO] Analizando dependencias del sistema...%COLOR_TXT%
set "DOCKER_READY=0"
set "CHOCO_MISSING=0"
set "DOCKER_MISSING=0"

:: Verificar Chocolatey
where choco >nul 2>&1
if %errorlevel% neq 0 goto CHOCO_NO
echo   [+] Chocolatey: %COLOR_TXT%INSTALADO%COLOR_TXT%
goto CHOCO_END
:CHOCO_NO
echo   [-] Chocolatey: %COLOR_ERR%NO INSTALADO%COLOR_TXT%
set "CHOCO_MISSING=1"
:CHOCO_END

:: Verificar Docker Desktop
where docker >nul 2>&1
if %errorlevel% neq 0 goto DOCKER_NO
echo   [+] Docker Desktop: %COLOR_TXT%INSTALADO%COLOR_TXT%

:: Verificar Motor Docker
docker info >nul 2>&1
if %errorlevel% neq 0 goto ENGINE_NO
echo   [+] Motor de Docker: %COLOR_TXT%EN EJECUCION%COLOR_TXT%
set "DOCKER_READY=1"
goto DOCKER_END

:ENGINE_NO
echo   [-] Motor de Docker: %COLOR_ERR%DETENIDO (Inicia Docker Desktop manualmente)%COLOR_TXT%
goto DOCKER_END

:DOCKER_NO
echo   [-] Docker Desktop: %COLOR_ERR%NO INSTALADO (Requisito indispensable para JullBrain)%COLOR_TXT%
set "DOCKER_MISSING=1"
:DOCKER_END

echo.

:: ===========================================================================
:: 2. AUTO-INSTALACIÃ“N (SOLO SI TIENE PERMISOS DE ADMINISTRADOR)
:: ===========================================================================
net session >nul 2>&1
if %errorlevel% equ 0 (
    set "IS_ADMIN=1"
) else (
    set "IS_ADMIN=0"
)

if "%DOCKER_READY%"=="1" goto START_DOCKER

if "%IS_ADMIN%"=="0" (
    echo %COLOR_ERR%[ALERTA] Faltan dependencias o Docker no esta en ejecucion.%COLOR_TXT%
    echo %COLOR_ERR%Cierra esta ventana, haz clic derecho en el archivo .bat y%COLOR_TXT%
    echo %COLOR_ERR%selecciona "Ejecutar como administrador" para instalar todo automaticamente.%COLOR_TXT%
    pause
    exit /b 1
)

echo %COLOR_H1%[INFO] Privilegios de administrador detectados. Iniciando instalacion de faltantes...%COLOR_TXT%

if "%CHOCO_MISSING%"=="1" (
    echo [INFO] Instalando Chocolatey...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    set "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
)

if "%DOCKER_MISSING%"=="1" (
    echo [INFO] Instalando Docker Desktop...
    choco install docker-desktop -y
    echo %COLOR_ERR%[IMPORTANTE] Docker Desktop instalado. REINICIA TU COMPUTADORA y vuelve a ejecutar.%COLOR_TXT%
    pause
    exit /b 1
)

if "%DOCKER_READY%"=="0" (
    exit /b 1
)

:START_DOCKER
:: ===========================================================================
:: 3. CONSTRUCCION Y EJECUCION DE CONVERSION
:: ===========================================================================
cd /d "%~dp0"

echo %COLOR_H1%=========================================================================================
echo [INICIO] Ejecutando el orquestador principal de JullBrain en Docker...
echo          Se analizaran las carpetas normativas_pdf y se procesaran hacia normativas_rag.
echo =========================================================================================%COLOR_TXT%
echo.

echo %COLOR_H1%[INFO] Verificando imagen de Docker...%COLOR_TXT%
docker compose build jullbrain
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] Hubo un problema al construir la imagen de Docker.%COLOR_TXT%
    pause
    exit /b 1
)

echo %COLOR_H1%[OK]%COLOR_TXT% Imagen lista. Ejecutando pipeline...
echo.

docker compose run --rm jullbrain

echo.
echo %COLOR_H1%=========================================================================================
echo [FIN] Proceso de conversion finalizado.
echo =========================================================================================%COLOR_TXT%
echo %RESET%
pause
exit /b 0
