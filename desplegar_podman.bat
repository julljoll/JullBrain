@echo off
cd /d "%~dp0"
title JullBrain Despliegue Automatizado en Podman / Podman Desktop

if exist "C:\Program Files\RedHat\Podman\podman.exe" set "PATH=%PATH%;C:\Program Files\RedHat\Podman"
if exist "%LOCALAPPDATA%\Programs\Podman\podman.exe" set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Podman"
if exist "%USERPROFILE%\AppData\Local\Programs\Podman\podman.exe" set "PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Podman"

echo =========================================================================================
echo   JullBrain - Despliegue en Contenedores Podman (Rootless OCI)
echo =========================================================================================

podman --version >nul 2>nul
if errorlevel 1 goto PODMAN_MISSING

echo.
echo [1/3] Limpiando contenedores anteriores (jullbrain_podman)...
echo -----------------------------------------------------------------------------------------
podman stop jullbrain_podman >nul 2>nul
podman rm jullbrain_podman >nul 2>nul

echo.
echo [2/3] Construyendo imagen OCI con Podman (jullbrain-app:latest)...
echo -----------------------------------------------------------------------------------------
podman build -t jullbrain-app:latest -f Containerfile .
if errorlevel 1 goto BUILD_ERROR

echo.
echo [3/3] Iniciando contenedor Rootless en puerto 8050...
echo -----------------------------------------------------------------------------------------
podman run -d -p 8050:8050 --name jullbrain_podman jullbrain-app:latest
if errorlevel 1 goto RUN_ERROR

echo.
echo =========================================================================================
echo   EXITO! Tu aplicacion JullBrain esta ejecutandose en Podman.
echo   URL del Dashboard: http://localhost:8050
echo =========================================================================================
echo Abriendo la interfaz en tu navegador predeterminado...
start http://localhost:8050
pause
exit /b 0

:PODMAN_MISSING
echo.
echo [ERROR] No se ha encontrado el ejecutable podman en tu sistema.
echo.
echo CAUSAS POSIBLES:
echo  1. Podman Desktop / Podman CLI no esta instalado en tu maquina.
echo  2. Podman Machine no esta iniciada en Podman Desktop.
echo.
echo INSTRUCCIONES DE INSTALACION Y CONFIGURACION:
echo  - Descarga e instala Podman Desktop desde: https://podman-desktop.io/
echo  - Abre Podman Desktop e inicia la Podman Machine.
echo.
echo ALTERNATIVA NATIVA (Sin Contenedores):
echo  - Puedes ejecutar la app usando el entorno de Python local con:
echo    python app.py
echo.
pause
exit /b 1

:BUILD_ERROR
echo.
echo [ERROR] La construccion de la imagen OCI en Podman ha fallado.
echo Revisa la salida de los mensajes anteriores.
pause
exit /b 1

:RUN_ERROR
echo.
echo [ERROR] No se pudo lanzar el contenedor en Podman.
echo Asegurate de que el puerto 8050 no este ocupado por otro servicio.
pause
exit /b 1
