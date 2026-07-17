# JullBrain V-2.1 — Pipeline RAG de Normativas Jurídicas Venezolanas

> Conversión automatizada de PDFs jurídicos y documentos a Markdown estructurado, JSON Jerárquico y vectores semánticos para sistemas de IA — Powered by IBM Docling + Granite Embedding R2.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org) [![Licencia Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg)](LICENSE) [![IBM Docling](https://img.shields.io/badge/IBM-Docling-purple)](https://github.com/docling-project/docling) [![sentence-transformers](https://img.shields.io/badge/sentence--transformers-5.6.0-green)](https://sbert.net)

**📖 Arquitectura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | **🗺️ Framework:** [`FRAMEWORK.md`](FRAMEWORK.md) | **🤖 Skills IA:** [`.agents/`](.agents/) | **📊 Diagrama:** [`jullbrain_architecture.svg`](jullbrain_architecture.svg)

---

## El Problema que Resuelve

Los modelos de lenguaje (LLM) fallan con PDFs de documentos legales y normativos porque:

- Los artículos aparecen fusionados en párrafos de 2,000+ palabras sin separación.
- Las tablas de PDFs se rompen o pierden su estructura.
- No hay metadata legal (Gaceta Oficial, fecha, tipo de instrumento) para filtrar búsquedas RAG.
- El chunking por caracteres o páginas parte artículos a la mitad, generando fragmentos incoherentes.
- Los chunks no tienen representación vectorial semántica para búsqueda por similitud.

**JullBrain** convierte esos PDFs en Markdown semánticamente estructurado, chunks JSON jerárquicos y vectores de embedding listos para ingestarse en **RAGFlow**. Todo de forma local, air-gapped y trazable.

---

## Arquitectura del Pipeline V-2.1

```text
[orquestador_JullBrain.bat]     ← Interfaz de inicio (Control Visual, Ctrl+C)
       │
       ▼
[Entorno Virtual Python]        ← docling_env (Instalación automática)
       │
       ▼
normativas_pdf/ | formatos_word/
       │
       ▼
[IBM Docling + OCR]             ← Extracción profunda + Hierarchical Chunker (JSON)
       │
       ▼
[legalizer.py]                  ← Jerarquía: TÍTULO › CAPÍTULO › Artículo + TOC
       │
       ▼
[metadata_extractor.py]         ← YAML frontmatter: Gaceta, fecha, SHA-256
       │
       ▼
[validator.py]                  ← Integridad: secuencia, duplicados, validación cruzada PDF
       │
       ├──────────────────────────────────────────────────┐
       ▼                                                  ▼
normativas_rag/                              normativas_chunks/
  ley-completa.md                              hierarchical_chunks.json
                                                          │
                                                          ▼
                                           [granite_embedder.py]  ← NUEVO en V-2.1
                                           ibm-granite/granite-embedding-multilingual-r2
                                           768 dim | 32 768 tokens | 200+ idiomas
                                                          │
                                                          ▼
                                           hierarchical_chunks_embedded.json
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
| `granite_embedder.py` | **[NUEVO V-2.1]** Motor de embeddings semánticos. Carga `ibm-granite/granite-embedding-multilingual-r2` vía `sentence-transformers` (backend local) u Ollama. Añade campo `embedding` a cada chunk sin modificar el contenido original (principio de espejo documental R7). |
| `pipeline_config.json` | Configuración persistente del pipeline (OCR, umbrales de integridad, Granite, RAGFlow, backend/batch/device de embeddings). |
| `app.py` | Dashboard Streamlit: **7 módulos** (Capas de Arquitectura, Orquestador de Conversión, Integridad Legal, Cadena de Custodia, Editor RAG, 🧬 Granite Embedding, Ajustes del Pipeline). |
| `orquestador_JullBrain.bat` | Lanzador principal. Activa el entorno virtual e inicia la interfaz interactiva en Streamlit. |

---

## Funciones Avanzadas

**🧬 Motor de Embeddings Granite R2 (Nuevo V-2.1)** — Genera vectores semánticos de 768 dimensiones por chunk usando `ibm-granite/granite-embedding-multilingual-r2` (200+ idiomas, 32 768 tokens de contexto). Produce `hierarchical_chunks_embedded.json` listo para RAGFlow. Configurable: `sentence-transformers` (local Python) u Ollama (API).

**Doble Validación Cruzada** — Implementación del Principio 10 (Error Cero). Compara los artículos detectados por el legalizer en Markdown contra el texto extraído directamente del PDF usando PyMuPDF (`fitz`), señalando discrepancias de forma exacta.

**Cadena de Custodia Digital** — Trazabilidad forense completa (ISO/IEC 27037 / R7). Genera un seguimiento de hashes SHA-256 de todas las normativas cargadas con opción de exportar el Acta de Custodia.

**Ajustes Persistentes** — Control completo del pipeline almacenado en `pipeline_config.json` y manejado directamente en el menú de Streamlit.

**Progress Bars y Procesamiento Uno a Uno** — Barra de progreso dinámica e interactiva en la interfaz visual de Streamlit para no congelar la UI y realizar ejecuciones controladas y secuenciales.

**Caché SHA-256 dinámica** — Cada PDF procesado se registra en `.conversion_cache/manifest.json`. Si arrastras un archivo sin cambios, lo salta en un milisegundo.

---

## Compatibilidad con IBM Granite

| Parámetro | Valor Configurado |
|-----------|------------------|
| Modelo de Inferencia | `granite4.1:8b` (via Ollama) |
| Temperatura Jurídica | `0.15` ≤ 0.2 — reduce variabilidad no verificable |
| Ventana de Contexto | 128 000 tokens |
| Modelo de Embeddings | `ibm-granite/granite-embedding-multilingual-r2` (recomendado) |
| Backend de Embeddings | `sentence-transformers` (local, sin dependencias externas) |
| Dispositivo de Cómputo | `cpu` (compatible Windows sin CUDA) |
| Batch Size | `32` chunks por iteración |
| Chunking Strategy | `hierarchical_chunks.json` (Hierarchical Chunker nativo Docling) |
| Política del Modelo | Abstención obligatoria si no existe respaldo documental |

---

## Nota sobre el Modelo de Embeddings

> ⚠️ El repositorio está configurado con `ibm-granite/granite-embedding-english-r2` por defecto (verificado y operativo). Para corpus en **español** (leyes venezolanas), se recomienda migrar a `ibm-granite/granite-embedding-multilingual-r2` (200+ idiomas, 32 768 tokens). Ambos modelos se descargan automáticamente de HuggingFace en la primera ejecución.
>
> **Fix Windows conocido**: Si aparece error `DLL load failed importing hf_xet`, ejecutar: `docling_env\Scripts\pip.exe uninstall hf_xet -y`

---

## Instalación y Ejecución

Solo necesitas tener [Python 3.10+](https://www.python.org/downloads/) instalado.

```cmd
:: 1. Clona el proyecto y entra en la carpeta
cd "ruta/a/JullBrain"

:: 2. Ejecuta el orquestador principal
orquestador_JullBrain.bat
```

> El archivo `.bat` detectará si falta el entorno virtual (`docling_env`), lo creará, instalará todas las dependencias de `requirements.txt` automáticamente e iniciará la interfaz visual en `http://localhost:8501`.

---

## Licencia

Distribuido bajo Licencia Apache 2.0. Ver [LICENSE](LICENSE) para más detalles.
Desarrollado para avanzar en la transformación tecnológica y la mitigación de alucinación en el ecosistema RAG/IA jurídica venezolano.
