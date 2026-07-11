---
name: JullBrain-pdf-to-rag
description: >
  Pipeline maestro para convertir PDFs de leyes y normativas venezolanas en Markdown estructurado y JSON.
  Ãšsalo siempre que el usuario mencione: convertir PDFs legales,
  procesar normativas, estructurar leyes para IA, generar chunks de artÃ­culos, ejecutar JullBrain,
  problemas con IBM Docling, errores en legalizer.py, metadata_extractor.py o
  validator.py. TambiÃ©n aplica cuando el usuario quiere mejorar, depurar o extender cualquier
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

# JullBrain V-2.0 â€” Skill Maestro del Pipeline PDF â†’ RAG (Docker + Hierarchical Chunking)

## Arquitectura del Sistema

```
normativas_pdf/   â†’   [Contenedor Docker jullbrain]   
                           â†“ (IBM Docling)
                      [legalizer.py] (EstructuraciÃ³n de TÃ­tulos/CapÃ­tulos)
                           â†“
                      [metadata_extractor.py]
                           â†“
                      [validator.py]
                           â†“
                      [HierarchicalChunker]
                           â†“
           normativas_rag/   +   normativas_chunks/
           (Markdown completo)   (hierarchical_chunks.json)
```

## MÃ³dulos del Pipeline

| MÃ³dulo | Responsabilidad | Skill especializado |
|--------|----------------|---------------------|
| `convert_normativas.py` | Motor Docling + OCR + Hierarchical Chunking | Este SKILL.md |
| `legalizer.py` | JerarquÃ­a legal (TÃ­tulos/CapÃ­tulos) | `JullBrain-legalizer/SKILL.md` |
| `metadata_extractor.py` | YAML frontmatter + SHA-256 | `JullBrain-metadata/SKILL.md` |
| `validator.py` | Integridad de secuencia | `JullBrain-validator/SKILL.md` |

> **Nota CrÃ­tica:** El antiguo mÃ³dulo `chunker.py` fue eliminado de la arquitectura. El motor de chunking se realiza mediante `docling.chunking.HierarchicalChunker` directamente en el orquestador `convert_normativas.py`.

---

## Flujo de DecisiÃ³n para Nuevos PDFs

```
Â¿El PDF ya estÃ¡ en normativas_rag/ y normativas_chunks/?
  â”œâ”€ SÃ , sin cambios â†’ Saltar (cachÃ© SHA-256 activa)
  â”œâ”€ SÃ , modificado â†’ Usar --force-reprocess
  â””â”€ NO â†’ Continuar con el flujo normal
```

---

## Comandos de Referencia RÃ¡pida

El proyecto usa `Docker Compose`. No se recomienda usar entornos virtuales locales.

```cmd
# ConstrucciÃ³n inicial de la imagen
docker compose build jullbrain

# EjecuciÃ³n interactiva (menÃº) o ejecuciÃ³n automÃ¡tica si no hay TTY
docker compose run --rm jullbrain

# Ejecutar comandos especÃ­ficos dentro del contenedor
docker compose run --rm jullbrain python convert_normativas.py --file-path "ley.pdf" --no-ocr

# Forzar reprocesado (ignorar cachÃ©)
docker compose run --rm jullbrain python convert_normativas.py --force-reprocess
```

---

## Formato de Salida Esperado

La salida consta de dos componentes:
1. **Archivo Maestro MD**: Se genera en `normativas_rag/nombre-de-la-ley.md`. Contiene la versiÃ³n completa legalizada con metadatos.
2. **Hierarchical Chunks**: Se generan en `normativas_chunks/nombre-de-la-ley/hierarchical_chunks.json`. Contiene un arreglo JSON donde cada objeto es un bloque semÃ¡ntico con sus metadatos (bounding box, pÃ¡gina, path) extraÃ­do directamente por el motor IA de IBM Docling.
