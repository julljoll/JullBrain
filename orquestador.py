"""
orquestador.py — JullBrain v0.2.0
==================================
Centro de Control y Orquestador Legal-RAG 100% Python + Tecnología IBM.
Iniciado desde orquestador_JullBrain.bat (local) o contenedor nativo Podman / Oracle Cloud.

Tecnología Exclusiva IBM:
- IBM Docling (Extracción estructural y chunking jerárquico sobre CPU)
- IBM Granite Embedding R2 (Vectores semánticos 768-dim en RAG/modelos_ia)
- IBM Granite 3.3 8B Instruct & IBM Granite Guardian 3.2/3.3 (Ciberseguridad y Anti-Alucinación)

Núcleo de Información:
- ./RAG/datos_brutos/             (Archivos originales inmutables)
- ./RAG/Informacion_docling_rag/  (Markdown legalizado + YAML OKF + JSON)
- ./RAG/normativas_chunks/        (Chunks atómicos para RAGFlow)
- ./RAG/modelos_ia/               (Bóveda local Air-Gapped de modelos IBM)
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from version import __version__

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

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.text import Text
from rich import box

import gpu_detector
<<<<<<< HEAD
from audit_logger import default_audit_logger
=======
from common_utils import sha256_file, get_pdf_page_count, load_json_config
>>>>>>> 9dc0729da20b5212662bb449cb68c84c940431b8

BASE_DIR = Path(__file__).resolve().parent
RAG_DIR = BASE_DIR / "RAG"
INPUT_DIR = RAG_DIR / "datos_brutos"
OUTPUT_DIR = RAG_DIR / "Informacion_docling_rag"
CHUNKS_DIR = RAG_DIR / "normativas_chunks"
MODELS_VAULT_DIR = RAG_DIR / "modelos_ia"
AUDIT_FILE = BASE_DIR / "audit_trail.jsonl"
CONFIG_FILE = BASE_DIR / "pipeline_config.json"


<<<<<<< HEAD
def sha256_file(path: Path) -> str:
    """Calcula el hash SHA-256 de un archivo en bloques de 64KB."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "ERROR_HASH"


def load_config() -> dict:
    """Carga pipeline_config.json de manera segura."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}
=======
def load_config() -> dict:
    """Carga pipeline_config.json de manera segura."""
    return load_json_config(CONFIG_FILE)
>>>>>>> 9dc0729da20b5212662bb449cb68c84c940431b8


def detectar_entorno() -> str:
    """Detecta el entorno de ejecución activo (local, podman, oracle)."""
    env = os.getenv("JULLBRAIN_ENV", "").lower()
    if env in ("local", "podman", "oracle"):
        return env
    if Path("/run/.containerenv").exists() or Path("/.dockerenv").exists():
        return "podman"
    return "local"


class JullBrainOrquestador:
    """Orquestador terminal principal para JullBrain & UMIF v0.2.0."""

    def __init__(self):
        self.console = Console(style="on #12161A", force_terminal=True, force_interactive=True)
        self.config = load_config()
        self.entorno = detectar_entorno()
        self.backend_gpu = "cpu"

    def inicializar_hardware_y_modelos(self) -> None:
        """Analiza el computador host, optimiza CPU para Docling y verifica la bóveda RAG/modelos_ia."""
        try:
            self.backend_gpu = gpu_detector.preguntar_backend_al_usuario(self.console, auto_select_cpu=True)
            vault_info = default_audit_logger.seal_and_verify_model_vault()
            status_vault = vault_info.get("integrity_status", "VERIFIED_OK")
            color = "bold green" if status_vault == "VERIFIED_OK" else "bold red"
            self.console.print(
                f"  [{color}]🔒 Bóveda Criptográfica IBM (RAG/modelos_ia): {status_vault} "
                f"({vault_info.get('total_artifacts', 0)} artefactos verificados con SHA-256)[/]\n"
            )
        except Exception as e:
            self.console.print(f"[yellow][!] Aviso en diagnóstico inicial: {e}. Usando CPU por defecto.[/]")
            self.backend_gpu = "cpu"

    def mostrar_banner(self) -> None:
        """Muestra el banner canónico de presentación de JullBrain & UMIF."""
        banner_ascii = r"""  =========================================================================================
    _____       _ _   ____            _                                                    
   |     |_   _| | | | __ ) _ __ __ _(_)_ __                                               
   | | | | | | | | | |  _ \| .__/ _` | | ._ \                                              
   | |_| | |_| | | | | |_) | | | (_| | | | | |                                             
    \___/ \__,_|_|_| |____/|_|  \__,_|_|_| |_|                                             
  ========================================================================================="""
        self.console.print(f"[bold #FECF06]{banner_ascii}[/]")
        self.console.print(f"\n[bold #FECF06]   JullBrain & UMIF Legal-RAG — Versión v{__version__} (Entorno: {self.entorno.upper()} | 100% IBM AI)[/]")
        self.console.print("""
[#00FF41]   Orquestador Forense de Conocimiento Jurídico e Inteligencia Artificial Local
   Especializado en estructuración de normativas y expedientes penales venezolanos.
   Desarrollado por: Jull Ortiz — Abogado & Diseñador UX/UI LegalTech & Forense Digital

   Stack IBM    : IBM Docling (CPU) + IBM Granite 3.3 + Granite Embedding R2 + Granite Guardian
   Núcleo Datos : ./RAG/ (datos_brutos | Informacion_docling_rag | normativas_chunks | modelos_ia)
   Despliegue   : Local (.bat) | Contenedor Nativo Podman (Win/Linux) | Oracle Cloud (OCI)
   Licencia     : Apache 2.0 — Web Oficial: http://www.sha256.us/[/]
[bold #FECF06]  =========================================================================================[/]\n""")

    def mostrar_menu(self) -> str:
        """Muestra el menú de operaciones y solicita opción al usuario."""
        self.console.print("[bold #FECF06]  SELECCIONE UNA OPCIÓN DEL CENTRO DE OPERACIONES JULLBRAIN:[/]")
        self.console.print()
        self.console.print("    [bold #00FF00][1][/] [white]Ver Estado del Núcleo ./RAG/ (Tabla de Documentos Brutos vs Procesados)[/]")
        self.console.print("    [bold #00FF41][2][/] [white]Convertir UN Archivo Específico con IBM Docling CPU (Modo Seguro - 1 por vez)[/]")
        self.console.print("    [bold #00FF41][3][/] [white]Convertir Todos los Archivos Pendientes (Procesamiento Secuencial Seguro)[/]")
        self.console.print("    [bold #00FF41][4][/] [white]Verificación QA de Integridad Cruzada (Validador Cruzado PDF vs MD)[/]")
        self.console.print("    [bold #00FF41][5][/] [white]Generar / Verificar Embeddings Locales con IBM Granite R2 (RAG/modelos_ia)[/]")
        self.console.print("    [bold #00FF41][6][/] [white]Solo Post-Procesado Legal (Legalizer + Frontmatter Canónico OKF)[/]")
        self.console.print("    [bold #00FF41][7][/] [white]Ejecutar Suite Exhaustiva de QA Testing & Ciberseguridad Offline[/]")
        self.console.print("    [bold #00FF41][8][/] [white]Descargar / Sellar Bóveda Local de Modelos IBM (RAG/modelos_ia) y Limpiar Caché[/]")
        self.console.print("    [bold #FECF06][9][/] [white]Ver Registro Forense Criptográfico (audit_trail.jsonl — HMAC-SHA256)[/]")
        self.console.print("    [bold #00FF41][0][/] [dim white]Salir[/]")
        self.console.print()
        self.console.print("[bold #FECF06]  =========================================================================================[/]")

        opcion = Prompt.ask("  [bold #FECF06]Ingrese el número de la opción deseada [0-9][/]", choices=[str(i) for i in range(10)], default="1")
        return opcion

    def escanear_archivos(self) -> List[Dict[str, Any]]:
        """Escanea recursivamente RAG/datos_brutos y comprueba su estado en RAG/Informacion_docling_rag."""
        extensions = [
            "*.pdf", "*.PDF", "*.png", "*.PNG", "*.jpg", "*.JPG",
            "*.jpeg", "*.JPEG", "*.tiff", "*.TIFF", "*.bmp", "*.BMP",
            "*.docx", "*.DOCX", "*.doc", "*.DOC"
        ]

        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        MODELS_VAULT_DIR.mkdir(parents=True, exist_ok=True)

        encontrados = []
        for ext in extensions:
            for f in INPUT_DIR.rglob(ext):
                if f.name.startswith("_repaired_") or f.name.startswith("_temp_") or f.name.startswith("~"):
                    continue
                encontrados.append(f)

        encontrados = sorted(list(set(encontrados)), key=lambda x: str(x).lower())

        resultados = []
        for idx, file_path in enumerate(encontrados, start=1):
            try:
                rel_path = file_path.relative_to(INPUT_DIR)
            except ValueError:
                rel_path = Path(file_path.name)

            categoria = rel_path.parent.name if rel_path.parent.name else "Raíz"
            md_path = OUTPUT_DIR / rel_path.with_suffix(".md")
            convertido = md_path.exists()
            paginas = get_pdf_page_count(file_path)
            tipo = "PDF" if file_path.suffix.lower() == ".pdf" else ("Word" if file_path.suffix.lower() in [".doc", ".docx"] else "Imagen")

            resultados.append({
                "indice": idx,
                "file_path": file_path,
                "rel_path": rel_path,
                "categoria": categoria,
                "nombre": file_path.name,
                "tipo": tipo,
                "paginas": paginas,
                "md_path": md_path,
                "convertido": convertido
            })

        return resultados

    def mostrar_tabla_estados(self) -> List[Dict[str, Any]]:
        """Muestra una tabla con los archivos normativos en ./RAG/ y su estado actual."""
        archivos = self.escanear_archivos()

        if not archivos:
            self.console.print(f"[bold yellow][!] No se encontraron documentos en: {INPUT_DIR}[/]")
            return []

        tabla = Table(
            title="📂 Núcleo ./RAG/ — Estado de Documentos Jurídicos (datos_brutos → Informacion_docling_rag)",
            title_style="bold #FECF06",
            box=box.ROUNDED,
            header_style="bold cyan"
        )
        tabla.add_column("#", justify="center", style="cyan", width=4)
        tabla.add_column("Categoría", style="bold white", width=18)
        tabla.add_column("Documento Fuente", style="white")
        tabla.add_column("Tipo", justify="center", style="yellow", width=8)
        tabla.add_column("Págs", justify="center", style="dim white", width=6)
        tabla.add_column("Estado de Conversión", justify="center", width=22)

        total_convertidos = 0
        for item in archivos:
            if item["convertido"]:
                total_convertidos += 1
                estado_str = "[bold green]🟢 Ya convertido [OK][/]"
            else:
                estado_str = "[bold yellow]🔴 Pendiente [..][/]"

            tabla.add_row(
                str(item["indice"]),
                item["categoria"],
                item["nombre"][:55] + ("..." if len(item["nombre"]) > 55 else ""),
                item["tipo"],
                str(item["paginas"]),
                estado_str
            )

        self.console.print(tabla)
        total_archivos = len(archivos)
        pendientes = total_archivos - total_convertidos

        resumen = Text()
        resumen.append("\n  Resumen del Núcleo RAG: ", style="bold")
        resumen.append(f"{total_archivos} documentos totales  |  ", style="white")
        resumen.append(f"{total_convertidos} convertidos  |  ", style="bold green")
        resumen.append(f"{pendientes} pendientes de transformar\n", style="bold yellow" if pendientes > 0 else "bold green")
        self.console.print(resumen)

        return archivos

    def convertir_archivo(self, archivo: Path) -> bool:
        """Convierte UN solo archivo verificando el hash SHA-256 pre y post conversión."""
        if not archivo.exists():
            self.console.print(f"[bold red][ERROR] El archivo no existe: {archivo}[/]")
            return False

        self.console.print(f"\n[bold cyan]─── Iniciando Conversión Forense IBM Docling (CPU): {archivo.name} ───[/]")
        sha_antes = sha256_file(archivo)
        self.console.print(f"[dim]  [SHA-256 Pre-Conversión]:  {sha_antes}[/]")

        inicio = datetime.now()
        cmd = [
            sys.executable,
            str(BASE_DIR / "convert_normativas.py"),
            "--single-file", str(archivo)
        ]

        resultado = subprocess.run(cmd, cwd=str(BASE_DIR))

        duracion = (datetime.now() - inicio).total_seconds()
        sha_despues = sha256_file(archivo)
        integridad_ok = (sha_antes == sha_despues)

        self._registrar_auditoria(
            archivo=archivo.name,
            sha_antes=sha_antes,
            sha_despues=sha_despues,
            integridad_ok=integridad_ok,
            exito=(resultado.returncode == 0),
            duracion_seg=duracion
        )

        self.console.print(f"[dim]  [SHA-256 Post-Conversión]: {sha_despues}[/]")

        if not integridad_ok:
            self.console.print(
                "[bold red]  [ALERTA FORENSE CRÍTICA] El archivo original fue alterado durante el proceso. "
                "Violación de la cadena de custodia registrada en audit_trail.jsonl.[/]"
            )
            return False

        self.console.print("  [bold green]✅ Integridad verificada: El archivo fuente se mantuvo 100% inalterado (Espejo Documental OK).[/]")

        if resultado.returncode == 0:
            self.console.print(f"  [bold green]✅ Conversión completada exitosamente en {duracion:.2f} segundos.[/]\n")
            return True

        self.console.print(f"  [bold red]❌ Error durante la conversión del documento (código: {resultado.returncode}).[/]\n")
        return False

    def _seleccionar_y_convertir(self, archivos: Optional[List[Dict[str, Any]]] = None) -> None:
        if not archivos:
            archivos = self.mostrar_tabla_estados()
        if not archivos:
            return

        pendientes = [a for a in archivos if not a["convertido"]]
        self.console.print("[bold yellow]Modo Seguro: Conversión individual en CPU (1 archivo por vez).[/]")
        self.console.print(f"Archivos pendientes disponibles: [cyan]{len(pendientes)}[/]")

        val_prompt = Prompt.ask("Ingrese el # de índice del archivo a convertir (o 'c' para cancelar)")
        if val_prompt.lower() == "c":
            return

        try:
            indice_elegido = int(val_prompt)
            seleccionado = next((a for a in archivos if a["indice"] == indice_elegido), None)
            if not seleccionado:
                self.console.print(f"[bold red]Índice fuera de rango: {indice_elegido}[/]")
                return
            self.convertir_archivo(seleccionado["file_path"])
        except ValueError:
            self.console.print("[bold red]Entrada no válida.[/]")

    def _convertir_todos_pendientes(self) -> None:
        archivos = self.escanear_archivos()
        pendientes = [a for a in archivos if not a["convertido"]]

        if not pendientes:
            self.console.print("[bold green]✅ No hay archivos pendientes. Todos los documentos están convertidos.[/]\n")
            return

        confirmar = Confirm.ask(
            f"Se detectaron [bold cyan]{len(pendientes)}[/] documentos pendientes. "
            f"¿Desea convertirlos secuencialmente en CPU (1 a la vez para proteger el sistema)?"
        )
        if not confirmar:
            return

        exitos = 0
        fallos = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            tarea = progress.add_task("Procesando documentos...", total=len(pendientes))
            for item in pendientes:
                progress.update(tarea, description=f"Procesando: [white]{item['nombre'][:35]}[/]")
                if self.convertir_archivo(item["file_path"]):
                    exitos += 1
                else:
                    fallos += 1
                progress.advance(tarea)

        self.console.print(f"\n[bold green]Proceso finalizado: {exitos} exitosos, {fallos} errores.[/]\n")

    def _registrar_auditoria(
        self,
        archivo: str,
        sha_antes: str,
        sha_despues: str,
        integridad_ok: bool,
        exito: bool,
        duracion_seg: float
    ) -> None:
        """Registra la conversión usando la cadena criptográfica HMAC-SHA256 de AuditLogger."""
        default_audit_logger.log_event(
            event_type="DOCLING_CONVERSION",
            user_id="orquestador_local",
            notebook_id=None,
            action_details={
                "entorno": self.entorno,
                "backend_gpu": self.backend_gpu or "cpu",
                "archivo": archivo,
                "sha256_pdf_antes": sha_antes,
                "sha256_pdf_despues": sha_despues,
                "integridad_pdf": "OK" if integridad_ok else "ALERTA_MODIFICACION",
                "exito_conversion": exito,
                "duracion_seg": round(duracion_seg, 2)
            }
        )

    def _ver_audit_log(self, ultimas: int = 20) -> None:
        if not AUDIT_FILE.exists():
            self.console.print("[yellow]No existe el archivo de auditoría audit_trail.jsonl todavía.[/]")
            return

        lineas = []
        try:
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            lineas.append(json.loads(line))
                        except Exception:
                            pass
        except Exception as e:
            self.console.print(f"[red]Error leyendo audit_trail.jsonl: {e}[/]")
            return

        if not lineas:
            self.console.print("[yellow]El registro de auditoría está vacío.[/]")
            return

        ultimas_entradas = lineas[-ultimas:]

        tabla = Table(
            title=f"📜 Registro Forense Criptográfico HMAC-SHA256 (Últimas {len(ultimas_entradas)} entradas)",
            title_style="bold #FECF06",
            box=box.ROUNDED,
            header_style="bold cyan"
        )
        tabla.add_column("Timestamp (UTC)", style="dim white", width=20)
        tabla.add_column("Archivo / Evento", style="bold white")
        tabla.add_column("Firma / SHA-256", style="cyan", width=18)
        tabla.add_column("Integridad", justify="center", width=14)
        tabla.add_column("Estado", justify="center", width=10)
        tabla.add_column("Duración", justify="right", style="yellow", width=9)

        for e in ultimas_entradas:
            ts = e.get("timestamp") or e.get("timestamp_utc", "")
            ts_str = ts[:19].replace("T", " ") if ts else "N/A"
            act_details = e.get("action_details", {}) if isinstance(e.get("action_details"), dict) else {}
            archivo = e.get("archivo") or act_details.get("archivo") or e.get("event_type") or "Evento"

            sha = e.get("signature_hash") or e.get("sha256_pdf_antes") or act_details.get("sha256_pdf_antes") or ""
            sha_resumen = sha[:12] + "..." if sha else "N/A"

            integ = e.get("integridad_pdf") or act_details.get("integridad_pdf")
            if integ:
                integ_str = "[bold green]OK[/]" if integ == "OK" else "[bold red]ALERTA[/]"
            elif e.get("event_type") == "SHA_VERIFICATION_FAILURE":
                integ_str = "[bold red]FALLO_SHA[/]"
            else:
                integ_str = "[green]FIRMADO[/]"

            exito_val = e.get("exito_conversion") if "exito_conversion" in e else act_details.get("exito_conversion")
            if exito_val is not None:
                exito_str = "[green]ÉXITO[/]" if exito_val else "[red]ERROR[/]"
            else:
                exito_str = "[cyan]AUDIT[/]"

            dur_val = e.get("duracion_seg") if "duracion_seg" in e else act_details.get("duracion_seg")
            dur = f"{dur_val:.1f}s" if dur_val is not None else "-"

            tabla.add_row(ts_str, str(archivo)[:45], sha_resumen, integ_str, exito_str, dur)

        self.console.print(tabla)
        self.console.print(f"Total registros históricos: [bold cyan]{len(lineas)}[/]\n")

    def _ejecutar_subproceso(self, cmd: List[str], titulo: str) -> int:
        self.console.rule(f"[bold cyan]{titulo}[/]")
        res = subprocess.run(cmd, cwd=str(BASE_DIR))
        self.console.rule()
        return res.returncode

    def _sincronizar_opensearch(self) -> None:
        """Sincroniza los chunks generados hacia el clúster OpenSearch (OpenRAG)."""
        from opensearch_indexer import default_opensearch_indexer
        self.console.rule("[bold cyan]Sincronización con Clúster OpenSearch (OpenRAG)[/]")
        health = default_opensearch_indexer.check_cluster_health()
        if health.get("connected"):
            self.console.print(f"[bold green]  [+] Clúster OpenSearch activo ({health.get('cluster_name')}, v{health.get('version')})[/]")
            self.console.print(f"[bold green]  [+] Índice destino: {health.get('index_name')} | Dimensión vector: {health.get('dimension')}[/]")
            stats = default_opensearch_indexer.bulk_index_corpus()
            self.console.print(f"[bold green]  [OK] Indexación masiva completada: {stats['indexed_chunks']} chunks cargados.[/]")
        else:
            self.console.print(f"[yellow]  [!] OpenSearch no responde en {health.get('host')}. Operando en Modo Local Offline.[/]")
            self.console.print("[dim]      Para encender OpenSearch y OpenRAG ejecute: iniciar_servicios_openrag.bat[/]")
        self.console.rule()

    def despachar(self, opcion: str) -> None:
        if opcion == "1":
            self.mostrar_tabla_estados()
        elif opcion == "2":
            self._seleccionar_y_convertir()
        elif opcion == "3":
            self._convertir_todos_pendientes()
        elif opcion == "4":
            self._ejecutar_subproceso(
                [sys.executable, str(BASE_DIR / "validator.py"), str(OUTPUT_DIR)],
                titulo="Verificación QA de Integridad Cruzada PDF vs MD"
            )
        elif opcion == "5":
            self._ejecutar_subproceso(
                [sys.executable, str(BASE_DIR / "granite_embedder.py")],
                titulo="Generación y Verificación de Embeddings IBM Granite R2 (Bóveda Local)"
            )
            self._sincronizar_opensearch()
        elif opcion == "6":
            self._ejecutar_subproceso(
                [sys.executable, str(BASE_DIR / "convert_normativas.py"), "--post-process-only"],
                titulo="Post-Procesado Legal (Legalizer + Frontmatter Canónico OKF)"
            )
        elif opcion == "7":
            self._ejecutar_subproceso(
                [sys.executable, "-m", "unittest", "discover", "tests", "-v"],
                titulo="Suite Exhaustiva de QA Testing & Ciberseguridad Offline"
            )
        elif opcion == "8":
            self._ejecutar_subproceso(
                [sys.executable, str(BASE_DIR / "convert_normativas.py"), "--bootstrap-models"],
                titulo="Descarga y Sellado SHA-256 de Modelos IBM en RAG/modelos_ia"
            )
            self._ejecutar_subproceso(
                [sys.executable, str(BASE_DIR / "cleanup.py")],
                titulo="Purgado de Caché Temporal y Liberación de Memoria RAM"
            )
        elif opcion == "9":
            self._ver_audit_log(ultimas=25)
        elif opcion == "0":
            self.console.print("[bold green]  Sesión de JullBrain finalizada de forma segura.[/]")
            sys.exit(0)

    def ejecutar(self) -> None:
        self.mostrar_banner()
        self.inicializar_hardware_y_modelos()

        while True:
            try:
                opcion = self.mostrar_menu()
                self.despachar(opcion)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operación cancelada por el usuario.[/]")
                break
            except Exception as e:
                self.console.print(f"[bold red]Error en orquestador: {e}[/]")


def main():
    if len(sys.argv) > 1:
        flag = sys.argv[1].lower()
        orq = JullBrainOrquestador()

<<<<<<< HEAD
        if flag == "--web":
            print("[INIT] Iniciando Servidor Headless FastAPI en http://127.0.0.1:8050...")
            cmd = [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8050"]
            subprocess.run(cmd, cwd=str(BASE_DIR))
            sys.exit(0)
        elif flag == "--full":
=======
        if flag in ("--full", "--convert-all"):
>>>>>>> 9dc0729da20b5212662bb449cb68c84c940431b8
            orq.mostrar_banner()
            orq.inicializar_hardware_y_modelos()
            orq._convertir_todos_pendientes()
            sys.exit(0)
        elif flag == "--qa":
            orq.despachar("4")
            sys.exit(0)
        elif flag == "--post":
            orq.despachar("6")
            sys.exit(0)
        elif flag == "--embed":
            orq.despachar("5")
            sys.exit(0)
        elif flag == "--test":
            orq.despachar("7")
            sys.exit(0)
        elif flag == "--clean":
            orq.despachar("8")
            sys.exit(0)
        elif flag in ("--opensearch", "--index-all"):
            orq.mostrar_banner()
            orq._sincronizar_opensearch()
            sys.exit(0)
        elif flag == "--audit":
            orq._ver_audit_log()
            sys.exit(0)
        elif flag in ("--single", "--single-file") and len(sys.argv) > 2:
            orq.mostrar_banner()
            orq.inicializar_hardware_y_modelos()
            archivo = Path(sys.argv[2])
            if not archivo.exists() and (INPUT_DIR / sys.argv[2]).exists():
                archivo = INPUT_DIR / sys.argv[2]
            orq.convertir_archivo(archivo)
            sys.exit(0)

    app_orq = JullBrainOrquestador()
    app_orq.ejecutar()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSesión finalizada. Progreso guardado.")
        sys.exit(0)
