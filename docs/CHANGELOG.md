# Registro de Cambios (Changelog) — JullBrain Legal-RAG

Todos los cambios notables en este proyecto son documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), y este proyecto se adhiere estrictamente a **[Semantic Versioning 2.0.0 (SemVer)](https://semver.org/lang/es/)** (`MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]`) a través de su fuente única de verdad en [`version.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/version.py).

---

## [0.3.0] - 2026-11-11

### ✨ Añadido (Added) — Incremento `MINOR` según SemVer 2.0.0 (Reglas 3, 4 y 7)
- **Marco de Trabajo Senior IBM Data Prep Kit (`DPK`) & IBM Granite RAG ([`jullbrain/`](file:///c:/VS%20CODE/CODIGO/JullBrain/jullbrain/__init__.py)):**
  - Nuevo motor [`jullbrain/dpk_framework.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/jullbrain/dpk_framework.py) basado en el patrón arquitectónico oficial de **IBM Research (`AbstractIBMTransform` / `IBMDataPrepPipeline`)** con sobre inmutable `TransformResult`, cálculo de hash `SHA-256` por etapa y firma de auditoría `HMAC-SHA256`.
  - Organización modular de la API pública en 6 subpaquetes de dominio: `jullbrain.transforms`, `jullbrain.granite`, `jullbrain.security`, `jullbrain.retrieval`, `jullbrain.runtime` y `jullbrain.interfaces`.
- **Empaquetado Senior PEP 621 ([`pyproject.toml`](file:///c:/VS%20CODE/CODIGO/JullBrain/pyproject.toml)):**
  - Vinculación dinámica de versión (`dynamic = ["version"]` -> `version.__version__`) para evitar desincronización de versiones.
- **Motor Normativo Semantic Versioning 2.0.0 ([`version.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/version.py)):**
  - Implementación completa de las 11 reglas de [https://semver.org/](https://semver.org/): declaración formal de API pública (`PUBLIC_API_DECLARATION`), validación con RegEx oficial BNF de SemVer 2.0.0 (`SEMVER_2_0_0_REGEX`), clase inmutable `SemanticVersion` con cálculo de precedencia (Regla 11) e incrementos deterministas (`bump_major`, `bump_minor`, `bump_patch`).

### 🔄 Cambiado (Changed)
- **Repositorio 100% Python (Cero HTML):**
  - Eliminación de `HTMLResponse` y plantillas HTML embebidas en [`app.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/app.py), operando como servidor REST JSON puro Zero-Trust.
  - Configuración de [`.gitattributes`](file:///c:/VS%20CODE/CODIGO/JullBrain/.gitattributes) para reporte 100% Python en GitHub Linguist y preservación de saltos de línea `CRLF` en archivos `.bat`.

### 🗑️ Eliminado (Removed)
- Eliminación de archivos `.HTML` redundantes en `RAG/datos_brutos/` y del archivo SVG duplicado en la raíz del repositorio (`jullbrain_architecture.svg`, conservado en `docs/jullbrain_architecture.svg`).

---

## [0.2.0] - 2026-11-10

### 🚀 Optimización Integral y Estandarización 100% IBM
- **Unificación Exclusiva con Google Antigravity:** Estandarización de [`.agents/AGENTS.md`](file:///c:/VS%20CODE/CODIGO/JullBrain/.agents/AGENTS.md), [`GEMINI.md`](file:///c:/VS%20CODE/CODIGO/JullBrain/GEMINI.md) y los 6 skills en `.agents/skills/` exclusivamente para **Google Antigravity**. Eliminación total de agentes externos (`qwen-code/`).
- **Consolidación del Núcleo `RAG/` y Bóveda Local `RAG/modelos_ia/`:** Unificación de datos brutos (`RAG/datos_brutos/`), salidas de Docling (`RAG/Informacion_docling_rag/`), chunks vectorizados (`RAG/normativas_chunks/`), bases de datos locales (`RAG/notebooks_db/`, `RAG/lightrag_db/`) y bóveda local de modelos IA (`RAG/modelos_ia/`).
- **Optimización de `IBM Docling` en Procesador (CPU) y Soporte Python 3.14:**
  - Autodiagnóstico de CPU, RAM, **Podman** y versión de Python (`Python 3.14.7` por defecto en la estación local) al iniciar [`orquestador_JullBrain.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador_JullBrain.bat) y [`gpu_detector.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/gpu_detector.py).
  - Configuración automática de hilos CPU (`AcceleratorOptions` + `OMP_NUM_THREADS` / `MKL_NUM_THREADS`) en [`convert_normativas.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/convert_normativas.py).
- **Contenedores Nativos Podman (Windows & Linux) y Nube Exclusiva Oracle Cloud (OCI):**
  - Nuevo [`Containerfile`](file:///c:/VS%20CODE/CODIGO/JullBrain/Containerfile) y [`podman-compose.yml`](file:///c:/VS%20CODE/CODIGO/JullBrain/podman-compose.yml) configurados para ejecución *rootless* (`--security-opt=no-new-privileges`, `--userns=keep-id`).
  - Actualización de [`deploy_oracle.sh`](file:///c:/VS%20CODE/CODIGO/JullBrain/deploy_oracle.sh) y [`oracle_config.json`](file:///c:/VS%20CODE/CODIGO/JullBrain/oracle_config.json) para desplegar con **Podman** y modelos locales en `/opt/jullbrain/RAG/modelos_ia`.
- **Eliminación de Código Basura e Instaladores:**
  - Purga definitiva de Chocolatey (`chocolatey/`), Streamlit (`.streamlit/` y dependencias), instaladores (`installer_tools/`), Google Colab y scripts de IBM Cloud Serverless.

### 🛡️ Avances en Ciberseguridad con Tecnología IBM
- **Guardrails Cognitivos en 6 Dimensiones ([`granite_guardian_guardrail.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_guardian_guardrail.py)):** Protección pre-inferencia (Prompt Injection/Jailbreak, HAP y detección/redacción de PII venezolano: Cédulas `V-/E-`, `RIF`, teléfonos y correos) y post-inferencia (`Groundedness` anti-alucinación).
- **Cadena de Custodia Criptográfica `HMAC-SHA256` ([`audit_logger.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/audit_logger.py)):** Hash-chaining inmutable con enlace `prev_hash`, verificación en tiempo constante (`hmac.compare_digest`), sellado `SHA-256` de la bóveda `RAG/modelos_ia/` (`seal_and_verify_model_vault()`) y validación binaria `%PDF-` (`validate_pdf_magic_bytes()`).
- **Endurecimiento Zero-Telemetry:** Desactivación estricta de telemetría (`HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`), `trust_remote_code=False` y cabeceras HTTP de seguridad en [`app.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/app.py).

---

## [0.1.0] - 2026-07-31

### Características Iniciales
- Pipeline inicial de conversión de PDFs normativos con `IBM Docling`, `legalizer.py`, `metadata_extractor.py` y `validator.py`.
- Búsqueda híbrida local BM25 + vectorial en `opensearch_indexer.py` y gestión de cuadernos con hash `SHA-256` en `notebook_manager.py`.
