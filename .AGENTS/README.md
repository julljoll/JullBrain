# JullBrain v0.2.0 — Arquitectura de Agentes y Skills (Google Antigravity + Stack IBM)

> **Agente Exclusivo:** **Google Antigravity**
> **Stack IA:** **IBM Docling (CPU)** + **IBM Granite 3.3** + **IBM Granite Embedding R2** + **IBM Granite Guardian 3.2/3.3**
> **Infraestructura:** Local (`orquestador_JullBrain.bat`) · **Podman** (Windows / Linux Rootless) · **Oracle Cloud (OCI)**

---

## 1. Flujo del Pipeline Soberano (`RAG/`)

```
RAG/datos_brutos/ (PDFs y Formatos Word)
       │
       ▼
[orquestador_JullBrain.bat] ──► Analiza CPU/RAM/Podman/Python 3.14 + Bóveda RAG/modelos_ia/
       │
       ├── [convert_normativas.py] ──► Validación Magic Bytes (%PDF-) + IBM Docling (CPU Threads)
       ├── [legalizer.py]          ──► Estructuración jerárquica (TÍTULO / CAPÍTULO / Artículo)
       ├── [metadata_extractor.py] ──► YAML Frontmatter + SHA-256 documental
       ├── [granite_embedder.py]   ──► Vectores IBM Granite Embedding R2 (768 dims desde RAG/modelos_ia)
       ├── [validator.py]          ──► Doble validación cruzada (Markdown vs PDF PyMuPDF)
       └── [granite_guardian_guardrail.py] + [audit_logger.py] ──► Ciberseguridad 6D + Cadena HMAC-SHA256
       │
       ├───────────────────────────────────────────────────────────┐
       ▼                                                           ▼
RAG/Informacion_docling_rag/                        RAG/normativas_chunks/
  *.md (Encabezado Canónico + YAML + Artículos)       *_chunks.json (Vectores listos para RAGFlow)
```

---

## 2. Catálogo de Skills Optimizados para Google Antigravity

| Skill | Directorio | Módulo Asociado |
| :--- | :--- | :--- |
| `JullBrain-controlador-iniciador-bat` | `.agents/skills/controlador-iniciador-bat/` | `orquestador_JullBrain.bat`, `Idea-Principal/header_canonico.bat` |
| `JullBrain-conversor-pdf-a-rag` | `.agents/skills/conversor-pdf-a-rag/` | `convert_normativas.py`, `orquestador.py`, `gpu_detector.py` |
| `JullBrain-analizador-jerarquia-legal` | `.agents/skills/analizador-jerarquia-legal/` | `legalizer.py` |
| `JullBrain-extractor-metadata-legal` | `.agents/skills/extractor-metadata-legal/` | `metadata_extractor.py` |
| `JullBrain-granite-embedder` | `.agents/skills/granite-embedder/` | `granite_embedder.py` |
| `JullBrain-validador-calidad-ocr` | `.agents/skills/validador-calidad-ocr/` | `validator.py`, `audit_logger.py`, `granite_guardian_guardrail.py` |
