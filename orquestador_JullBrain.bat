@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"
title JullBrain - Orquestador Legal-RAG y Centro de Control Web

:: --- 1. Auto-Elevacion de Privilegios (si se ejecuta directamente) ---
if not "%~1"=="" goto SKIP_ELEVATION
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
:SKIP_ELEVATION

:: --- 2. Extraer caracter ESC de forma nativa e inmune a codificaciones ---
for /F "delims=#" %%a in ('"prompt #$E# & for %%b in (1) do rem"') do set "ESC=%%a"

set "C_BG=%ESC%[48;2;18;22;26m"
set "C_H1=%ESC%[38;2;254;207;6m"
set "C_TXT=%ESC%[38;2;0;255;65m"
set "C_OK=%ESC%[38;2;0;255;0m"
set "C_ERR=%ESC%[38;2;255;85;85m"
set "C_R=%ESC%[0m"

echo %C_BG%%C_TXT%
cls

:BANNER
echo.
echo %C_H1%  =========================================================================================%C_R%
echo %C_H1%    _____       _ _   ____            _                                                    %C_R%
echo %C_H1%   ^|     ^|_   _^| ^| ^| ^| __ ^) _ __ __ _^(_^)_ __                                               %C_R%
echo %C_H1%   ^| ^| ^| ^| ^| ^| ^| ^| ^| ^|  _ \^| .__/ _` ^| ^| ._ \                                              %C_R%
echo %C_H1%   ^| ^|_^| ^| ^|_^| ^| ^| ^| ^| ^|_^) ^| ^| ^| ^(_^| ^| ^| ^| ^| ^|                                             %C_R%
echo %C_H1%    \___/ \__,_^|_^|_^| ^|____/^|_^|  \__,_^|_^|_^| ^|_^|                                             %C_R%
echo %C_H1%  =========================================================================================%C_R%
echo.
echo %C_H1%   JullBrain RAG-Pipeline - Version 2.0 (Entorno Local de Python)%C_R%
echo.
echo %C_TXT%   Este script Orquesta el Diseno y Estructura de Conocimientos para la%C_R%
echo %C_TXT%   Inteligencia Artificial, esta especializado en converir leyes venezolanas%C_R%
echo %C_TXT%   a estructuras para el entrenamiento de Inteligencias Artificiales-%C_R%
echo %C_TXT%   Desarollado por; Jull Ortiz -Rol: Arquitecto de Datos con y para la%C_R%
echo %C_TXT%   inteligencia artificial juridica%C_R%
echo.
echo %C_TXT%   Motor de IA  : IBM Docling (Licencia MIT) -%C_R%
echo %C_TXT%                  https://github.com/docling-project/docling-ibm-models.git%C_R%
echo %C_TXT%   Proposito    : Aportar tecnologia al Estado venezolano para prevenir%C_R%
echo %C_TXT%                  la corrupcion y el retardo procesal.%C_R%
echo %C_TXT%   Desarrollador: Desarrollado Por: Jull Ortiz - Rol: Arquitecto de Datos con IA.%C_R%
echo %C_TXT%                  Licencia del Orquestador: Apache 2.0%C_R%
echo %C_TXT%   Web          : http://www.sha256.us/%C_R%
echo %C_H1%  =========================================================================================%C_R%
echo.

:: --- 3. Verificacion y Activacion del Entorno Virtual ---
if not exist "docling_env\Scripts\activate.bat" (
    echo %C_ERR%  [ERROR] Entorno virtual docling_env no encontrado.%C_R%
    echo %C_TXT%  Buscando interprete Python en el sistema...%C_R%
    set "PY_CMD=python"
    py -3.12 --version >nul 2>&1 && set "PY_CMD=py -3.12"
    echo %C_TXT%  Creando entorno virtual local con %PY_CMD%...%C_R%
    %PY_CMD% -m venv docling_env
    if errorlevel 1 (
        echo %C_ERR%  [ERROR] No se pudo crear el entorno virtual. Instale Python 3.12+ o verifique PATH.%C_R%
        pause
        exit /b 1
    )
)

echo %C_H1%  [INIT] Activando entorno virtual JullBrain...%C_R%
call docling_env\Scripts\activate.bat
if errorlevel 1 (
    echo %C_ERR%  [ERROR] No se pudo activar el entorno virtual en docling_env\%C_R%
    pause
    exit /b 1
)
:: Restaurar UTF-8 inmediatamente tras salir de activate.bat
chcp 65001 >nul 2>nul
echo %C_OK%  [OK] Entorno virtual activado.%C_R%
echo.

:: Si se pasa un argumento por linea de comandos, saltar directo a la accion
if /i "%~1"=="--web" goto LAUNCH_WEB
if /i "%~1"=="--full" goto EXEC_FULL
if /i "%~1"=="--qa" goto EXEC_QA
if /i "%~1"=="--post" goto EXEC_POST
if /i "%~1"=="--embed" goto EXEC_EMBED
if /i "%~1"=="--test" goto EXEC_TEST
if /i "%~1"=="--clean" goto EXEC_CLEAN

:MENU
echo %C_H1%  SELECCIONE UNA OPCION DEL CENTRO DE OPERACIONES:%C_R%
echo.
echo     %C_OK%[1] Iniciar Centro de Control Web (HTML5/CSS3) - http://localhost:8050%C_R%
echo     %C_TXT%[2] Conversion Completa con IBM Docling (Ingesta + Legalizer + Metadata + QA)%C_R%
echo     %C_TXT%[3] Verificacion QA Cruzada (Validador Cruzado PDF vs MD)%C_R%
echo     %C_TXT%[4] Solo Post-Procesado Legal (Legalizer + Frontmatter YAML)%C_R%
echo     %C_TXT%[5] Generar / Verificar Embeddings Semanticos con Granite R2 (Vectores 768-dim)%C_R%
echo     %C_TXT%[6] Ejecutar Suite de QA Testing Offline (Air-Gapped)%C_R%
echo     %C_TXT%[7] Purgar Cache Temporal y Resetear Memoria%C_R%
echo     %C_TXT%[0] Salir%C_R%
echo.
echo %C_H1%  =========================================================================================%C_R%
set "OPTION="
set /p OPTION="  Ingrese el numero de la opcion deseada [0-7]: "

if not defined OPTION goto MENU
if "%OPTION%"=="1" goto LAUNCH_WEB
if "%OPTION%"=="2" goto EXEC_FULL
if "%OPTION%"=="3" goto EXEC_QA
if "%OPTION%"=="4" goto EXEC_POST
if "%OPTION%"=="5" goto EXEC_EMBED
if "%OPTION%"=="6" goto EXEC_TEST
if "%OPTION%"=="7" goto EXEC_CLEAN
if "%OPTION%"=="0" goto EXIT_PROG

echo %C_ERR%  [ERROR] Opcion no valida.%C_R%
goto MENU

:LAUNCH_WEB
echo.
echo %C_OK%  [INIT] Levantando Servidor Web FastAPI e Interfaz HTML5...%C_R%
echo %C_H1%  >>> Abre tu navegador en: http://localhost:8050%C_R%
start http://localhost:8050
python -m uvicorn app:app --host 127.0.0.1 --port 8050
pause
goto MENU

:EXEC_FULL
echo.
echo %C_OK%  [INIT] Ejecutando Conversion Completa con IBM Docling...%C_R%
python convert_normativas.py
pause
goto MENU

:EXEC_QA
echo.
echo %C_OK%  [INIT] Ejecutando Validador QA de Integridad Cruzada...%C_R%
python validator.py RAG\Informacion_docling_rag
pause
goto MENU

:EXEC_POST
echo.
echo %C_OK%  [INIT] Ejecutando Post-Procesado Legal sobre Markdown...%C_R%
python convert_normativas.py --post-process-only
pause
goto MENU

:EXEC_EMBED
echo.
echo %C_OK%  [INIT] Generando / Verificando Embeddings con Granite R2...%C_R%
python granite_embedder.py
pause
goto MENU

:EXEC_TEST
echo.
echo %C_OK%  [INIT] Ejecutando Suite Exhaustiva de QA Testing Offline...%C_R%
python -m unittest discover tests
pause
goto MENU

:EXEC_CLEAN
echo.
echo %C_OK%  [INIT] Purgando cache temporal y liberando memoria...%C_R%
python cleanup.py
pause
goto MENU

:EXIT_PROG
echo.
echo %C_OK%  Sesion finalizada correctamente.%C_R%
exit /b 0
