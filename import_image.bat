@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title JullBrain - Importacion de Imagen Podman TAR (Windows)

for %%F in ("%CD%") do set "RAW_FOLDER=%%~nxF"
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "'%RAW_FOLDER%'.ToLower()"`) do set "PROJECT_NAME=%%I"

echo =========================================================================================
echo   JullBrain Enterprise Legal Platform — Importación de Imagen Podman TAR
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

if not exist "!PROJECT_NAME!.tar" (
    echo [ERROR CRITICO] No se encontro el archivo !PROJECT_NAME!.tar en este directorio.
    echo Asegurate de haber copiado el paquete TAR generado previamente por export_image.bat.
    goto IMPORT_ERROR
)

echo [1/1] Cargando imagen OCI desde !PROJECT_NAME!.tar...
echo -----------------------------------------------------------------------------------------
podman load -i "!PROJECT_NAME!.tar"
if errorlevel 1 goto IMPORT_ERROR

echo.
echo =========================================================================================
echo   EXITO: La imagen !PROJECT_NAME!:latest ha sido importada correctamente en Podman.
echo   Puedes ejecutar el sistema mediante: podman run -d -p 8050:8050 !PROJECT_NAME!:latest
echo =========================================================================================
echo.
pause
exit /b 0

:PODMAN_MISSING
echo [ERROR CRITICO] Podman CLI no está instalado o no se encuentra en el PATH.
pause
exit /b 1

:IMPORT_ERROR
echo [ERROR CRITICO] Ocurrió un error durante la importación de la imagen.
pause
exit /b 1
