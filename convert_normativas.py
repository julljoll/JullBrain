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
import platform
import time

# Modulos de post-procesamiento legal (Fases 1-5)
try:
    from legalizer import legalize
    from metadata_extractor import inject_frontmatter, sha256_file, load_manifest, save_manifest
    from validator import validate_md_file
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
    console = Console(style="on #252525", force_terminal=True, force_interactive=True)
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
    from docling.chunking import HierarchicalChunker
except ImportError as e:
    logger.error("No se pudo importar Docling. Asegúrate de activar el entorno virtual correcto e instalar 'docling'.")
    logger.error(f"Detalle del error: {e}")
    sys.exit(1)

# Rutas predeterminadas (usando rutas dinámicas relativas al directorio del script)
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR   = BASE_DIR / "RAG" / "datos_brutos"
OUTPUT_DIR  = BASE_DIR / "RAG" / "Informacion_docling_rag"
CACHE_DIR   = BASE_DIR / ".conversion_cache"
MANIFEST_PATH = CACHE_DIR / "manifest.json"

# Cabecera de derechos de autor y licencia (Apache 2.0)
HEADER_TEMPLATE = """# 🏛️ PROCESAMIENTO ESTRUCTURADO DE NORMATIVAS Y LEYES

> [!NOTE]
> **JULLBRAIN RAG-PIPELINE - VERSIÓN 2.0 (ENTORNO LOCAL DE PYTHON)**
> 
> Este script Orquesta el Diseño y Estructura de Conocimientos para la Inteligencia Artificial, está especializado en convertir leyes venezolanas a estructuras para el entrenamiento de IAs.
> 
> * **Motor de IA:** IBM Docling (Licencia MIT) - https://github.com/docling-project/docling-ibm-models.git
> * **Propósito:** Aportar tecnología y automatización al Estado venezolano para prevenir la corrupción y el retardo procesal.
> * **Desarrollado por:** Jull Ortiz - Rol: Arquitecto de Datos con y para la Inteligencia Artificial Jurídica - Web: http://www.sha256.us/
> * **Licencia del Orquestador:** Apache 2.0

---

"""

# Pie de página de derechos de autor y licencia (Apache 2.0)
FOOTER_TEMPLATE = ""

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
    parser = argparse.ArgumentParser(description="JullBrain - Convertidor de Normativas y Formatos RAG - IBM Docling")
    parser.add_argument("--chunk-mode",      action="store_true", help="Ejecuta la conversión de un fragmento de PDF/imagen en subproceso.")
    parser.add_argument("--file-path",        type=str,            help="Ruta del archivo a convertir.")
    parser.add_argument("--start",            type=int,            help="Página de inicio (1-based, inclusive).")
    parser.add_argument("--end",              type=int,            help="Página de fin (1-based, inclusive).")
    parser.add_argument("--output-json",      type=str,            help="Ruta donde guardar el JSON del documento generado.")
    parser.add_argument("--no-ocr",           action="store_true", help="Desactiva el OCR en el procesamiento del PDF.")

    parser.add_argument("--no-chunks",        action="store_true", help="No genera chunks individuales por artículo.")
    parser.add_argument("--post-process-only",action="store_true", help="Solo aplica el post-procesado legal a los .md existentes sin re-convertir con Docling.")
    parser.add_argument("--input-dir",        type=str,            help="Directorio de origen de PDFs/imágenes (ej. RAG/datos_brutos).")
    parser.add_argument("--output-dir",       type=str,            help="Directorio de destino de Markdown estructurado.")

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
    global INPUT_DIR, OUTPUT_DIR
    if getattr(args, 'input_dir', None):
        INPUT_DIR = Path(args.input_dir).resolve()
    if getattr(args, 'output_dir', None):
        OUTPUT_DIR = Path(args.output_dir).resolve()

    if not INPUT_DIR.exists():
        logger.error(f"La carpeta de origen no existe: {INPUT_DIR}")
        sys.exit(1)


    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Advertir si el pipeline legal no está disponible
    if not LEGAL_PIPELINE_AVAILABLE:
        logger.warning(f"[!] Modulos de post-procesamiento no disponibles: {_legal_import_error}")
        logger.warning("[!] Se generara solo el Markdown crudo de Docling sin estructuracion legal.")

    # Cargar manifest de conversion (cache SHA-256)
    manifest = load_manifest(str(MANIFEST_PATH)) if LEGAL_PIPELINE_AVAILABLE else {}

    # MODO POST-PROCESS-ONLY: solo re-aplica legalizer a .md existentes
    if getattr(args, 'post_process_only', False):
        if not LEGAL_PIPELINE_AVAILABLE:
            logger.error("[ERR] --post-process-only requiere los modulos legalizer/metadata_extractor.")
            sys.exit(1)
        console.print("\n[bold cyan][RUN] Modo post-procesado: Aplicando pipeline legal a archivos .md existentes...\n[/]")
        post_count = 0
        for md_file in sorted(OUTPUT_DIR.rglob("*.md")):
            try:
                raw    = md_file.read_text(encoding='utf-8')
                
                # 1. Separar YAML frontmatter si existe
                rest = raw
                if raw.startswith('---\n'):
                    end_fm = raw.find('\n---\n', 4)
                    if end_fm > 0:
                        rest = raw[end_fm + 5:]
                
                # 2. Separar la cabecera, el cuerpo y el pie de página de licencia
                first_sep = rest.find('\n---\n')
                if first_sep >= 0:
                    mit_header = HEADER_TEMPLATE
                    body_and_footer = rest[first_sep + 5:]
                    
                    footer_idx = body_and_footer.rfind('FIN DEL DOCUMENTO ESTRUCTURADO')
                    if footer_idx < 0:
                        footer_idx = body_and_footer.rfind('DERECHOS DE AUTOR Y LICENCIA APACHE 2.0')
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
                # En post-procesado no re-generamos chunks JSON ya que requiere el documento original parseado
                # if not getattr(args, 'no_chunks', False):
                #     chunk_file(str(md_file))
                post_count += 1
                console.print(f"[bold green][OK] Post-procesado:[/] {md_file.name}")
            except Exception as e:
                console.print(f"[bold red][ERR] {md_file.name}: {e}[/]")
        console.print(f"\n[bold cyan][OK] {post_count} archivos post-procesados.[/]\n")
        return

    # 1. Cabecera del Sistema de Justicia
    banner_text = Text()
    banner_text.append("[SYS] JULLBRAIN - MI CEREBRO PERSONAL\n", style="bold yellow")
    banner_text.append("JullBrain: Convertidor de Normativas y Formatos a RAG / IA\n", style="bold cyan")
    banner_text.append("Motor de Extracción: IBM Docling (https://github.com/docling-project/docling)\n\n", style="italic white")
    banner_text.append("Desarrollador: Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales) | Copyright (c) 2026 Apache License 2.0", style="bold green")
    console.print(Panel(banner_text, border_style="cyan", box=box.ROUNDED, expand=False))

    try:
        cpu_model = platform.processor() or "N/A"
        cpu_count = os.cpu_count() or 1
        import psutil
        ram_total = psutil.virtual_memory().total / (1024**3)
        ram_avail = psutil.virtual_memory().available / (1024**3)
        hw_text = Text()
        hw_text.append(f"CPU: ", style="bold")
        hw_text.append(f"{cpu_model}  ", style="green")
        hw_text.append(f"({cpu_count} núcleos)", style="white")
        hw_text.append(f"  |  RAM: ", style="bold")
        hw_text.append(f"{ram_total:.1f} GB", style="green")
        hw_text.append(f"  (libre: {ram_avail:.1f} GB)", style="white")
        console.print(Panel(hw_text, border_style="dim white", box=box.ROUNDED, expand=False))
    except ImportError:
        cpu_text = Text()
        cpu_text.append(f"CPU: ", style="bold")
        cpu_text.append(f"{platform.processor() or 'N/A'}  ", style="green")
        cpu_text.append(f"({os.cpu_count() or 1} núcleos)", style="white")
        console.print(Panel(cpu_text, border_style="dim white", box=box.ROUNDED, expand=False))
    print()

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
            if (INPUT_DIR / args.file_path).exists():
                single_path = INPUT_DIR / args.file_path
        
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
            pdf_files.extend(list(INPUT_DIR.rglob(ext)))
        pdf_files = list(set(pdf_files))
        pdf_files = [f for f in pdf_files if not f.name.startswith("_repaired_") and not f.name.startswith("_temp_")]
        
        word_extensions = ["*.docx", "*.DOCX", "*.doc", "*.DOC"]
        for ext in word_extensions:
            word_files.extend(list(INPUT_DIR.rglob(ext)))
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
            try:
                rel_path = file_path.relative_to(INPUT_DIR)
            except ValueError:
                rel_path = Path(file_path.name)
            md_path = OUTPUT_DIR / rel_path.with_suffix(".md")
            pages = get_pdf_page_count(file_path)

            already_converted = md_path.exists()

            status_text = "[bold green]Ya convertido [OK][/]" if already_converted else "[bold yellow]Pendiente [..][/]"
            
            all_files_data.append({
                "type": "PDF/Imagen",
                "file_path": file_path,
                "pages": pages,
                "md_filename": str(rel_path.with_suffix(".md")),
                "status_text": status_text,
                "converted": already_converted
            })

        # Escanear documentos Word
        for file_path in word_files:
            try:
                rel_path = file_path.relative_to(INPUT_DIR)
            except ValueError:
                rel_path = Path(file_path.name)
            md_path = OUTPUT_DIR / rel_path.with_suffix(".md")

            already_converted = md_path.exists()

            status_text = "[bold green]Ya convertido [OK][/]" if already_converted else "[bold yellow]Pendiente [..][/]"
            
            all_files_data.append({
                "type": "Word",
                "file_path": file_path,
                "pages": "N/A",
                "md_filename": str(rel_path.with_suffix(".md")),
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
        return

    console.print(f"\n[bold cyan]Se detectaron {len(pending_files)} archivos pendientes para convertir.[/]\n")

    console.print(f"\n[bold yellow][RUN] Iniciando conversión de {len(pending_files)} archivos nuevos...[/]\n")
    
    console.print(Panel(
        "[bold white]Puedes detener la transformación en cualquier momento presionando [yellow]Ctrl + C[/yellow].\n"
        "El progreso de los archivos completados se guardará de forma segura automáticamente.[/]",
        title="[bold green]CONTROL DE EJECUCIÓN[/]",
        border_style="green",
        box=box.ROUNDED
    ))
    
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
            try:
                rel_path = file_path.relative_to(INPUT_DIR)
            except ValueError:
                rel_path = Path(file_path.name)
            output_md_path = OUTPUT_DIR / rel_path.with_suffix(".md")
            
            output_md_path.parent.mkdir(parents=True, exist_ok=True)
            md_filename = output_md_path.name
            
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
                    
                    completed_pages = 0
                    for cached_json in temp_jsons:
                        parts = cached_json.stem.split('_')
                        if len(parts) == 3 and parts[0] == 'chunk':
                            completed_pages += int(parts[2]) - int(parts[1]) + 1

                    file_task = progress.add_task(
                        f"[cyan]{file_desc}",
                        total=num_pages
                    )

                    progress.update(file_task, completed=completed_pages)

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
                                    completed_pages += end - start + 1
                                    progress.update(
                                        file_task,
                                        completed=completed_pages,
                                        description=f"[cyan]{file_desc}[/]  {completed_pages}/{num_pages} pág"
                                    )
                                except Exception as e:
                                    raise RuntimeError(f"Error procesando lote {start}-{end}: {e}")

                    progress.update(file_task, description=f"[cyan]{file_desc}[/]  [bold green]{num_pages}/{num_pages} pág[/]")
                    
                    temp_jsons.sort(key=lambda p: int(p.stem.split('_')[1]))
                    
                    docs = []
                    for temp_json in temp_jsons:
                        if temp_json.exists():
                            docs.append(DoclingDocument.load_from_json(temp_json))
                            
                    if not docs:
                        raise RuntimeError("No se pudieron cargar los fragmentos JSON temporales.")
                        
                    merged_doc = DoclingDocument.concatenate(docs)
                    markdown_content = merged_doc.export_to_markdown()
                    final_doc = merged_doc
                    
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
                        final_doc = img_doc
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

                        # Generar archivo paralelo de Chunks Jerárquicos en JSON para LightRAG
                        if not getattr(args, 'no_chunks', False) and 'final_doc' in locals() and final_doc:
                            try:
                                chunker = HierarchicalChunker()
                                chunks = list(chunker.chunk(final_doc))
                                chunks_data = []
                                for c in chunks:
                                    c_text = chunker.contextualize(c) if hasattr(chunker, 'contextualize') else (c.text if hasattr(c, 'text') else str(c))
                                    c_meta = c.meta.export_to_dict() if hasattr(c.meta, 'export_to_dict') else str(c.meta)
                                    chunks_data.append({"text": c_text, "meta": c_meta})
                                json_output_path = output_md_path.with_suffix(".json")
                                with open(json_output_path, "w", encoding="utf-8") as f_json:
                                    json.dump(chunks_data, f_json, ensure_ascii=False, indent=2)
                                logger.info(f"[OK] Archivo paralelo de chunks jerárquicos generado: {json_output_path.name}")
                            except Exception as _e_chunk:
                                logger.warning(f"No se pudo generar el JSON paralelo de chunks para {md_filename}: {_e_chunk}")

                        # Fase 5: Validar integridad de articulos
                        val_report = validate_md_file(str(output_md_path))
                        if val_report.overall_status == "ERROR":
                            console.print(f"  [bold red][VALIDACION ERROR] {md_filename}: {val_report.sequence_gaps}[/]")
                        elif val_report.overall_status == "WARNING":
                            console.print(f"  [bold yellow][VALIDACION WARNING] {md_filename}: arts. detectados={val_report.articles_found}[/]")
                        else:
                            console.print(f"  [bold green][VALIDACION OK] {md_filename}: {val_report.articles_found} articulos[/]")

                        # Actualizar manifest SHA-256
                        manifest[str(rel_path)] = {
                            'sha256':       sha256_pdf(file_path),
                            'md_file':      str(rel_path.with_suffix(".md")),
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

                    # Si es Word, también actualizamos su manifest
                    if file_type == "Word":
                        manifest[str(rel_path)] = {
                            'sha256':   sha256_pdf(file_path),
                            'md_file':  str(rel_path.with_suffix(".md")),
                        }
                        save_manifest(str(MANIFEST_PATH), manifest)

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
    try:
        main()
    except KeyboardInterrupt:
        if 'console' in globals() and console is not None:
            from rich.panel import Panel
            from rich import box
            console.print("\n")
            console.print(Panel(
                "[bold white]El usuario ha detenido manualmente el proceso (Ctrl + C).\n"
                "Todo el progreso completado hasta ahora ha sido guardado.[/]",
                title="[bold red]PROCESO CANCELADO[/]",
                border_style="red",
                box=box.DOUBLE
            ))
        else:
            print("\nProceso cancelado manualmente por el usuario. Progreso guardado.")
        sys.exit(130)
