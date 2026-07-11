# IBM Docling â€” GuÃ­a de Troubleshooting para JullBrain

> **Entorno Docker**: JullBrain V2.0 se ejecuta de forma aislada dentro de contenedores de Docker. No necesitas instalar Python, Tesseract ni Poppler localmente en tu sistema anfitriÃ³n. Todo estÃ¡ gestionado internamente en la imagen.

## Errores Conocidos de Docling

### `RuntimeError: CUDA out of memory`
Reducir el tamaÃ±o del batch de 15 a 8 pÃ¡ginas en `convert_normativas.py`:
```python
BATCH_SIZE = 8  # Reducir si hay problemas de memoria GPU
```

### Problemas de OCR en la imagen Docker
Si tienes errores nativos de compilaciÃ³n o OCR al levantar el contenedor, asegÃºrate de que el `Dockerfile` contenga la instalaciÃ³n de Tesseract:
```dockerfile
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-spa poppler-utils
```

### OCR produce texto ilegible (caracteres aleatorios)
El PDF probablemente tiene capas de imagen de baja resoluciÃ³n.
Intentar con EasyOCR como primario en lugar de Tesseract.
```python
# En convert_normativas.py, forzar EasyOCR
pipeline_options = PdfPipelineOptions(do_ocr=True, ocr_options=EasyOcrOptions())
```

### Tablas no detectadas correctamente
Activar el modo de detecciÃ³n avanzada de tablas (si no estÃ¡ activo por defecto):
```python
pipeline_options = PdfPipelineOptions(
    do_table_structure=True,
    table_structure_options=TableStructureOptions(do_cell_matching=True)
)
```

## ConfiguraciÃ³n Ã“ptima por Tipo de PDF

| Tipo de PDF | ConfiguraciÃ³n recomendada | Tiempo estimado |
|------------|--------------------------|-----------------|
| Digital nativo | `--no-ocr` | Muy rÃ¡pido (< 30 seg/100 pÃ¡gs) |
| Escaneado alta calidad | OCR Tesseract | Moderado (2-5 min/100 pÃ¡gs) |
| Escaneado baja calidad | OCR EasyOCR | Lento (5-15 min/100 pÃ¡gs) |
| Mixto (digital + imÃ¡genes) | OCR completo | Moderado-lento |

## Logs y DepuraciÃ³n

Activar logging detallado de Docling:
```python
import logging
logging.getLogger("docling").setLevel(logging.DEBUG)
```

Los logs se guardan en `.conversion_cache/conversion.log` si el script los dirige ahÃ­.
