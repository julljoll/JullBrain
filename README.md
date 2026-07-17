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
| `validator.py` | Verifica secuencia numérica, previene duplicados, detecta artículos corruptos y ejecuta validación cruzada con PyMuPDF. |
| `pipeline_config.json` | Configuración persistente del pipeline (OCR, umbrales de integridad, Granite, RAGFlow). |
| `app.py` | Dashboard Streamlit: 6 módulos (Capas de Arquitectura, Orquestador de Conversión, Integridad Legal, Cadena de Custodia, Editor RAG, Ajustes del Pipeline). |
| `orquestador_JullBrain.bat` | Lanzador principal. Activa el entorno virtual e inicia la interfaz interactiva en Streamlit. |

---

## Funciones Avanzadas

**Doble Validación Cruzada** — Implementación del Principio 10 (Error Cero). Compara los artículos detectados por el legalizer en Markdown contra el texto extraído directamente del PDF usando PyMuPDF (`fitz`), señalando discrepancias de forma exacta.

**Cadena de Custodia Digital** — Trazabilidad forense completa (ISO/IEC 27037 / R7). Genera un seguimiento de hashes SHA-256 de todas las normativas cargadas con opción de exportar el Acta de Custodia.

**Ajustes Persistentes** — Control completo del pipeline almacenado en `pipeline_config.json` y manejado directamente en el menú de Streamlit.

**Progress Bars y Procesamiento Uno a Uno** — Barra de progreso dinámica e interactiva en la interfaz visual de Streamlit para no congelar la UI y realizar ejecuciones controladas y secuenciales.

**Caché SHA-256 dinámica** — Cada PDF procesado se registra en `.conversion_cache/manifest.json`. Si arrastras un archivo sin cambios, lo salta en un milisegundo.

---

## Compatibilidad con IBM Granite 4.0

| Parámetro | Valor Recomendado / Configurado |
|-----------|---------------------------------|
| Modelo de Inferencia | `granite4.1:8b` (o superior) |
| Temperatura Jurídica | ≤ 0.2 (fija para reducir variabilidad no verificable) |
| Ventana de Contexto | 128,000 tokens |
| Embeddings del Dataset | `granite-embedding-30m-english` (RAGFlow) |
| Chunking Strategy | `hierarchical_chunks.json` (Hierarchical Chunker) |
| Política del Modelo | Abstención obligatoria si no existe respaldo documental |

---

## Instalación y Ejecución

Solo necesitas tener [Python 3.10+](https://www.python.org/downloads/) instalado.

```cmd
:: 1. Clona el proyecto y entra en la carpeta
cd "ruta/a/JullBrain"

:: 2. Ejecuta el orquestador principal
orquestador_JullBrain.bat
```

> El archivo `.bat` detectará si falta el entorno virtual (`docling_env`), lo creará, instalará todas las dependencias necesarias de `requirements.txt` automáticamente e iniciará la interfaz visual en `http://localhost:8501`.

---

## Licencia

Distribuido bajo Licencia Apache 2.0. Ver [LICENSE](LICENSE) para más detalles.
Desarrollado para avanzar en la transformación tecnológica y la mitigación de alucinación en el ecosistema RAG/IA jurídica venezolano.
