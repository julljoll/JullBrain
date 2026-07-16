# JullBrain V-2.0 — Pipeline RAG de Normativas y Formatos (Mi Cerebro Personal)

> Conversión automatizada de PDFs jurídicos y documentos a Markdown estructurado y JSON Jerárquico para sistemas de IA — Powered by IBM Docling.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org) [![Licencia Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg)](LICENSE) [![IBM Docling](https://img.shields.io/badge/IBM-Docling-purple)](https://github.com/docling-project/docling)

**📖 Documentación completa:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | **🗺️ Mapa del framework:** [`FRAMEWORK.md`](FRAMEWORK.md) | **🤖 Skills IA:** [`.AGENTS/_index.md`](.AGENTS/_index.md) | **📊 Diagramas:** [Arquitectura](jullbrain_architecture.svg) y [Pipeline](jullbrain_pipeline.svg)

---

## El Problema que Resuelve

Los modelos de lenguaje (LLM) fallan con PDFs de documentos legales y normativos porque:

- Los artículos aparecen fusionados en párrafos de 2,000+ palabras sin separación.
- Las tablas de PDFs se rompen o pierden su estructura.
- No hay metadata legal (Gaceta Oficial, fecha, tipo de instrumento) para filtrar búsquedas RAG.
- El chunking por caracteres o páginas parte artículos a la mitad, generando fragmentos incoherentes.

**JullBrain** convierte esos PDFs en Markdown semánticamente estructurado y en un formato JSON listo (`hierarchical_chunks.json`), con fragmentos inteligentes, listo para ingestarse en **RAGFlow**. Todo esto de forma nativa en tu entorno local.

---

## Arquitectura del Pipeline V-2.0

```text
[orquestador_JullBrain.bat]     ← Interfaz de inicio (Control Visual, Ctrl+C)
       │
       ▼
[Entorno Virtual Python]     ← Entorno aislado (Instalación automática)
       │
       ▼
normativas_pdf/
       │
       ▼
[IBM Docling + OCR]          ← Extracción profunda + Hierarchical Chunker (JSON)
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
  ley-completa.md                                          hierarchical_chunks.json
                                                                      │
                                                                      ▼
                                                                  RAGFlow
```

---

## Módulos del Sistema

| Módulo | Función |
|--------|---------|
| `convert_normativas.py` | Motor principal: Orquestación Docling, soporte recursivo de carpetas, Barras de Progreso Visuales (`rich`), Caché SHA-256 y manejo `Ctrl+C`. |
| `legalizer.py` | Detecta jerarquía (TÍTULO/CAPÍTULO/Artículo) y genera TOC interactivos en Markdown. |
| `HierarchicalChunker` | Integrado vía Docling. Extrae chunks semánticos listos para RAGFlow. |
| `metadata_extractor.py` | Inyecta YAML frontmatter con Gaceta, fecha, tipo de documento y huella digital (SHA-256). |
| `validator.py` | Verifica secuencia numérica, previene duplicados y detecta artículos corruptos o cortos. |
| `orquestador_JullBrain.bat` | Lanzador principal. Instala automáticamente dependencias en un entorno virtual aislado y ejecuta la conversión. |

---

## Funciones Avanzadas

**Arquitectura Python Nativa** — JullBrain V2.0 corre directamente en tu sistema utilizando entornos virtuales (`docling_env`) de forma transparente, instalando todo automáticamente.

**Progress Bars TTY** — Monitoreo hiper-visual del proceso en consola, con animaciones fluidas y detalladas de cada etapa de extracción.

**Interrupción Segura (Ctrl+C)** — Puedes detener el análisis en cualquier momento. JullBrain interceptará la señal y guardará a salvo todo el progreso que ya había logrado procesar.

**Recuperación automática de fallos** — Si un lote falla con OCR activo, el sistema reintenta automáticamente sin OCR en ese lote en lugar de interrumpir la conversión.

**Soporte de Subcarpetas Recursivas** — Preserva la estructura jerárquica y de carpetas del origen (`normativas_pdf/` y `formatos_word/`) directamente en las salidas (`normativas_rag/`, `formatos_rag/` y `normativas_chunks/`), manteniendo la clasificación de documentos intacta.

**Caché SHA-256 dinámica** — Cada PDF procesado se registra en `.conversion_cache/manifest.json`. Si arrastras un archivo sin cambios, lo salta en un milisegundo.

---

## Resultados Actuales

| Documento | Artículos | Tasa de Conversión |
|-----------|-----------|--------------------|
| Código Penal | 640 | 98.3% |
| Código Orgánico Procesal Penal | 355 | 99.4% |
| Ley Especial de Delitos Informáticos | 35 | 100% |
| Ley sobre Mensajes de Datos | 56 | 98.2% |
| Creación del CENIF | 74 | 100% |

---

## Instalación y Ejecución

Solo necesitas tener [Python 3.10+](https://www.python.org/downloads/) instalado. Todo el resto es automatizado.

```cmd
:: 1. Clona el proyecto y entra en la carpeta
cd "ruta/a/JullBrain"

:: 2. Ejecuta el orquestador principal
orquestador_JullBrain.bat
```

> **Autoinstalación**: El archivo `.bat` detectará si falta el entorno virtual, lo creará, instalará todas las dependencias necesarias de `requirements.txt` automáticamente y comenzará la conversión de tus archivos PDF.

---

## Licencia
Distribuido bajo Licencia Apache 2.0. Ver [LICENSE](LICENSE) para más detalles.
Desarrollador para avanzar en la transformación tecnológica del ecosistema RAG/IA venezolano.
