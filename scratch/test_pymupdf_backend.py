import sys
from pathlib import Path

# Intentar importar el backend de PyMuPDF para Docling
try:
    from docling.backend.pymupdf_backend import PyMuPdfDocumentBackend
    print("[OK] PyMuPdfDocumentBackend importado con éxito.")
except ImportError as e:
    print(f"[-] No se pudo importar PyMuPdfDocumentBackend: {e}")
    try:
        from docling.backend.pdfium_backend import PyPdfiumDocumentBackend
        print("[OK] PyPdfiumDocumentBackend importado.")
    except ImportError:
        pass
