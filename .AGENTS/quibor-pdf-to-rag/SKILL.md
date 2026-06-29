---
name: quibor-pdf-to-rag
description: >
  Pipeline maestro para convertir PDFs de leyes y normativas venezolanas en Markdown estructurado
  listo para sistemas RAG/LLM. Úsalo siempre que el usuario mencione: convertir PDFs legales,
  procesar normativas, estructurar leyes para IA, generar chunks de artículos, ejecutar QUIBOR,
  problemas con IBM Docling, errores en legalizer.py, chunker.py, metadata_extractor.py o
  validator.py. También aplica cuando el usuario quiere mejorar, depurar o extender cualquier
  componente del pipeline. Trigger agresivo: si la conversación involucra documentos jurídicos
  venezolanos + IA/RAG, consulta este skill antes de responder.
compatibility:
  python: ">=3.10"
  tools: [bash_tool, create_file, str_replace, view]
  dependencies:
    - docling
    - tesseract-ocr
    - easyocr
    - pyyaml
    - rich
    - hashlib (stdlib)
---

# QUIBOR V-1.0 — Skill Maestro del Pipeline PDF → RAG

## Arquitectura del Sistema

```
normativas_pdf/   →   [IBM Docling]   →   [legalizer.py]   →   [metadata_extractor.py]
                                                ↓                        ↓
                                         [validator.py]   →   [chunker.py]
                                                                         ↓
                                         normativas_rag/   +   normativas_chunks/
```

## Módulos del Pipeline

| Módulo | Responsabilidad | Skill especializado |
|--------|----------------|---------------------|
| `convert_normativas.py` | Motor Docling + OCR + batching | Este SKILL.md |
| `legalizer.py` | Jerarquía legal, separación artículos | `quibor-legalizer/SKILL.md` |
| `metadata_extractor.py` | YAML frontmatter + SHA-256 | `quibor-metadata/SKILL.md` |
| `validator.py` | Integridad de secuencia | `quibor-validator/SKILL.md` |
| `chunker.py` | Un `.md` por artículo | `quibor-legalizer/SKILL.md` |

> **Regla de routing**: Si el problema es específico de un módulo, carga el skill especializado.
> Si es un problema de integración, configuración general o nuevo PDF, trabaja desde aquí.

---

## Flujo de Decisión para Nuevos PDFs

```
¿El PDF ya está en normativas_rag/?
  ├─ SÍ, sin cambios → Saltar (caché SHA-256 activa)
  ├─ SÍ, modificado → Usar --force-reprocess
  └─ NO → Continuar con el flujo normal

¿El PDF es digital nativo (no escaneado)?
  ├─ SÍ → Usar --no-ocr (5× más rápido)
  └─ NO → OCR completo con Tesseract + fallback EasyOCR

¿El PDF tiene más de 100 páginas?
  ├─ SÍ → El batching automático (15 págs/lote, 3 threads) ya lo cubre
  └─ NO → Procesamiento directo en un solo paso
```

---

## Comandos de Referencia Rápida

```cmd
# Conversión completa (OCR + legalizer + metadata + chunks)
docling_env\Scripts\python.exe convert_normativas.py

# PDF específico, nativo digital
docling_env\Scripts\python.exe convert_normativas.py --file-path "ley.pdf" --no-ocr

# Forzar reprocesado (ignorar caché)
docling_env\Scripts\python.exe convert_normativas.py --force-reprocess

# Solo re-estructurar (sin volver a correr Docling)
docling_env\Scripts\python.exe convert_normativas.py --post-process-only

# Validar todos los documentos procesados
docling_env\Scripts\python.exe validator.py normativas_rag

# Generar chunks manualmente para un .md existente
docling_env\Scripts\python.exe chunker.py "normativas_rag/ley.md"
```

---

## Diagnóstico de Errores Comunes

### Error: `UnicodeEncodeError` al procesar español
**Causa**: Stdout no configurado en UTF-8 (Windows).
**Solución**: Agregar al inicio de cualquier script Python del proyecto:
```python
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
```

### Error: Docling falla en lote específico
**Comportamiento esperado**: El sistema reintenta sin OCR ese lote automáticamente.
Si el error persiste, consultar `references/docling-troubleshooting.md`.

### Artículos fusionados / mal separados
**Causa**: El regex de `legalizer.py` no cubre el patrón del nuevo documento.
**Acción**: Cargar `quibor-legalizer/SKILL.md` para ampliar los patrones.

### Caché desactualizada / resultados viejos
```cmd
del .conversion_cache\manifest.json
:: o usar la flag:
convert_normativas.py --force-reprocess
```

---

## Formato de Salida Esperado

### `normativas_rag/ley.md` (documento completo)
```markdown
---
tipo_instrumento: "Código"
nombre_oficial: "Código Penal de Venezuela"
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"
articulos_detectados: 640
categorias: ["penal"]
hash_pdf_sha256: "abc123..."
---

## TÍTULO I - De la aplicación de la Ley Penal

### ÍNDICE DE ARTÍCULOS
| Art. | Descripción | Ubicación |
...

###### Artículo 1 - Principio de Legalidad
Nadie podrá ser castigado...
```

### `normativas_chunks/ley/articulo_0001.md` (chunk individual)
```markdown
---
ley: "Código Penal de Venezuela"
articulo: 1
ubicacion: "TÍTULO I - De la aplicación de la Ley Penal"
gaceta_oficial: "5.494 Extraordinario"
fecha_publicacion: "2000-10-20"
hash_pdf_sha256: "abc123..."
---

# Artículo 1 — Principio de Legalidad
**Ley:** Código Penal de Venezuela
**Ubicación:** TÍTULO I

Nadie podrá ser castigado por un hecho que no estuviere...
```

---

## Extensión: Soporte de Nuevos Formatos Legales

Para documentos ISO/NIST con numeración por secciones (no artículos):
→ Ver `references/section-numbering-extension.md` para implementar el parser alternativo.

Para leyes con tablas complejas:
→ Docling las extrae automáticamente. Verificar en el .md de salida que las tablas estén en formato Markdown válido.

---

## Calidad RAG: Métricas de Referencia

| Documento | Artículos detectados | Chunks | Tasa de éxito |
|-----------|---------------------|--------|--------------|
| Código Penal (640 arts.) | 640 | 629 | 98.3% |
| COPP (355 arts.) | 355 | 353 | 99.4% |
| Ley Delitos Informáticos (35 arts.) | 35 | 35 | 100% |
| Ley Mensajes de Datos (56 arts.) | 56 | 55 | 98.2% |
| Creación CENIF (74 arts.) | 74 | 74 | 100% |

**Umbral de alerta**: Si la tasa de chunks/artículos cae por debajo del 95%, ejecutar `validator.py` y revisar los patrones en `legalizer.py`.
