# IBM Docling — Guía de Troubleshooting para QUIBOR

## Instalación y Entorno Virtual

```cmd
:: Crear entorno virtual (solo la primera vez)
python -m venv docling_env

:: Activar entorno
docling_env\Scripts\activate

:: Instalar dependencias principales
pip install docling
pip install pytesseract easyocr
pip install pyyaml rich

:: Verificar Docling disponible
python -c "from docling.document_converter import DocumentConverter; print('OK')"
```

## Tesseract OCR en Windows

Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
Instalar en: `C:\Program Files\Tesseract-OCR\`
Agregar al PATH o configurar en el script:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Errores Conocidos de Docling

### `RuntimeError: CUDA out of memory`
Reducir el tamaño del batch de 15 a 8 páginas en `convert_normativas.py`:
```python
BATCH_SIZE = 8  # Reducir si hay problemas de memoria GPU
```

### `FileNotFoundError: poppler not found`
Instalar poppler vía Chocolatey (requiere admin):
```cmd
choco install poppler
```

### OCR produce texto ilegible (caracteres aleatorios)
El PDF probablemente tiene capas de imagen de baja resolución.
Intentar con EasyOCR como primario:
```python
# En convert_normativas.py, forzar EasyOCR
pipeline_options = PdfPipelineOptions(do_ocr=True, ocr_options=EasyOcrOptions())
```

### Tablas no detectadas correctamente
Activar el modo de detección avanzada de tablas:
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
