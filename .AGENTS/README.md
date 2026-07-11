# JullBrain V-2.0 â€” Pipeline RAG de Normativas Legales Venezolanas

> ConversiÃ³n automatizada de PDFs jurÃ­dicos a Markdown estructurado y JSON para sistemas de IA â€” Powered by IBM Docling & Docker

[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://docker.com) [![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE) [![IBM Docling](https://img.shields.io/badge/IBM-Docling-purple)](https://github.com/DS4SD/docling)

---

## El Problema que Resuelve

Los modelos de lenguaje (LLM) fallan con PDFs de documentos legales venezolanos porque:

- Los artÃ­culos aparecen fusionados en pÃ¡rrafos de 2,000+ palabras sin separaciÃ³n.
- Las tablas de PDFs se rompen o pierden su estructura.
- No hay metadata legal (Gaceta Oficial, fecha, tipo de instrumento) para filtrar bÃºsquedas RAG.
- El chunking tradicional parte artÃ­culos a la mitad, generando fragmentos incoherentes.

**JullBrain** soluciona esto usando el `HierarchicalChunker` nativo de IBM Docling integrado en una arquitectura Dockerizada, logrando extraer fragmentos semÃ¡nticos inteligentes con metadata completa.

---

## Arquitectura del Pipeline (V2.0)

```
normativas_pdf/
       â”‚
       â–¼
[Contenedor Docker: jullbrain] â†  EjecuciÃ³n aislada (No requiere Python local)
       â”‚
       â”œâ”€â”€ [convert_normativas.py] â†  Docling + OCR
       â”‚
       â”œâ”€â”€ [legalizer.py]          â†  EstructuraciÃ³n jerÃ¡rquica previa (TÃ TULOS, CAPÃ TULOS)
       â”‚
       â””â”€â”€ [HierarchicalChunker]   â†  GeneraciÃ³n semÃ¡ntica de JSON chunks
       â”‚
       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” 
       â–¼                                                              â–¼
normativas_rag/                                          normativas_chunks/
  ley-completa.md                                          ley/hierarchical_chunks.json
  (Markdown + YAML + TOC)                                  (Vectores listos para RAGFlow)
```

---

## MÃ³dulos del Sistema

| MÃ³dulo | FunciÃ³n | Skill de IA Asociado |
|--------|---------|----------------------|
| `convert_normativas.py` | Motor principal: Docling + OCR + HierarchicalChunker | `jullbrain-pdf-to-rag` |
| `legalizer.py` | Detecta TÃ TULO/CAPÃ TULO/ArtÃ­culo para guiar al chunker | `jullbrain-legalizer` |
| `metadata_extractor.py` | YAML frontmatter con Gaceta, fecha, tipo, SHA-256 | `jullbrain-metadata` |
| `validator.py` | Verifica secuencia, duplicados, artÃ­culos corruptos | `jullbrain-validator` |
| `iniciar_conversion.bat`| Orquestador Docker (Auto-instala Chocolatey/Docker) | `jullbrain-pdf-to-rag` |

> **NOTA IMPORTANTE**: El antiguo mÃ³dulo `chunker.py` fue deprecado y eliminado en favor del `HierarchicalChunker` nativo de Docling.

---

## Funciones Avanzadas

**DockerizaciÃ³n Total** â€” Se acabaron los problemas de dependencias en Windows o Mac. Todo el repositorio se empaqueta en una imagen limpia de Python 3.12 con Tesseract preconfigurado.

**Hierarchical Chunking** â€” IntegraciÃ³n nativa con el motor de fragmentaciÃ³n de IBM Docling, generando salidas en `JSON` con bounding boxes, jerarquÃ­a y categorÃ­as detectadas por IA.

**RecuperaciÃ³n automÃ¡tica de fallos** â€” Si un lote falla con OCR activo, el sistema reintenta automÃ¡ticamente sin OCR en ese lote.

---

## InstalaciÃ³n y EjecuciÃ³n

Todo el sistema es autogestionado mediante scripts por lotes. 

> **EjecuciÃ³n Recomendada**:
> Simplemente haz doble clic en `iniciar_conversion.bat` en tu computadora. 
> 
> El script solicitarÃ¡ permisos de administrador e instalarÃ¡ automÃ¡ticamente `Chocolatey` y `Docker Desktop` si no estÃ¡n presentes. Finalmente, compilarÃ¡ y ejecutarÃ¡ el contenedor de JullBrain procesando los PDFs.

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
â”œâ”€â”€ normativas_pdf/              [ENTRADA]   PDFs originales
â”œâ”€â”€ normativas_rag/              [SALIDA]    Markdown completo por ley (YAML + TOC)
â”œâ”€â”€ normativas_chunks/           [SALIDA]    JSON (hierarchical_chunks.json) para RAGFlow
â”œâ”€â”€ .conversion_cache/           [SISTEMA]   CachÃ© SHA-256
â”œâ”€â”€ docker-compose.yml           [SISTEMA]   ConfiguraciÃ³n del contenedor y volÃºmenes
â”œâ”€â”€ Dockerfile                   [SISTEMA]   Receta de la imagen base (tesseract + dependencias)
â”‚
â”œâ”€â”€ convert_normativas.py        Motor principal + Hierarchical Chunking
â”œâ”€â”€ legalizer.py                 JerarquÃ­a legal
â”œâ”€â”€ metadata_extractor.py        YAML frontmatter + metadata legal
â”œâ”€â”€ validator.py                 ValidaciÃ³n de integridad
â”œâ”€â”€ iniciar_conversion.bat       Orquestador interactivo (Auto-instalador Docker)
â”‚
â””â”€â”€ .AGENTS/                     [IA]        Skills de asistencia de IA (jullbrain-*)
```
