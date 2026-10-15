# Diagramas UML y de Arquitectura — JullBrain Enterprise

---

## 📐 1. Diagrama de Ingesta Documental y RAG Pipeline (Mermaid)

```mermaid
flowchart TD
    A[Documento Legal / Expediente] --> B[IBM Docling Ingestion]
    B --> C[DocTags & Structural Extraction]
    C --> D[Legalizer Hierarchical Chunking]
    D --> E[IBM Granite Embeddings R2]
    E --> F[OpenSearch Indexer BM25 + Vector]
    E --> G[PostgreSQL + pgvector]

    H[Usuario en Open WebUI] --> I[Pregunta Legal]
    I --> J[IBM Granite Guardian Guardrail]
    J --> K[OpenSearch Hybrid Search BM25 + Vector]
    K --> L[Reciprocal Rank Fusion RRF]
    L --> M[Cross-Encoder Reranker]
    M --> N[Validación de Evidencia Documental]
    N -->|Evidencia Encontrada| O[IBM Granite 3.3 8B Inferencia temp=0.0]
    N -->|Sin Evidencia| P["No encontré evidencia suficiente..."]
    O --> Q[Respuesta con Citas Estrictas + Audit Log SHA256]
```

---

## 🏛️ 2. Diagrama de Secuencia de Gestión de Cuadernos (SHA-256)

```mermaid
sequenceDiagram
    autonumber
    actor Usuario
    participant UI as Open WebUI / Dash
    participant NM as NotebookManager
    participant DB as PostgreSQL
    participant AL as AuditLogger

    Usuario->>UI: Crear/Abrir Cuaderno (Expediente)
    UI->>NM: verify_and_load_notebook(id, user)
    NM->>NM: Calcular Hash SHA-256 (UUID+UTC+Salt)
    alt Hash Coincide (Integridad Válida)
        NM->>AL: Log Event: READ_NOTEBOOK (SHA256_VERIFIED)
        NM-->>UI: Cargar Expediente y Documentos
    else Hash No Coincide (Corrupción/Alteración)
        NM->>AL: Log Event: SHA_VERIFICATION_FAILURE
        NM-->>UI: Lanza NotebookIntegrityError (Acceso Denegado)
    end
```
