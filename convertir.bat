@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"
title JullBrain - Orquestador y Validador QA de IBM Docling

set "HEADLESS=0"
if not "%~1"=="" set "HEADLESS=1"

if /i "%~1"=="--full" goto EXEC_FULL
if /i "%~1"=="--qa" goto EXEC_QA
if /i "%~1"=="--post" goto EXEC_POST
if /i "%~1"=="--embed" goto EXEC_EMBED
if /i "%~1"=="--web" goto EXEC_WEB
if /i "%~1"=="--clean" goto EXEC_CLEAN

:MENU
cls
echo =========================================================================================
echo   JullBrain - IBM Technology Architecture Design -- Venezuela Legal RAG Pipeline
echo =========================================================================================
echo.
echo   Este script Orquesta el Diseno, Conversion y Control de Calidad (QA) para la
echo   Inteligencia Artificial Juridica venezolana (IBM Docling + Granite Embedding R2).
echo   Desarrollado por: Jull Ortiz - Rol: Arquitecto de Datos con IA.
echo.
echo   Carpetas Activas:
echo   - Entrada (Datos Brutos) : %CD%\RAG\datos_brutos
echo   - Salida  (RAG Y Chunks) : %CD%\RAG\Informacion_docling_rag
echo =========================================================================================
echo.
echo   SELECCIONE UNA OPCION DEL PLAN DE TRABAJO / QA:
echo.
echo     [1] Conversion Completa con IBM Docling (Ingesta + Legalizer + Metadata + QA)
echo     [2] Ejecutar Plan de Verificacion de Calidad (QA Y Validador Cruzado PDF vs MD)
echo     [3] Solo Post-Procesado Legal (Legalizer + Frontmatter YAML sin re-convertir)
echo     [4] Generar Embeddings Semanticos con Granite R2 (Vectores 768-dim)
echo     [5] Iniciar Dashboard Web de Control (Plotly Dash - http://localhost:8050)
echo     [6] Limpiar Cache y Resetear Estado del Pipeline
echo     [0] Salir
echo.
echo =========================================================================================
set /p OPTION="Ingrese el numero de la opcion deseada [0-6]: "

if "%OPTION%"=="1" goto EXEC_FULL
if "%OPTION%"=="2" goto EXEC_QA
if "%OPTION%"=="3" goto EXEC_POST
if "%OPTION%"=="4" goto EXEC_EMBED
if "%OPTION%"=="5" goto EXEC_WEB
if "%OPTION%"=="6" goto EXEC_CLEAN
if "%OPTION%"=="0" goto EXIT_PROG

echo.
echo [ERROR] Opcion no valida. Presione cualquier tecla para reintentar...
if "%HEADLESS%"=="0" pause >nul
goto MENU


:CHECK_ENV
echo.
echo [QA Pre-flight] Verificando entorno virtual 'docling_env'...
if not exist "docling_env\Scripts\activate.bat" goto ERR_ENV_MISSING

call docling_env\Scripts\activate.bat
if %errorlevel% neq 0 goto ERR_ENV_ACTIVATE

echo [OK] Entorno virtual 'docling_env' activado correctamente.
echo.

if not exist "RAG\datos_brutos" mkdir "RAG\datos_brutos" >nul 2>nul
if not exist "RAG\Informacion_docling_rag" mkdir "RAG\Informacion_docling_rag" >nul 2>nul
if not exist ".conversion_cache" mkdir ".conversion_cache" >nul 2>nul
if not exist "scratch" mkdir "scratch" >nul 2>nul
exit /b 0

:ERR_ENV_MISSING
echo.
echo [ERROR CRITICO] No se encontro el entorno virtual en: %CD%\docling_env
echo Por favor, asegurese de haber instalado el entorno virtual con las dependencias.
echo.
if "%HEADLESS%"=="0" pause
exit /b 1

:ERR_ENV_ACTIVATE
echo.
echo [ERROR] Fallo la activacion de docling_env.
echo.
if "%HEADLESS%"=="0" pause
exit /b 1


:EXEC_FULL
call :CHECK_ENV
if %errorlevel% neq 0 exit /b 1
echo =========================================================================================
echo   [1/2] INICIANDO CONVERSION COMPLETA CON IBM DOCLING + LEGALIZER + QA
echo =========================================================================================
echo.
python convert_normativas.py
if %errorlevel% neq 0 goto ERR_CONVERT

echo.
echo =========================================================================================
echo   [2/2] EJECUTANDO PLAN DE VERIFICACION DE CALIDAD (QA CRUZADO PDF vs MD)
echo =========================================================================================
echo.
python validator.py RAG\Informacion_docling_rag
echo.
echo [OK] Proceso de Conversion y Verificacion completado con exito.
if "%HEADLESS%"=="1" exit /b 0
pause
goto MENU

:ERR_CONVERT
echo.
echo [ERROR] Se detectaron problemas durante la conversion con Docling.
echo.
if "%HEADLESS%"=="0" pause
exit /b 1


:EXEC_QA
call :CHECK_ENV
if %errorlevel% neq 0 exit /b 1
echo =========================================================================================
echo   EJECUTANDO PLAN DE VERIFICACION DE CALIDAD (QA Y VALIDADOR CRUZADO)
echo =========================================================================================
echo.
python validator.py RAG\Informacion_docling_rag
set "QA_CODE=%errorlevel%"
if %QA_CODE% neq 0 goto QA_WARN
goto QA_OK

:QA_WARN
echo.
echo [!] Se detectaron inconsistencias o advertencias durante el QA.
echo.
if "%HEADLESS%"=="1" exit /b %QA_CODE%
pause
goto MENU

:QA_OK
echo.
echo [OK] Todos los documentos superaron el control de calidad (QA).
echo.
if "%HEADLESS%"=="1" exit /b 0
pause
goto MENU


:EXEC_POST
call :CHECK_ENV
if %errorlevel% neq 0 exit /b 1
echo =========================================================================================
echo   RE-APLICANDO POST-PROCESADO LEGAL (LEGALIZER + FRONTMATTER YAML)
echo =========================================================================================
echo.
python convert_normativas.py --post-process-only
echo.
echo [OK] Post-procesado ejecutado.
if "%HEADLESS%"=="1" exit /b 0
pause
goto MENU


:EXEC_EMBED
call :CHECK_ENV
if %errorlevel% neq 0 exit /b 1
echo =========================================================================================
echo   GENERANDO EMBEDDINGS SEMANTICOS CON IBM GRANITE EMBEDDING R2
echo =========================================================================================
echo.
python granite_embedder.py
echo.
echo [OK] Proceso de generacion de vectores completado.
if "%HEADLESS%"=="1" exit /b 0
pause
goto MENU


:EXEC_WEB
call :CHECK_ENV
if %errorlevel% neq 0 exit /b 1
echo =========================================================================================
echo   INICIANDO DASHBOARD WEB DE CONTROL JULLBRAIN (PLOTLY DASH)
echo   URL del Dashboard: http://localhost:8050
echo =========================================================================================
echo.
start http://localhost:8050
python app.py
if "%HEADLESS%"=="1" exit /b 0
pause
goto MENU


:EXEC_CLEAN
call :CHECK_ENV
if %errorlevel% neq 0 exit /b 1
echo =========================================================================================
echo   LIMPIEZA DE CACHE Y MEMORIA DEL PIPELINE
echo =========================================================================================
echo.
python cleanup.py
echo.
echo [OK] Cache y archivos temporales purgados con exito.
if "%HEADLESS%"=="1" exit /b 0
pause
goto MENU


:EXIT_PROG
echo.
echo Gracias por usar JullBrain Legal-RAG. Hasta pronto!
echo.
exit /b 0