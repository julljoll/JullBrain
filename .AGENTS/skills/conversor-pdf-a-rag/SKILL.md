---
name: JullBrain-conversor-pdf-a-rag
description: Pipeline maestro para convertir PDFs de leyes y normativas venezolanas en Markdown estructurado y JSON utilizando exclusivamente tecnología IBM (IBM Docling en CPU + IBM Granite Embedding R2 + IBM Granite Guardian). Úsalo siempre que el usuario mencione convertir PDFs legales, procesar normativas en la carpeta RAG/, optimizar Docling en CPU, generar chunks de artículos, o depurar convert_normativas.py, gpu_detector.py u orquestador.py.
---

# 📄 JullBrain — Conversor PDF a RAG con Tecnología IBM (`convert_normativas.py`)

Este skill gobierna el pipeline central de conversión documental de **JullBrain v0.2.0** operado desde **Google Antigravity**.

---

## 1. Arquitectura del Núcleo `RAG/` y Ejecución CPU-First

En **JullBrain v0.2.0**, toda la información y los modelos de IA residen dentro del directorio `RAG/`:

| Ruta en el Repositorio | Propósito |
| :--- | :--- |
| `RAG/datos_brutos/` | Entrada de documentos originales (PDFs de Gacetas Oficiales, leyes, códigos y `Formatos_Word/`). |
| `RAG/Informacion_docling_rag/` | Salida de documentos `.md` completos (con encabezado canónico + YAML frontmatter) y `.json` crudos de Docling. |
| `RAG/normativas_chunks/` | Salida de `*_chunks.json` jerárquicos enriquecidos con vectores `ibm-granite/granite-embedding-english-r2` (`768` dims). |
| `RAG/modelos_ia/` | Bóveda local criptográfica de modelos IA (`docling/`, `granite_embeddings/`, `granite_llm/`, `granite_guardian/`, `huggingface/`, `torch/`, `ollama/`). |

### Optimización de `IBM Docling` en Procesador (CPU)
Dado que `IBM Docling` se ejecuta en **CPU**, [`convert_normativas.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/convert_normativas.py) y [`gpu_detector.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/gpu_detector.py) aplican:
1. Detección automática de núcleos físicos y lógicos (`configurar_entorno_cpu_docling()`), asignando el número óptimo de hilos (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `TORCH_NUM_THREADS`).
2. Configuración explícita de `AcceleratorOptions(num_threads=cpu_threads, device=AcceleratorDevice.CPU)` en `PdfPipelineOptions`.
3. Carga de pesos neuronales de layout y TableFormer desde la bóveda local `RAG/modelos_ia/docling` (`artifacts_path`), evitando descargas repetitivas y permitiendo operación 100% *Air-Gapped*.

---

## 2. Flujo de Procesamiento Seguro por Documento

1. **Validación Forense de Magic Bytes (`%PDF-`)**:
   - Antes de abrir cualquier PDF con Docling, se invoca `validate_pdf_magic_bytes(pdf_path)` de [`audit_logger.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/audit_logger.py) para descartar archivos corruptos o payloads disfrazados.
2. **Conversión con `IBM Docling` (Con Fallback Resiliente)**:
   - Convierte el PDF por lotes de páginas con OCR selectivo; si un lote falla con OCR, reintenta automáticamente sin OCR (`converter_no_ocr`) sin abortar la ley completa.
3. **Estructuración Jerárquica (`legalizer.py`) y Metadata (`metadata_extractor.py`)**:
   - Aplica jerarquía legal venezolana (`TÍTULO` -> `CAPÍTULO` -> `Artículo`), genera el YAML frontmatter con SHA-256 y antepone el encabezado canónico oficial (sin pie de página).
4. **Fragmentación (`HierarchicalChunker`) + Embeddings (`IBM Granite Embedding R2`)**:
   - Genera los chunks atómicos y los vectoriza localmente con [`granite_embedder.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_embedder.py).
5. **Doble Validación Cruzada (`validator.py`) + Auditoría `HMAC-SHA256`**:
   - Contrasta el conteo de artículos en Markdown contra el PDF original vía PyMuPDF (`cross_validate_against_pdf()`) y registra el evento firmado en `audit_logger.py`.

---

## 3. Comandos Clave del Pipeline

```powershell
# 1. Descargar y sellar con SHA-256 los modelos de IBM Docling y Granite en RAG/modelos_ia/
python convert_normativas.py --bootstrap-models

# 2. Procesar todo el corpus en RAG/datos_brutos/
python convert_normativas.py

# 3. Forzar reprocesamiento ignorando caché SHA-256
python convert_normativas.py --force
```
