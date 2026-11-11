# ⚖️ JullBrain v0.3.0 — Sistema Legal-RAG Soberano con Tecnología IBM

[![SemVer 2.0.0](https://img.shields.io/badge/SemVer-2.0.0--v0.3.0-blue)](https://semver.org/lang/es/)
[![Stack IBM](https://img.shields.io/badge/IBM%20AI-Docling%20%7C%20Granite%203.3%20%7C%20Granite%20Guardian-052FAD)](https://github.com/ibm-granite)
[![Python 3.12-3.14](https://img.shields.io/badge/Python-3.12%20--%203.14-3776AB)](https://www.python.org/)

> **Pipeline Jurídico-Forense Determinista para Normativas Venezolanas**
> **Stack IA Exclusivo IBM:** `IBM Data Prep Kit (DPK)` · `IBM Docling (CPU)` · `IBM Granite 3.3 8B` · `IBM Granite Embedding R2 (768d)` · `IBM Granite Guardian 3.2/3.3 (6D)`
> **Agente de Ingeniería Exclusivo:** **Google Antigravity**
> **Versionado:** **[Semantic Versioning 2.0.0 (`v0.3.0`)](https://semver.org/)** gestionado desde [`version.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/version.py)
> **Entornos de Ejecución:** Local (`orquestador_JullBrain.bat`), **Podman** Nativo (Windows / Linux Rootless) y **Oracle Cloud Infrastructure (OCI)**

---

## 1. Arquitectura de Núcleo Único (`RAG/`) y Ciberseguridad IBM

Todo el flujo de información y los pesos de los modelos de Inteligencia Artificial residen de forma aislada dentro del directorio `RAG/` para garantizar soberanía de datos, operación *Air-Gapped* y cadena de custodia forense (**ISO/IEC 27037**, **ISO/IEC 42001**, **NIST AI RMF**):

```text
JullBrain/
├── RAG/                                  [NÚCLEO CENTRAL DE INFORMACIÓN Y MODELOS IA]
│   ├── datos_brutos/                     PDFs de Gacetas Oficiales, Códigos, Leyes y Formatos_Word/
│   ├── Informacion_docling_rag/          Markdown estructurado (Encabezado Canónico + YAML) y JSON Docling
│   ├── normativas_chunks/                Chunks jerárquicos por artículo + Vectores Granite Embedding R2
│   ├── modelos_ia/                       Bóveda Criptográfica Local de Modelos IA (Sellada con SHA-256)
│   │   ├── docling/                      Modelos locales de layout y TableFormer de IBM Docling (CPU)
│   │   ├── granite_embeddings/           ibm-granite/granite-embedding-english-r2 (768 dimensiones)
│   │   ├── granite_llm/                  ibm-granite/granite-3.3-8b-instruct-GGUF
│   │   ├── granite_guardian/             ibm-granite/granite-guardian-3.2-5b (Guardrails 6D)
│   │   ├── huggingface/                  Caché local aislada (Zero-Telemetry)
│   │   ├── torch/                        Caché local PyTorch
│   │   └── ollama/                       Almacén local de blobs GGUF para Ollama / Podman
│   ├── notebooks_db/                     Expedientes jurídicos aislados con verificación SHA-256
│   └── lightrag_db/                      Grafo de conocimiento normativo (GraphRAG)
│
├── jullbrain/                            [FRAMEWORK SENIOR: IBM DATA PREP KIT (DPK) & GRANITE RAG]
│   ├── dpk_framework.py                  Motor de Transformaciones Deterministas (AbstractIBMTransform / Pipeline)
│   ├── transforms/                       Dominio 1: Ingesta Docling (CPU), Jerarquía, Metadata y Validación
│   ├── granite/                          Dominio 2: Embeddings IBM Granite R2 (768d) y LightRAG (Granite 3.3)
│   ├── security/                         Dominio 3: IBM Granite Guardian (6D) y Cadena Forense HMAC-SHA256
│   ├── retrieval/                        Dominio 4: Búsqueda Híbrida BM25 + k-NN RRF y Cuadernos SHA-256
│   ├── runtime/                          Dominio 5: Perfilador de Hardware (CPU/RAM/Podman) y Limpieza
│   └── interfaces/                       Dominio 6: Consola TUI Rich, API REST FastAPI y Open WebUI Pipe
│
├── pyproject.toml                        Definición Senior PEP 621 del paquete y CLI entrypoints
├── orquestador_JullBrain.bat             Iniciador Local Maestro (Analiza CPU/RAM/Podman/Python 3.14)
├── orquestador.py                        Consola interactiva TUI (Rich)
├── convert_normativas.py                 Motor IBM Docling (CPU Threads) + HierarchicalChunker
├── legalizer.py                          Analizador determinista de jerarquía legal venezolana
├── metadata_extractor.py                 Extractor de YAML Frontmatter y SHA-256 documental
├── granite_embedder.py                   Motor de Embeddings IBM Granite R2 desde bóveda local
├── granite_guardian_guardrail.py         Guardrails Cognitivos 6D (Prompt Injection, HAP, PII, Groundedness)
├── validator.py                          Doble validación cruzada (Markdown vs PDF original con PyMuPDF)
├── audit_logger.py                       Cadena criptográfica inmutable HMAC-SHA256 y sellado de bóveda
├── app.py                                Portal Web & API REST Zero-Trust (FastAPI)
├── Containerfile / Dockerfile            Imagen nativa para Podman Rootless (Windows & Linux)
├── podman-compose.yml                    Orquestación multicontenedor para Podman
├── deploy_oracle.sh / oracle_config.json Despliegue exclusivo en Oracle Cloud Infrastructure (OCI)
└── Idea-Principal/                       Especificación y validador del Encabezado Canónico (.bat / .md)
```

---

## 2. Ejecución Local en Windows (`orquestador_JullBrain.bat`)

El proyecto se ejecuta localmente mediante un único punto de entrada:

```cmd
orquestador_JullBrain.bat
```

Al iniciarse, `orquestador_JullBrain.bat` ejecuta automáticamente **5 fases**:
1. **Análisis de Hardware Host**: Detecta núcleos e hilos del procesador para optimizar `IBM Docling` en CPU (`OMP_NUM_THREADS` / `MKL_NUM_THREADS`), calcula la memoria RAM disponible y verifica la presencia de **Podman**.
2. **Verificación del Núcleo `RAG/` y Bóveda `RAG/modelos_ia/`**: Crea y valida toda la estructura de directorios locales y desactiva cualquier telemetría externa (`HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`).
3. **Autodiagnóstico y Reparación de Python (`3.14` / `3.13` / `3.12`)**: Detecta la versión más reciente de Python de 64 bits instalada en la estación de trabajo (configurado por defecto para `Python 3.14`), repara o actualiza automáticamente `docling_env` si la ruta base cambió e instala las dependencias de `requirements.txt`.
4. **Aprovisionamiento y Sellado `SHA-256` de Modelos Locales**: Descarga e instala los modelos de `IBM Docling` e `IBM Granite Embedding R2` dentro de `RAG/modelos_ia/` y genera el manifiesto criptográfico `vault_manifest_sha256.json`.
5. **Lanzamiento del Orquestador**: Inicia el menú interactivo en `orquestador.py` o el portal FastAPI en `http://localhost:8080`.

---

## 3. Ejecución Nativa en Podman (Windows y Linux Rootless)

JullBrain está configurado nativamente para ejecutarse dentro de **Podman** sin privilegios de root (`--security-opt=no-new-privileges`, `--userns=keep-id`):

```bash
# Construir la imagen desde el Containerfile nativo
podman build -f Containerfile -t localhost/jullbrain-ibm:0.2.0 .

# Levantar el enclave completo (Core + Ollama con modelos locales en ./RAG/modelos_ia)
podman compose -f podman-compose.yml up -d
```

---

## 4. Despliegue en la Nube: Exclusivamente Oracle Cloud (OCI)

La única nube soportada por diseño de seguridad es **Oracle Cloud Infrastructure (OCI)** (instancias Ampere A1 ARM64 o GPU A10), operando con **Podman** y almacenando todos los modelos de IA localmente en `/opt/jullbrain/RAG/modelos_ia`:

```bash
bash deploy_oracle.sh
```

---

## 5. Avances en Ciberseguridad con Tecnología IBM

1. **Bóveda Criptográfica Local (`RAG/modelos_ia/`)**: Todos los modelos se cargan desde almacenamiento local con `trust_remote_code=False` y verificación de integridad `SHA-256` (`seal_and_verify_model_vault()`).
2. **Guardrails Cognitivos en 6 Dimensiones (`IBM Granite Guardian 3.2/3.3`)**:
   - *Pre-inferencia*: Detección de Prompt Injection / Jailbreak, contenido HAP y redacción automática de PII venezolano (Cédulas `V-/E-`, `RIF`, teléfonos, correos).
   - *Post-inferencia*: Verificación determinista y semántica de `Groundedness` (anclaje documental de cada artículo citado).
3. **Cadena de Custodia Inmutable (`HMAC-SHA256-CHAIN`)**: Bitácora forense en `logs/audit_forensic.jsonl` donde cada evento enlaza criptográficamente el hash del evento anterior y se verifica con `hmac.compare_digest`.
4. **Sanitización Forense de Entrada (`validate_pdf_magic_bytes`)**: Inspección estricta de cabecera binaria `%PDF-` antes de invocar `IBM Docling`.
