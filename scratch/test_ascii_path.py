import sys
import shutil
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker

BASE_DIR = Path(r"c:\VS CODE\CODIGO\JullBrain")
PDF_DELITOS = BASE_DIR / "normativas_pdf" / "Informatica" / "Ley Especial de Delitos informáticos (2001). Publicado en Gaceta Oficial Nº 37.313 .pdf"
PDF_CENIF = BASE_DIR / "normativas_pdf" / "Informatica" / "Creación del CENIF (2012). Centro Nacional de Informática Forense. Publicado en Gaceta Oficial N° 39.847 de fecha 20 de enero..pdf"

converter = DocumentConverter()
chunker = HierarchicalChunker()

def test_with_ascii_name(pdf_path, temp_name):
    print(f"\n======================================")
    print(f"Probando archivo original: {pdf_path.name}")
    if not pdf_path.exists():
        print("¡El archivo original no existe!")
        return
        
    temp_path = BASE_DIR / "scratch" / temp_name
    print(f"Copiando a ruta ASCII temporal: {temp_path}")
    shutil.copy(pdf_path, temp_path)
    
    try:
        print(f"Convirtiendo con Docling usando ruta temporal...")
        result = converter.convert(temp_path)
        doc = result.document
        print("Conversión exitosa.")
        
        print("Generando chunks jerárquicos...")
        doc_chunks = list(chunker.chunk(doc))
        print(f"Número de chunks generados: {len(doc_chunks)}")
    except Exception as e:
        print(f"[ERROR] Falló el proceso: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if temp_path.exists():
            temp_path.unlink()
            print("Archivo temporal eliminado.")

test_with_ascii_name(PDF_DELITOS, "temp_delitos.pdf")
test_with_ascii_name(PDF_CENIF, "temp_cenif.pdf")
