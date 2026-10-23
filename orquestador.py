"""
orquestador.py — JullBrain V3.0
================================
Centro de Control y Orquestador Legal-RAG 100% Python.
Reemplaza toda la lógica previa de orquestador_JullBrain.bat.
El archivo .bat queda como bootstrap mínimo (≤18 líneas) para iniciar este script.

Tecnología:
- IBM Docling (Extracción y conversión estructural)
- IBM Granite R2 (Embeddings semánticos multidimensionales)
- Rich (Interfaz terminal interactiva)
- Cómputo: CPU / GPU AMD RX 580 (DirectML / ROCm)

Principios Forenses:
- Inmutabilidad de datos originales (verificación SHA-256 pre y post conversión).
- Registro estricto de auditoría append-only (audit_trail.jsonl).
- Conversión segura: un archivo por vez para no ralentizar el equipo.
"""

import os
import sys
import json
import hashlib
import subprocess
import platform
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Configuración obligatoria de codificación UTF-8 para terminal en Windows
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

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.text import Text
from rich import box

import gpu_detector

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "RAG" / "datos_brutos"
OUTPUT_DIR = BASE_DIR / "RAG" / "Informacion_docling_rag"
AUDIT_FILE = BASE_DIR / "audit_trail.jsonl"
CONFIG_FILE = BASE_DIR / "pipeline_config.json"
GPU_CONFIG_FILE = BASE_DIR / "gpu_config.json"


def sha256_file(path: Path) -> str:
    """Calcula el hash SHA-256 de un archivo en bloques para proteger la memoria RAM."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "ERROR_HASH"


def load_config() -> dict:
    """Carga pipeline_config.json de manera segura."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def detectar_entorno() -> str:
    """Detecta el entorno de ejecución activo (local, colab, oracle, ibmcloud)."""
    env = os.getenv("JULLBRAIN_ENV", "").lower()
    if env in ("local", "colab", "oracle", "ibmcloud"):
        return env
    if "google.colab" in sys.modules or os.environ.get("COLAB_GPU"):
        return "colab"
    return "local"


def get_pdf_page_count(file_path: Path) -> Any:
    """Retorna el número de páginas de un PDF de forma rápida."""
    if file_path.suffix.lower() == ".pdf":
        try:
            import fitz
            doc = fitz.open(file_path)
            num = len(doc)
            doc.close()
            return num
        except Exception:
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                return len(reader.pages)
            except Exception:
                return "?"
    return 1


class JullBrainOrquestador:
    """Orquestador terminal principal para JullBrain V3.0."""

    def __init__(self):
        self.console = Console(style="on #12161A", force_terminal=True, force_interactive=True)
        self.config = load_config()
        self.entorno = detectar_entorno()
        self.backend_gpu = None

    def inicializar_gpu(self) -> None:
        """Pregunta o confirma el dispositivo de cómputo GPU/CPU al inicio."""
        try:
            self.backend_gpu = gpu_detector.preguntar_backend_al_usuario(self.console)
        except Exception as e:
            self.console.print(f"[yellow][!] No se pudo interrogar GPU: {e}. Usando CPU por defecto.[/]")
            self.backend_gpu = "cpu"

    def mostrar_banner(self) -> None:
        """Muestra el banner de presentación idéntico al banner de orquestador_JullBrain.bat."""
        banner_ascii = r"""  =========================================================================================
    _____       _ _   ____            _                                                    
   |     |_   _| | | | __ ) _ __ __ _(_)_ __                                               
   | | | | | | | | | |  _ \| .__/ _` | | ._ \                                              
   | |_| | |_| | | | | |_) | | | (_| | | | | |                                             
    \___/ \__,_|_|_| |____/|_|  \__,_|_|_| |_|                                             
  ========================================================================================="""
        self.console.print(f"[bold #FECF06]{banner_ascii}[/]")
        self.console.print("\n[bold #FECF06]   JullBrain RAG-Pipeline - Version 3.0 (Entorno Local 100% Python)[/]")
        self.console.print("""
[#00FF41]   Este script Orquesta el Diseno y Estructura de Conocimientos para la
   Inteligencia Artificial, esta especializado en converir leyes venezolanas
   a estructuras para el entrenamiento de Inteligencias Artificiales-
   Desarollado por; Jull Ortiz -Rol: Arquitecto de Datos con y para la
   inteligencia artificial juridica

   Motor de IA  : IBM Docling (Licencia MIT) -
                  https://github.com/docling-project/docling-ibm-models.git
   Proposito    : Aportar tecnologia al Estado venezolano para prevenir
                  la corrupcion y el retardo procesal.
   Desarrollador: Desarrollado Por: Jull Ortiz - Rol: Arquitecto de Datos con IA.
                  Licencia del Orquestador: Apache 2.0
   Web          : http://www.sha256.us/[/]
[bold #FECF06]  =========================================================================================[/]\n""")

    def mostrar_menu(self) -> str:
        """Muestra el menú de operaciones y solicita opción al usuario."""
        self.console.print("[bold #FECF06]  SELECCIONE UNA OPCION DEL CENTRO DE OPERACIONES JULLBRAIN:[/]")
        self.console.print()
        self.console.print("    [bold #00FF00][1][/] [white]Ver Estado de Archivos Normativos (Tabla RAG de Conversión)[/]")
        self.console.print("    [bold #00FF41][2][/] [white]Convertir UN Archivo Específico (Modo Seguro - 1 por vez)[/]")
        self.console.print("    [bold #00FF41][3][/] [white]Convertir Todos los Archivos Pendientes (Procesamiento Secuencial Seguro)[/]")
        self.console.print("    [bold #00FF41][4][/] [white]Verificación QA de Integridad Cruzada (Validador Cruzado PDF vs MD)[/]")
        self.console.print("    [bold #00FF41][5][/] [white]Generar / Verificar Embeddings Semánticos con Granite R2 (Vectores 768-dim)[/]")
        self.console.print("    [bold #00FF41][6][/] [white]Solo Post-Procesado Legal (Legalizer + Frontmatter YAML)[/]")
        self.console.print("    [bold #00FF41][7][/] [white]Ejecutar Suite Exhaustiva de QA Testing Offline (Air-Gapped)[/]")
        self.console.print("    [bold #00FF41][8][/] [white]Purgar Caché Temporal y Resetear Memoria RAM[/]")
        self.console.print("    [bold #FECF06][9][/] [white]Ver Registro Forense de Auditoría (audit_trail.jsonl)[/]")
        self.console.print("    [bold #00FF41][0][/] [dim white]Salir[/]")
        self.console.print()
        self.console.print("[bold #FECF06]  =========================================================================================[/]")

        opcion = Prompt.ask("  [bold #FECF06]Ingrese el número de la opción deseada [0-9][/]", choices=[str(i) for i in range(10)], default="1")
        return opcion

    def escanear_archivos(self) -> List[Dict[str, Any]]:
        """
        Escanea recursivamente INPUT_DIR para localizar archivos legales brutos
        y comprueba su estado de conversión en OUTPUT_DIR.
        """
        extensions = [
            "*.pdf", "*.PDF",
            "*.png", "*.PNG",
            "*.jpg", "*.JPG",
            "*.jpeg", "*.JPEG",
            "*.tiff", "*.TIFF",
            "*.bmp", "*.BMP",
            "*.docx", "*.DOCX",
            "*.doc", "*.DOC"
        ]

        if not INPUT_DIR.exists():
            INPUT_DIR.mkdir(parents=True, exist_ok=True)
        if not OUTPUT_DIR.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
        """Muestra una tabla con los archivos normativos y su estado actual."""
        archivos = self.escanear_archivos()

        if not archivos:
            self.console.print(f"[bold yellow][!] No se encontraron documentos en: {INPUT_DIR}[/]")
            return []

        tabla = Table(
            title="📂 Estado de Documentos Jurídicos en Corpus RAG",
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
        resumen.append(f"\n  Resumen del Corpus: ", style="bold")
        resumen.append(f"{total_archivos} documentos totales  |  ", style="white")
        resumen.append(f"{total_convertidos} convertidos  |  ", style="bold green")
        resumen.append(f"{pendientes} pendientes de transformar\n", style="bold yellow" if pendientes > 0 else "bold green")
        self.console.print(resumen)

        return archivos

    def convertir_archivo(self, archivo: Path) -> bool:
        """
        Convierte UN solo archivo respetando la inmutabilidad y la trazabilidad forense.
        Verifica el hash SHA-256 antes y después de la conversión.
        """
        if not archivo.exists():
            self.console.print(f"[bold red][ERROR] El archivo no existe: {archivo}[/]")
            return False

        self.console.print(f"\n[bold cyan]─── Iniciando Conversión Forense: {archivo.name} ───[/]")
        sha_antes = sha256_file(archivo)
        self.console.print(f"[dim]  [SHA-256 Pre-Conversión]:  {sha_antes}[/]")

        inicio = datetime.now()
        cmd = [
            sys.executable,
            str(BASE_DIR / "convert_normativas.py"),
            "--single-file", str(archivo)
        ]

        # Ejecutar subproceso heredando stdout para preservar indicadores de progreso y logs limpios
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
        else:
            self.console.print("  [bold green]✅ Integridad verificada: El archivo fuente se mantuvo 100% inalterado (Espejo Documental OK).[/]")

        if resultado.returncode == 0:
            self.console.print(f"  [bold green]✅ Conversión completada exitosamente en {duracion:.2f} segundos.[/]\n")
            return True
        else:
            self.console.print(f"  [bold red]❌ Error durante la conversión del documento (código de salida: {resultado.returncode}).[/]\n")
            return False

    def _seleccionar_y_convertir(self, archivos: Optional[List[Dict[str, Any]]] = None) -> None:
        """Permite al usuario seleccionar un documento específico para procesar de forma segura."""
        if not archivos:
            archivos = self.mostrar_tabla_estados()

        if not archivos:
            return

        pendientes = [a for a in archivos if not a["convertido"]]
        self.console.print("[bold yellow]Modo Seguro: Conversión individual (1 archivo por vez).[/]")

        if pendientes:
            self.console.print(f"Archivos pendientes disponibles: [cyan]{len(pendientes)}[/]")
        else:
            self.console.print("[green]Todos los archivos del corpus ya están convertidos. Puede seleccionar cualquiera para reprocesar.[/]")

        val_prompt = Prompt.ask("Ingrese el # de índice del archivo a convertir (o 'c' para cancelar)")
        if val_prompt.lower() == 'c':
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
        """Convierte todos los archivos pendientes de forma secuencial y segura."""
        archivos = self.escanear_archivos()
        pendientes = [a for a in archivos if not a["convertido"]]

        if not pendientes:
            self.console.print("[bold green]✅ No hay archivos pendientes. Todos los documentos están convertidos.[/]\n")
            return

        confirmar = Confirm.ask(
            f"Se detectaron [bold cyan]{len(pendientes)}[/] documentos pendientes. "
            f"¿Desea convertirlos secuencialmente (1 a la vez para no sobrecargar el equipo)?"
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
                ok = self.convertir_archivo(item["file_path"])
                if ok:
                    exitos += 1
                else:
                    fallos += 1
                progress.advance(tarea)

        self.console.print(f"\n[bold green]Proceso finalizado: {exitos} exitosos, {fallos} errores.[/]\n")

    def _registrar_auditoria(self, archivo: str, sha_antes: str,
                              sha_despues: str, integridad_ok: bool,
                              exito: bool, duracion_seg: float) -> None:
        """Agrega un registro inmutable al log forense audit_trail.jsonl."""
        from datetime import timezone
        entrada = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entorno": self.entorno,
            "backend_gpu": self.backend_gpu or "cpu",
            "archivo": archivo,
            "sha256_pdf_antes": sha_antes,
            "sha256_pdf_despues": sha_despues,
            "integridad_pdf": "OK" if integridad_ok else "ALERTA_MODIFICACION",
            "exito_conversion": exito,
            "duracion_seg": round(duracion_seg, 2)
        }
        try:
            with open(AUDIT_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entrada, ensure_ascii=False) + '\n')
        except Exception as e:
            self.console.print(f"[red][WARN] No se pudo escribir en audit_trail.jsonl: {e}[/]")

    def _ver_audit_log(self, ultimas: int = 20) -> None:
        """Muestra las últimas N operaciones del log forense audit_trail.jsonl."""
        if not AUDIT_FILE.exists():
            self.console.print("[yellow]No existe el archivo de auditoría audit_trail.jsonl todavía.[/]")
            return

        lineas = []
        try:
            with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
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
            title=f"📜 Registro Forense de Auditoría (Últimas {len(ultimas_entradas)} entradas)",
            title_style="bold #FECF06",
            box=box.ROUNDED,
            header_style="bold cyan"
        )
        tabla.add_column("Timestamp (UTC)", style="dim white", width=20)
        tabla.add_column("Archivo", style="bold white")
        tabla.add_column("SHA-256 Resumen", style="cyan", width=18)
        tabla.add_column("Integridad", justify="center", width=14)
        tabla.add_column("Estado", justify="center", width=10)
        tabla.add_column("Duración", justify="right", style="yellow", width=9)

        for e in ultimas_entradas:
            ts = e.get("timestamp") or e.get("timestamp_utc", "")
            ts_str = ts[:19].replace("T", " ") if ts else "N/A"
            archivo = e.get("archivo") or e.get("event_type") or e.get("notebook_id", "Evento")
            
            # Hash
            act_details = e.get("action_details", {}) if isinstance(e.get("action_details"), dict) else {}
            sha = e.get("sha256_pdf_antes") or e.get("signature_hash") or act_details.get("sha256_hash") or act_details.get("expected_hash") or ""
            sha_resumen = sha[:12] + "..." if sha else "N/A"

            # Integridad
            if "integridad_pdf" in e:
                integ = e["integridad_pdf"]
                integ_str = "[bold green]OK[/]" if integ == "OK" else "[bold red]ALERTA[/]"
            elif e.get("event_type") == "SHA_VERIFICATION_FAILURE":
                integ_str = "[bold red]FALLO_SHA[/]"
            else:
                integ_str = "[green]VÁLIDO[/]"

            # Estado
            if "exito_conversion" in e:
                exito_str = "[green]ÉXITO[/]" if e["exito_conversion"] else "[red]ERROR[/]"
            else:
                exito_str = "[cyan]AUDIT[/]"

            dur = f"{e.get('duracion_seg', 0):.1f}s" if "duracion_seg" in e else "-"

            tabla.add_row(
                ts_str,
                str(archivo)[:45],
                sha_resumen,
                integ_str,
                exito_str,
                dur
            )

        self.console.print(tabla)
        self.console.print(f"Total registros históricos: [bold cyan]{len(lineas)}[/]\n")

    def _ejecutar_subproceso(self, cmd: List[str], titulo: str) -> int:
        """Ejecuta un subproceso Python preservando la consola en tiempo real."""
        self.console.rule(f"[bold cyan]{titulo}[/]")
        res = subprocess.run(cmd, cwd=str(BASE_DIR))
        self.console.rule()
        return res.returncode

    def despachar(self, opcion: str) -> None:
        """Enruta la opción seleccionada."""
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
                titulo="Generación de Embeddings Semánticos IBM Granite R2"
            )
        elif opcion == "6":
            self._ejecutar_subproceso(
                [sys.executable, str(BASE_DIR / "convert_normativas.py"), "--post-process-only"],
                titulo="Post-Procesado Legal (Legalizer + Frontmatter YAML)"
            )
        elif opcion == "7":
            self._ejecutar_subproceso(
                [sys.executable, "-m", "unittest", "discover", "tests"],
                titulo="Suite Exhaustiva de QA Testing Offline"
            )
        elif opcion == "8":
            self._ejecutar_subproceso(
                [sys.executable, str(BASE_DIR / "cleanup.py")],
                titulo="Purgado de Caché Temporal y Memoria RAM"
            )
        elif opcion == "9":
            self._ver_audit_log(ultimas=25)
        elif opcion == "0":
            self.console.print("[bold green]  Sesión de JullBrain finalizada correctamente.[/]")
            sys.exit(0)

    def ejecutar(self) -> None:
        """Bucle interactivo principal del orquestador."""
        self.mostrar_banner()
        self.inicializar_gpu()

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
    # Soporte para banderas por línea de comando directas
    if len(sys.argv) > 1:
        flag = sys.argv[1].lower()
        orq = JullBrainOrquestador()

        if flag == "--web":
            print("[INIT] Iniciando Servidor Web FastAPI en http://127.0.0.1:8050...")
            cmd = [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8050"]
            subprocess.run(cmd, cwd=str(BASE_DIR))
            sys.exit(0)
        elif flag == "--full":
            orq.mostrar_banner()
            orq.inicializar_gpu()
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
        elif flag == "--audit":
            orq._ver_audit_log()
            sys.exit(0)
        elif flag == "--single-file" and len(sys.argv) > 2:
            orq.mostrar_banner()
            orq.inicializar_gpu()
            archivo = Path(sys.argv[2])
            if not archivo.exists() and (INPUT_DIR / sys.argv[2]).exists():
                archivo = INPUT_DIR / sys.argv[2]
            orq.convertir_archivo(archivo)
            sys.exit(0)

    # Si no hay argumentos, entra en modo interactivo
    app = JullBrainOrquestador()
    app.ejecutar()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSesión finalizada. Progreso guardado.")
        sys.exit(0)
