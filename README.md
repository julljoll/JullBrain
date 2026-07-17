# JullBrain V-2.1 — Pipeline RAG de Normativas Jurídicas Venezolanas

> Conversión automatizada de PDFs jurídicos y documentos a Markdown estructurado, JSON Jerárquico y vectores semánticos para sistemas de IA — Powered by IBM Docling + Granite Embedding R2.

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://python.org) [![Licencia Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg)](LICENSE) [![IBM Docling](https://img.shields.io/badge/IBM-Docling-purple)](https://github.com/docling-project/docling) [![sentence-transformers](https://img.shields.io/badge/sentence--transformers-5.6.0-green)](https://sbert.net)

**📖 Arquitectura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | **📊 Diagrama:** [`jullbrain_architecture.svg`](jullbrain_architecture.svg) | **🤖 Skills IA:** [`.AGENTS/skills/`](.AGENTS/skills/)

---

## ⚖️ El Problema que Resuelve

Los modelos de lenguaje (LLM) fallan con PDFs de documentos legales y normativos porque:
- Los artículos aparecen fusionados en párrafos de 2000+ palabras sin separación clara.
- Las tablas de los PDFs se rompen o pierden su estructura semántica.
- No hay metadata legal (Gaceta Oficial, fecha de publicación, tipo de instrumento) para filtrar búsquedas RAG.
- El chunking por caracteres o páginas parte artículos a la mitad, generando fragmentos incoherentes.
- Los chunks no tienen representación vectorial semántica calibrada en español para búsquedas por similitud.

**JullBrain** convierte esos PDFs en Markdown semánticamente estructurado, chunks JSON jerárquicos y vectores de embedding de 768 dimensiones optimizados para **RAGFlow**. Todo de forma local, *air-gapped* y auditable forensemente.

---

## 🛠️ Estructura Nativa del Proyecto

Este repositorio está organizado nativamente para facilitar la ejecución y el mantenimiento del pipeline:

```text
JullBrain/
├── 📁 .AGENTS/                       ← Instrucciones y Skills para asistentes de IA (copilots)
│   ├── AGENTS.md                     ← Directrices de comportamiento y roles del equipo (R1-R7)
│   └── 📁 skills/                    ← Módulos de conocimiento especializado para agentes
│       ├── analizador-jerarquia-legal/
│       ├── conversor-pdf-a-rag/
│       ├── extractor-metadata-legal/
│       ├── granite-embedder/
│       └── validador-calidad-ocr/
│
├── 📁 docs/                          ← Documentación detallada del proyecto
│   └── ARCHITECTURE.md               ← Detalles técnicos del flujo y del dashboard
│
├── 📁 normativas_pdf/                ← [Input] Directorio de entrada para PDFs legales
├── 📁 formatos_word/                 ← [Input] Directorio para documentos Word (.doc/.docx)
├── 📁 normativas_rag/                ← [Output] Markdown consolidado (con YAML y TOC)
├── 📁 normativas_chunks/             ← [Output] Chunks JSON generados por el pipeline
│
├── 📁 docling_env/                   ← Entorno virtual de Python (se crea automáticamente)
├── 📁 .conversion_cache/             ← Caché SHA-256 para evitar reprocesar archivos
│
├── 📄 app.py                         ← Dashboard de control visual en Streamlit (UI principal)
├── 📄 convert_normativas.py          ← Orquestador y CLI principal del pipeline de conversión
├── 📄 legalizer.py                   ← Módulo de jerarquización legal y generación de TOC
├── 📄 metadata_extractor.py          ← Extractor de YAML frontmatter y cálculo de hashes
├── 📄 validator.py                   ← Validador de calidad y doble validación cruzada
├── 📄 granite_embedder.py            ← Motor de embeddings semánticos Granite R2
│
├── 📄 pipeline_config.json           ← Configuración persistente del pipeline
├── 📄 requirements.txt               ← Dependencias de Python
├── 📄 jullbrain_architecture.svg     ← Diagrama visual de la arquitectura
├── 📄 orquestador_JullBrain.bat      ← Script de arranque y configuración automática
└── 📄 LICENSE                        ← Licencia Apache 2.0
```

---

## 🔄 Flujo del Pipeline V-2.1

El procesamiento de documentos sigue un flujo unidireccional y secuencial:

```text
[PDF/Word de Entrada] 
       │
       ▼
[IBM Docling + OCR] ───────► [Caché SHA-256] (Salta archivos sin cambios)
       │
       ▼
[legalizer.py] ────────────► Jerarquiza: TÍTULO › CAPÍTULO › Artículo + TOC Markdown
       │
       ▼
[metadata_extractor.py] ───► Inyecta YAML Frontmatter (Gaceta, Fecha, Huella SHA-256)
       │
       ▼
[validator.py] ────────────► Doble validación cruzada (Legalizer vs PyMuPDF)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
[normativas_rag/*.md]           [normativas_chunks/*.json]
                                         │
                                         ▼
                                [granite_embedder.py] (Embeddings R2 768-dim)
                                         │
                                         ▼
                                [hierarchical_chunks_embedded.json]
                                         │
                                         ▼
                                      RAGFlow
```

---

## 📦 Módulos del Sistema

| Módulo / Script | Tipo | Función Principal |
|---|---|---|
| `app.py` | UI | **Dashboard Streamlit**: Interfaz con 7 paneles para monitorización, conversiones, edición RAG y control de embeddings. |
| `convert_normativas.py` | Core | **Orquestador Principal**: Procesa recursivamente carpetas, gestiona el flujo del pipeline y maneja la caché SHA-256. |
| `granite_embedder.py` | Core | **Motor de Embeddings**: Carga `granite-embedding-311m-multilingual-r2` localmente para generar representaciones vectoriales sin alterar los datos originales (R7). |
| `legalizer.py` | Helper | **Estructurador Legal**: Normaliza la jerarquía de los artículos y crea la Tabla de Contenidos interactiva. |
| `metadata_extractor.py` | Helper | **Extractor**: Analiza el texto para extraer datos de publicación (Gaceta, fecha) e inyectar el frontmatter YAML. |
| `validator.py` | Helper | **Integridad**: Compara el conteo de artículos del pipeline con una extracción nativa por PDF para asegurar un 100% de consistencia. |
| `orquestador_JullBrain.bat` | Script | **Lanzador**: Configura el entorno virtual (`docling_env`), instala dependencias y arranca la interfaz Streamlit. |

---

## ⚙️ Configuración Persistente (`pipeline_config.json`)

El pipeline se comporta dinámicamente según las variables definidas en `pipeline_config.json` (modificables desde el Dashboard):

- `ragflow_embedding_model`: Modelo de embeddings activo (`ibm-granite/granite-embedding-311m-multilingual-r2`).
- `embedding_backend`: Motor de ejecución (`sentence-transformers` para local / `ollama` para API).
- `embedding_device`: Dispositivo de hardware (`cpu` por defecto para Windows / `cuda` si está disponible).
- `embedding_batch_size`: Cantidad de chunks procesados simultáneamente (por defecto `32`).
- `ocr_activo`: Activa/Desactiva el reconocimiento de texto OCR en Docling para PDFs escaneados.

---

## 🧬 Compatibilidad con IBM Granite & RAGFlow

| Parámetro | Valor Configurado / Recomendado |
|-----------|---------------------------------|
| **Modelo de Embeddings** | `ibm-granite/granite-embedding-311m-multilingual-r2` |
| **Dimensión de Vectores** | 768 dimensiones |
| **Contexto del Modelo** | 32 768 tokens (ideal para artículos extensos) |
| **Modelo de Inferencia (LLM)**| `granite4.1:8b` (o superior) |
| **Temperatura Jurídica** | `0.15` (≤ 0.2 para evitar alucinaciones) |
| **Abstención del LLM** | Obligatoria si la consulta no tiene respaldo en los documentos recuperados |

> 💡 **Nota sobre el Español**: Se ha migrado por defecto al modelo **Multilingual R2**. Esto asegura que las leyes venezolanas tengan la máxima precisión semántica, evitando la pérdida de contexto que ocurría con modelos entrenados únicamente en inglés.

---

## 🚀 Instalación y Ejecución

Solo requieres tener instalado **Python 3.10+** en tu sistema Windows.

1. Abre una consola de comando (CMD) en la raíz del proyecto:
   ```cmd
   cd "ruta/a/JullBrain"
   ```
2. Ejecuta el orquestador principal:
   ```cmd
   orquestador_JullBrain.bat
   ```

El archivo `.bat` detectará automáticamente si el entorno virtual (`docling_env`) no ha sido creado, descargará e instalará todas las dependencias listadas en `requirements.txt` (incluyendo PyTorch y Sentence-Transformers) e iniciará la interfaz visual en `http://localhost:8501`.

---

## ⚖️ Licencia y Principio Forense

- **Licencia**: Distribuido bajo la Licencia Apache 2.0.
- **Principio de Espejo Documental (R7)**: Ninguna transformación en el pipeline altera el texto original capturado del expediente o norma. El campo de embedding se inyecta como metadata adicional para garantizar la validez probatoria de la información procesada.
