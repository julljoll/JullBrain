import os
import sys
import logging
import argparse
import subprocess
import tempfile
import gc
from pathlib import Path
import pypdf
import fitz

# Configurar el registro de eventos (logging) para ver el progreso detallado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("convert_normativas")

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling_core.types.doc import DoclingDocument
except ImportError as e:
    logger.error("No se pudo importar Docling. Asegúrate de activar el entorno virtual correcto e instalar 'docling'.")
    logger.error(f"Detalle del error: {e}")
    sys.exit(1)

# Rutas predeterminadas (usando rutas absolutas según lo requerido)
INPUT_DIR = Path(r"D:\VS CODE\IBM DOCLING\normativas_pdf")
OUTPUT_DIR = Path(r"D:\VS CODE\IBM DOCLING\normativas_rag")
CACHE_DIR = Path(r"D:\VS CODE\IBM DOCLING\.conversion_cache")

# Cabecera de derechos de autor y licencia (MIT)
HEADER_TEMPLATE = """# 🏛️ PROCESAMIENTO ESTRUCTURADO DE NORMATIVAS Y LEYES

> [!NOTE]
> **DERECHOS DE AUTOR Y LICENCIA MIT**
>
> Este archivo de texto estructurado ha sido generado y optimizado automáticamente para su consumo por sistemas de Inteligencia Artificial (RAG).
> 
> * **Creador:** Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales)
> * **Propósito:** Avanzar en la transformación tecnológica del sistema de justicia venezolano.
> * **Licencia:** MIT License
> * **Copyright (c) 2026 Jull Ortiz**
>
> Se concede permiso por la presente, sin cargo, a cualquier persona que obtenga una copia de este software y de los archivos de documentación asociados, para utilizarlo sin restricciones, incluyendo el derecho a usar, copiar, modificar, fusionar y publicar. El aviso de copyright anterior y este aviso de permiso se incluirán en todas las copias o partes sustanciales del archivo.

---

"""

# Pie de página de derechos de autor y licencia (MIT)
FOOTER_TEMPLATE = """

---

> [!IMPORTANT]
> **FIN DEL DOCUMENTO ESTRUCTURADO**
>
> Generado bajo la Licencia MIT.
> **Autor:** Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales) | *Impulsando la transformación tecnológica del sistema de justicia venezolano (2026)*
"""

def main():
    parser = argparse.ArgumentParser(description="Convertidor de Normativas RAG - IBM Docling")
    parser.add_argument("--chunk-mode", action="store_true", help="Ejecuta la conversión de un fragmento de PDF/imagen en subproceso.")
    parser.add_argument("--file-path", type=str, help="Ruta del archivo a convertir.")
    parser.add_argument("--start", type=int, help="Página de inicio (1-based, inclusive).")
    parser.add_argument("--end", type=int, help="Página de fin (1-based, inclusive).")
    parser.add_argument("--output-json", type=str, help="Ruta donde guardar el JSON del documento generado.")
    parser.add_argument("--no-ocr", action="store_true", help="Desactiva el OCR en el procesamiento del PDF.")
    
    args = parser.parse_args()

    # MODO SUBPROCESO (Procesa un solo lote/imagen y guarda el JSON del modelo)
    if args.chunk_mode:
        if not args.file_path or not args.output_json:
            logger.error("Faltan parámetros requeridos para el modo subproceso.")
            sys.exit(1)
            
        file_path = Path(args.file_path)
        output_json = Path(args.output_json)
        
        try:
            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
                pipeline_options = PdfPipelineOptions()
                pipeline_options.do_ocr = not args.no_ocr
                pipeline_options.do_table_structure = True
                
                converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(
                            backend=PyPdfiumDocumentBackend,
                            pipeline_options=pipeline_options
                        )
                    }
                )
                
                page_range = None
                if args.start is not None and args.end is not None:
                    page_range = (args.start, args.end)
                    
                result = converter.convert(file_path, page_range=page_range)
            else:
                # Procesar imagen
                converter = DocumentConverter()
                result = converter.convert(file_path)
                
            result.document.save_as_json(output_json)
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error en subproceso al procesar {file_path.name}: {e}")
            sys.exit(1)

    # MODO ORQUESTRADOR PRINCIPAL
    logger.info("=== INICIANDO SERVICIO DE CONVERSIÓN DE NORMATIVAS ===")
    
    if not INPUT_DIR.exists():
        logger.error(f"La carpeta de origen no existe: {INPUT_DIR}")
        sys.exit(1)
        
    if not OUTPUT_DIR.exists():
        logger.info(f"Creando la carpeta de destino: {OUTPUT_DIR}")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Extensiones soportadas
    extensions = [
        "*.pdf", "*.PDF",
        "*.png", "*.PNG",
        "*.jpg", "*.JPG",
        "*.jpeg", "*.JPEG",
        "*.tiff", "*.TIFF",
        "*.bmp", "*.BMP"
    ]
    
    all_files = []
    for ext in extensions:
        all_files.extend(list(INPUT_DIR.glob(ext)))
        
    # Filtrar temporales y duplicados
    all_files = list(set(all_files))
    all_files = [f for f in all_files if not f.name.startswith("_repaired_") and not f.name.startswith("_temp_")]
    
    if not all_files:
        logger.info(f"No se encontraron archivos PDF ni imágenes en: {INPUT_DIR}")
        logger.info("Terminando proceso sin tareas pendientes.")
        return

    logger.info(f"Se encontraron {len(all_files)} archivos en total.")
    
    # Conversión incremental: excluir los ya convertidos
    pending_files = []
    for file_path in all_files:
        md_filename = f"{file_path.stem}.md"
        md_path = OUTPUT_DIR / md_filename
        if md_path.exists():
            logger.debug(f"Archivo ya convertido: {file_path.name} -> Saltando.")
        else:
            pending_files.append(file_path)
            
    if not pending_files:
        logger.info("Todos los archivos ya han sido convertidos anteriormente. No hay archivos nuevos.")
        return

    logger.info(f"Detectados {len(pending_files)} archivos nuevos para procesar.")
    
    success_count = 0
    fail_count = 0
    
    # Resolver la ruta absoluta del propio script para llamarse a sí mismo en los subprocesos
    script_path = Path(__file__).resolve()
    
    for idx, file_path in enumerate(pending_files, start=1):
        md_filename = f"{file_path.stem}.md"
        output_md_path = OUTPUT_DIR / md_filename
        
        logger.info(f"[{idx}/{len(pending_files)}] Procesando: {file_path.name}...")
        
        try:
            suffix = file_path.suffix.lower()
            
            if suffix == ".pdf":
                # Leer total de páginas
                try:
                    reader = pypdf.PdfReader(file_path)
                    num_pages = len(reader.pages)
                except Exception as e:
                    try:
                        import fitz
                        doc = fitz.open(file_path)
                        num_pages = len(doc)
                        doc.close()
                    except Exception:
                        raise RuntimeError(f"No se pudo determinar el número de páginas: {e}")
                
                logger.info(f"  El PDF tiene {num_pages} páginas.")
                
                # Tamaño de lote de páginas por subproceso
                BATCH_SIZE = 15
                temp_jsons = []
                
                # Directorio de caché persistente para este archivo específico
                file_cache_dir = CACHE_DIR / file_path.stem
                file_cache_dir.mkdir(parents=True, exist_ok=True)
                
                # Generar los argumentos de los lotes de páginas
                batches = []
                for start_page in range(1, num_pages + 1, BATCH_SIZE):
                    end_page = min(start_page + BATCH_SIZE - 1, num_pages)
                    # En lugar de usar la carpeta temporal, usamos la carpeta de caché persistente
                    json_path = file_cache_dir / f"chunk_{start_page}_{end_page}.json"
                    batches.append((start_page, end_page, json_path))
                
                # Filtrar lotes que ya hayan sido convertidos previamente con éxito
                pending_batches = []
                for start_page, end_page, json_path in batches:
                    if json_path.exists():
                        try:
                            # Intentar cargar para verificar integridad del JSON
                            DoclingDocument.load_from_json(json_path)
                            logger.info(f"  [CACHE] Lote páginas {start_page} a {end_page} ya convertido anteriormente. Omitiendo.")
                            temp_jsons.append(json_path)
                        except Exception:
                            logger.warning(f"  [CACHE] Lote páginas {start_page} a {end_page} corrupto. Se volverá a procesar.")
                            pending_batches.append((start_page, end_page, json_path))
                    else:
                        pending_batches.append((start_page, end_page, json_path))
                
                if pending_batches:
                    # Ejecutar los lotes en paralelo usando ThreadPoolExecutor
                    from concurrent.futures import ThreadPoolExecutor, as_completed
                    
                    # Determinar el número de trabajadores basados en los núcleos de CPU
                    MAX_WORKERS = max(1, min(3, os.cpu_count() - 1 if os.cpu_count() else 2))
                    logger.info(f"  -> Iniciando conversión en paralelo con {MAX_WORKERS} hilos para {len(pending_batches)} lotes pendientes...")
                    
                    def process_batch(start_page, end_page, temp_json_path):
                        logger.info(f"  -> [Inicio] Procesando páginas {start_page} a {end_page}...")
                        cmd = [
                            sys.executable,
                            str(script_path),
                            "--chunk-mode",
                            "--file-path", str(file_path),
                            "--start", str(start_page),
                            "--end", str(end_page),
                            "--output-json", str(temp_json_path)
                        ]
                        
                        # Intentar con OCR habilitado
                        res = subprocess.run(cmd, capture_output=True, text=True)
                        
                        if res.returncode != 0:
                            ocr_error = f"STDOUT: {res.stdout.strip()}\nSTDERR: {res.stderr.strip()}"
                            logger.warning(f"  [AVISO] Falló la conversión del lote {start_page}-{end_page} con OCR. Detalle:\n{ocr_error}")
                            logger.warning("  [REINTENTO] Reintentando lote sin OCR...")
                            
                            # Fallback sin OCR
                            cmd_no_ocr = cmd + ["--no-ocr"]
                            res_no_ocr = subprocess.run(cmd_no_ocr, capture_output=True, text=True)
                            
                            if res_no_ocr.returncode != 0:
                                error_msg = f"STDOUT: {res_no_ocr.stdout.strip()}\nSTDERR: {res_no_ocr.stderr.strip()}"
                                raise RuntimeError(f"Fallo crítico en lote {start_page}-{end_page} sin OCR:\n{error_msg}")
                        
                        logger.info(f"  [OK] Lote {start_page}-{end_page} finalizado.")
                        return temp_json_path

                    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                        future_to_batch = {
                            executor.submit(process_batch, start, end, path): (start, end)
                            for start, end, path in pending_batches
                        }
                        
                        for future in as_completed(future_to_batch):
                            start, end = future_to_batch[future]
                            try:
                                json_path = future.result()
                                temp_jsons.append(json_path)
                            except Exception as e:
                                raise RuntimeError(f"Error procesando lote {start}-{end}: {e}")
                
                # Ordenar los JSONs para garantizar el orden secuencial correcto de las páginas
                temp_jsons.sort(key=lambda p: int(p.stem.split('_')[1]))
                
                # Cargar y fusionar los fragmentos en el proceso principal
                logger.info("  Fusing chunks into a single document...")
                docs = []
                for temp_json in temp_jsons:
                    if temp_json.exists():
                        docs.append(DoclingDocument.load_from_json(temp_json))
                        
                if not docs:
                    raise RuntimeError("No se pudieron cargar los fragmentos JSON temporales.")
                    
                merged_doc = DoclingDocument.concatenate(docs)
                markdown_content = merged_doc.export_to_markdown()
                
                # Limpiar carpeta de caché si la conversión fue exitosa
                try:
                    import shutil
                    shutil.rmtree(file_cache_dir)
                    logger.info(f"  [CACHE] Carpeta de caché temporal eliminada con éxito: {file_cache_dir.name}")
                except Exception as e:
                    logger.warning(f"  [AVISO] No se pudo limpiar la carpeta de caché {file_cache_dir.name}: {e}")
                    
            else:
                # Es una imagen
                logger.info("  Procesando imagen en subproceso...")
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_json_path = Path(temp_dir) / "image_doc.json"
                    cmd = [
                        sys.executable,
                        str(script_path),
                        "--chunk-mode",
                        "--file-path", str(file_path),
                        "--output-json", str(temp_json_path)
                    ]
                    
                    res = subprocess.run(cmd, capture_output=True, text=True)
                    if res.returncode != 0:
                        error_msg = f"STDOUT: {res.stdout.strip()}\nSTDERR: {res.stderr.strip()}"
                        raise RuntimeError(f"Fallo convirtiendo imagen:\n{error_msg}")
                        
                    if not temp_json_path.exists():
                        raise RuntimeError("El subproceso no generó el JSON intermedio de la imagen.")
                        
                    img_doc = DoclingDocument.load_from_json(temp_json_path)
                    markdown_content = img_doc.export_to_markdown()

            # Ensamble final
            final_content = HEADER_TEMPLATE + markdown_content + FOOTER_TEMPLATE
            
            with open(output_md_path, "w", encoding="utf-8") as f:
                f.write(final_content)
                
            logger.info(f"[ÉXITO] Convertido y guardado en: {md_filename}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"[FALLO] Error al procesar {file_path.name}: {str(e)}")
            fail_count += 1
            # Limpiar archivo markdown parcial o corrupto si se creó
            if output_md_path.exists():
                try:
                    output_md_path.unlink()
                except Exception:
                    pass
                    
        # Invocar recolección de basura para limpiar memoria en el proceso principal
        gc.collect()

    logger.info("=== PROCESAMIENTO FINALIZADO ===")
    logger.info(f"Resumen: {success_count} exitosos, {fail_count} fallidos de {len(pending_files)} archivos procesados.")

if __name__ == "__main__":
    main()
