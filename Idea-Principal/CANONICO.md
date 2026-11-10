# Documento Canónico Maestro — JullBrain v0.2.0 (Legal-RAG Soberano con Tecnología IBM)

> **Estado:** CANÓNICO OFICIAL (`v0.2.0`)
> **Arquitectura IA:** Exclusivamente Tecnología IBM (`IBM Docling`, `IBM Granite 3.3`, `IBM Granite Embedding R2`, `IBM Granite Guardian 3.2/3.3`)
> **Agente de Desarrollo y Orquestación:** Exclusivamente **Google Antigravity**
> **Ejecución:** Local (`orquestador_JullBrain.bat`), Contenedores Nativos **Podman** (Windows / Linux Rootless) y Nube **Oracle Cloud Infrastructure (OCI)**

---

## 1. Propósito y Alcance Soberano

**JullBrain** es un ecosistema de Inteligencia Artificial Jurídica e Informática Forense diseñado bajo estándares internacionales (**ISO/IEC 27037**, **ISO/IEC 42001**, **NIST AI RMF**) para el procesamiento determinista de leyes, gacetas oficiales y expedientes judiciales venezolanos.

### Decisiones Arquitectónicas No Negociables (`v0.2.0`)
1. **Tecnología de IA 100% IBM**:
   - **Extracción Documental (CPU-First):** `IBM Docling` ejecutándose nativamente en procesador (CPU) con afinidad dinámica de hilos (`OMP_NUM_THREADS` / `MKL_NUM_THREADS`) calculada al iniciar `orquestador_JullBrain.bat`.
   - **Embeddings Semánticos Jurídicos:** `ibm-granite/granite-embedding-english-r2` (768 dimensiones, `safetensors`, `trust_remote_code=False`).
   - **Inferencia Jurídica Determinista:** `ibm-granite/granite-3.3-8b-instruct-GGUF` (Temperatura `0.0` a `0.1`).
   - **Ciberseguridad y Guardrails Cognitivos:** `ibm-granite/granite-guardian-3.2-5b` (6 dimensiones: Prompt Injection/Jailbreak, HAP, PII Venezolano, Groundedness, Context Relevance y Answer Relevance).
2. **Núcleo Único de Información (`RAG/`)**:
   - `RAG/datos_brutos/`: Corpus normativo original (PDFs y Formatos Word).
   - `RAG/Informacion_docling_rag/`: Markdown estructurado con encabezado canónico y JSON de salida Docling.
   - `RAG/normativas_chunks/`: Chunks jerárquicos por artículo enriquecidos con vectores IBM Granite Embedding R2.
   - `RAG/modelos_ia/`: Bóveda local criptográfica de todos los modelos IA (`docling/`, `granite_embeddings/`, `granite_llm/`, `granite_guardian/`, `huggingface/`, `torch/`, `ollama/`) con manifiesto `vault_manifest_sha256.json`.
   - `RAG/notebooks_db/` y `RAG/lightrag_db/`: Cuadernos forenses aislados y grafos de conocimiento locales.
3. **Agente Exclusivo Google Antigravity**:
   - Todo el ciclo de ingeniería, mantenimiento y auditoría de código está unificado exclusivamente para **Google Antigravity** (`.agents/AGENTS.md`, `GEMINI.md` y `.agents/skills/`). Queda prohibido cualquier otro agente o IA externa.
4. **Cero Instaladores, Cero Chocolatey, Cero Streamlit**:
   - Se eliminan por completo Chocolatey, Streamlit y empaquetadores de escritorio. La ejecución local se realiza únicamente mediante `orquestador_JullBrain.bat` (con autodiagnóstico de hardware y entorno Python 3.12–3.14) y la interfaz web ligera Zero-Trust en FastAPI (`app.py`).
5. **Despliegue Exclusivo en Podman y Oracle Cloud (OCI)**:
   - Contenerización nativa en **Podman** (`Containerfile` y `podman-compose.yml`) compatible con Windows y Linux en modo *rootless* (`--security-opt=no-new-privileges`).
   - Única nube autorizada: **Oracle Cloud Infrastructure (OCI)** (`deploy_oracle.sh`, `oracle_config.json`), manteniendo los modelos IA guardados localmente en el volumen seguro `/opt/jullbrain/RAG/modelos_ia`.

---

## 2. Especificación del Encabezado Canónico (`.bat` y `.md`)

Todo archivo `.bat` maestro (`orquestador_JullBrain.bat`, `Idea-Principal/header_canonico.bat`) y todo documento Markdown generado por `convert_normativas.py` debe incluir el encabezado canónico oficial y ser validado mediante [`parser_header_canonico.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/Idea-Principal/parser_header_canonico.py).

### Campos Obligatorios del Bloque de Metadatos (`REM`)
- `Author (GitHub)`
- `Role`
- `Email`
- `Collaboration` (Exclusivamente Google Antigravity + IBM Granite / Docling)
- `Project (GitHub)`
- `License`
- `System Architecture`
- `Stack (Core)`
- `Stack (RAG & DB)`
- `Stack (AI Inference)`
- `Stack (Orchestration)`
- `Security Standards`

---

## 3. Avances de Ciberseguridad IBM Implementados

| Capa de Seguridad | Tecnología / Estándar | Implementación en JullBrain |
| :--- | :--- | :--- |
| **Bóveda Local de Modelos IA** | SHA-256 Model Vault (`NIST AI RMF`) | Todos los pesos de Docling y Granite residen en `RAG/modelos_ia/` y son sellados con `seal_and_verify_model_vault()`. |
| **Cadena de Custodia Criptográfica** | `HMAC-SHA256` Hash-Chaining (`ISO/IEC 27037`) | Cada evento en `audit_logger.py` incluye `prev_hash` y `hmac_sha256` verificables en tiempo constante (`hmac.compare_digest`). |
| **Guardrails Cognitivos 6D** | `IBM Granite Guardian 3.2/3.3` | Escaneo pre-inferencia (Prompt Injection/Jailbreak, HAP, PII Venezolano) y post-inferencia (Groundedness anti-alucinación). |
| **Sanitización Forense de PDFs** | Inspección de Magic Bytes `%PDF-` | `validate_pdf_magic_bytes()` bloquea payloads maliciosos o archivos truncados antes de invocar `IBM Docling`. |
| **Aislamiento Zero-Telemetry** | Air-Gapped Ready | `HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`, `trust_remote_code=False` y cabeceras HTTP CSP/X-Frame-Options estrictas. |
