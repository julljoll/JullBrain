@echo off
setlocal EnableDelayedExpansion
title JullBrain - Document Converter (Python Native)

:: Set cyan text on black background
color 0b

echo =========================================================================================
echo    JullBrain - Version 2.0 (Native Python Environment)
echo =========================================================================================
echo.
echo This project converts PDF files and Word documents to structured Markdown and JSON.
echo.
echo [+] Execution: Local Python Virtual Environment.
echo =========================================================================================
echo.

cd /d "%~dp0"
set "VENV_DIR=docling_env"

echo [STATUS] Checking system dependencies...

:: 1. Check if local virtual environment exists and has python
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo   [+] Virtual environment '%VENV_DIR%': DETECTED
    set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
    goto VENV_READY
)

:: 2. Check if python is installed globally to create the virtual environment
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   [-] Global Python: NOT DETECTED
    echo [ERROR] Python was not found in the system.
    echo Please install Python 3.10+ and add it to the system PATH.
    pause
    exit /b 1
)

echo   [+] Global Python: DETECTED
echo [INFO] Creating local virtual environment '%VENV_DIR%'...
python -m venv %VENV_DIR%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

:VENV_READY
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: Upgrade pip and install requirements
echo [INFO] Installing/upgrading dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo =========================================================================================
echo [START] Running JullBrain orchestrator...
echo         Processing PDFs in normativas_pdf to normativas_rag.
echo =========================================================================================
echo.

python convert_normativas.py

echo.
echo =========================================================================================
echo [END] Conversion process finished.
echo =========================================================================================
pause
exit /b 0
