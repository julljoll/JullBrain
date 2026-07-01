# QUIBOR-RAG V-2.0 — Pipeline RAG de Normativas y Formatos Legales Venezolanos

> Conversión automatizada de PDFs jurídicos a Markdown estructurado para sistemas de IA — Powered by IBM Docling

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org) [![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE) [![IBM Docling](https://img.shields.io/badge/IBM-Docling-purple)](https://github.com/DS4SD/docling)

---

## El Problema que Resuelve

Los modelos de lenguaje (LLM) fallan con PDFs de documentos legales venezolanos porque:

- Los artículos aparecen fusionados en párrafos de 2,000+ palabras sin separación.
- Las tablas de PDFs se rompen o pierden su estructura.
- No hay metadata legal (Gaceta Oficial, fecha, tipo de instrumento) para filtrar búsquedas RAG.
- El chunking por páginas parte artículos a la mitad, generando fragmentos incoherentes.

**QUIBOR-RAG** convierte esos PDFs en Markdown semánticamente estructurado, con un artículo por chunk, listo para ingestarse en LangChain, LlamaIndex, ChromaDB o cualquier sistema RAG.

---

## Arquitectura del Pipeline

```
normativas_pdf/
       │
       ▼
[IBM Docling + OCR]          ← Extracción visual profunda (layout, tablas, OCR)
       │
       ▼
[legalizer.py]               ← Jerarquía: TÍTULO › CAPÍTULO › Artículo
       │
       ▼
[metadata_extractor.py]      ← YAML frontmatter: Gaceta, fecha, SHA-256
       │
       ▼
[validator.py]               ← Integridad: secuencia, duplicados, corruptos
       │
       ├──────────────────────────────────────────────────────────────┐
       ▼                                                              ▼
normativas_rag/                                          normativas_chunks/
  ley-completa.md                                          ley/articulo_0001.md
  (con YAML + TOC)                                         ley/articulo_0002.md
                                                           ...
```

---

## Módulos del Sistema

| Módulo | Función | Skill de IA Asociado |
|--------|---------|----------------------|
| `convert_normativas.py` | Motor principal: Docling + batching paralelo + caché SHA-256 | `quibor-pdf-to-rag` |
| `legalizer.py` | Detecta TÍTULO/CAPÍTULO/Artículo; genera TOC | `quibor-legalizer` |
| `chunker.py` | Un `.md` por artículo para embeddings precisos | `quibor-legalizer` |
| `metadata_extractor.py` | YAML frontmatter con Gaceta, fecha, tipo, SHA-256 | `quibor-metadata` |
| `validator.py` | Verifica secuencia, duplicados, artículos corruptos | `quibor-validator` |
| `iniciar_conversion.bat` | Menú interactivo + verificación de dependencias | `quibor-pdf-to-rag` |

---

## Funciones Avanzadas

**Procesamiento concurrente por lotes** — PDFs extensos se dividen en lotes de 15 páginas procesados en paralelo (ThreadPoolExecutor, 3 threads). Previene caídas por memoria RAM y optimiza CPU.

**Recuperación automática de fallos** — Si un lote falla con OCR activo, el sistema reintenta automáticamente sin OCR en ese lote en lugar de interrumpir la conversión completa.

**Caché SHA-256 dinámica** — Cada PDF procesado se registra en `.conversion_cache/manifest.json` con su hash. Archivos sin cambios se saltan automáticamente; forzar reprocesado con `--force-reprocess`.

**Soporte multiformato** — Procesa PDF, PNG, JPG, JPEG, TIFF y BMP. Las imágenes se convierten directamente a Markdown estructurado.

**Codificación UTF-8 explícita** — Configuración de stdout/stderr en Windows para caracteres del español (tildes, eñes, diéresis) sin bloqueos.

---

## Resultados Actuales

| Documento | Artículos | Chunks | Tasa |
|-----------|-----------|--------|------|
| Código Penal | 640 | 629 | 98.3% |
| Código Orgánico Procesal Penal | 355 | 353 | 99.4% |
| Ley Especial de Delitos Informáticos | 35 | 35 | 100% |
| Ley sobre Mensajes de Datos | 56 | 55 | 98.2% |
| Creación del CENIF | 74 | 74 | 100% |

> Los documentos ISO/NIST usan secciones numeradas (no artículos). Se detectan pero sin separación de artículos. Ver `quibor-pdf-to-rag/references/section-numbering-extension.md` para la hoja de ruta de soporte.

---

## Instalación

> **Primera ejecución**: requiere CMD como Administrador para instalar Chocolatey y Tesseract OCR.

```cmd
:: 1. Navegar al proyecto
cd /d "D:\VS CODE\IBM DOCLING"

:: 2. Lanzar el asistente interactivo
iniciar_conversion.bat
```

El instalador verifica y configura automáticamente: Python 3.10+, Tesseract OCR, entorno virtual `docling_env`, y todas las dependencias pip.

**Instalación manual del entorno virtual:**

```cmd
python -m venv docling_env
docling_env\Scripts\activate
pip install docling pytesseract easyocr pyyaml rich
```

---

## Modos de Ejecución

| Opción | Modo | Cuándo usarlo |
|--------|------|---------------|
| `1` | Conversión completa | Primera vez o PDF nuevo |
| `2` | Solo post-procesado | Cambios en `legalizer.py` sin re-correr Docling |
| `3` | Forzar reprocesado | Ignorar caché y reconvertir todo |
| `4` | Sin OCR (rápido) | PDFs digitales nativos (no escaneados) |
| `5` | Un archivo con OCR | Procesar un PDF específico |
| `6` | Un archivo sin OCR | PDF específico, nativo digital |
| `7` | Sin chunks | Solo el `.md` consolidado, sin artículos individuales |
| `8` | Validar normativas | Reporte de integridad de todos los documentos |

**Comandos directos (sin menú):**

```cmd
:: PDF específico, digital nativo (más rápido)
docling_env\Scripts\python.exe convert_normativas.py --file-path "codigo penal.pdf" --no-ocr

:: Forzar reprocesado completo
docling_env\Scripts\python.exe convert_normativas.py --force-reprocess

:: Validar todos los documentos convertidos
docling_env\Scripts\python.exe validator.py normativas_rag

:: Generar chunks de un .md ya convertido
docling_env\Scripts\python.exe chunker.py "normativas_rag/codigo penal.md"
```

---

## Estructura del Proyecto

```
IBM DOCLING/
├── normativas_pdf/              [ENTRADA]   PDFs originales
├── normativas_rag/              [SALIDA]    Markdown completo por ley (YAML + TOC)
├── normativas_chunks/           [SALIDA]    Un .md por artículo (RAG preciso)
├── .conversion_cache/           [SISTEMA]   Caché SHA-256 + manifest.json
├── docling_env/                 [SISTEMA]   Entorno virtual Python
│
├── convert_normativas.py        Motor principal
├── legalizer.py                 Jerarquía legal + separación de artículos
├── metadata_extractor.py        YAML frontmatter + metadata legal
├── validator.py                 Validación de integridad
├── chunker.py                   Generador de chunks individuales
├── iniciar_conversion.bat       Orquestador interactivo
│
└── .quibor-skills/              [IA]        Skills de asistencia de IA
    ├── quibor-pdf-to-rag/       Pipeline maestro
    ├── quibor-legalizer/        legalizer.py + chunker.py
    ├── quibor-metadata/         metadata_extractor.py
    └── quibor-validator/        validator.py
```

---

## Formato de Salida

### `normativas_rag/ley.md` — Documento consolidado

```markdown
---
tipo_instrumento: "Código"
nombre_oficial: "Código Penal de Venezuela"
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"
articulos_detectados: 640
categorias: ["penal"]
hash_pdf_sha256: "abc123..."
---

## TÍTULO I - De la aplicación de la Ley Penal

### ÍNDICE DE ARTÍCULOS
| Art. | Descripción | Ubicación |
| ---- | ----------- | --------- |
| 1    | Principio de Legalidad | TÍTULO I |
...

###### Artículo 1 — Principio de Legalidad

Nadie podrá ser castigado por un hecho que no estuviere
expresamente previsto como punible por la ley...

---

###### Artículo 2 — Retroactividad Favorable
...
```

### `normativas_chunks/ley/articulo_0001.md` — Chunk individual

```markdown
---
ley: "Código Penal de Venezuela"
articulo: 1
ubicacion: "TÍTULO I - De la aplicación de la Ley Penal"
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"
hash_pdf_sha256: "abc123..."
---

# Artículo 1 — Principio de Legalidad
**Ley:** Código Penal de Venezuela
**Ubicación:** TÍTULO I

Nadie podrá ser castigado por un hecho que no estuviere...
```

---

## Integración con Sistemas RAG

Los chunks generados son compatibles directamente con:

```python
# LangChain
from langchain_community.document_loaders import DirectoryLoader
loader = DirectoryLoader("normativas_chunks/", glob="**/*.md")

# LlamaIndex
from llama_index.core import SimpleDirectoryReader
documents = SimpleDirectoryReader("normativas_chunks/").load_data()

# ChromaDB — filtros por metadata
results = collection.query(
    query_texts=["¿Qué dice sobre el delito informático?"],
    where={"categorias": {"$contains": "delitos_informaticos"}}
)
```

---

## Skills de IA Incluidos

Este repositorio incluye un conjunto de skills especializados para asistentes de IA (Claude, GPT, etc.). Los skills viven en `.quibor-skills/` y se cargan automáticamente cuando la IA trabaja con este proyecto.

| Skill | Cubre | Cuándo cargarlo |
|-------|-------|-----------------|
| `quibor-pdf-to-rag` | Pipeline completo, Docling, errores de configuración | Primera consulta general |
| `quibor-legalizer` | `legalizer.py`, `chunker.py`, patrones de artículos | Artículos mal detectados |
| `quibor-metadata` | `metadata_extractor.py`, YAML, SHA-256, Gaceta | Metadata incompleta |
| `quibor-validator` | `validator.py`, métricas de calidad, reportes | Validar después de conversión |

---

## Automatización Programada (Windows)

```
Programador de tareas → Crear tarea básica
  Nombre: QUIBOR-RAG
  Desencadenador: Al iniciar sesión / Programado
  Acción: Iniciar programa → iniciar_conversion.bat
  Iniciar en: D:\VS CODE\IBM DOCLING
```

---

## Licencia y Desarrollador

**Licencia MIT** — Libre uso, modificación y distribución.

| | |
|--|--|
| **Desarrollador** | Jull Ortiz — Arquitecto de Información IA |
| **Correo** | julljoll@gmail.com |
| **Web** | [sha256.us](https://sha256.us) |
| **Instagram** | [@sha256.us](https://www.instagram.com/sha256.us/) |
| **Propósito** | Transformación tecnológica del sistema de justicia venezolano |
| **Copyright** | © 2026 Jull Ortiz |

*Desarrollado con dedicación para acelerar y fortalecer la digitalización jurídica de Venezuela.*
