@echo off
cd /d "%~dp0"
title JullBrain - Exportador de Imagen para Podman Desktop

if exist "C:\Program Files\RedHat\Podman\podman.exe" set "PATH=%PATH%;C:\Program Files\RedHat\Podman"
if exist "%LOCALAPPDATA%\Programs\Podman\podman.exe" set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Podman"
if exist "%USERPROFILE%\AppData\Local\Programs\Podman\podman.exe" set "PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Podman"

echo =========================================================================================
echo   JullBrain - Exportacion de Imagen OCI para Podman Desktop (.tar)
echo =========================================================================================

podman --version >nul 2>nul
if errorlevel 1 goto PODMAN_MISSING

echo.
echo [1/2] Verificando y Construyendo imagen jullbrain-app:latest...
echo -----------------------------------------------------------------------------------------
podman build -t jullbrain-app:latest -f Containerfile .
if errorlevel 1 goto BUILD_ERROR

echo.
echo [2/2] Exportando imagen a paquete comprimido OCI jullbrain-app-podman.tar...
echo -----------------------------------------------------------------------------------------
if exist jullbrain-app-podman.tar del /f /q jullbrain-app-podman.tar

podman save -o jullbrain-app-podman.tar jullbrain-app:latest
if errorlevel 1 goto SAVE_ERROR

echo.
echo =========================================================================================
echo   IMAGEN EXPORTADA CON EXITO!
echo   Archivo generado: jullbrain-app-podman.tar
echo =========================================================================================
echo.
echo COMO IMPORTAR ESTA IMAGEN EN PODMAN DESKTOP:
echo  1. Abre la aplicacion Podman Desktop en tu sistema.
echo  2. Ve a la pestana Images (Imagenes) en el menu lateral izquierdo.
echo  3. Haz clic en el boton Import image.
echo  4. Selecciona el archivo jullbrain-app-podman.tar ubicado en esta carpeta:
echo     %CD%\jullbrain-app-podman.tar
echo  5. Una vez cargada, haz clic en Run para iniciar el contenedor en el puerto 8050.
echo =========================================================================================
echo.
pause
exit /b 0

:PODMAN_MISSING
echo.
echo [ERROR] Podman CLI no esta instalado o no se encuentra en el PATH.
pause
exit /b 1

:BUILD_ERROR
echo.
echo [ERROR] Error al compilar la imagen OCI.
pause
exit /b 1

:SAVE_ERROR
echo.
echo [ERROR] Error al exportar la imagen tarball.
pause
exit /b 1
