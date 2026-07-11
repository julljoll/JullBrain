@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion
title JullBrain - Convertidor de Normativas (Docker)

:: Get the ESC character for custom colors
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"

:: Define colors: Background #252525 (Dark Grey), H1 #FECF06 (Yellow/Gold), Text #00FF41 (Green), Error #FF5555 (Light Red)
set "BG_COLOR=%ESC%[48;2;37;37;37m"
set "COLOR_H1=%ESC%[38;2;254;207;6m"
set "COLOR_TXT=%ESC%[38;2;0;255;65m"
set "COLOR_ERR=%ESC%[38;2;255;85;85m"
set "RESET=%ESC%[0m"

:: ===========================================================================
:: 1. AUTO-ELEVACIÃ“N DE PRIVILEGIOS DE ADMINISTRADOR
:: ===========================================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo %BG_COLOR%%COLOR_H1%[INFO] Solicitando permisos de Administrador...%RESET%
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

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
echo %COLOR_H1%[i] PROCESO DE EJECUCIÃ“N DEL SCRIPT:%COLOR_TXT%
echo  [>] 1. VerificaciÃ³n automÃ¡tica de requisitos locales (Chocolatey, Docker).
echo  [>] 2. ConstrucciÃ³n de la imagen aislada de IA (Tesseract OCR, Docling, Python 3.12).
echo  [>] 3. Escaneo y conversiÃ³n de archivos PDF/imÃ¡genes ('normativas_pdf/').
echo  [>] 4. AplicaciÃ³n del pipeline RAG (Hierarchical Chunking + Metadata) usando Docker Compose.
echo %COLOR_H1%=========================================================================================%COLOR_TXT%
echo.

:: ===========================================================================
:: 2. VERIFICACION E INSTALACION DE CHOCOLATEY
:: ===========================================================================
echo %COLOR_H1%[VERIFICACION] Comprobando Chocolatey...%COLOR_TXT%
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Chocolatey no esta instalado. Instalando desde script local...
    if exist "%~dp0installer_tools\install_choco.ps1" (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0installer_tools\install_choco.ps1'"
    ) else (
        echo %COLOR_ERR%[ERROR] No se encontro el instalador de Chocolatey.%COLOR_TXT%
        echo         Descargando de internet...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    )
    
    :: Refrescar variables de entorno
    if exist "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" (
        call "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" >nul 2>&1
    )
    set "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
) else (
    echo %COLOR_H1%[OK]%COLOR_TXT% Chocolatey ya esta instalado.
)
echo.

:: ===========================================================================
:: 3. VERIFICACION E INSTALACION DE DOCKER DESKTOP
:: ===========================================================================
echo %COLOR_H1%[VERIFICACION] Comprobando si Docker esta instalado...%COLOR_TXT%
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Docker no esta instalado. Instalando con Chocolatey...
    choco install docker-desktop -y
    
    if exist "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" (
        call "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" >nul 2>&1
    )
    
    echo %COLOR_H1%=========================================================================================%COLOR_TXT%
    echo %COLOR_ERR%[IMPORTANTE] Docker Desktop ha sido instalado.%COLOR_TXT%
    echo Es MUY PROBABLE que necesites REINICIAR LA COMPUTADORA para que funcionen los servicios
    echo de virtualizacion (WSL2 / Hyper-V) y para aplicar los grupos de usuario de Docker.
    echo.
    echo Por favor, abre "Docker Desktop" desde el menu de inicio para aceptar los terminos y
    echo terminar la configuracion si no reinicias.
    echo %COLOR_H1%=========================================================================================%COLOR_TXT%
    pause
) else (
    echo %COLOR_H1%[OK]%COLOR_TXT% Docker esta instalado.
)

:: Verificar si el motor esta corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] Docker esta instalado pero el motor no esta en ejecucion.%COLOR_TXT%
    echo   Por favor, inicia Docker Desktop manualmente desde tu menu de inicio y vuelve a ejecutar.
    pause
    exit /b 1
)
echo %COLOR_H1%[OK]%COLOR_TXT% Docker esta en ejecucion.
echo.

:: ===========================================================================
:: 4. CONSTRUCCION Y EJECUCION CON DOCKER COMPOSE
:: ===========================================================================
cd /d "%~dp0"

echo %COLOR_H1%[INFO] Construyendo la imagen de Docker (esto usara cache si no hay cambios)...%COLOR_TXT%
docker compose build jullbrain
if %errorlevel% neq 0 (
    echo %COLOR_ERR%[ERROR] Hubo un problema al construir la imagen de Docker.%COLOR_TXT%
    pause
    exit /b 1
)
echo %COLOR_H1%[OK]%COLOR_TXT% Imagen construida correctamente.
echo.

echo %COLOR_H1%=========================================================================================
echo [INICIO] Ejecutando el orquestador principal de conversion en Docker...
echo =========================================================================================%COLOR_TXT%
echo.

docker compose run --rm jullbrain

echo.
echo %COLOR_H1%=========================================================================================
echo [FIN] Proceso de conversion finalizado.
echo =========================================================================================%COLOR_TXT%
echo %RESET%
pause
exit /b 0

