# JullBrain — Arquitectura del Sistema V-2.1

> Pipeline de **6 etapas** para conversión de documentos legales venezolanos → Markdown estructurado → JSON Jerárquico → Vectores Semánticos → RAGFlow.
> Versión: 2.1 | Entorno: Nativo (Virtual Environment) | Motor: IBM Docling + Granite Embedding R2

---

## Visión General

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                       JullBrain Pipeline V-2.1                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  normativas_pdf/      formatos_word/                                     │
│  (PDF, PNG, JPG,      (.doc, .docx)                                      │
│   TIFF, BMP)                                                             │
│       │                    │                                             │
│       ▼                    ▼                                             │
│  ┌────────────────────────────────────────────────┐                      │
│  │                IBM Docling                     │  ← Layout y OCR      │
│  │   + HierarchicalChunker (Salida JSON nativa)   │  ← Segmentación      │
│  └───────────────────────┬────────────────────────┘                      │
│                          │                                               │
│                          ▼                                               │
│  ┌────────────────────────────────────────────────┐                      │
│  │                 legalizer.py                   │  ← Jerarquía TÍTULO  │
│  │           (Generación de TOC Markdown)         │    CAPÍTULO/Artículo │
│  └───────────────────────┬────────────────────────┘                      │
│                          │                                               │
│                          ▼                                               │
│  ┌────────────────────────────────────────────────┐                      │
│  │            metadata_extractor.py               │  ← YAML frontmatter  │
│  │                                                │    (SHA-256, Fecha)  │
│  └───────────────────────┬────────────────────────┘                      │
│                          │                                               │
│                          ▼                                               │
│  ┌────────────────────────────────────────────────┐                      │
│  │                 validator.py                   │  ← Verifica          │
│  │                                                │    integridad final  │
│  └───────────────────────┬────────────────────────┘                      │
│                          │                                               │
│               ┌──────────┴──────────┐                                    │
│               ▼                     ▼                                    │
│      normativas_rag/         normativas_chunks/                          │
│      (ley completa.md)       (hierarchical_chunks.json)                  │
│                                      │                                   │
│                                      ▼  [NUEVO V-2.1]                    │
│                         ┌────────────────────────────┐                   │
│                         │     granite_embedder.py    │  ← Embeddings      │
│                         │  ibm-granite/multilingual  │    semánticos      │
│                         │  768 dim | 32 768 tokens   │    768 dim         │
│                         └────────────┬───────────────┘                   │
│                                      │                                   │
│                                      ▼                                   │
│                         hierarchical_chunks_embedded.json                │
│                                      │                                   │
│                                      ▼                                   │
│                  RAGFlow (Motor nativo de ingesta vectorial)             │
│                                      │                                   │
│                                      ▼                                   │
│                         IBM Granite 4.1:8b (Inferencia)                  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Módulos del Sistema

### 1. `convert_normativas.py` — Orquestador Principal
- **Rol**: Coordina todo el pipeline dentro del entorno virtual de Python.
- **Batching**: Divide PDFs en lotes procesados en paralelo para optimizar memoria RAM.
- **Estructura Recursiva**: Procesa subcarpetas completas manteniendo la estructura de directorios original en las salidas.
- **Caché**: SHA-256 por PDF, salta archivos sin cambios.
- **Visualización**: Interfaz de carga dinámica y colorida con `rich.progress`.
- **Control de Ejecución**: Permite detener el procesamiento a mitad de camino (`Ctrl+C`).

### 2. `HierarchicalChunker` (Integrado en Docling)
- **Rol**: Segmenta los documentos usando la inteligencia nativa de Docling basándose en la estructura.
- **Salida**: Genera `hierarchical_chunks.json` con metadatos completos y contenido semánticamente fragmentado, listo para RAGFlow.

### 3. `legalizer.py` — Estructurador Legal
- **Rol**: Limpia, normaliza y detecta jerarquía legal.
- **Detecta**: TÍTULO (H2) → CAPÍTULO (H3) → SECCIÓN (H4) → Artículo (H6).
- **Genera**: Tabla de contenido (TOC) interactiva con anclajes a cada artículo.

### 4. `metadata_extractor.py` — Extractor de Metadatos
- **Rol**: Inyecta YAML frontmatter con metadatos semánticos.
- **Campos**: Gaceta Oficial, fecha de publicación, tipo de instrumento, SHA-256 del PDF.

### 5. `validator.py` — Validador de Integridad
- **Rol**: Verifica la calidad de la conversión legal para garantizar que RAGFlow no alucine.
- **Checks**: Secuencia numérica, duplicados, saltos de artículos, validación cruzada con PyMuPDF.
- **Doble Validación**: Principio 10 (Error Cero) — compara legalizer vs extracción directa del PDF.

### 6. `granite_embedder.py` — Motor de Embeddings Semánticos `[NUEVO V-2.1]`
- **Rol**: Convierte los chunks en vectores numéricos de alta dimensión para búsqueda semántica.
- **Modelo recomendado**: `ibm-granite/granite-embedding-multilingual-r2` (200+ idiomas, español incluido).
- **Modelo configurado por defecto**: `ibm-granite/granite-embedding-english-r2` (verificado operativo).
- **Dimensión**: 768 (R2 multilingual) | Contexto: 32 768 tokens.
- **Backends**: `sentence-transformers` (Python local) u `ollama` (API REST).
- **Principio R7**: Añade campo `embedding` sin modificar ningún campo original del chunk.
- **CLI**: `python granite_embedder.py --health` | `--embed-text` | `--embed-file`.

### 7. `orquestador_JullBrain.bat` — Lanzador Nativo
- **Rol**: Crea y activa el entorno virtual de Python, instala dependencias automáticamente y lanza Streamlit.

---

## Flujo de Datos Completo V-2.1

```text
Entrada (PDF/Word)
  → IBM Docling (OCR + HierarchicalChunker → JSON)
  → convert_normativas.py (Orquestador)
    → legalizer.py (Jerarquía legal)
    → metadata_extractor.py (YAML frontmatter + SHA-256)
    → validator.py (Integridad + doble validación cruzada)
  → Salida A: normativas_rag/*.md
  → Salida B: normativas_chunks/hierarchical_chunks.json
              → granite_embedder.py (Embeddings R2 768-dim)
              → normativas_chunks/hierarchical_chunks_embedded.json
                → RAGFlow (Knowledge Base vectorial)
                  → IBM Granite 4.1:8b (Inferencia jurídica T=0.15)
```

---

## Panel de Control Streamlit — 7 Módulos (`app.py`)

| # | Panel | Función |
|---|-------|---------|
| 1 | Pipeline de Arquitectura | KPIs del corpus, diagrama de fases, compatibilidad Granite, monitor de recursos |
| 2 | Orquestar Conversiones | Lanzar pipeline, cargar PDFs/Word, progreso en vivo |
| 3 | Integridad y Reportes | Reportes de validación por normativa, alertas de calidad |
| 4 | Cadena de Custodia | Trazabilidad SHA-256, exportar Acta de Custodia digital |
| 5 | Editor de Leyes RAG | Editor Ace Markdown/YAML para corregir outputs del pipeline |
| 6 | 🧬 Granite Embedding | Health check del modelo, test de embedding, embeber chunks, guía RAGFlow |
| 7 | Ajustes del Pipeline | Configuración persistente en `pipeline_config.json` |

---

## Configuración del Pipeline (`pipeline_config.json`)

| Clave | Tipo | Valor Actual | Descripción |
|-------|------|-------------|-------------|
| `ocr_activo` | bool | `true` | Activa OCR en IBM Docling |
| `generar_chunks` | bool | `true` | Genera `hierarchical_chunks.json` |
| `min_article_chars` | int | `50` | Mínimo de caracteres para artículo válido |
| `quality_threshold_critical` | float | `0.90` | Umbral crítico de integridad |
| `quality_threshold_warning` | float | `0.95` | Umbral de advertencia de integridad |
| `granite_model` | str | `granite4.1:8b` | Modelo de inferencia (Ollama) |
| `granite_temperature` | float | `0.15` | Temperatura jurídica |
| `granite_context_window` | int | `128000` | Ventana de contexto (tokens) |
| `ragflow_api_url` | str | `http://localhost:9380/api/v1` | Endpoint RAGFlow |
| `ragflow_embedding_model` | str | `ibm-granite/granite-embedding-english-r2` | Modelo de embeddings activo |
| `embedding_backend` | str | `sentence-transformers` | Motor de embeddings |
| `embedding_batch_size` | int | `32` | Chunks por lote |
| `embedding_device` | str | `cpu` | Dispositivo de cómputo |

---

## Gestión de Caché

- **Manifest**: `.conversion_cache/manifest.json`
- **Skip automático**: PDFs sin cambios se saltan basándose en su hash SHA-256.
- **Caché HuggingFace**: `%USERPROFILE%\.cache\huggingface\hub\` (modelos de embedding).

## Manejo de Errores

| Error | Estrategia |
|---|---|
| Lote Docling falla con OCR | Reintento automático sin OCR. |
| Archivo .doc heredado | Intenta conversión a .docx via win32com (si aplica en Windows host). |
| Pipeline legal falla | Guarda Markdown crudo, continua con siguiente archivo. |
| User Interrupt (Ctrl+C) | Se detiene con elegancia, conservando archivos terminados. |
| `DLL load failed importing hf_xet` | `pip uninstall hf_xet -y` — fuerza descarga HTTP estándar. |
| Embedding falla con dim=384 | Verificar `ragflow_embedding_model` en config (debe ser R2, no 30m). |
