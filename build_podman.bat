@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title JullBrain - Construccion de Imagen Podman (Windows)

:: Detectar nombre del proyecto dinamicamente basado en el nombre del directorio en minusculas
for %%F in ("%CD%") do set "RAW_FOLDER=%%~nxF"
set "PROJECT_NAME=!RAW_FOLDER!"
for %%L in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do (
    set "PROJECT_NAME=!PROJECT_NAME:%%L=%%L!"
)
:: Convertir a minusculas puro
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "'%RAW_FOLDER%'.ToLower()"`) do set "PROJECT_NAME=%%I"

echo =========================================================================================
echo   JullBrain Enterprise Legal Platform — Construcción Podman
echo   Proyecto Detectado: !PROJECT_NAME!
echo =========================================================================================
echo.

:: 1. Verificar si Podman está instalado
where podman >nul 2>nul
if errorlevel 1 (
    if exist "C:\Program Files\RedHat\Podman\podman.exe" set "PATH=%PATH%;C:\Program Files\RedHat\Podman"
    if exist "%LOCALAPPDATA%\Programs\Podman\podman.exe" set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Podman"
    if exist "%USERPROFILE%\AppData\Local\Programs\Podman\podman.exe" set "PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Podman"
)

podman --version >nul 2>nul
if errorlevel 1 goto PODMAN_MISSING

echo [1/2] Verificando instalacion de Podman... OK
podman --version
echo.

echo [2/2] Construyendo la imagen OCI (!PROJECT_NAME!:latest)...
echo -----------------------------------------------------------------------------------------
podman build -t !PROJECT_NAME!:latest -f Containerfile .
if errorlevel 1 goto BUILD_ERROR

echo.
echo =========================================================================================
echo   EXITO: La imagen !PROJECT_NAME!:latest ha sido construida correctamente.
echo =========================================================================================
echo.
pause
exit /b 0

:PODMAN_MISSING
echo.
echo [ERROR CRITICO] Podman no esta instalado o no se encuentra en la variable PATH.
echo Instala Podman Desktop desde: https://podman-desktop.io/
echo.
pause
exit /b 1

:BUILD_ERROR
echo.
echo [ERROR CRITICO] Ocurrio un error durante la construccion de la imagen Podman.
echo El proceso ha sido detenido. Revisa la salida de error anterior.
echo.
pause
exit /b 1
