# JullBrain — Organización como Framework IBM

> Este repositorio está organizado siguiendo las convenciones de frameworks IBM
> para facilitar la navegación, el mantenimiento y la comprensión de la arquitectura.

---

## Mapa Conceptual IBM ↔ Proyecto

```text
FRAMEWORK IBM                      JULLBRAIN (IBM DOCLING V2.0 Nativo)
═══════════════                    ════════════════════════════════════

src/                                *.py (raíz del proyecto)
  ├── core/                         convert_normativas.py   ← Orquestador
  ├── pipeline/                     legalizer.py            ← Jerarquía legal
  ├── pipeline/                     metadata_extractor.py   ← YAML frontmatter
  ├── pipeline/                     validator.py            ← Validación de integridad
  └── pipeline/                     granite_embedder.py     ← Embeddings semánticos R2

scripts/                            orquestador_JullBrain.bat  ← Lanzador Automático

data/                               
  ├── input/                        normativas_pdf/         ← PDFs de entrada
  ├── input/                        formatos_word/          ← Word de entrada
  ├── output/                       normativas_rag/         ← Markdown completo
  ├── output/                       normativas_chunks/      ← Chunks JSON Jerárquicos
  └── cache/                        .conversion_cache/      ← Caché SHA-256

docs/                               docs/                   ← Documentación técnica
                                    FRAMEWORK.md            ← Este archivo

agents/                             .AGENTS/                ← Skills de IA
  ├── _index.md                                               ← Índice maestro
  ├── agent.md                                                ← Rol de IA
  ├── jullbrain-pdf-to-rag/                                  ← Skill pipeline
  ├── jullbrain-legalizer/                                   ← Skill legalizer
  ├── jullbrain-metadata/                                    ← Skill metadata
  ├── jullbrain-validator/                                   ← Skill validator
  └── jullbrain-launcher/                                    ← Skill para bat CLI

config/                             requirements.txt         ← Dependencias Python
                                    .gitignore               ← Exclusiones git
```

---

## Estructura Física del Repositorio

```text
IBM DOCLING/
│
├── 📁 docs/                          ← Documentación (este es tu mapa)
│   ├── ARCHITECTURE.md               ← Arquitectura detallada del pipeline
│   └── README.md                     ← Índice de documentación
│
├── 📁 .AGENTS/                       ← Skills para asistentes de IA
│   ├── _index.md                     ← PUNTO DE ENTRADA: lee esto primero
│   ├── agent.md                      ← Rol y directrices de comportamiento
│   ├── jullbrain-pdf-to-rag/         ← Skill: Pipeline maestro
│   ├── jullbrain-legalizer/          ← Skill: Legalizer Markdown
│   ├── jullbrain-metadata/           ← Skill: Metadata extraction
│   ├── jullbrain-validator/          ← Skill: Validador
│   └── jullbrain-launcher/           ← Skill: CLI Bat protection
│
├── 📁 normativas_pdf/                ← [data/input] PDFs de leyes venezolanas
├── 📁 formatos_word/                 ← [data/input] Documentos Word (.doc/.docx)
├── 📁 normativas_rag/                ← [data/output] Markdown consolidado (YAML + TOC)
├── 📁 normativas_chunks/             ← [data/output] Chunks JSON generados por Docling
├── 📁 .conversion_cache/             ← [data/cache] Caché SHA-256
│
│   📄 [src/core]     convert_normativas.py    ← Motor principal (orquestador)
│   📄 [src/pipeline] legalizer.py             ← Estructurador legal
│   📄 [src/pipeline] metadata_extractor.py    ← Extractor de metadatos
│   📄 [src/pipeline] validator.py             ← Validador de integridad
│   📄 [src/pipeline] granite_embedder.py      ← Embeddings semánticos Granite R2
│
│   📄 [config]   requirements.txt             ← Dependencias Python
│   📄 [config]   .gitignore                   ← Exclusiones git
│
│   📄 [scripts]  orquestador_JullBrain.bat       ← Lanzador inteligente
│
│   📄 FRAMEWORK.md                            ← Este archivo
│   📄 README.md                               ← README principal
```

---

## Convenciones del Framework

### Entorno Nativo
Toda la ejecución de Python 3.10+ y dependencias complejas (Docling, PyTorch, OCR) ocurren dentro de un entorno virtual local administrado automáticamente por `orquestador_JullBrain.bat`.

### Pipeline de Datos
El flujo es estrictamente unidireccional y secuencial:
```text
input → IBM Docling (JSON Chunks) → legalizer → metadata → validator → output (.md)
```

### Skills de IA
Los skills en `.AGENTS/` permiten que asistentes de IA comprendan y extiendan el proyecto sin necesidad de leer todo el código fuente, respetando siempre la estructura del entorno nativo.

---

## Convención de Nomenclatura

| Elemento | Convención | Ejemplo |
|---|---|---|
| Módulos Python | snake_case | `convert_normativas.py` |
| Directorios de datos | snake_case | `normativas_pdf/` |
| Skills IA | kebab-case | `jullbrain-pdf-to-rag/` |
| Salidas Markdown | nombre-ley.md | `codigo-penal.md` |
| Salidas JSON | `hierarchical_chunks.json` | `hierarchical_chunks.json` |
