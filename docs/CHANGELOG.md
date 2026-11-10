# Registro de Cambios (Changelog) — JullBrain Legal-RAG

Todos los cambios relevantes de arquitectura, ciberseguridad y optimización se documentan en este archivo.

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
