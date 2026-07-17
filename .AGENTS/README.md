# JullBrain V-2.0 — Pipeline RAG de Normativas Legales Venezolanas

> Conversión automatizada de PDFs jurídicos a Markdown estructurado y JSON para sistemas de IA — Powered by IBM Docling & Docker

[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://docker.com) [![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE) [![IBM Docling](https://img.shields.io/badge/IBM-Docling-purple)](https://github.com/DS4SD/docling)

---

## El Problema que Resuelve

Los modelos de lenguaje (LLM) fallan con PDFs de documentos legales venezolanos porque:

- Los artículos aparecen fusionados en párrafos de 2,000+ palabras sin separación.
- Las tablas de PDFs se rompen o pierden su estructura.
- No hay metadata legal (Gaceta Oficial, fecha, tipo de instrumento) para filtrar búsquedas RAG.
- El chunking tradicional parte artículos a la mitad, generando fragmentos incoherentes.

**JullBrain** soluciona esto usando el `HierarchicalChunker` nativo de IBM Docling integrado en una arquitectura Dockerizada, logrando extraer fragmentos semánticos inteligentes con metadata completa.

---

## Arquitectura del Pipeline (V2.0)

```
normativas_pdf/
       │
       ▼
[Contenedor Docker: jullbrain] ← Ejecución aislada (No requiere Python local)
       │
       ├── [convert_normativas.py] ← Docling + OCR
       │
       ├── [legalizer.py]          ← Estructuración jerárquica previa (TÍTULOS, CAPÍTULOS)
       │
       └── [HierarchicalChunker]   ← Generación semántica de JSON chunks
       │
       ├──────────────────────────────────────────────────────────────────────────────┐
       ▼                                                                              ▼
normativas_rag/                                          normativas_chunks/
  ley-completa.md                                          ley/hierarchical_chunks.json
  (Markdown + YAML + TOC)                                  (Vectores listos para RAGFlow)
```

---

## Módulos del Sistema

| Módulo | Función | Skill de IA Asociado |
|--------|---------|----------------------|
| `convert_normativas.py` | Motor principal: Docling + OCR + HierarchicalChunker | `jullbrain-pdf-to-rag` |
| `legalizer.py` | Detecta TÍTULO/CAPÍTULO/Artículo para guiar al chunker | `jullbrain-legalizer` |
| `metadata_extractor.py` | YAML frontmatter con Gaceta, fecha, tipo, SHA-256 | `jullbrain-metadata` |
| `validator.py` | Verifica secuencia, duplicados, artículos corruptos + validación cruzada PDF | `jullbrain-validator` |
| `pipeline_config.json` | Configuración persistente del pipeline (OCR, umbrales, Granite, RAGFlow) | — |
| `app.py` | Dashboard Streamlit: 6 módulos (Arquitectura, Conversiones, Integridad, Custodia, Editor, Ajustes) | — |
| `orquestador_JullBrain.bat`| Orquestador (lanza Streamlit con entorno virtual) | `jullbrain-pdf-to-rag` |

> **NOTA IMPORTANTE**: El antiguo módulo `chunker.py` fue deprecado y eliminado en favor del `HierarchicalChunker` nativo de Docling.

---

## Funciones Avanzadas

**Dockerización Total** — Se acabaron los problemas de dependencias en Windows o Mac. Todo el repositorio se empaqueta en una imagen limpia de Python 3.12 con Tesseract preconfigurado.

**Hierarchical Chunking** — Integración nativa con el motor de fragmentación de IBM Docling, generando salidas en `JSON` con bounding boxes, jerarquía y categorías detectadas por IA.

**Recuperación automática de fallos** — Si un lote falla con OCR activo, el sistema reintenta automáticamente sin OCR en ese lote.

**Doble Validación Cruzada** — El validator.py extrae artículos del PDF original con PyMuPDF y los contrasta contra el Markdown generado por el legalizer, asegurando que ningún artículo se pierda en la conversión (Principio 10: Error Cero).

**Cadena de Custodia Digital** — Módulo integrado en el dashboard que registra y verifica hashes SHA-256 de todos los documentos del pipeline, con exportación de acta forense (Requisito R7, ISO/IEC 27037).

**Configuración Persistente** — Todos los parámetros del pipeline se almacenan en `pipeline_config.json` y se gestionan desde el dashboard de Streamlit (Principio 11).

---

## Compatibilidad con IBM Granite 4.0

| Parámetro | Valor Recomendado |
|-----------|-------------------|
| Modelo de Inferencia | `granite4.1:8b` (piloto) — Granite 4.0 cuando esté disponible |
| Temperatura Jurídica | ≤ 0.2 (fija, no configurable por usuario final) |
| Ventana de Contexto | 128,000 tokens |
| Modelo de Embeddings | `granite-embedding-30m-english` |
| Formato de Chunks | `hierarchical_chunks.json` (IBM Docling HierarchicalChunker) |
| Abstención Obligatoria | Sí — el sistema dice "no encontrado" si no hay respaldo documental |

---

## Integración Exclusiva con RAGFlow

Todo el pipeline está diseñado EXCLUSIVAMENTE para que la salida sea consumida por **RAGFlow**. 
No diseñes para LangChain, LlamaIndex o LanceDB a menos que se indique lo contrario. El JSON generado por `HierarchicalChunker` cumple con la estructura esperada para el motor nativo de ingesta vectorial de RAGFlow.

---

## Instalación y Ejecución

Todo el sistema es autogestionado mediante scripts por lotes. 

> **Ejecución Recomendada**:
> Simplemente haz doble clic en `orquestador_JullBrain.bat` en tu computadora. 
> 
> El script solicitará permisos de administrador e instalará automáticamente `Chocolatey` y `Docker Desktop` si no están presentes. Finalmente, compilará y ejecutará el contenedor de JullBrain procesando los PDFs.

**Comandos de Desarrollo (Si usas terminal):**
```cmd
:: 1. Construir la imagen
docker compose build jullbrain

:: 2. Procesar todos los archivos pendientes
docker compose run --rm jullbrain
```

---

## Estructura del Proyecto

```
JullBrain/
├── normativas_pdf/              [ENTRADA]   PDFs originales
├── normativas_rag/              [SALIDA]    Markdown completo por ley (YAML + TOC)
├── normativas_chunks/           [SALIDA]    JSON (hierarchical_chunks.json) para RAGFlow
├── .conversion_cache/           [SISTEMA]   Caché SHA-256 + manifest.json
├── .streamlit/config.toml       [SISTEMA]   Tema visual del dashboard
│
├── app.py                       Dashboard Streamlit (6 módulos)
├── convert_normativas.py        Motor principal + Hierarchical Chunking
├── legalizer.py                 Jerarquía legal
├── metadata_extractor.py        YAML frontmatter + metadata legal
├── validator.py                 Validación de integridad + validación cruzada PDF
├── pipeline_config.json         Configuración persistente del pipeline
├── orquestador_JullBrain.bat    Orquestador (lanza Streamlit con venv)
│
└── .AGENTS/                     [IA]        Skills, fases y directrices del agente
```
