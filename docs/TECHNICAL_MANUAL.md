# Manual Técnico — JullBrain Enterprise Legal Platform

---

## 🏛️ Arquitectura del Sistema

**JullBrain** es una Plataforma Enterprise de Inteligencia Documental Legal estilo *NotebookLM*, optimizada para funcionar en entornos **100% locales y air-gapped** (sin conexión a Internet).

### Componentes de la Arquitectura:

1. **Interfaz Web & Orquestación de Chat:**
   - **Open WebUI (Oficial):** Interfaz para usuarios finales, gestión de workspaces, notebooks y chat documental.
   - **Plotly Dash (`app.py`):** Panel de control visual administrativo para monitoreo de integridad, auditoría y métricas del pipeline.

2. **Backend RAG & Motor de Inferencia:**
   - **Modelo LLM:** `ibm-granite/granite-3.3-8b-instruct-GGUF` (Parámetros: `temp=0.0`, `top_p=0.05`, `top_k=20`, `repeat_penalty=1.15`, seed fija).
   - **Guardrails:** IBM Granite Guardian (`granite-guardian`) para filtrado de seguridad.

3. **Ingesta y Procesamiento Documental:**
   - **IBM Docling & DocTags:** Ingesta de PDF, DOCX, PPTX, XLSX, TXT, CSV, HTML, MD, EPUB, Imágenes y PDFs escaneados (OCR Tesseract en español).
   - **Chunker Jerárquico Legal (`legalizer.py`):** Descomposición de normativas preservando estructura completa de capítulos, artículos, incisos y cláusulas.

4. **Almacenamiento & Búsqueda Híbrida:**
   - **OpenSearch:** Búsqueda Léxica (BM25) + Búsqueda Vectorial (`knn_vector`) + Fusión Recíproca de Rangos (RRF) + Cross-Encoder Reranker.
   - **PostgreSQL + pgvector (`db_schema.sql`):** Persistencia relacional y vectorial de usuarios, cuadernos/expedientes, documentos, notas, vectores y firmas SHA-256.

5. **Auditoría & Firma Criptográfica:**
   - **`audit_logger.py`:** Logs inmutables firmados con hash SHA-256 (timestamp UTC, usuario, IP).
   - **`notebook_manager.py`:** Aislamiento de expedientes con hash criptográfico y eliminación transaccional con rollback.

---

## ⚙️ Esquema de Base de Datos (PostgreSQL + pgvector)

Ver archivo de migración en [`db_schema.sql`](file:///c:/VS%20CODE/CODIGO/JullBrain/db_schema.sql).

- `users`: Gestión de roles (RBAC) y credenciales.
- `notebooks`: Expedientes independientes atados por hash SHA-256 inmutable.
- `documents`: Documentos ingeridos por expediente.
- `document_chunks`: Fragmentos legales estructurados con DocTags.
- `document_embeddings`: Vectores de 384 dimensiones de IBM Granite Embedding R2.
- `audit_logs`: Registro inmutable append-only con firma de integridad SHA-256.

---

## 🔒 Parámetros Estrictos de Inferencia

```json
{
  "model": "ibm-granite/granite-3.3-8b-instruct-GGUF",
  "temperature": 0.0,
  "top_p": 0.05,
  "top_k": 20,
  "repeat_penalty": 1.15,
  "fixed_seed": 42
}
```

---

## 🛠️ API & Pipelines de Integración (`openwebui_pipeline.py`)

Open WebUI se comunica con el backend de JullBrain a través de la API REST estándar de Pipelines. Toda solicitud pasa obligatoriamente por el pipeline de recuperación híbrida y guardrails antes de generar la respuesta con citas estructuradas.
