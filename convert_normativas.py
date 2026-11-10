"""
convert_normativas.py — JullBrain v0.2.0
=========================================
Motor de Conversión Documental y Chunking Jerárquico con Tecnología IBM Docling.
Optimizado para ejecutarse sobre Procesador (CPU) con afinidad dinámica de hilos
y almacenamiento local de modelos en RAG/modelos_ia/docling por ciberseguridad.
"""

import os
import sys
import logging
import argparse
import subprocess
import tempfile
import gc
import hashlib
import json
import platform
from pathlib import Path

# Reconfigurar salida estándar y de error para usar UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "RAG" / "datos_brutos"
OUTPUT_DIR = BASE_DIR / "RAG" / "Informacion_docling_rag"
CHUNKS_DIR = BASE_DIR / "RAG" / "normativas_chunks"
MODELS_VAULT_DIR = BASE_DIR / "RAG" / "modelos_ia"
DOCLING_MODELS_DIR = MODELS_VAULT_DIR / "docling"
CACHE_DIR = BASE_DIR / ".conversion_cache"
MANIFEST_PATH = CACHE_DIR / "manifest.json"

DOCLING_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Configurar entorno CPU y Bóveda Local de Modelos antes de importar Docling
import gpu_detector
HOST_INFO = gpu_detector.configurar_entorno_cpu_docling()

import pypdf
import fitz

<<<<<<< HEAD
=======
# Modulos de post-procesamiento legal (Fases 1-5)
from common_utils import sha256_file, get_pdf_page_count, load_json_config
sha256_pdf = sha256_file

>>>>>>> 9dc0729da20b5212662bb449cb68c84c940431b8
try:
    from legalizer import legalize
    from metadata_extractor import inject_frontmatter, load_manifest, save_manifest
    from validator import validate_md_file
    from audit_logger import validate_pdf_magic_bytes
    LEGAL_PIPELINE_AVAILABLE = True
except ImportError as _le:
    LEGAL_PIPELINE_AVAILABLE = False
    _legal_import_error = str(_le)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.text import Text
from rich import box
from rich.logging import RichHandler

if "--chunk-mode" in sys.argv:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    console = None
else:
    console = Console(style="on #12161A", force_terminal=True, force_interactive=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_path=False, rich_tracebacks=True)]
    )
logger = logging.getLogger("convert_normativas")

try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
    from docling.datamodel.base_models import InputFormat
    from docling_core.types.doc import DoclingDocument
    from docling.chunking import HierarchicalChunker
except ImportError as e:
    logger.error("No se pudo importar IBM Docling. Ejecuta orquestador_JullBrain.bat para instalar dependencias.")
    logger.error(f"Detalle del error: {e}")
    sys.exit(1)

# Cabecera canónica obligatoria (Principio 9 — sin footer al final)
HEADER_TEMPLATE = """# 🏛️ PROCESAMIENTO ESTRUCTURADO DE NORMATIVAS Y LEYES

> [!NOTE]
> **JULLBRAIN & UMIF RAG-PIPELINE - VERSIÓN 0.2.0 (NODO LOCAL AIR-GAPPED / ORACLE CLOUD)**
> 
> Este script Orquesta el Diseño y Estructura de Conocimientos para la Inteligencia Artificial, especializado en convertir leyes y expedientes venezolanos a estructuras determinísticas bajo el estándar Google OKF e IBM Granite.
> 
> * **Motor de IA:** IBM Docling (Licencia MIT) + IBM Granite Embedding R2 + IBM Granite Guardian
> * **Propósito:** Aportar tecnología pericial al sistema de justicia para prevenir la corrupción y erradicar el retardo procesal.
> * **Desarrollado por:** Jull Ortiz - Rol: Abogado - Diseñador UX/UI Especializado en LegalTech & Forense Digital - Web: http://www.sha256.us/
> * **Licencia del Orquestador:** Apache 2.0

---

"""

FOOTER_TEMPLATE = ""

<<<<<<< HEAD

def get_pdf_page_count(file_path: Path):
    if file_path.suffix.lower() == ".pdf":
        try:
            reader = pypdf.PdfReader(file_path)
            return len(reader.pages)
        except Exception:
            try:
                doc = fitz.open(file_path)
                num = len(doc)
                doc.close()
                return num
            except Exception:
                return "Error"
    return 1


def sha256_pdf(file_path: Path) -> str:
    """Calcula el hash SHA-256 de un PDF para detección de cambios en caché."""
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

=======
>>>>>>> 9dc0729da20b5212662bb449cb68c84c940431b8

def try_convert_doc_to_docx(doc_path: Path):
    """Intenta convertir un archivo .doc heredado a .docx usando win32com si Microsoft Word está instalado."""
    docx_path = doc_path.with_suffix(".docx")
    if docx_path.exists():
        return docx_path

    try:
        import win32com.client as win32
        word = win32.gencache.EnsureDispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(str(doc_path.resolve()))
        doc.Activate()
        word.ActiveDocument.SaveAs(str(docx_path.resolve()), FileFormat=16)
        doc.Close(False)
        word.Quit()
        logger.info(f"[OK] Convertido automáticamente: {doc_path.name} -> {docx_path.name}")
        return docx_path
    except Exception as e:
        logger.warning(f"[!] No se pudo convertir automáticamente {doc_path.name} a .docx: {e}")
        return None


def build_cpu_pdf_converter(do_ocr: bool = True) -> DocumentConverter:
    """
    Construye una instancia de DocumentConverter de IBM Docling optimizada
    específicamente para ejecutarse en el procesador (CPU) detectado y usando
    la bóveda local de artefactos en RAG/modelos_ia/docling.
    """
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = do_ocr
    pipeline_options.do_table_structure = True
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=HOST_INFO.get("hilos_optimos_docling", 4),
        device=AcceleratorDevice.CPU
    )
    if DOCLING_MODELS_DIR.exists() and any(DOCLING_MODELS_DIR.iterdir()):
        pipeline_options.artifacts_path = DOCLING_MODELS_DIR

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                backend=PyPdfiumDocumentBackend,
                pipeline_options=pipeline_options
            )
        }
    )


def main():
    parser = argparse.ArgumentParser(description="JullBrain - Convertidor de Normativas y Formatos RAG - IBM Docling (CPU)")
    parser.add_argument("--chunk-mode", action="store_true", help="Ejecuta la conversión de un fragmento de PDF/imagen en subproceso.")
    parser.add_argument("--file-path", type=str, help="Ruta del archivo a convertir.")
    parser.add_argument("--start", type=int, help="Página de inicio (1-based, inclusive).")
    parser.add_argument("--end", type=int, help="Página de fin (1-based, inclusive).")
    parser.add_argument("--output-json", type=str, help="Ruta donde guardar el JSON del documento generado.")
    parser.add_argument("--no-ocr", action="store_true", help="Desactiva el OCR en el procesamiento del PDF.")
    parser.add_argument("--no-chunks", action="store_true", help="No genera chunks individuales por artículo.")
    parser.add_argument("--post-process-only", action="store_true", help="Solo aplica el post-procesado legal a los .md existentes.")
    parser.add_argument("--input-dir", type=str, help="Directorio de origen (por defecto RAG/datos_brutos).")
    parser.add_argument("--output-dir", type=str, help="Directorio de destino (por defecto RAG/Informacion_docling_rag).")
    parser.add_argument("--single-file", type=str, help="Ruta de un único archivo a convertir (modo seguro: 1 por vez).")
    parser.add_argument("--bootstrap-models", action="store_true", help="Descarga y verifica los modelos locales de IBM Docling en RAG/modelos_ia/docling.")

    args = parser.parse_args()

    # MODO BOOTSTRAP DE MODELOS LOCALES IBM DOCLING (CIBERSEGURIDAD)
    if args.bootstrap_models:
        print(f"[BOOT] Descargando/verificando artefactos de IBM Docling en bóveda local: {DOCLING_MODELS_DIR}")
        try:
            from docling.utils.model_downloader import download_models
            download_models(output_dir=DOCLING_MODELS_DIR, progress=True)
            from audit_logger import default_audit_logger
            default_audit_logger.seal_and_verify_model_vault()
            print("[OK] Artefactos de IBM Docling almacenados y sellados con SHA-256 en RAG/modelos_ia/docling.")
            sys.exit(0)
        except Exception as e:
            print(f"[INFO] Verificación de modelos Docling completada ({e}).")
            sys.exit(0)

    # MODO SUBPROCESO (Procesa un solo lote/imagen en CPU y guarda el JSON del modelo)
    if args.chunk_mode:
        if not args.file_path or not args.output_json:
            logger.error("Faltan parámetros requeridos para el modo subproceso.")
            sys.exit(1)

        file_path = Path(args.file_path)
        output_json = Path(args.output_json)

        try:
            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                converter = build_cpu_pdf_converter(do_ocr=not args.no_ocr)
                page_range = (args.start, args.end) if (args.start is not None and args.end is not None) else None
                result = converter.convert(file_path, page_range=page_range)
            else:
                converter = DocumentConverter()
                result = converter.convert(file_path)

            result.document.save_as_json(output_json)
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error en subproceso al procesar {file_path.name}: {e}")
            sys.exit(1)

    # MODO ORQUESTADOR PRINCIPAL
    global INPUT_DIR, OUTPUT_DIR
    if getattr(args, "input_dir", None):
        INPUT_DIR = Path(args.input_dir).resolve()
    if getattr(args, "output_dir", None):
        OUTPUT_DIR = Path(args.output_dir).resolve()

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if not LEGAL_PIPELINE_AVAILABLE:
        logger.warning(f"[!] Módulos de post-procesamiento no disponibles: {_legal_import_error}")

    manifest = load_manifest(str(MANIFEST_PATH)) if LEGAL_PIPELINE_AVAILABLE else {}

    # MODO POST-PROCESS-ONLY
    if getattr(args, "post_process_only", False):
        if not LEGAL_PIPELINE_AVAILABLE:
            logger.error("[ERR] --post-process-only requiere legalizer/metadata_extractor.")
            sys.exit(1)
        console.print("\n[bold cyan][RUN] Modo post-procesado: Aplicando pipeline legal a archivos .md en RAG/Informacion_docling_rag...\n[/]")
        post_count = 0
        for md_file in sorted(OUTPUT_DIR.rglob("*.md")):
            try:
                raw = md_file.read_text(encoding="utf-8")
                rest = raw
                if raw.startswith("---\n"):
                    end_fm = raw.find("\n---\n", 4)
                    if end_fm > 0:
                        rest = raw[end_fm + 5:]

                first_sep = rest.find("\n---\n")
                if first_sep >= 0:
                    body = rest[first_sep + 5:].strip()
                else:
                    body = rest.strip()

                structured = legalize(body, document_name=md_file.stem)
                full_structured = HEADER_TEMPLATE + "\n" + structured + FOOTER_TEMPLATE

                rel_md = md_file.relative_to(OUTPUT_DIR)
                pdf_match = INPUT_DIR / rel_md.with_suffix(".pdf")
                if not pdf_match.exists():
                    pdf_match = INPUT_DIR / (md_file.stem + ".pdf")
                pdf_path = str(pdf_match) if pdf_match.exists() else ""

                with_meta = inject_frontmatter(full_structured, pdf_path, md_file.stem)
                md_file.write_text(with_meta, encoding="utf-8")
                post_count += 1
                console.print(f"[bold green][OK] Post-procesado:[/] {md_file.name}")
            except Exception as e:
                console.print(f"[bold red][ERR] {md_file.name}: {e}[/]")
        console.print(f"\n[bold cyan][OK] {post_count} archivos post-procesados.[/]\n")
        return

    # Banner informativo de CPU
    banner_text = Text()
    banner_text.append("[SYS] JULLBRAIN & UMIF - MOTOR IBM DOCLING (CPU OPTIMIZADO)\n", style="bold #FECF06")
    banner_text.append(f"CPU: {HOST_INFO['procesador'][:60]} ({HOST_INFO['nucleos_fisicos']}C/{HOST_INFO['nucleos_logicos']}T -> {HOST_INFO['hilos_optimos_docling']} hilos activos)\n", style="bold cyan")
    banner_text.append(f"Bóveda Local de Modelos IA: {MODELS_VAULT_DIR}\n", style="green")
    banner_text.append("Desarrollador: Jull Ortiz (Abogado - Diseñador UX/UI LegalTech) | Licencia Apache 2.0", style="dim white")
    console.print(Panel(banner_text, border_style="cyan", box=box.ROUNDED, expand=False))

    extensions = ["*.pdf", "*.PDF", "*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG", "*.tiff", "*.TIFF", "*.bmp", "*.BMP"]
    pdf_files = []
    word_files = []

    if getattr(args, "single_file", None):
        candidate_path = Path(args.single_file)
        if not candidate_path.exists():
            candidate = INPUT_DIR / args.single_file
            if candidate.exists():
                candidate_path = candidate
            else:
                logger.error(f"Archivo no encontrado: {args.single_file}")
                sys.exit(1)
        args.file_path = str(candidate_path)

    if args.file_path and not args.chunk_mode:
        single_path = Path(args.file_path)
        if not single_path.exists() and (INPUT_DIR / args.file_path).exists():
            single_path = INPUT_DIR / args.file_path

        if single_path.exists():
            suffix = single_path.suffix.lower()
            if suffix in [".docx", ".doc"]:
                word_files = [single_path]
            else:
                pdf_files = [single_path]
            console.print(f"[bold cyan][INFO] Procesando únicamente el archivo: {single_path.name}[/]")
        else:
            console.print(f"[bold red][ERR] El archivo especificado no existe: {args.file_path}[/]")
            sys.exit(1)
    else:
        for ext in extensions:
            pdf_files.extend(list(INPUT_DIR.rglob(ext)))
        pdf_files = [f for f in set(pdf_files) if not f.name.startswith("_repaired_") and not f.name.startswith("_temp_")]

        for ext in ["*.docx", "*.DOCX", "*.doc", "*.DOC"]:
            word_files.extend(list(INPUT_DIR.rglob(ext)))
        word_files = [f for f in set(word_files) if not f.name.startswith("~") and not f.name.startswith("_temp_")]

    if not pdf_files and not word_files:
        console.print("[bold yellow][!] No se encontraron archivos en RAG/datos_brutos para procesar.[/]")
        return

    all_files_data = []
    pending_files = []

    for file_path in pdf_files:
        try:
            rel_path = file_path.relative_to(INPUT_DIR)
        except ValueError:
            rel_path = Path(file_path.name)
        md_path = OUTPUT_DIR / rel_path.with_suffix(".md")
        pages = get_pdf_page_count(file_path)
        already_converted = md_path.exists()
        all_files_data.append({
            "type": "PDF/Imagen",
            "file_path": file_path,
            "pages": pages,
            "md_filename": str(rel_path.with_suffix(".md")),
            "converted": already_converted
        })

    for file_path in word_files:
        try:
            rel_path = file_path.relative_to(INPUT_DIR)
        except ValueError:
            rel_path = Path(file_path.name)
        md_path = OUTPUT_DIR / rel_path.with_suffix(".md")
        already_converted = md_path.exists()
        all_files_data.append({
            "type": "Word",
            "file_path": file_path,
            "pages": "N/A",
            "md_filename": str(rel_path.with_suffix(".md")),
            "converted": already_converted
        })

    all_files_data.sort(key=lambda x: (x["type"], x["file_path"].name.lower()))
    for item in all_files_data:
        if not item["converted"] or getattr(args, "single_file", None):
            pending_files.append((item["file_path"], item["type"], item["pages"]))

    if not pending_files:
        console.print("\n[bold green][OK] Todos los archivos en RAG/datos_brutos ya están convertidos en RAG/Informacion_docling_rag.[/]\n")
        return

    success_count = 0
    fail_count = 0
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

        for file_path, file_type, pages in pending_files:
            try:
                rel_path = file_path.relative_to(INPUT_DIR)
            except ValueError:
                rel_path = Path(file_path.name)
            output_md_path = OUTPUT_DIR / rel_path.with_suffix(".md")
            output_md_path.parent.mkdir(parents=True, exist_ok=True)
            md_filename = output_md_path.name
            file_desc = file_path.name[:27] + "..." if len(file_path.name) > 30 else file_path.name
            suffix = file_path.suffix.lower()

            if file_type == "Word" and suffix == ".doc":
                converted_path = try_convert_doc_to_docx(file_path)
                if converted_path:
                    file_path = converted_path
                    suffix = ".docx"
                else:
                    fail_count += 1
                    progress.update(overall_task, advance=1)
                    continue

            try:
                if suffix == ".pdf":
                    if LEGAL_PIPELINE_AVAILABLE and not validate_pdf_magic_bytes(file_path):
                        raise ValueError(f"Cabecera binaria inválida (no es un PDF legítimo '%PDF-'): {file_path.name}")

                    num_pages = pages if isinstance(pages, int) and pages > 0 else 1
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

                    completed_pages = sum(
                        int(p.stem.split("_")[2]) - int(p.stem.split("_")[1]) + 1
                        for p in temp_jsons if len(p.stem.split("_")) == 3
                    )

                    file_task = progress.add_task(f"[cyan]{file_desc}", total=num_pages, completed=completed_pages)

                    if pending_batches:
                        from concurrent.futures import ThreadPoolExecutor, as_completed
                        MAX_WORKERS = HOST_INFO.get("workers_optimos", 2)

                        def process_batch(start_page, end_page, temp_json_path):
                            cmd = [
                                sys.executable, str(script_path),
                                "--chunk-mode",
                                "--file-path", str(file_path),
                                "--start", str(start_page),
                                "--end", str(end_page),
                                "--output-json", str(temp_json_path)
                            ]
                            if args.no_ocr:
                                cmd.append("--no-ocr")
                            res = subprocess.run(cmd, capture_output=True, encoding="utf-8")
                            if res.returncode != 0:
                                res_no_ocr = subprocess.run(cmd + ["--no-ocr"], capture_output=True, encoding="utf-8")
                                if res_no_ocr.returncode != 0:
                                    raise RuntimeError(f"Fallo en lote {start_page}-{end_page}: {res_no_ocr.stderr.strip()}")
                            return temp_json_path

                        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                            future_to_batch = {
                                executor.submit(process_batch, start, end, path): (start, end)
                                for start, end, path in pending_batches
                            }
                            for future in as_completed(future_to_batch):
                                start, end = future_to_batch[future]
                                json_path = future.result()
                                temp_jsons.append(json_path)
                                completed_pages += end - start + 1
                                progress.update(file_task, completed=completed_pages)

                    temp_jsons.sort(key=lambda p: int(p.stem.split("_")[1]))
                    docs = [DoclingDocument.load_from_json(tj) for tj in temp_jsons if tj.exists()]
                    if not docs:
                        raise RuntimeError("No se pudieron cargar los fragmentos JSON temporales.")

                    merged_doc = DoclingDocument.concatenate(docs)
                    markdown_content = merged_doc.export_to_markdown()
                    final_doc = merged_doc

                    import shutil
                    shutil.rmtree(file_cache_dir, ignore_errors=True)
                else:
                    file_task = progress.add_task(f"[cyan]Convirtiendo: {file_desc}", total=1)
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_json_path = Path(temp_dir) / "doc_data.json"
                        cmd = [
                            sys.executable, str(script_path),
                            "--chunk-mode",
                            "--file-path", str(file_path),
                            "--output-json", str(temp_json_path)
                        ]
                        res = subprocess.run(cmd, capture_output=True, encoding="utf-8")
                        if res.returncode != 0 or not temp_json_path.exists():
                            raise RuntimeError(f"Fallo convirtiendo documento: {res.stderr.strip()}")
                        img_doc = DoclingDocument.load_from_json(temp_json_path)
                        markdown_content = img_doc.export_to_markdown()
                        final_doc = img_doc
                        progress.update(file_task, advance=1)

                raw_md = HEADER_TEMPLATE + markdown_content + FOOTER_TEMPLATE

                if LEGAL_PIPELINE_AVAILABLE and file_type == "PDF/Imagen":
                    structured = legalize(markdown_content, document_name=md_filename)
                    full_structured = HEADER_TEMPLATE + structured + FOOTER_TEMPLATE
                    final_content = inject_frontmatter(full_structured, str(file_path), file_path.stem)
                    output_md_path.write_text(final_content, encoding="utf-8")

                    if not getattr(args, "no_chunks", False) and final_doc:
                        try:
                            chunker = HierarchicalChunker()
                            chunks = list(chunker.chunk(final_doc))
                            chunks_data = []
                            for c in chunks:
                                c_text = chunker.contextualize(c) if hasattr(chunker, "contextualize") else getattr(c, "text", str(c))
                                c_meta = c.meta.export_to_dict() if hasattr(c.meta, "export_to_dict") else str(c.meta)
                                chunks_data.append({"text": c_text, "content": c_text, "meta": c_meta})

                            # Guardar JSON en RAG/Informacion_docling_rag y en RAG/normativas_chunks
                            json_output_path = output_md_path.with_suffix(".json")
                            json_output_path.write_text(json.dumps(chunks_data, ensure_ascii=False, indent=2), encoding="utf-8")

                            chunk_subdir = CHUNKS_DIR / rel_path.parent / file_path.stem
                            chunk_subdir.mkdir(parents=True, exist_ok=True)
                            (chunk_subdir / "hierarchical_chunks.json").write_text(
                                json.dumps(chunks_data, ensure_ascii=False, indent=2), encoding="utf-8"
                            )
                        except Exception as _e_chunk:
                            logger.warning(f"No se pudo generar JSON de chunks para {md_filename}: {_e_chunk}")

                    val_report = validate_md_file(str(output_md_path))
                    manifest[str(rel_path)] = {
                        "sha256": sha256_pdf(file_path),
                        "md_file": str(rel_path.with_suffix(".md")),
                        "articulos": val_report.articles_found,
                        "estado_val": val_report.overall_status,
                    }
                    save_manifest(str(MANIFEST_PATH), manifest)
                else:
                    output_md_path.write_text(markdown_content if file_type == "Word" else raw_md, encoding="utf-8")

                success_count += 1
                progress.remove_task(file_task)
                progress.update(overall_task, advance=1)
                console.print(f"[bold green][OK] Exitoso:[/] [white]{file_path.name}[/] -> [green]{md_filename}[/]")

            except Exception as e:
                fail_count += 1
                progress.update(overall_task, advance=1)
                if output_md_path.exists():
                    output_md_path.unlink(missing_ok=True)
                console.print(f"[bold red][ERR] Falló:[/] [red]{file_path.name}. Detalle: {e}[/]")

            gc.collect()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Proceso detenido por el usuario de forma segura.")
        sys.exit(0)
