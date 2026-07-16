# JullBrain — Arquitectura del Sistema

> Pipeline de 5 etapas para conversión de documentos legales venezolanos → Markdown estructurado y JSON (Hierarchical Chunking) para RAGFlow.
> Versión: 2.0 | Entorno: Nativo (Virtual Environment) | Motor: IBM Docling

---

## Visión General

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        JullBrain Pipeline V-2.0                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  normativas_pdf/      formatos_word/                                    │
│  (PDF, PNG, JPG,      (.doc, .docx)                                     │
│   TIFF, BMP)                                                            │
│       │                    │                                            │
│       ▼                    ▼                                            │
│  ┌────────────────────────────────────────────────┐                     │
│  │                IBM Docling                     │  ← Layout y OCR     │
│  │   + HierarchicalChunker (Salida JSON nativa)   │  ← Segmentación     │
│  └───────────────────────┬────────────────────────┘                     │
│                          │                                              │
│                          ▼                                              │
│  ┌────────────────────────────────────────────────┐                     │
│  │                 legalizer.py                   │  ← Jerarquía TÍTULO │
│  │           (Generación de TOC Markdown)         │    CAPÍTULO/Artículo│
│  └───────────────────────┬────────────────────────┘                     │
│                          │                                              │
│                          ▼                                              │
│  ┌────────────────────────────────────────────────┐                     │
│  │            metadata_extractor.py               │  ← YAML frontmatter │
│  │                                                │    (SHA-256, Fecha) │
│  └───────────────────────┬────────────────────────┘                     │
│                          │                                              │
│                          ▼                                              │
│  ┌────────────────────────────────────────────────┐                     │
│  │                 validator.py                   │  ← Verifica         │
│  │                                                │    integridad final │
│  └───────────────────────┬────────────────────────┘                     │
│                          │                                              │
│               ┌──────────┴──────────┐                                   │
│               ▼                     ▼                                   │
│      normativas_rag/         normativas_chunks/                         │
│      (ley completa.md)       (hierarchical_chunks.json)                 │
│                                                                         │
│               ▼                                                         │
│             RAGFlow (Motor nativo de ingesta vectorial)                 │
└─────────────────────────────────────────────────────────────────────────┘
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
- **Rol**: Reemplaza al antiguo `chunker.py`. Segmenta los documentos usando la inteligencia nativa de Docling basándose en la estructura.
- **Salida**: Genera un archivo unificado `hierarchical_chunks.json` que contiene los metadatos completos y el contenido semánticamente fragmentado, ideal para su inyección directa a RAGFlow.

### 3. `legalizer.py` — Estructurador Legal
- **Rol**: Limpia, normaliza y detecta jerarquía legal.
- **Detecta**: TÍTULO (H2) → CAPÍTULO (H3) → SECCIÓN (H4) → Artículo (H6).
- **Genera**: Tabla de contenido (TOC) interactiva con anclajes a cada artículo.

### 4. `metadata_extractor.py` — Extractor de Metadatos
- **Rol**: Inyecta YAML frontmatter con metadatos semánticos.

### 5. `validator.py` — Validador de Integridad
- **Rol**: Verifica la calidad de la conversión legal para garantizar que RAGFlow no alucine.
- **Checks**: Secuencia numérica, duplicados, saltos de artículos.

### 6. `orquestador_JullBrain.bat` — Lanzador Nativo
- **Rol**: Crea y activa el entorno virtual de Python, instala dependencias automáticamente y ejecuta la conversión de forma segura.

---

## Flujo de Datos

### Pipeline Normal (Entorno Local)
```text
Entrada (PDF/Word) 
  → Docling (Extracción y JSON Chunks) 
  → convert_normativas.py (Orquestador)
  → export_to_markdown()
  → legalize() 
  → inject_frontmatter() 
  → validate_md_file() 
  → Salida: normativas_rag/*.md + normativas_chunks/*_chunks.json
```

---

## Gestión de Caché

- **Manifest**: `.conversion_cache/manifest.json`
- **Skip automático**: PDFs sin cambios se saltan basándose en su hash SHA-256.

## Manejo de Errores

| Error | Estrategia |
|---|---|
| Lote Docling falla con OCR | Reintento automático sin OCR. |
| Archivo .doc heredado | Intenta conversión a .docx via win32com (si aplica en Windows host). |
| Pipeline legal falla | Guarda Markdown crudo, continua con siguiente archivo. |
| User Interrupt (Ctrl+C) | Se detiene con elegancia, conservando archivos terminados. |
