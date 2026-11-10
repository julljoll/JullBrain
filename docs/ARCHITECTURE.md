# 🏛️ Arquitectura Técnica y de Ciberseguridad — JullBrain v0.2.0 (Stack Exclusivo IBM)

> **Versión:** `0.2.0`
> **Tecnología IA:** `IBM Docling (CPU)` · `IBM Granite 3.3 8B` · `IBM Granite Embedding R2 (768d)` · `IBM Granite Guardian 3.2/3.3`
> **Agente de Ingeniería:** **Google Antigravity**
> **Infraestructura:** Local (`orquestador_JullBrain.bat`), **Podman** (Windows / Linux Rootless) y **Oracle Cloud (OCI)**

---

## 1. Diagrama del Pipeline Soberano (`RAG/`)

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        JullBrain v0.2.0 — Núcleo Soberano RAG/                   │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  [1] RAG/datos_brutos/ (PDFs de Leyes Venezolanas y Formatos_Word/)              │
│         │                                                                        │
│         ▼                                                                        │
│  [2] Validación Forense Magic Bytes (%PDF-) + Hash SHA-256 (audit_logger.py)     │
│         │                                                                        │
│         ▼                                                                        │
│  [3] IBM Docling (CPU-Optimized via AcceleratorOptions & OMP/MKL Threads)        │
│      Pesos cargados desde: RAG/modelos_ia/docling/                               │
│         │                                                                        │
│         ├──► legalizer.py (Jerarquía TÍTULO / CAPÍTULO / Artículo)               │
│         ├──► metadata_extractor.py (YAML Frontmatter + Gaceta Oficial + SHA-256) │
│         └──► validator.py (Doble Validación Cruzada: Markdown vs PDF PyMuPDF)    │
│         │                                                                        │
│         ├───────────────────────────────────────────┐                            │
│         ▼                                           ▼                            │
│  RAG/Informacion_docling_rag/*.md          HierarchicalChunker (Chunks Atómicos) │
│  (Encabezado Canónico + YAML + Ley)                 │                            │
│                                                     ▼                            │
│                                            granite_embedder.py                   │
│                                            ibm-granite/granite-embedding-english-r2│
│                                            (768 dims desde RAG/modelos_ia/)      │
│                                                     │                            │
│                                                     ▼                            │
│                                            RAG/normativas_chunks/*_chunks.json   │
│                                                     │                            │
│                                                     ▼                            │
│  [4] Recuperación Híbrida BM25 + k-NN (opensearch_indexer.py / RAGFlow)          │
│         │                                                                        │
│         ▼                                                                        │
│  [5] Guardrail Pre/Post Inferencia: IBM Granite Guardian 3.2/3.3 (6 Dimensiones) │
│      + Inferencia Determinista: IBM Granite 3.3 8B (T = 0.0 - 0.1)               │
│      + Registro en Cadena Criptográfica HMAC-SHA256 (logs/audit_forensic.jsonl)  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Módulos Principales del Repositorio

| Módulo | Responsabilidad Técnica |
| :--- | :--- |
| [`orquestador_JullBrain.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador_JullBrain.bat) | Punto de entrada local en Windows: analiza CPU/RAM/Podman/Python 3.14, repara `docling_env`, aprovisiona modelos en `RAG/modelos_ia/` y lanza `orquestador.py`. |
| [`gpu_detector.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/gpu_detector.py) | Analiza el computador host (`analizar_computadora_host()`), calcula la afinidad de hilos CPU para `IBM Docling` (`configurar_entorno_cpu_docling()`) y verifica Podman y la bóveda de modelos. |
| [`convert_normativas.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/convert_normativas.py) | Motor de conversión PDF → Markdown y JSON con `IBM Docling` en CPU, validación `%PDF-`, enriquecimiento con `GraniteEmbedder` y opción `--bootstrap-models`. |
| [`legalizer.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/legalizer.py) | Estructurador determinista de legislación venezolana (`LIBRO`, `TÍTULO`, `CAPÍTULO`, `SECCIÓN`, `Artículo`) y separador de artículos fusionados. |
| [`metadata_extractor.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/metadata_extractor.py) | Extractor de Gaceta Oficial, fecha, tipo de instrumento y hash `SHA-256` en formato YAML frontmatter. |
| [`validator.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/validator.py) | Validador de secuencia numérica de artículos y doble validación cruzada contra el PDF original mediante PyMuPDF (`cross_validate_against_pdf()`). |
| [`granite_embedder.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_embedder.py) | Motor de embeddings `ibm-granite/granite-embedding-english-r2` (`768` dims) con almacenamiento local en `RAG/modelos_ia/granite_embeddings` y sellado `SHA-256`. |
| [`granite_guardian_guardrail.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_guardian_guardrail.py) | Guardrail de ciberseguridad IBM Granite Guardian 3.2/3.3 en 6 dimensiones (Prompt Injection/Jailbreak, HAP, PII Venezolano, Groundedness, Context/Answer Relevance). |
| [`audit_logger.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/audit_logger.py) | Bitácora forense con encadenamiento criptográfico `HMAC-SHA256-CHAIN`, verificación en tiempo constante (`hmac.compare_digest`) y sellado de `RAG/modelos_ia/`. |
| [`app.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/app.py) | Servidor web y API REST Zero-Trust en FastAPI con cabeceras de seguridad HTTP (`CSP`, `X-Frame-Options`, `X-Content-Type-Options`) y endpoint `/api/v1/security/vault`. |
| [`Containerfile`](file:///c:/VS%20CODE/CODIGO/JullBrain/Containerfile) / [`podman-compose.yml`](file:///c:/VS%20CODE/CODIGO/JullBrain/podman-compose.yml) | Contenerización nativa para **Podman** en modo *rootless* (Windows y Linux). |
| [`deploy_oracle.sh`](file:///c:/VS%20CODE/CODIGO/JullBrain/deploy_oracle.sh) / [`oracle_config.json`](file:///c:/VS%20CODE/CODIGO/JullBrain/oracle_config.json) | Automatización de despliegue en **Oracle Cloud Infrastructure (OCI)** con Podman y bóveda local de modelos. |
