# JullBrain — Organización como Framework IBM

> Este repositorio está organizado siguiendo las convenciones de frameworks IBM
> para facilitar la navegación, el mantenimiento y la comprensión de la arquitectura.

---

## Mapa Conceptual IBM ↔ Proyecto

```
FRAMEWORK IBM                      JULLBRAIN (IBM DOCLING)
═══════════════                    ════════════════════════

src/                                *.py (raíz del proyecto)
  ├── core/                         convert_normativas.py   ← Orquestador
  ├── pipeline/                     legalizer.py            ← Jerarquía legal
  ├── pipeline/                     metadata_extractor.py   ← YAML frontmatter
  ├── pipeline/                     validator.py            ← Validación
  └── pipeline/                     chunker.py              ← Chunk generator

scripts/                            iniciar_conversion.bat  ← Lanzador interactivo
                                    *.bat                   ← Scripts batch

data/                               
  ├── input/                        normativas_pdf/         ← PDFs de entrada
  ├── input/                        formatos_word/          ← Word de entrada
  ├── output/                       normativas_rag/         ← Markdown completo
  ├── output/                       formatos_rag/           ← Word → Markdown
  ├── output/                       normativas_chunks/      ← Chunks por artículo
  └── cache/                        .conversion_cache/      ← Caché SHA-256

docs/                               docs/                   ← Documentación técnica
                                    FRAMEWORK.md            ← Este archivo

agents/                             .AGENTS/                ← Skills de IA
  ├── _index.md                                               ← Índice maestro
  ├── agent.md                                                ← Rol de IA
  ├── jullbrain-pdf-to-rag/                                  ← Skill pipeline
  ├── jullbrain-legalizer/                                   ← Skill legalizer
  ├── jullbrain-metadata/                                    ← Skill metadata
  └── jullbrain-validator/                                   ─ Skill validator

tools/
  ├── packaging/                    chocolatey/              ← Paquete Chocolatey
  └── installer/                    installer_tools/         ← InnoSetup installer

env/                                docling_env/             ← Entorno virtual Python

config/                             requirements.txt         ← Dependencias Python
                                    Dockerfile              ← Config Docker
                                    docker-compose.yml      ← Orquestación Docker
                                    .gitignore              ← Exclusiones git
                                    .dockerignore           ← Exclusiones Docker

examples/                           (usar normativas_pdf/ como ejemplos)

tests/                              (pendiente — ver validación con validator.py)
```

---

## Estructura Física del Repositorio

```
IBM DOCLING/
│
├── 📁 docs/                          ← Documentación (este es tu mapa)
│   ├── ARCHITECTURE.md               ← Arquitectura detallada del pipeline
│   └── README.md                     ← Índice de documentación
│
├── 📁 .AGENTS/                       ← Skills para asistentes de IA
│   ├── _index.md                     ← PUNTO DE ENTRADA: lee esto primero
│   ├── agent.md                      ← Rol y directrices de comportamiento
│   ├── README.md                     ← Visión general de skills
│   ├── pipeline_caso_civil.svg       ← Diagrama de pipeline
│   ├── jullbrain-pdf-to-rag/         ← Skill: Pipeline maestro
│   ├── jullbrain-legalizer/          ← Skill: Legalizer + Chunker
│   ├── jullbrain-metadata/           ← Skill: Metadata extraction
│   └── jullbrain-validator/          ← Skill: Validador
│
├── 📁 normativas_pdf/                ← [data/input] PDFs de leyes venezolanas
├── 📁 formatos_word/                 ← [data/input] Documentos Word (.doc/.docx)
├── 📁 normativas_rag/                ← [data/output] Markdown consolidado (YAML + TOC)
├── 📁 formatos_rag/                  ← [data/output] Word convertido a Markdown
├── 📁 normativas_chunks/             ← [data/output] Chunks individuales por artículo
├── 📁 .conversion_cache/             ← [data/cache] Caché SHA-256
├── 📁 chocolatey/                    ← [tools/packaging] Paquete Chocolatey
├── 📁 installer_tools/               ← [tools/installer] Instalador InnoSetup
├── 📁 docling_env/                   ← [env] Entorno virtual Python
│
│   📄 [src/core]  convert_normativas.py       ← Motor principal (orquestador)
│   📄 [src/pipeline] legalizer.py             ← Estructurador legal
│   📄 [src/pipeline] metadata_extractor.py    ← Extractor de metadatos
│   📄 [src/pipeline] validator.py             ← Validador de integridad
│   📄 [src/pipeline] chunker.py               ← Generador de chunks
│   📄 [src/gui]     gui.py                    ← Interfaz gráfica (Flet)
│
│   📄 [config]   requirements.txt             ← Dependencias Python
│   📄 [config]   Dockerfile                   ← Build Docker
│   📄 [config]   docker-compose.yml           ← Orquestación Docker
│   📄 [config]   .gitignore                   ← Exclusiones git
│   📄 [config]   .dockerignore                ← Exclusiones Docker
│
│   📄 [scripts]  iniciar_conversion.bat       ← Lanzador interactivo
│
│   📄 FRAMEWORK.md                            ← Este archivo
│   📄 README.md                               ← README principal
│   └── ... (iconos, plan de nube, spec, etc.)
```

---

## Convenciones del Framework

### Modularidad
Cada módulo Python (`legalizer.py`, `validator.py`, etc.) es independiente y
puede ejecutarse por separado. La comunicación entre módulos es a través de
archivos Markdown intermedios.

### Pipeline de Datos
El flujo es estrictamente unidireccional:
```
input → Docling → legalizer → metadata → validator → chunker → output
```

### Configuración
- `requirements.txt` — Dependencias Python
- `Dockerfile` + `docker-compose.yml` — Despliegue containerizado
- `JullBrain.spec` — PyInstaller para GUI

### Skills de IA
Los skills en `.AGENTS/` permiten que asistentes de IA comprendan y
extiendan el proyecto sin necesidad de leer todo el código fuente.

---

## Convención de Nomenclatura

| Elemento | Convención | Ejemplo |
|---|---|---|
| Módulos Python | snake_case | `convert_normativas.py` |
| Directorios de datos | snake_case | `normativas_pdf/` |
| Skills IA | kebab-case | `jullbrain-pdf-to-rag/` |
| Chunks | `articulo_NNNN.md` | `articulo_0001.md` |
| Salidas Markdown | nombre-ley.md | `codigo-penal.md` |
| Tags Docker | lowercase | `jullbrain:latest` |
