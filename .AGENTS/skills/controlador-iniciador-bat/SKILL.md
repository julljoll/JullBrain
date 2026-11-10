---
name: JullBrain-controlador-iniciador-bat
description: Skill para administrar, proteger y modificar la lógica visual, estructural y de autodiagnóstico de hardware del iniciador local orquestador_JullBrain.bat en Google Antigravity. Úsalo siempre que el usuario pida modificar el .bat, arreglar problemas de consola en Windows, actualizar la detección de CPU/RAM/Podman/Python 3.14, verificar la bóveda local RAG/modelos_ia, o validar el encabezado canónico.
---

# 🚀 JullBrain — Controlador del Iniciador Maestro (`orquestador_JullBrain.bat`)

Este skill define las reglas inquebrantables para mantener y evolucionar [`orquestador_JullBrain.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador_JullBrain.bat) y [`header_canonico.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/Idea-Principal/header_canonico.bat) dentro de **Google Antigravity**.

---

## 1. Arquitectura de 6 Fases de `orquestador_JullBrain.bat` (`v0.2.0`)

1. **Encabezado Canónico Oficial (`REM`)**:
   - Debe coincidir con [`Idea-Principal/header_canonico.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/Idea-Principal/header_canonico.bat) y aprobar [`parser_header_canonico.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/Idea-Principal/parser_header_canonico.py).
2. **Autoelevación UAC + Configuración UTF-8 (`chcp 65001`) + Variables Zero-Telemetry**:
   - Solicita privilegios de administrador en Windows (`fltmc` / `ShellExecute` `"runas"`).
   - Configura variables locales para la bóveda de modelos IA:
     - `JULLBRAIN_MODEL_VAULT=%CD%\RAG\modelos_ia`
     - `DOCLING_ARTIFACTS_PATH=%CD%\RAG\modelos_ia\docling`
     - `HF_HOME=%CD%\RAG\modelos_ia\huggingface`
     - `TORCH_HOME=%CD%\RAG\modelos_ia\torch`
     - `OLLAMA_MODELS=%CD%\RAG\modelos_ia\ollama`
     - `HF_HUB_DISABLE_TELEMETRY=1` y `DO_NOT_TRACK=1`
3. **FASE 1 — Análisis de Computadora Host (CPU para IBM Docling, RAM y Podman)**:
   - Detecta `NUMBER_OF_PROCESSORS` y calcula los hilos óptimos para `IBM Docling` en CPU (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`).
   - Consulta la memoria RAM total y verifica si **Podman** está instalado (`podman --version`).
4. **FASE 2 — Estructura del Núcleo `RAG/` y Bóveda Local `RAG/modelos_ia/`**:
   - Garantiza la existencia de `RAG\datos_brutos`, `RAG\Informacion_docling_rag`, `RAG\normativas_chunks`, `RAG\modelos_ia\{docling,granite_embeddings,granite_llm,granite_guardian,huggingface,torch,ollama}`, `RAG\notebooks_db`, `RAG\lightrag_db` y `logs`.
5. **FASE 3 y 4 — Autoreparación del Entorno Virtual Python (`3.14` / `3.13` / `3.12`) e Instalación**:
   - Verifica si `docling_env\Scripts\python.exe` es funcional; si el Python base del sistema fue actualizado (p. ej. a `%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe`), repara o recrea automáticamente `docling_env`.
   - Verifica e instala las dependencias de [`requirements.txt`](file:///c:/VS%20CODE/CODIGO/JullBrain/requirements.txt) y ejecuta `convert_normativas.py --bootstrap-models` si la bóveda local aún no está sellada.
6. **FASE 5 — Lanzamiento de [`orquestador.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador.py)**:
   - Ejecuta el menú interactivo y mantiene una cláusula `pause` de protección ante cualquier código de salida distinto de `0`.

---

## 2. Reglas Críticas No Negociables para Archivos `.bat`

1. **Prohibido usar Chocolatey, Streamlit o Instaladores Externos**:
   - El `.bat` opera únicamente con herramientas nativas de Windows, Python (`3.12 - 3.14`) y **Podman**.
2. **Prohibido usar paréntesis literales sin escapar dentro de bloques `if (...) else (...)`**:
   - Todo paréntesis literal en un `echo` dentro de un bloque `if/else` rompe `cmd.exe`. Usa corchetes `[...]` o guiones.
3. **Codificación Obligatoria UTF-8 sin BOM + CRLF (`\r\n`)**:
   - Las herramientas de escritura de archivos suelen guardar con `LF` (`\n`). En `cmd.exe`, los archivos con `LF` provocan saltos de etiquetas y cierre súbito de la ventana.
   - **SIEMPRE** que edites `orquestador_JullBrain.bat` o `Idea-Principal/header_canonico.bat`, debes ejecutar inmediatamente este comando en PowerShell:

```powershell
$Path = "c:\VS CODE\CODIGO\JullBrain\orquestador_JullBrain.bat"; $Text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8); $Text = $Text -replace "`r?`n", "`r`n"; [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding $False))
```

4. **Validación Canónica Post-Edición**:
   - Ejecuta `python Idea-Principal/parser_header_canonico.py orquestador_JullBrain.bat` para confirmar que no hay BOM, que los saltos son CRLF y que todos los campos canónicos están intactos.
