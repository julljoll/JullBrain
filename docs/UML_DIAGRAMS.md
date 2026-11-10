# Diagramas UML y de Arquitectura — JullBrain v0.2.0 (Stack IBM)

---

## 📐 1. Diagrama de Ingesta Documental, Bóveda Local y Pipeline RAG (Mermaid)

```mermaid
flowchart TD
    A["PDF / Word en RAG/datos_brutos/"] --> B["Validación Magic Bytes (%PDF-) + SHA-256 (audit_logger.py)"]
    B --> C["IBM Docling en CPU (Hilos Optimizados via gpu_detector.py)"]
    V["Bóveda Local Sellada SHA-256 (RAG/modelos_ia/)"] --> C
    C --> D["legalizer.py + metadata_extractor.py (Jerarquía + YAML + Encabezado Canónico)"]
    D --> E["validator.py (Doble Validación Cruzada: Markdown vs PDF PyMuPDF)"]
    E --> F["RAG/Informacion_docling_rag/*.md"]
    D --> G["HierarchicalChunker + GraniteEmbedder R2 (768 dims)"]
    V --> G
    G --> H["RAG/normativas_chunks/*_chunks.json"]
    H --> I["Motor Híbrido Local / OpenSearch (BM25 + Vector 768d + RRF + Reranker)"]

    J["Operador Jurídico (Consola Rich / FastAPI / Open WebUI)"] --> K["Consulta Normativa"]
    K --> L["IBM Granite Guardian 3.2/3.3 (Pre-Inferencia: Jailbreak, HAP, PII Venezolano)"]
    L -->|Seguro| I
    L -->|Bloqueado| M["Rechazo Inmediato + Evento en Cadena HMAC-SHA256"]
    I --> N{"¿Evidencia Encontrada?"}
    N -->|Sí| O["IBM Granite 3.3 8B (Inferencia Determinista T=0.0)"]
    N -->|No| P["Abstención Explícita Obligatoria"]
    O --> Q["IBM Granite Guardian (Post-Inferencia: Groundedness Check)"]
    Q --> R["Respuesta con Citas Verificadas + Firma en logs/audit_forensic.jsonl"]
```

---

## 🏛️ 2. Diagrama de Secuencia: Cadena de Custodia `SHA-256` y `HMAC-SHA256-CHAIN`

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Juez / Fiscal / Perito
    participant API as FastAPI (app.py) / Orquestador
    participant GG as GraniteGuardianGuardrail
    participant NM as NotebookManager (RAG/notebooks_db)
    participant AL as AuditLogger (HMAC-SHA256-CHAIN)

    Operador->>API: Abrir Expediente / Realizar Consulta
    API->>NM: verify_and_load_notebook(notebook_id, user_id)
    NM->>NM: Recalcular SHA-256 (UUID + UTC + Nombre + Usuario + Salt)
    alt Firma SHA-256 Intacta
        NM->>AL: log_event("READ_NOTEBOOK", status="SHA256_VERIFIED")
        AL->>AL: Enlazar prev_hash + Firmar con HMAC-SHA256 (compare_digest)
        API->>GG: check_prompt_safety(user_message)
        GG-->>API: Prompt Verificado (Sin Jailbreak / PII Protegido)
        API-->>Operador: Respuesta Anclada con Semáforo Verde
    else Alteración Detectada en Disco
        NM->>AL: log_event("SHA_VERIFICATION_FAILURE", severity="CRITICAL")
        NM-->>API: NotebookIntegrityError
        API-->>Operador: HTTP 403 — Acceso Denegado por Violación de Custodia
    end
```
