@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title JullBrain - Exportacion de Imagen Podman TAR (Windows)

for %%F in ("%CD%") do set "RAW_FOLDER=%%~nxF"
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "'%RAW_FOLDER%'.ToLower()"`) do set "PROJECT_NAME=%%I"

echo =========================================================================================
echo   JullBrain Enterprise Legal Platform — Exportación TAR
echo   Proyecto Detectado: !PROJECT_NAME!
echo =========================================================================================
echo.

where podman >nul 2>nul
if errorlevel 1 (
    if exist "C:\Program Files\RedHat\Podman\podman.exe" set "PATH=%PATH%;C:\Program Files\RedHat\Podman"
    if exist "%LOCALAPPDATA%\Programs\Podman\podman.exe" set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Podman"
    if exist "%USERPROFILE%\AppData\Local\Programs\Podman\podman.exe" set "PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Podman"
)

podman --version >nul 2>nul
if errorlevel 1 goto PODMAN_MISSING

echo [1/2] Verificando la imagen !PROJECT_NAME!:latest...
podman image inspect !PROJECT_NAME!:latest >nul 2>nul
if errorlevel 1 (
    echo [ADVERTENCIA] La imagen !PROJECT_NAME!:latest no existe. Compilando primero...
    call build_podman.bat
    if errorlevel 1 goto SAVE_ERROR
)

echo.
echo [2/2] Generando paquete ejecutable TAR (!PROJECT_NAME!.tar)...
echo -----------------------------------------------------------------------------------------
if exist "!PROJECT_NAME!.tar" del /f /q "!PROJECT_NAME!.tar"

podman save -o "!PROJECT_NAME!.tar" !PROJECT_NAME!:latest
if errorlevel 1 goto SAVE_ERROR

echo.
echo =========================================================================================
echo   EXITO: Paquete TAR generado correctamente: !PROJECT_NAME!.tar
echo =========================================================================================
echo.
pause
exit /b 0

:PODMAN_MISSING
echo [ERROR CRITICO] Podman no está disponible en el sistema.
pause
exit /b 1

:SAVE_ERROR
echo [ERROR CRITICO] Ocurrió un fallo durante la exportación de la imagen TAR.
pause
exit /b 1
