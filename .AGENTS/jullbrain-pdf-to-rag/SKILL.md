---
name: JullBrain-pdf-to-rag
description: >
  Pipeline maestro para convertir PDFs de leyes y normativas venezolanas en Markdown estructurado y JSON.
  Úsalo siempre que el usuario mencione: convertir PDFs legales,
  procesar normativas, estructurar leyes para IA, generar chunks de artículos, ejecutar JullBrain,
  problemas con IBM Docling, errores en legalizer.py, metadata_extractor.py o
  validator.py. También aplica cuando el usuario quiere mejorar, depurar o extender cualquier
  componente del pipeline. El pipeline corre totalmente en Docker.
compatibility:
  python: ">=3.12"
  tools: [bash_tool, create_file, str_replace, view]
  dependencies:
    - docling
    - tesseract-ocr
    - docker
    - rich
---

# JullBrain V-2.0 — Skill Maestro del Pipeline PDF → RAGFlow (Docker + Hierarchical Chunking)

## Arquitectura del Sistema

```
normativas_pdf/   →   [Contenedor Docker jullbrain]   
                           ↓ (IBM Docling)
                      [legalizer.py] (Estructuración de Títulos/Capítulos)
                           ↓
                      [metadata_extractor.py]
                           ↓
                      [validator.py]
                           ↓
                      [HierarchicalChunker]
                           ↓
           normativas_rag/   +   normativas_chunks/
           (Markdown completo)   (hierarchical_chunks.json)
                                       ↓
                                    RAGFlow
```

## Módulos del Pipeline

| Módulo | Responsabilidad | Skill especializado |
|--------|----------------|---------------------|
| `convert_normativas.py` | Motor Docling + OCR + Hierarchical Chunking | Este SKILL.md |
| `legalizer.py` | Jerarquía legal (Títulos/Capítulos) | `JullBrain-legalizer/SKILL.md` |
| `metadata_extractor.py` | YAML frontmatter + SHA-256 | `JullBrain-metadata/SKILL.md` |
| `validator.py` | Integridad de secuencia | `JullBrain-validator/SKILL.md` |

> **Nota Crítica:** El antiguo módulo `chunker.py` fue eliminado de la arquitectura. El motor de chunking se realiza mediante `docling.chunking.HierarchicalChunker` directamente en el orquestador `convert_normativas.py`.

---

## Integración Exclusiva con RAGFlow

Todo el pipeline está diseñado EXCLUSIVAMENTE para que la salida sea consumida por **RAGFlow**. 
No diseñes para LangChain, LlamaIndex o LanceDB a menos que se indique lo contrario. El JSON generado por `HierarchicalChunker` cumple con la estructura esperada para el motor nativo de ingesta vectorial de RAGFlow.

---

## Flujo de Decisión para Nuevos PDFs

```
¿El PDF ya está en normativas_rag/ y normativas_chunks/?
  ├─ Sí, sin cambios → Saltar (caché SHA-256 activa)
  ├─ Sí, modificado → Usar --force-reprocess
  └─ NO → Continuar con el flujo normal
```

---

## Comandos de Referencia Rápida

El proyecto usa `Docker Compose`. No se recomienda usar entornos virtuales locales.

```cmd
# Construcción inicial de la imagen
docker compose build jullbrain

# Ejecución interactiva (menú) o ejecución automática si no hay TTY
docker compose run --rm jullbrain

# Ejecutar comandos específicos dentro del contenedor
docker compose run --rm jullbrain python convert_normativas.py --file-path "ley.pdf" --no-ocr

# Forzar reprocesado (ignorar caché)
docker compose run --rm jullbrain python convert_normativas.py --force-reprocess
```

---

## Formato de Salida Esperado

La salida consta de dos componentes:
1. **Archivo Maestro MD**: Se genera en `normativas_rag/nombre-de-la-ley.md`. Contiene la versión completa legalizada con metadatos.
2. **Hierarchical Chunks**: Se generan en `normativas_chunks/nombre-de-la-ley/hierarchical_chunks.json`. Contiene un arreglo JSON donde cada objeto es un bloque semántico con sus metadatos (bounding box, página, path) extraído directamente por el motor IA de IBM Docling, formateado para inyectar en RAGFlow.
