@echo off

chcp 65001 >nul 2>nul
cd /d "%~dp0"
title JullBrain - Orquestador de Conocimientos para IA Juridica

:: --- Definir colores exactos ---
set "C_BG=[48;2;82;64;0m"
set "C_H1=[38;2;254;207;6m"
set "C_TXT=[38;2;0;255;65m"
set "C_OK=[38;2;0;255;0m"
set "C_ERR=[38;2;255;85;85m"
set "C_R=[0m%C_BG%%C_TXT%"

:: Aplicar color de fondo a toda la ventana
echo %C_BG%%C_TXT%
cls

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

:: --- Activar Entorno Virtual ---
echo %C_H1%  [INIT] Activando entorno virtual JullBrain...%C_R%
call docling_env\Scripts\activate.bat
if errorlevel 1 (
    echo %C_ERR%  [ERROR] No se pudo activar el entorno virtual en docling_env\%C_R%
    pause
    exit /b 1
)
echo %C_OK%  [OK] Entorno virtual activado.%C_R%
echo.

:: --- Mostrar Enlace Local y Lanzar ---
echo %C_H1%  =========================================================================================%C_R%
echo %C_OK%    SERVIDOR WEB INICIADO CON EXITO%C_R%
echo %C_TXT%    Abre la interfaz visual en tu navegador web:%C_R%
echo %C_H1%    ^>^>^> URL Local: http://localhost:8501%C_R%
echo %C_TXT%    Presione Ctrl + C en esta ventana para apagar el servidor de Streamlit.%C_R%
echo %C_H1%  =========================================================================================%C_R%
echo.
call streamlit run app.py
echo.
echo %C_OK%  Servidor de Streamlit finalizado.%C_R%
pause
exit /b 0
