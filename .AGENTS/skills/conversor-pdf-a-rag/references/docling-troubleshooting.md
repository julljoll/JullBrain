# IBM Docling — Guía de Troubleshooting para JullBrain

> **Entorno Docker**: JullBrain V2.0 se ejecuta de forma aislada dentro de contenedores de Docker. No necesitas instalar Python, Tesseract ni Poppler localmente en tu sistema anfitrión. Todo está gestionado internamente en la imagen.

## Errores Conocidos de Docling

### `RuntimeError: CUDA out of memory`
Reducir el tamaño del batch de 15 a 8 páginas en `convert_normativas.py`:
```python
BATCH_SIZE = 8  # Reducir si hay problemas de memoria GPU
```

### Problemas de OCR en la imagen Docker
Si tienes errores nativos de compilación o OCR al levantar el contenedor, asegúrate de que el `Dockerfile` contenga la instalación de Tesseract:
```dockerfile
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-spa poppler-utils
```

### OCR produce texto ilegible (caracteres aleatorios)
El PDF probablemente tiene capas de imagen de baja resolución.
Intentar con EasyOCR como primario en lugar de Tesseract.
```python
# En convert_normativas.py, forzar EasyOCR
pipeline_options = PdfPipelineOptions(do_ocr=True, ocr_options=EasyOcrOptions())
```

### Tablas no detectadas correctamente
Activar el modo de detección avanzada de tablas (si no está activo por defecto):
```python
pipeline_options = PdfPipelineOptions(
    do_table_structure=True,
    table_structure_options=TableStructureOptions(do_cell_matching=True)
)
```

## Configuración Óptima por Tipo de PDF

| Tipo de PDF | Configuración recomendada | Tiempo estimado |
|------------|--------------------------|-----------------|
| Digital nativo | `--no-ocr` | Muy rápido (< 30 seg/100 págs) |
| Escaneado alta calidad | OCR Tesseract | Moderado (2-5 min/100 págs) |
| Escaneado baja calidad | OCR EasyOCR | Lento (5-15 min/100 págs) |
| Mixto (digital + imágenes) | OCR completo | Moderado-lento |

## Logs y Depuración

Activar logging detallado de Docling:
```python
import logging
logging.getLogger("docling").setLevel(logging.DEBUG)
```

Los logs se guardan en `.conversion_cache/conversion.log` si el script los dirige ahí.
