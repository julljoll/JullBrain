# JullBrain — Arquitectura del Sistema

> Pipeline de 5 etapas para conversión de documentos legales venezolanos → Markdown estructurado para RAG.
> Versión: 2.0 | Motor: IBM Docling | Stack: Python 3.10+

---

## Visión General

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        JullBrain Pipeline V-2.0                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  normativas_pdf/      formatos_word/                                    │
│  (PDF, PNG, JPG,      (.doc, .docx)                                    │
│   TIFF, BMP)                                                           │
│       │                    │                                            │
│       ▼                    ▼                                            │
│  ┌──────────┐       ┌──────────┐                                       │
│  │  Docling  │       │  Docling  │    ← IBM Docling (layout + OCR)      │
│  │  + OCR    │       │  (no OCR) │                                       │
│  └────┬─────┘       └────┬─────┘                                       │
│       │                  │                                              │
│       ▼                  ▼                                              │
│  ┌─────────────────────────────┐                                        │
│  │      legalizer.py           │  ← Jerarquía TÍTULO/CAPÍTULO/Artículo  │
│  │   + generación de TOC       │    + detección de parágrafos/literales │
│  └─────────────┬───────────────┘                                        │
│                ▼                                                        │
│  ┌─────────────────────────────┐                                        │
│  │   metadata_extractor.py     │  ← YAML frontmatter (Gaceta, fecha,    │
│  │                             │    SHA-256, tipo de instrumento)       │
│  └─────────────┬───────────────┘                                        │
│                ▼                                                        │
│  ┌─────────────────────────────┐                                        │
│  │      validator.py           │  ← Verifica secuencia, duplicados,     │
│  │                             │    artículos cortos, frontmatter       │
│  └─────────────┬───────────────┘                                        │
│                ▼                                                        │
│  ┌─────────────────────────────┐                                        │
│  │       chunker.py            │  ← Divide en chunks individuales       │
│  │                             │    (1 .md por artículo)                │
│  └─────────────┬───────────────┘                                        │
│                │                                                        │
│         ┌──────┴──────┐                                                 │
│         ▼             ▼                                                 │
│  normativas_rag/  normativas_chunks/                                    │
│  (ley completa)   (ley/articulo_NNNN.md)                                │
│                                                                         │
│         ▼                                                               │
│  Sistemas RAG: LangChain, LlamaIndex, ChromaDB, LanceDB                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Módulos del Sistema

### 1. `convert_normativas.py` — Orquestador Principal
- **Rol**: Coordina todo el pipeline
- **Batching**: Divide PDFs en lotes de 15 páginas, procesa con ThreadPoolExecutor (3 workers)
- **Caché**: SHA-256 por PDF, salta archivos sin cambios
- **OCR**: Tesseract → fallback EasyOCR si falla
- **Subprocesos**: Cada lote se ejecuta como subproceso Python separado (`--chunk-mode`)
- **Flags**:
  - `--no-ocr`: Desactiva OCR (5x más rápido)
  - `--no-chunks`: Solo .md consolidado
  - `--post-process-only`: Re-aplica pipeline sin Docling
  - `--force-reprocess`: Ignora caché
  - `--file-path`: Archivo específico

### 2. `legalizer.py` — Estructurador Legal
- **Rol**: Detecta jerarquía legal y separa artículos
- **Detecta**: TÍTULO (H2) → CAPÍTULO (H3) → SECCIÓN (H4) → Artículo (H6)
- **Genera**: TOC automático con tabla de artículos
- **Maneja**: Parágrafos, numerales, literales, artículos derogados
- **Patrones**: Soportados → `Artículo N`, `Art. N`, `ARTÍCULO N`, `Artículo N°`

### 3. `metadata_extractor.py` — Extractor de Metadatos
- **Rol**: Inyecta YAML frontmatter con metadatos semánticos
- **Extrae**: Tipo de instrumento, nombre oficial, Gaceta, fecha, SHA-256
- **Valida**: Campos requeridos, formato ISO 8601, hash de 64 caracteres
- **Schema**: 18 campos en YAML frontmatter

### 4. `validator.py` — Validador de Integridad
- **Rol**: Verifica calidad de la conversión
- **Checks**: Secuencia numérica, duplicados, artículos cortos, frontmatter, TOC
- **Reportes**: Rich console table con colores por score
- **Umbrales**: critical < 0.90, warning < 0.95, good < 0.98, excellent = 1.0

### 5. `chunker.py` — Generador de Chunks
- **Rol**: Divide Markdown legalizado en archivos individuales por artículo
- **Formato**: `normativas_chunks/ley/articulo_0001.md`
- **Frontmatter**: ley, artículo, ubicación, gaceta, fecha, sha256 por chunk

### 6. `gui.py` — Interfaz Gráfica (Flet)
- **Rol**: GUI opcional con explorador de archivos, consola en vivo, estadísticas
- **Dark theme**: Consistente con la paleta del proyecto

---

## Flujo de Datos

### Pipeline Normal
```
PDF → Docling (JSON chunks) → merge → export_to_markdown()
  → legalize() → inject_frontmatter() → validate_md_file() → chunk_file()
  → normativas_rag/*.md + normativas_chunks/*/articulo_*.md
```

### Pipeline de Post-Procesado (--post-process-only)
```
normativas_rag/*.md → parse frontmatter → remove MIT header/footer
  → legalize() → inject_frontmatter() → validate_md_file() → chunk_file()
```

---

## Gestión de Caché

- **Manifest**: `.conversion_cache/manifest.json`
- **Key**: SHA-256 del PDF original
- **Skip automático**: PDFs sin cambios se saltan
- **Forzar**: `--force-reprocess` o borrar manifest manualmente

```
manifest.json:
{
  "codigo_penal.pdf": {
    "sha256": "abc123...",
    "md_file": "codigo_penal.md",
    "articulos": 640,
    "estado_val": "OK"
  }
}
```

---

## Manejo de Errores

| Error | Estrategia |
|---|---|
| Lote Docling falla con OCR | Reintento automático sin OCR |
| Archivo .doc heredado | Intenta conversión a .docx via win32com |
| Pipeline legal falla | Guarda Markdown crudo, continua con siguiente archivo |
| UnicodeEncodeError | stdout/stderr reconfigure(encoding='utf-8') |
| Módulo no importado | Log warning, continua sin pipeline legal |

---

## Formatos de Salida

### Consolidado (`normativas_rag/ley.md`)
```markdown
---
tipo_instrumento: "Código"
nombre_oficial: "Código Penal de Venezuela"
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"
articulos_detectados: 640
hash_pdf_sha256: "abc123..."
---

## TÍTULO I - De la aplicación de la Ley Penal
### ÍNDICE DE ARTÍCULOS
| Art. | Descripción | Ubicación |
|------|-------------|-----------|
| 1    | Principio de Legalidad | TÍTULO I |
...

###### Artículo 1 — Principio de Legalidad

Nadie podrá ser castigado por un hecho...
```

### Chunk Individual (`normativas_chunks/ley/articulo_0001.md`)
```markdown
---
ley: "Código Penal de Venezuela"
articulo: 1
ubicacion: "TÍTULO I - De la aplicación de la Ley Penal"
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"
hash_pdf_sha256: "abc123..."
---

###### Artículo 1 — Principio de Legalidad

Nadie podrá ser castigado...
```

---

## Stack Tecnológico

| Componente | Tecnología | Propósito |
|---|---|---|
| Lenguaje | Python 3.10+ | Core del pipeline |
| OCR | Tesseract + EasyOCR | Reconocimiento en PDFs escaneados |
| Document parsing | IBM Docling | Layout, tablas, estructura |
| UI Consola | Rich | Progress bars, tablas, colores |
| GUI | Flet | Interfaz gráfica opcional |
| Serialización | PyYAML | Frontmatter metadata |
| PDF | PyMuPDF + pypdf | Page count, fallbacks |
| Cache | hashlib (SHA-256) | Detección de cambios |
| Paralelismo | ThreadPoolExecutor | Batching concurrente |
| Container | Docker + Compose | Despliegue server |
| Instalador | InnoSetup + Chocolatey | Distribución Windows |

---

## Despliegue

### Local (Windows)
```cmd
iniciar_conversion.bat
```

### Docker
```bash
docker-compose up --build
```

### Cloud (IBM Code Engine / Oracle VM)
Ver: `Plan para desplegar el proyecto en la nube.txt` y `Intro Plan nube RAG.txt`
