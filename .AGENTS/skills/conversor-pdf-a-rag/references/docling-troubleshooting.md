# IBM Docling (CPU) — Guía de Troubleshooting para JullBrain v0.2.0

> **Entorno Local y Podman**: JullBrain v0.2.0 ejecuta `IBM Docling` en procesador (**CPU**) con afinidad dinámica de hilos (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`) y almacena sus modelos localmente en `RAG/modelos_ia/docling`.

## 1. Optimización de Rendimiento en CPU

En [`convert_normativas.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/convert_normativas.py), `PdfPipelineOptions` utiliza `AcceleratorOptions` apuntando explícitamente a `AcceleratorDevice.CPU`:

```python
from docling.datamodel.pipeline_options import AcceleratorDevice, AcceleratorOptions, PdfPipelineOptions

pipeline_options = PdfPipelineOptions(
    do_ocr=True,
    do_table_structure=True,
    artifacts_path=Path("RAG/modelos_ia/docling"),
    accelerator_options=AcceleratorOptions(
        num_threads=cpu_threads,
        device=AcceleratorDevice.CPU,
    ),
)
```

## 2. Problemas Frecuentes y Soluciones

### 1. Descarga bloqueada en modo Air-Gapped (`HF_HUB_OFFLINE=1`)
Asegúrate de aprovisionar previamente la bóveda local ejecutando:
```powershell
python convert_normativas.py --bootstrap-models
```
Esto descarga los artefactos de layout y TableFormer de `IBM Docling` en `RAG/modelos_ia/docling` y los sella con `SHA-256` en `RAG/modelos_ia/vault_manifest_sha256.json`.

### 2. Uso elevado de RAM en PDFs de más de 200 páginas
Ajusta `"batch_size_pages"` en [`pipeline_config.json`](file:///c:/VS%20CODE/CODIGO/JullBrain/pipeline_config.json) (por defecto `15` páginas por lote).

### 3. Fallo de OCR en páginas escaneadas deterioradas
El pipeline incluye recuperación automática por lote: si `converter.convert()` falla con OCR activo, reintenta ese lote con `converter_no_ocr` sin abortar el documento completo.
