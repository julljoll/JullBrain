# Manual Técnico — JullBrain v0.2.0 (Stack Exclusivo IBM)

---

## 🏛️ 1. Arquitectura del Sistema

**JullBrain v0.2.0** es una plataforma soberana de Inteligencia Documental Jurídica e Informática Forense diseñada para operar **100% en local (*Air-Gapped*)**, dentro de contenedores nativos **Podman** (Windows / Linux Rootless) o en **Oracle Cloud Infrastructure (OCI)**, utilizando exclusivamente tecnología de IA de **IBM** y orquestación de ingeniería con **Google Antigravity**.

### Componentes Principales:

1. **Iniciador Local, Consola TUI y Portal API Zero-Trust:**
   - **[`orquestador_JullBrain.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador_JullBrain.bat):** Analiza el procesador (CPU), RAM, **Podman** y entorno Python (`3.12 - 3.14`), repara `docling_env` y configura las rutas de la bóveda local `RAG/modelos_ia/`.
   - **[`orquestador.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador.py):** Consola interactiva en terminal (`Rich`) para ingesta, conversión, validación QA y auditoría forense.
   - **[`app.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/app.py) & [`openwebui_pipeline.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/openwebui_pipeline.py):** Servidor REST FastAPI con cabeceras de seguridad Zero-Trust (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Cache-Control: no-store`) e integración con Open WebUI.

2. **Ingesta Documental en CPU y Estructuración Legal:**
   - **`IBM Docling` ([`convert_normativas.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/convert_normativas.py)):** Ejecución optimizada en procesador (**CPU**) mediante `AcceleratorOptions(num_threads=cpu_threads, device=AcceleratorDevice.CPU)` y modelos locales en `RAG/modelos_ia/docling/`.
   - **[`legalizer.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/legalizer.py) & [`metadata_extractor.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/metadata_extractor.py):** Estructuración jerárquica determinista (`LIBRO > TÍTULO > CAPÍTULO > SECCIÓN > Artículo`) e inyección de YAML Frontmatter con hash `SHA-256`.
   - **[`validator.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/validator.py):** Doble validación cruzada (Markdown generado vs extracción directa del PDF original con PyMuPDF).

3. **Motor de Embeddings, Búsqueda Híbrida e Inferencia IBM Granite:**
   - **Embeddings ([`granite_embedder.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_embedder.py)):** Modelo oficial `ibm-granite/granite-embedding-english-r2` de **`768` dimensiones**, cargado localmente desde `RAG/modelos_ia/granite_embeddings/` con `trust_remote_code=False`.
   - **Búsqueda Híbrida ([`opensearch_indexer.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/opensearch_indexer.py)):** Combinación de búsqueda léxica Okapi BM25 + Similitud Coseno vectorial (`768` dims) + Fusión Recíproca de Rangos (RRF) + Reranker léxico-semántico.
   - **Inferencia LLM:** `ibm-granite/granite-3.3-8b-instruct-GGUF` con parámetros deterministas (`temperature=0.0`, `top_p=0.05`, `top_k=20`, `repeat_penalty=1.15`, `seed=42`).

4. **Ciberseguridad Cognitiva y Cadena de Custodia Forense:**
   - **[`granite_guardian_guardrail.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_guardian_guardrail.py):** Guardrail en 6 dimensiones con `ibm-granite/granite-guardian-3.2-5b` (Prompt Injection/Jailbreak, HAP, PII Venezolano, Groundedness, Context Relevance y Answer Relevance).
   - **[`audit_logger.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/audit_logger.py):** Bitácora forense en `logs/audit_forensic.jsonl` con *hash-chaining* `HMAC-SHA256` (`prev_hash` + `hmac_sha256`), verificación en tiempo constante (`hmac.compare_digest`), sellado de bóveda (`seal_and_verify_model_vault()`) e inspección binaria `%PDF-` (`validate_pdf_magic_bytes()`).
   - **[`notebook_manager.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/notebook_manager.py):** Aislamiento de expedientes en `RAG/notebooks_db/` con verificación obligatoria `SHA-256` y borrado transaccional con rollback.

---

## 🔒 2. Parámetros Estrictos de Configuración ([`pipeline_config.json`](file:///c:/VS%20CODE/CODIGO/JullBrain/pipeline_config.json))

```json
{
  "version": "0.2.0",
  "granite_model": "ibm-granite/granite-3.3-8b-instruct-GGUF",
  "granite_temperature": 0.0,
  "granite_top_p": 0.05,
  "granite_top_k": 20,
  "granite_repeat_penalty": 1.15,
  "granite_fixed_seed": 42,
  "ragflow_embedding_model": "ibm-granite/granite-embedding-english-r2",
  "guardian_model": "ibm-granite/granite-guardian-3.2-5b"
}
```

---

## 🛠️ 3. Endpoints Principales de la API REST ([`app.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/app.py))

| Método | Ruta | Función |
| :--- | :--- | :--- |
| `GET` | `/health` | Estado de salud del nodo local/Podman, bóveda de modelos `RAG/modelos_ia/` y guardrails. |
| `GET` | `/api/v1/security/vault` | Verifica criptográficamente el manifiesto `SHA-256` de los modelos en `RAG/modelos_ia/`. |
| `POST` | `/api/v1/upload` | Valida cabecera binaria `%PDF-`, calcula `SHA-256` y almacena el PDF en `RAG/datos_brutos/`. |
| `POST` | `/api/v1/notebooks` | Crea un expediente jurídico aislado en `RAG/notebooks_db/` firmado con `SHA-256`. |
| `POST` | `/api/v1/query` | Ejecuta el pipeline completo: Guardrail 6D ➔ Búsqueda Híbrida RRF ➔ Evidencia/Abstención ➔ Auditoría `HMAC-SHA256`. |
