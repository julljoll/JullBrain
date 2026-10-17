@echo off
:: ===================================================================
::  JullBrain V-2.0 - Script de Post-Instalacion
::  Crea entorno virtual, instala dependencias y verifica Tesseract.
:: ===================================================================
chcp 65001 > nul
setlocal EnableDelayedExpansion

set "INSTALL_DIR=%~1"
if "%INSTALL_DIR%"=="" set "INSTALL_DIR=%~dp0"

:: Log file
set "LOG=%INSTALL_DIR%\instalacion.log"
echo [%DATE% %TIME%] === INICIO DE INSTALACION === > "%LOG%"

echo.
echo =========================================================
echo  JullBrain V-2.0 - Configurando entorno...
echo =========================================================
echo.

:: ------- 1. Verificar Python -------
echo [1/5] Verificando Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/5] Python no encontrado. Buscando en rutas comunes...
    set "PY_PATHS=C:\Python313;C:\Python312;C:\Python311;C:\Python310;%USERPROFILE%\AppData\Local\Programs\Python\Python313;%USERPROFILE%\AppData\Local\Programs\Python\Python312;%USERPROFILE%\AppData\Local\Programs\Python\Python311;%USERPROFILE%\AppData\Local\Programs\Python\Python310;C:\tools\python"
    for %%p in (!PY_PATHS!) do (
        if exist "%%p\python.exe" (
            set "PATH=!PATH!;%%p;%%p\Scripts"
            echo [1/5] Python encontrado en: %%p
            goto :PYTHON_FOUND
        )
    )
    echo [ERROR] Python no esta instalado. Instale Python 3.10+ desde https://python.org
    echo [ERROR] Python no encontrado >> "%LOG%"
    pause
    exit /b 1
)
:PYTHON_FOUND
python --version >> "%LOG%" 2>&1
echo [1/5] Python verificado.

:: ------- 2. Crear entorno virtual -------
echo [2/5] Creando entorno virtual docling_env...
if exist "%INSTALL_DIR%\docling_env" (
    echo [2/5] Entorno virtual ya existe, omitiendo creacion.
) else (
    python -m venv "%INSTALL_DIR%\docling_env" >> "%LOG%" 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        echo [ERROR] Error al crear venv >> "%LOG%"
        pause
        exit /b 1
    )
    echo [2/5] Entorno virtual creado.
)

:: ------- 3. Actualizar pip -------
echo [3/5] Actualizando pip...
"%INSTALL_DIR%\docling_env\Scripts\python.exe" -m pip install --upgrade pip >> "%LOG%" 2>&1
echo [3/5] Pip actualizado.

:: ------- 4. Instalar dependencias -------
echo [4/5] Instalando dependencias (esto puede tardar 5-15 minutos)...
echo       docling, PyMuPDF, pypdf, rich, PyYAML, psutil...
echo.

"%INSTALL_DIR%\docling_env\Scripts\python.exe" -m pip install docling PyMuPDF pypdf rich PyYAML psutil >> "%LOG%" 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Algunas dependencias pueden no haberse instalado. Revise instalacion.log
) else (
    echo [4/5] Dependencias instaladas correctamente.
)

:: ------- 5. Instalar Tesseract OCR (opcional, via winget) -------
echo [5/5] Verificando Tesseract OCR...
where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo [5/5] Intentando instalar Tesseract OCR (OCR para PDFs escaneados)...
    winget install --id UB-Mannheim.TesseractOCR --silent --accept-package-agreements --accept-source-agreements >> "%LOG%" 2>&1
    if %errorlevel% == 0 (
        echo [5/5] Tesseract OCR instalado correctamente.
    ) else (
        echo [5/5] Tesseract OCR no pudo instalarse automaticamente.
        echo       Para OCR en PDFs escaneados, instale manualmente desde:
        echo       https://github.com/UB-Mannheim/tesseract/wiki
    )
) else (
    echo [5/5] Tesseract OCR ya esta instalado.
)

echo.
echo =========================================================
echo  Instalacion completada exitosamente!
echo  Ejecute orquestador_JullBrain.bat para comenzar.
echo =========================================================
echo.
echo [%DATE% %TIME%] === INSTALACION COMPLETADA === >> "%LOG%"
exit /b 0
