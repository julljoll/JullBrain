@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion
title JullBrain - Convertidor de Normativas (Docker)

:: ===========================================================================
:: 1. AUTO-ELEVACIÃ“N DE PRIVILEGIOS DE ADMINISTRADOR
:: ===========================================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Solicitando permisos de Administrador para instalar dependencias...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: ===========================================================================
:: BANNER PRINCIPAL
:: ===========================================================================
cls
echo =========================================================================================
echo    JULLBRAIN - CONVERTIDOR AUTOMATIZADO
echo =========================================================================================
echo.
echo                        ---  M I   C E R E B R O   P E R S O N A L  ---
echo =========================================================================================
echo [SYS] JullBrain V-2.0: Convertidor Automatizado de Normativas, Leyes y Formatos Word para RAG / IA
echo =========================================================================================
echo.
echo [+] Informacion del Desarrollador:
echo     [-] Nombre: Jull Ortiz
echo     [-] Correo: julljoll@gmail.com
echo [+] Proposito: Avanzar en la transformacion tecnologica del sistema de justicia venezolano.
echo [+] Ejecucion: Entorno Dockerizado
echo =========================================================================================
echo.

:: ===========================================================================
:: 2. VERIFICACION E INSTALACION DE CHOCOLATEY
:: ===========================================================================
echo [VERIFICACION] Comprobando Chocolatey...
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Chocolatey no esta instalado. Instalando desde script local...
    if exist "%~dp0installer_tools\install_choco.ps1" (
        powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0installer_tools\install_choco.ps1'"
    ) else (
        echo [ERROR] No se encontro el instalador de Chocolatey en installer_tools\install_choco.ps1.
        echo         Descargando de internet...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    )
    
    :: Refrescar variables de entorno para que choco este disponible en esta sesion
    if exist "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" (
        call "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" >nul 2>&1
    )
    :: Agregamos choco temporalmente al PATH en caso de que RefreshEnv falle
    set "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
) else (
    echo [OK] Chocolatey ya esta instalado.
)
echo.

:: ===========================================================================
:: 3. VERIFICACION E INSTALACION DE DOCKER DESKTOP
:: ===========================================================================
echo [VERIFICACION] Comprobando si Docker esta instalado...

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Docker no esta instalado. Instalando con Chocolatey...
    choco install docker-desktop -y
    
    :: Refrescar variables de entorno nuevamente
    if exist "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" (
        call "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd" >nul 2>&1
    )
    
    echo =========================================================================================
    echo [IMPORTANTE] Docker Desktop ha sido instalado.
    echo Es MUY PROBABLE que necesites REINICIAR LA COMPUTADORA para que funcionen los servicios
    echo de virtualizacion (WSL2 / Hyper-V) y para aplicar los grupos de usuario de Docker.
    echo.
    echo Por favor, abre "Docker Desktop" desde el menu de inicio para aceptar los terminos y
    echo terminar la configuracion si no reinicias.
    echo =========================================================================================
    pause
) else (
    echo [OK] Docker esta instalado.
)

:: Verificar si el motor esta corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker esta instalado pero el motor no esta en ejecucion.
    echo   Por favor, inicia Docker Desktop manualmente y vuelve a ejecutar este script.
    pause
    exit /b 1
)
echo [OK] Docker esta en ejecucion.
echo.

:: ===========================================================================
:: 4. CONSTRUCCION Y EJECUCION CON DOCKER COMPOSE
:: ===========================================================================
cd /d "%~dp0"

echo [INFO] Construyendo la imagen de Docker (esto usara cache si no hay cambios)...
docker compose build jullbrain
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema al construir la imagen de Docker.
    pause
    exit /b 1
)
echo [OK] Imagen construida correctamente.
echo.

echo =========================================================================================
echo [INICIO] Ejecutando el orquestador principal de conversion en Docker...
echo =========================================================================================
echo.

docker compose run --rm jullbrain

echo.
echo =========================================================================================
echo [FIN] Proceso de conversion finalizado.
echo =========================================================================================
pause
exit /b 0

