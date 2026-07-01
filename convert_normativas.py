import os
import sys
import logging
import argparse
import subprocess
import tempfile
import gc
import hashlib
import json
from pathlib import Path
import pypdf
import fitz

# Modulos de post-procesamiento legal (Fases 1-5)
try:
    from legalizer import legalize
    from metadata_extractor import inject_frontmatter, sha256_file, load_manifest, save_manifest
    from validator import validate_md_file
    from chunker import chunk_file
    LEGAL_PIPELINE_AVAILABLE = True
except ImportError as _le:
    LEGAL_PIPELINE_AVAILABLE = False
    _legal_import_error = str(_le)

# Reconfigurar la salida estándar y de error para usar UTF-8 y evitar errores de codificación en Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Rich imports para interfaz elegante
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.text import Text
from rich import box
from rich.logging import RichHandler

# Configurar el registro de eventos (logging) para ver el progreso detallado
if "--chunk-mode" in sys.argv:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    console = None
else:
    console = Console(style="on #252525")
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_path=False, rich_tracebacks=True)]
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

# Rutas predeterminadas (usando rutas dinámicas relativas al directorio del script)
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR   = BASE_DIR / "normativas_pdf"
OUTPUT_DIR  = BASE_DIR / "normativas_rag"
CACHE_DIR   = BASE_DIR / ".conversion_cache"
CHUNKS_DIR  = BASE_DIR / "normativas_chunks"
MANIFEST_PATH = CACHE_DIR / "manifest.json"

WORD_INPUT_DIR   = BASE_DIR / "formatos_word"
WORD_OUTPUT_DIR  = BASE_DIR / "formatos_rag"
WORD_MANIFEST_PATH = CACHE_DIR / "manifest_word.json"

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

<!-- RAG_IGNORE_START -->
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
<!-- RAG_IGNORE_END -->
"""

def get_pdf_page_count(file_path):
    if file_path.suffix.lower() == ".pdf":
        try:
            reader = pypdf.PdfReader(file_path)
            return len(reader.pages)
        except Exception:
            try:
                import fitz
                doc = fitz.open(file_path)
                num = len(doc)
                doc.close()
                return num
            except Exception:
                return "Error"
    return 1  # Para imágenes

def sha256_pdf(file_path: Path) -> str:
    """Calcula el hash SHA-256 de un PDF para deteccion de cambios en cache."""
    h = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def try_convert_doc_to_docx(doc_path: Path):
    """Intenta convertir un archivo .doc heredado a .docx usando win32com si Microsoft Word está instalado.
    Retorna Path al archivo .docx creado o None si falla."""
    docx_path = doc_path.with_suffix(".docx")
    if docx_path.exists():
        return docx_path
    
    try:
        import win32com.client as win32
        # Intentar conectar con Word
        word = win32.gencache.EnsureDispatch('Word.Application')
        word.Visible = False
        doc = word.Documents.Open(str(doc_path.resolve()))
        doc.Activate()
        word.ActiveDocument.SaveAs(str(docx_path.resolve()), FileFormat=16) # 16 = wdFormatXMLDocument
        doc.Close(False)
        word.Quit()
        logger.info(f"[OK] Convertido automáticamente: {doc_path.name} -> {docx_path.name}")
        return docx_path
    except Exception as e:
        logger.warning(f"[!] No se pudo convertir automáticamente {doc_path.name} a .docx: {e}")
        logger.warning("[!] Para procesar archivos .doc heredados, se requiere Microsoft Word instalado en el sistema.")
        logger.warning("[!] Por favor, guarde el archivo manualmente como .docx en la carpeta formatos_word.")
        return None


def main():
    parser = argparse.ArgumentParser(description="QUIBOR-RAG - Convertidor de Normativas y Formatos RAG - IBM Docling")
    parser.add_argument("--chunk-mode",      action="store_true", help="Ejecuta la conversión de un fragmento de PDF/imagen en subproceso.")
    parser.add_argument("--file-path",        type=str,            help="Ruta del archivo a convertir.")
    parser.add_argument("--start",            type=int,            help="Página de inicio (1-based, inclusive).")
    parser.add_argument("--end",              type=int,            help="Página de fin (1-based, inclusive).")
    parser.add_argument("--output-json",      type=str,            help="Ruta donde guardar el JSON del documento generado.")
    parser.add_argument("--no-ocr",           action="store_true", help="Desactiva el OCR en el procesamiento del PDF.")
    parser.add_argument("--force-reprocess",  action="store_true", help="Re-procesa archivos ya convertidos ignorando la caché.")
    parser.add_argument("--no-chunks",        action="store_true", help="No genera chunks individuales por artículo.")
    parser.add_argument("--post-process-only",action="store_true", help="Solo aplica el post-procesado legal a los .md existentes sin re-convertir con Docling.")

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
    if not INPUT_DIR.exists():
        logger.error(f"La carpeta de origen no existe: {INPUT_DIR}")
        sys.exit(1)

    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not WORD_INPUT_DIR.exists():
        WORD_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not WORD_OUTPUT_DIR.exists():
        WORD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Advertir si el pipeline legal no está disponible
    if not LEGAL_PIPELINE_AVAILABLE:
        logger.warning(f"[!] Modulos de post-procesamiento no disponibles: {_legal_import_error}")
        logger.warning("[!] Se generara solo el Markdown crudo de Docling sin estructuracion legal.")

    # Cargar manifest de conversion (cache SHA-256)
    manifest = load_manifest(str(MANIFEST_PATH)) if LEGAL_PIPELINE_AVAILABLE else {}
    word_manifest = load_manifest(str(WORD_MANIFEST_PATH)) if LEGAL_PIPELINE_AVAILABLE else {}

    # MODO POST-PROCESS-ONLY: solo re-aplica legalizer a .md existentes
    if getattr(args, 'post_process_only', False):
        if not LEGAL_PIPELINE_AVAILABLE:
            logger.error("[ERR] --post-process-only requiere los modulos legalizer/metadata_extractor.")
            sys.exit(1)
        console.print("\n[bold cyan][RUN] Modo post-procesado: Aplicando pipeline legal a archivos .md existentes...\n[/]")
        post_count = 0
        for md_file in sorted(OUTPUT_DIR.glob("*.md")):
            try:
                raw    = md_file.read_text(encoding='utf-8')
                
                # 1. Separar YAML frontmatter si existe
                rest = raw
                if raw.startswith('---\n'):
                    end_fm = raw.find('\n---\n', 4)
                    if end_fm > 0:
                        rest = raw[end_fm + 5:]
                
                # 2. Separar la cabecera MIT, el cuerpo y el pie de página MIT
                first_sep = rest.find('\n---\n')
                if first_sep >= 0:
                    mit_header = rest[:first_sep + 5]
                    body_and_footer = rest[first_sep + 5:]
                    
                    footer_idx = body_and_footer.rfind('FIN DEL DOCUMENTO ESTRUCTURADO')
                    if footer_idx < 0:
                        footer_idx = body_and_footer.rfind('DERECHOS DE AUTOR Y LICENCIA MIT')
                    
                    if footer_idx >= 0:
                        last_sep = body_and_footer.rfind('\n---\n', 0, footer_idx)
                        if last_sep >= 0:
                            body = body_and_footer[:last_sep].strip()
                        else:
                            body = body_and_footer.strip()
                    else:
                        last_sep = body_and_footer.rfind('\n---\n')
                        if last_sep >= 0:
                            body = body_and_footer[:last_sep].strip()
                        else:
                            body = body_and_footer.strip()
                    mit_footer = FOOTER_TEMPLATE
                else:
                    mit_header = HEADER_TEMPLATE
                    body = rest.strip()
                    mit_footer = FOOTER_TEMPLATE

                # 3. Aplicar legalizer al cuerpo real
                structured = legalize(body, document_name=md_file.stem)
                
                # 4. Re-ensamblar el documento con las plantillas
                full_structured = mit_header + '\n' + structured + mit_footer

                # 5. Inyectar YAML frontmatter actualizado
                pdf_match = INPUT_DIR / (md_file.stem + '.pdf')
                pdf_path  = str(pdf_match) if pdf_match.exists() else ''
                with_meta = inject_frontmatter(full_structured, pdf_path, md_file.stem)
                md_file.write_text(with_meta, encoding='utf-8')
                if not getattr(args, 'no_chunks', False):
                    chunk_file(str(md_file))
                post_count += 1
                console.print(f"[bold green][OK] Post-procesado:[/] {md_file.name}")
            except Exception as e:
                console.print(f"[bold red][ERR] {md_file.name}: {e}[/]")
        console.print(f"\n[bold cyan][OK] {post_count} archivos post-procesados.[/]\n")
        return

    # 1. Cabecera del Sistema de Justicia
    banner_text = Text()
    banner_text.append("[SYS] SISTEMA DE JUSTICIA VENEZOLANO\n", style="bold yellow")
    banner_text.append("QUIBOR-RAG: Convertidor de Normativas y Formatos a RAG / IA\n", style="bold cyan")
    banner_text.append("Motor de Extracción: IBM Docling\n\n", style="italic white")
    banner_text.append("Desarrollador: Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales) | Copyright (c) 2026 MIT License", style="bold green")
    console.print(Panel(banner_text, border_style="cyan", box=box.ROUNDED, expand=False))

    # Extensiones soportadas
    extensions = [
        "*.pdf", "*.PDF",
        "*.png", "*.PNG",
        "*.jpg", "*.JPG",
        "*.jpeg", "*.JPEG",
        "*.tiff", "*.TIFF",
        "*.bmp", "*.BMP"
    ]
    
    pdf_files = []
    word_files = []
    
    if args.file_path and not args.chunk_mode:
        single_path = Path(args.file_path)
        if not single_path.exists():
            # Intentar buscar en INPUT_DIR o en WORD_INPUT_DIR
            if (INPUT_DIR / args.file_path).exists():
                single_path = INPUT_DIR / args.file_path
            elif (WORD_INPUT_DIR / args.file_path).exists():
                single_path = WORD_INPUT_DIR / args.file_path
        
        if single_path.exists():
            suffix = single_path.suffix.lower()
            if suffix in [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                pdf_files = [single_path]
            elif suffix in [".docx", ".doc"]:
                word_files = [single_path]
            else:
                pdf_files = [single_path]
            console.print(f"[bold cyan][INFO] Procesando unicamente el archivo: {single_path.name}[/]")
        else:
            console.print(f"[bold red][ERR] El archivo especificado no existe: {args.file_path}[/]")
            sys.exit(1)
    else:
        for ext in extensions:
            pdf_files.extend(list(INPUT_DIR.glob(ext)))
        pdf_files = list(set(pdf_files))
        pdf_files = [f for f in pdf_files if not f.name.startswith("_repaired_") and not f.name.startswith("_temp_")]
        
        word_extensions = ["*.docx", "*.DOCX", "*.doc", "*.DOC"]
        for ext in word_extensions:
            word_files.extend(list(WORD_INPUT_DIR.glob(ext)))
        word_files = list(set(word_files))
        word_files = [f for f in word_files if not f.name.startswith("~") and not f.name.startswith("_temp_")]
        
    if not pdf_files and not word_files:
        console.print(f"[bold yellow][!] No se encontraron archivos PDF, imágenes ni documentos Word para procesar.[/]")
        return

    # 2. Generar y mostrar la tabla de estados
    table = Table(
        title="Lista de Archivos y Estados de Conversión", 
        title_style="bold magenta", 
        box=box.MINIMAL_DOUBLE_HEAD
    )
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Tipo", style="bold blue")
    table.add_column("Archivo Origen", style="white")
    table.add_column("Detalle", justify="center", style="yellow")
    table.add_column("Archivo MD (Destino)", style="green")
    table.add_column("Estado de Conversión", justify="center")

    all_files_data = []
    pending_files = []

    with console.status("[bold green]Escaneando archivos y cargando metadatos...", spinner="dots"):
        # Escanear PDF/imágenes
        for file_path in pdf_files:
            md_filename = f"{file_path.stem}.md"
            md_path     = OUTPUT_DIR / md_filename
            pages       = get_pdf_page_count(file_path)

            already_converted = False
            if md_path.exists() and not getattr(args, 'force_reprocess', False):
                cached_hash = manifest.get(file_path.name, {}).get('sha256', '')
                if cached_hash:
                    current_hash = sha256_pdf(file_path)
                    already_converted = (cached_hash == current_hash)
                else:
                    already_converted = True

            status_text = "[bold green]Ya convertido [OK][/]" if already_converted else "[bold yellow]Pendiente [..][/]"
            
            all_files_data.append({
                "type": "PDF/Imagen",
                "file_path": file_path,
                "pages": pages,
                "md_filename": md_filename,
                "status_text": status_text,
                "converted": already_converted
            })

        # Escanear documentos Word
        for file_path in word_files:
            md_filename = f"{file_path.stem}.md"
            md_path     = WORD_OUTPUT_DIR / md_filename

            already_converted = False
            if md_path.exists() and not getattr(args, 'force_reprocess', False):
                cached_hash = word_manifest.get(file_path.name, {}).get('sha256', '')
                if cached_hash:
                    current_hash = sha256_pdf(file_path)
                    already_converted = (cached_hash == current_hash)
                else:
                    already_converted = True

            status_text = "[bold green]Ya convertido [OK][/]" if already_converted else "[bold yellow]Pendiente [..][/]"
            
            all_files_data.append({
                "type": "Word",
                "file_path": file_path,
                "pages": "N/A",
                "md_filename": md_filename,
                "status_text": status_text,
                "converted": already_converted
            })

    # Ordenar por tipo y luego alfabéticamente
    all_files_data.sort(key=lambda x: (x["type"], x["file_path"].name.lower()))

    for idx, item in enumerate(all_files_data, start=1):
        pages_str = str(item["pages"]) if isinstance(item["pages"], int) else item["pages"]
        table.add_row(
            str(idx),
            item["type"],
            item["file_path"].name,
            pages_str,
            item["md_filename"],
            item["status_text"]
        )
        if not item["converted"]:
            pending_files.append((item["file_path"], item["type"], item["pages"]))

    console.print(table)

    if not pending_files:
        console.print("\n[bold green][OK] Todos los archivos ya han sido convertidos anteriormente. No hay tareas pendientes.[/]\n")
        confirm = input("Quieres iniciar el proceso ? escri S/N ")
        if confirm.strip().lower() in ['s', 'si', 'y', 'yes']:
            console.print("\n[bold yellow]No hay archivos nuevos por procesar.[/]\n")
        else:
            console.print("\n[bold yellow]Operación cancelada por el usuario.[/]\n")
        return

    console.print(f"\n[bold cyan]Se detectaron {len(pending_files)} archivos pendientes para convertir.[/]\n")
    confirm = input("Quieres iniciar el proceso ? escri S/N ")
    if confirm.strip().lower() not in ['s', 'si', 'y', 'yes']:
        console.print("\n[bold red]Operación cancelada por el usuario.[/]\n")
        sys.exit(0)

    console.print(f"\n[bold yellow][RUN] Iniciando conversión de {len(pending_files)} archivos nuevos...[/]\n")
    
    success_count = 0
    fail_count = 0
    errors_list = []
    
    script_path = Path(__file__).resolve()

    progress_columns = [
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40, finished_style="green", complete_style="cyan"),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
    ]

    with Progress(*progress_columns, console=console) as progress:
        overall_task = progress.add_task("[bold magenta]Progreso General", total=len(pending_files))
        
        for idx, (file_path, file_type, pages) in enumerate(pending_files, start=1):
            md_filename = f"{file_path.stem}.md"
            output_dir = OUTPUT_DIR if file_type == "PDF/Imagen" else WORD_OUTPUT_DIR
            output_md_path = output_dir / md_filename
            
            file_desc = file_path.name
            if len(file_desc) > 30:
                file_desc = file_desc[:27] + "..."
                
            suffix = file_path.suffix.lower()
            markdown_content = ""
            
            # Conversión dinámica de .doc a .docx si es necesario
            if file_type == "Word" and suffix == ".doc":
                converted_path = try_convert_doc_to_docx(file_path)
                if converted_path:
                    file_path = converted_path
                    suffix = ".docx"
                else:
                    fail_count += 1
                    progress.update(overall_task, advance=1)
                    errors_list.append((file_path.name, "No se pudo convertir archivo .doc a .docx. Se requiere Microsoft Word."))
                    continue
            
            try:
                if suffix == ".pdf":
                    num_pages = pages if isinstance(pages, int) else 0
                    if num_pages == 0:
                        num_pages = get_pdf_page_count(file_path)
                        if not isinstance(num_pages, int):
                            num_pages = 1
                    
                    BATCH_SIZE = 15
                    temp_jsons = []
                    
                    file_cache_dir = CACHE_DIR / file_path.stem.strip()
                    file_cache_dir.mkdir(parents=True, exist_ok=True)
                    
                    batches = []
                    for start_page in range(1, num_pages + 1, BATCH_SIZE):
                        end_page = min(start_page + BATCH_SIZE - 1, num_pages)
                        json_path = file_cache_dir / f"chunk_{start_page}_{end_page}.json"
                        batches.append((start_page, end_page, json_path))
                    
                    pending_batches = []
                    for start_page, end_page, json_path in batches:
                        if json_path.exists():
                            try:
                                DoclingDocument.load_from_json(json_path)
                                temp_jsons.append(json_path)
                            except Exception:
                                pending_batches.append((start_page, end_page, json_path))
                        else:
                            pending_batches.append((start_page, end_page, json_path))
                    
                    num_batches = len(batches)
                    file_task = progress.add_task(
                        f"[cyan]Convirtiendo PDF: {file_desc}", 
                        total=num_batches
                    )
                    
                    progress.update(file_task, completed=len(temp_jsons))
                    
                    if pending_batches:
                        from concurrent.futures import ThreadPoolExecutor, as_completed
                        MAX_WORKERS = max(1, min(3, os.cpu_count() - 1 if os.cpu_count() else 2))
                        
                        def process_batch(start_page, end_page, temp_json_path):
                            cmd = [
                                sys.executable,
                                str(script_path),
                                "--chunk-mode",
                                "--file-path", str(file_path),
                                "--start", str(start_page),
                                "--end", str(end_page),
                                "--output-json", str(temp_json_path)
                            ]
                            if args.no_ocr:
                                cmd.append("--no-ocr")
                            
                            res = subprocess.run(cmd, capture_output=True, encoding='utf-8')
                            
                            if res.returncode != 0:
                                cmd_no_ocr = cmd + ["--no-ocr"]
                                res_no_ocr = subprocess.run(cmd_no_ocr, capture_output=True, encoding='utf-8')
                                
                                if res_no_ocr.returncode != 0:
                                    error_msg = f"STDOUT: {res_no_ocr.stdout.strip()}\nSTDERR: {res_no_ocr.stderr.strip()}"
                                    raise RuntimeError(f"Fallo crítico en lote {start_page}-{end_page} sin OCR:\n{error_msg}")
                            
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
                                    progress.update(file_task, advance=1)
                                except Exception as e:
                                    raise RuntimeError(f"Error procesando lote {start}-{end}: {e}")
                    
                    temp_jsons.sort(key=lambda p: int(p.stem.split('_')[1]))
                    
                    docs = []
                    for temp_json in temp_jsons:
                        if temp_json.exists():
                            docs.append(DoclingDocument.load_from_json(temp_json))
                            
                    if not docs:
                        raise RuntimeError("No se pudieron cargar los fragmentos JSON temporales.")
                        
                    merged_doc = DoclingDocument.concatenate(docs)
                    markdown_content = merged_doc.export_to_markdown()
                    
                    try:
                        import shutil
                        shutil.rmtree(file_cache_dir)
                    except Exception as e:
                        logger.warning(f"No se pudo limpiar la carpeta de caché {file_cache_dir.name}: {e}")
                        
                else:
                    # Imagen o Word Document
                    desc_type = "Imagen" if file_type == "PDF/Imagen" else "Documento"
                    file_task = progress.add_task(
                        f"[cyan]Convirtiendo {desc_type}: {file_desc}", 
                        total=1
                    )
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_json_path = Path(temp_dir) / "doc_data.json"
                        cmd = [
                            sys.executable,
                            str(script_path),
                            "--chunk-mode",
                            "--file-path", str(file_path),
                            "--output-json", str(temp_json_path)
                        ]
                        
                        res = subprocess.run(cmd, capture_output=True, encoding='utf-8')
                        if res.returncode != 0:
                            error_msg = f"STDOUT: {res.stdout.strip()}\nSTDERR: {res.stderr.strip()}"
                            raise RuntimeError(f"Fallo convirtiendo {desc_type.lower()}:\n{error_msg}")
                            
                        if not temp_json_path.exists():
                            raise RuntimeError("El subproceso no generó el JSON intermedio.")
                            
                        img_doc = DoclingDocument.load_from_json(temp_json_path)
                        markdown_content = img_doc.export_to_markdown()
                        progress.update(file_task, advance=1)

                # Guardar el archivo final (contenido crudo de Docling)
                raw_md = HEADER_TEMPLATE + markdown_content + FOOTER_TEMPLATE

                # --- PIPELINE DE POST-PROCESAMIENTO LEGAL ---
                if LEGAL_PIPELINE_AVAILABLE and file_type == "PDF/Imagen":
                    try:
                        # Fase 1: Estructurar jerarquia legal y separar articulos
                        structured = legalize(markdown_content, document_name=md_filename)

                        # Fase 2: Inyectar YAML frontmatter con metadatos semanticos
                        full_structured = HEADER_TEMPLATE + structured + FOOTER_TEMPLATE
                        pdf_path_str = str(file_path)
                        final_content = inject_frontmatter(full_structured, pdf_path_str, file_path.stem)

                        # Guardar Markdown legalizado
                        with open(output_md_path, "w", encoding="utf-8") as f:
                            f.write(final_content)

                        # Fase 5: Validar integridad de articulos
                        val_report = validate_md_file(str(output_md_path))
                        if val_report.overall_status == "ERROR":
                            console.print(f"  [bold red][VALIDACION ERROR] {md_filename}: {val_report.sequence_gaps}[/]")
                        elif val_report.overall_status == "WARNING":
                            console.print(f"  [bold yellow][VALIDACION WARNING] {md_filename}: arts. detectados={val_report.articles_found}[/]")
                        else:
                            console.print(f"  [bold green][VALIDACION OK] {md_filename}: {val_report.articles_found} articulos[/]")

                        # Fase 3: Generar chunks individuales por articulo
                        if not getattr(args, 'no_chunks', False):
                            try:
                                chunk_paths = chunk_file(str(output_md_path))
                                console.print(f"  [bold cyan][CHUNKS] {len(chunk_paths)} chunks generados[/]")
                            except Exception as ce:
                                console.print(f"  [bold yellow][CHUNKS] Error generando chunks: {ce}[/]")

                        # Actualizar manifest SHA-256
                        manifest[file_path.name] = {
                            'sha256':       sha256_pdf(file_path),
                            'md_file':      md_filename,
                            'articulos':    val_report.articles_found,
                            'estado_val':   val_report.overall_status,
                        }
                        save_manifest(str(MANIFEST_PATH), manifest)

                    except Exception as le:
                        logger.warning(f"[!] Pipeline legal fallo para {md_filename}: {le}. Guardando Markdown crudo.")
                        with open(output_md_path, "w", encoding="utf-8") as f:
                            f.write(raw_md)
                else:
                    # Sin pipeline legal o es un documento Word: guardar Markdown crudo/limpio
                    content_to_save = markdown_content if file_type == "Word" else raw_md
                    with open(output_md_path, "w", encoding="utf-8") as f:
                        f.write(content_to_save)

                    # Si es Word, también actualizamos su manifest_word.json
                    if file_type == "Word":
                        word_manifest[file_path.name] = {
                            'sha256':   sha256_pdf(file_path),
                            'md_file':  md_filename,
                        }
                        save_manifest(str(WORD_MANIFEST_PATH), word_manifest)

                success_count += 1
                progress.remove_task(file_task)
                progress.update(overall_task, advance=1)
                console.print(f"[bold green][OK] Exitoso:[/] [white]{file_path.name}[/] -> [green]{md_filename}[/]")
                
            except Exception as e:
                fail_count += 1
                progress.remove_task(file_task)
                progress.update(overall_task, advance=1)
                
                if output_md_path.exists():
                    try:
                        output_md_path.unlink()
                    except Exception:
                        pass
                        
                console.print(f"[bold red][ERR] Falló:[/] [red]{file_path.name}. Detalle: {str(e)}[/]")
                errors_list.append((file_path.name, str(e)))
                
            gc.collect()

    # Resumen final
    summary_text = Text()
    summary_text.append("📊 Resumen de la Ejecución:\n\n", style="bold cyan")
    summary_text.append(f"• Archivos procesados con éxito: ", style="white")
    summary_text.append(f"{success_count}\n", style="bold green")
    summary_text.append(f"• Archivos fallidos: ", style="white")
    summary_text.append(f"{fail_count}\n", style="bold red" if fail_count > 0 else "green")
    
    if errors_list:
        summary_text.append("\n[!] Detalle de errores detectados:\n", style="bold red")
        for filename, err in errors_list:
            summary_text.append(f"  - {filename}:\n    ", style="bold red")
            summary_text.append(f"{err}\n", style="red")
            
    panel_title = "PROCESO FINALIZADO" if fail_count == 0 else "PROCESO FINALIZADO CON ERRORES"
    panel_style = "green" if fail_count == 0 else "red"
    
    console.print(Panel(summary_text, title=panel_title, border_style=panel_style, box=box.ROUNDED))

if __name__ == "__main__":
    main()
