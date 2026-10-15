import sys
from pathlib import Path
import fitz  # PyMuPDF
from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker

BASE_DIR = Path(r"c:\VS CODE\CODIGO\JullBrain")
PDF_DELITOS = BASE_DIR / "normativas_pdf" / "Informatica" / "Ley Especial de Delitos informáticos (2001). Publicado en Gaceta Oficial Nº 37.313 .pdf"
PDF_CENIF = BASE_DIR / "normativas_pdf" / "Informatica" / "Creación del CENIF (2012). Centro Nacional de Informática Forense. Publicado en Gaceta Oficial N° 39.847 de fecha 20 de enero..pdf"

converter = DocumentConverter()
chunker = HierarchicalChunker()

def repair_pdf(pdf_path: Path) -> Path:
    repaired_path = pdf_path.parent / f"_repaired_{pdf_path.name}"
    print(f"Intentando reparar {pdf_path.name} usando PyMuPDF (fitz)...")
    try:
        doc = fitz.open(pdf_path)
        doc.save(repaired_path, garbage=4, deflate=True, clean=True)
        doc.close()
        print(f"Reparación exitosa. Guardado en: {repaired_path.name}")
        return repaired_path
    except Exception as e:
        print(f"Error reparando PDF con fitz: {e}")
        return None

def test_file(pdf_path):
    print(f"\n======================================")
    print(f"Probando archivo: {pdf_path.name}")
    if not pdf_path.exists():
        print("¡El archivo PDF no existe!")
        return
        
    # Intentar reparar primero
    repaired = repair_pdf(pdf_path)
    path_to_use = repaired if repaired else pdf_path
    
    try:
        print(f"Convirtiendo con Docling usando {path_to_use.name}...")
        result = converter.convert(path_to_use)
        doc = result.document
        print("Conversión exitosa.")
        
        print("Generando chunks jerárquicos...")
        doc_chunks = list(chunker.chunk(doc))
        print(f"Número de chunks generados: {len(doc_chunks)}")
        
        # Eliminar archivo reparado de prueba
        if repaired and repaired.exists():
            repaired.unlink()
            print("Archivo temporal reparado eliminado.")
    except Exception as e:
        print(f"[ERROR] Falló el proceso: {e}")
        import traceback
        traceback.print_exc()

# Probar los dos archivos con problemas
test_file(PDF_DELITOS)
test_file(PDF_CENIF)
