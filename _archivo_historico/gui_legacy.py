import os
import sys
import subprocess
import threading
import time
from pathlib import Path
import flet as ft

# Directories
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "normativas_pdf"
OUTPUT_DIR = BASE_DIR / "normativas_rag"
WORD_INPUT_DIR = BASE_DIR / "formatos_word"
WORD_OUTPUT_DIR = BASE_DIR / "formatos_rag"
CACHE_DIR = BASE_DIR / ".conversion_cache"
MANIFEST_PATH = CACHE_DIR / "manifest.json"
WORD_MANIFEST_PATH = CACHE_DIR / "manifest_word.json"

# Make sure folders exist
for folder in [INPUT_DIR, OUTPUT_DIR, WORD_INPUT_DIR, WORD_OUTPUT_DIR, CACHE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

class JullBrainApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "JullBrain — Interfaz de Conversión Inteligente"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#1a1a1a"
        self.page.window_width = 1100
        self.page.window_height = 800
        self.page.window_resizable = True
        
        # State
        self.running_process = None
        self.ocr_enabled = True
        self.force_reprocess = False
        self.no_chunks = False
        
        self.init_ui()
        self.refresh_stats()

    def init_ui(self):
        # Header Banner
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.BALANCE, color="#FECF06", size=40),
                    ft.Text("JullBrain", size=32, weight=ft.FontWeight.BOLD, color="#FECF06"),
                    ft.Container(
                        content=ft.Text("v2.0 - Powered by IBM Docling", size=12, italic=True, color="#888888"),
                        margin=ft.margin.only(top=10)
                    )
                ], alignment=ft.MainAxisAlignment.START),
                ft.Text("Mi Cerebro Personal — Procesamiento Automatizado de Normativas, Leyes y Formatos", size=14, color="#00FF41", weight=ft.FontWeight.W_500)
            ]),
            padding=20,
            bgcolor="#252525",
            border_radius=10,
            border=ft.border.all(1, "#333333")
        )

        # Left Panel: Controls & Quick Access
        self.btn_convert = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.PLAY_ARROW, color="#1a1a1a"),
                ft.Text("Iniciar Conversión", size=16, weight=ft.FontWeight.BOLD, color="#1a1a1a")
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#00FF41",
            height=50,
            on_click=self.start_conversion
        )
        
        self.btn_stop = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.icons.STOP, color="#ffffff"),
                ft.Text("Detener", size=16, weight=ft.FontWeight.BOLD, color="#ffffff")
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#FF5555",
            height=50,
            disabled=True,
            on_click=self.stop_conversion
        )

        self.ocr_checkbox = ft.Checkbox(label="Activar OCR (Recomendado para PDFs escaneados)", value=True, on_change=self.toggle_ocr)
        self.force_checkbox = ft.Checkbox(label="Forzar re-procesado (Ignorar caché)", value=False, on_change=self.toggle_force)
        self.chunks_checkbox = ft.Checkbox(label="Omitir generación de chunks individuales", value=False, on_change=self.toggle_chunks)

        controls_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Configuración", size=18, weight=ft.FontWeight.BOLD, color="#FECF06"),
                    ft.Divider(color="#444444"),
                    self.ocr_checkbox,
                    self.force_checkbox,
                    self.chunks_checkbox,
                    ft.VerticalDivider(height=10),
                    self.btn_convert,
                    self.btn_stop
                ], spacing=15),
                padding=20
            ),
            bgcolor="#252525"
        )

        # Quick Access Folders
        folders_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Carpetas del Sistema", size=18, weight=ft.FontWeight.BOLD, color="#FECF06"),
                    ft.Divider(color="#444444"),
                    ft.Row([
                        ft.IconButton(ft.icons.FOLDER, tooltip="PDFs de entrada", on_click=lambda _: self.open_folder(INPUT_DIR)),
                        ft.Text("Normativas Entrada (PDF/Img)", size=12)
                    ]),
                    ft.Row([
                        ft.IconButton(ft.icons.FOLDER_SPECIAL, tooltip="Salida Markdown de PDFs", on_click=lambda _: self.open_folder(OUTPUT_DIR)),
                        ft.Text("Normativas Salida (RAG Markdown)", size=12)
                    ]),
                    ft.Row([
                        ft.IconButton(ft.icons.FOLDER, tooltip="Documentos Word de entrada", on_click=lambda _: self.open_folder(WORD_INPUT_DIR)),
                        ft.Text("Formatos Entrada (Word .doc/.docx)", size=12)
                    ]),
                    ft.Row([
                        ft.IconButton(ft.icons.FOLDER_SPECIAL, tooltip="Salida Markdown de Word", on_click=lambda _: self.open_folder(WORD_OUTPUT_DIR)),
                        ft.Text("Formatos Salida (RAG Markdown)", size=12)
                    ])
                ], spacing=10),
                padding=20
            ),
            bgcolor="#252525"
        )

        # Right Panel: Tabs (Dashboard / File Explorer / Help)
        self.log_box = ft.TextField(
            multiline=True,
            read_only=True,
            min_lines=15,
            max_lines=20,
            text_size=12,
            bgcolor="#0d0d0d",
            border_color="#333333",
            color="#00FF41",
            value="[JullBrain] Listo para procesar documentos.\nPresione 'Iniciar Conversión' para comenzar."
        )

        self.progress_bar = ft.ProgressBar(value=0, color="#00FF41", bgcolor="#444444", visible=False)
        self.progress_text = ft.Text("", size=12, italic=True, visible=False)

        # Stats Cards
        self.stat_pdf_in = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color="#00FF41")
        self.stat_pdf_out = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color="#00FF41")
        self.stat_word_in = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color="#00FF41")
        self.stat_word_out = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color="#00FF41")

        stats_row = ft.Row([
            self.create_stat_card("PDFs Origen", self.stat_pdf_in, ft.icons.PICTURE_AS_PDF),
            self.create_stat_card("PDFs RAG (.md)", self.stat_pdf_out, ft.icons.MARKDOWN),
            self.create_stat_card("Word Origen", self.stat_word_in, ft.icons.ARTICLE),
            self.create_stat_card("Word RAG (.md)", self.stat_word_out, ft.icons.MARKDOWN),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

        # Tab 1: Console / Dashboard
        dashboard_tab = ft.Column([
            stats_row,
            ft.Text("Progreso de Conversión", size=18, weight=ft.FontWeight.BOLD, color="#FECF06"),
            self.progress_bar,
            self.progress_text,
            self.log_box
        ], spacing=15, scroll=ft.ScrollMode.AUTO)

        # Tab 2: File Explorer Table
        self.files_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Destino", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )
        explorer_tab = ft.Column([
            ft.Row([
                ft.Text("Explorador de Archivos", size=18, weight=ft.FontWeight.BOLD, color="#FECF06"),
                ft.IconButton(ft.icons.REFRESH, on_click=lambda _: self.refresh_files_list())
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color="#444444"),
            ft.Container(self.files_table, border_radius=10, bgcolor="#252525", padding=10)
        ], spacing=15, scroll=ft.ScrollMode.AUTO)

        # Tab 3: Help / Licenses
        help_tab = ft.Column([
            ft.Text("Manual de Uso y Licencias", size=18, weight=ft.FontWeight.BOLD, color="#FECF06"),
            ft.Divider(color="#444444"),
            ft.Text("JullBrain es una herramienta para procesar, limpiar y estructurar PDFs y Word legados hacia Markdown listo para RAG (Retrieval-Augmented Generation) en sistemas de Inteligencia Artificial.", size=14),
            ft.Markdown(
                """
### Licencias
Este software está distribuido bajo la **Licencia Apache 2.0**.

* **Desarrollador de JullBrain**: Jull Ortiz (Copyright (c) 2026)
* **Motor de Extracción**: IBM Docling (Licencia MIT, Copyright (c) 2024-present IBM Corp.)
                """
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO)

        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Consola de Conversión", icon=ft.icons.TERMINAL, content=dashboard_tab),
                ft.Tab(text="Archivos Locales", icon=ft.icons.FOLDER_OPEN, content=explorer_tab),
                ft.Tab(text="Acerca de", icon=ft.icons.HELP_OUTLINE, content=help_tab),
            ],
            expand=1
        )

        # Layout Assembly
        self.page.add(
            header,
            ft.Row([
                ft.Column([controls_card, folders_card], width=350, spacing=20),
                ft.Container(tabs, expand=True, padding=ft.padding.only(left=20))
            ], alignment=ft.MainAxisAlignment.START, expand=True)
        )

    def create_stat_card(self, title: str, text_control: ft.Text, icon):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color="#FECF06", size=24),
                        ft.Text(title, size=12, color="#aaaaaa")
                    ]),
                    ft.Container(text_control, alignment=ft.alignment.center)
                ], alignment=ft.MainAxisAlignment.CENTER),
                width=160,
                height=80,
                padding=10
            ),
            bgcolor="#252525"
        )

    def toggle_ocr(self, e):
        self.ocr_enabled = e.control.value

    def toggle_force(self, e):
        self.force_reprocess = e.control.value

    def toggle_chunks(self, e):
        self.no_chunks = e.control.value

    def open_folder(self, path: Path):
        try:
            os.startfile(str(path))
        except Exception as e:
            self.write_log(f"[ERROR] No se pudo abrir la carpeta: {e}")

    def write_log(self, text: str):
        self.log_box.value += "\n" + text
        self.page.update()

    def refresh_stats(self):
        pdf_in = len([f for f in INPUT_DIR.glob("*") if f.suffix.lower() in [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]])
        pdf_out = len(list(OUTPUT_DIR.glob("*.md")))
        word_in = len([f for f in WORD_INPUT_DIR.glob("*") if f.suffix.lower() in [".doc", ".docx"]])
        word_out = len(list(WORD_OUTPUT_DIR.glob("*.md")))

        self.stat_pdf_in.value = str(pdf_in)
        self.stat_pdf_out.value = str(pdf_out)
        self.stat_word_in.value = str(word_in)
        self.stat_word_out.value = str(word_out)
        self.page.update()
        
        self.refresh_files_list()

    def refresh_files_list(self):
        rows = []
        
        # PDFs & Images
        for f in INPUT_DIR.glob("*"):
            if f.suffix.lower() in [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                dest = OUTPUT_DIR / f"{f.stem}.md"
                status = "Convertido" if dest.exists() else "Pendiente"
                status_color = "#00FF41" if dest.exists() else "#FECF06"
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f.name)),
                    ft.DataCell(ft.Text("PDF/Imagen", color="#43a047")),
                    ft.DataCell(ft.Text(status, color=status_color)),
                    ft.DataCell(ft.Text(f"{f.stem}.md" if dest.exists() else "-")),
                ]))
                
        # Word Files
        for f in WORD_INPUT_DIR.glob("*"):
            if f.suffix.lower() in [".doc", ".docx"] and not f.name.startswith("~"):
                dest = WORD_OUTPUT_DIR / f"{f.stem}.md"
                status = "Convertido" if dest.exists() else "Pendiente"
                status_color = "#00FF41" if dest.exists() else "#FECF06"
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f.name)),
                    ft.DataCell(ft.Text("Documento Word", color="#1e88e5")),
                    ft.DataCell(ft.Text(status, color=status_color)),
                    ft.DataCell(ft.Text(f"{f.stem}.md" if dest.exists() else "-")),
                ]))
                
        self.files_table.rows = rows
        self.page.update()

    def start_conversion(self, e):
        self.btn_convert.disabled = True
        self.btn_stop.disabled = False
        self.progress_bar.visible = True
        self.progress_bar.value = None # Indeterminate spinner
        self.progress_text.visible = True
        self.progress_text.value = "Iniciando pipeline de IA..."
        self.log_box.value = "[JullBrain] Iniciando proceso..."
        self.page.update()

        # Run process in a thread to keep GUI responsive
        threading.Thread(target=self.run_conversion_process, daemon=True).start()

    def run_conversion_process(self):
        python_exe = BASE_DIR / "docling_env" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = sys.executable if "python" in Path(sys.executable).name.lower() else "python"
            
        args = [str(python_exe), str(BASE_DIR / "convert_normativas.py")]
        
        if not self.ocr_enabled:
            args.append("--no-ocr")
        if self.force_reprocess:
            args.append("--force-reprocess")
        if self.no_chunks:
            args.append("--no-chunks")

        # Simulate user input 'S' using stdin
        try:
            self.running_process = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            # Send 'S\n' immediately when the script asks
            # (The script starts, scans files, prints table, then asks confirmation)
            # We can read output and when we see the confirmation prompt, we send 'S\n'.
            
            # Start background thread to feed 'S' to stdin
            threading.Thread(target=self.auto_confirm, daemon=True).start()

            for line in iter(self.running_process.stdout.readline, ''):
                self.write_log(line.strip())
                self.parse_line_for_progress(line)
                
            self.running_process.wait()
            
        except Exception as ex:
            self.write_log(f"\n[ERROR] Proceso abortado: {ex}")
            
        finally:
            self.running_process = None
            self.btn_convert.disabled = False
            self.btn_stop.disabled = True
            self.progress_bar.visible = False
            self.progress_text.visible = False
            self.refresh_stats()

    def auto_confirm(self):
        # Wait a small delay and send 'S' to confirm setup
        time.sleep(2)
        if self.running_process and self.running_process.stdin:
            try:
                self.running_process.stdin.write("S\n")
                self.running_process.stdin.flush()
            except Exception:
                pass

    def parse_line_for_progress(self, line: str):
        # Search for progress patterns like "Exitoso:" or "Falló:" or "Progreso General"
        if "Exitoso:" in line or "Falló:" in line:
            self.progress_text.value = f"Procesando: {line.strip()}"
            self.page.update()
        elif "Progreso General" in line:
            # rich progress text looks like: Progreso General ━━━━━━━━━━━━━━━━━━━━ 1/2 0:00:01
            try:
                parts = line.split()
                for p in parts:
                    if "/" in p:
                        done, total = map(int, p.split("/"))
                        self.progress_bar.value = done / total
                        self.progress_text.value = f"Progreso: {done} de {total} archivos completados"
                        self.page.update()
                        break
            except Exception:
                pass

    def stop_conversion(self, e):
        if self.running_process:
            try:
                self.running_process.terminate()
                self.write_log("\n[!] Conversión cancelada por el usuario.")
            except Exception as ex:
                self.write_log(f"\n[ERROR] No se pudo detener: {ex}")
        self.btn_convert.disabled = False
        self.btn_stop.disabled = True
        self.progress_bar.visible = False
        self.progress_text.visible = False
        self.page.update()

def main(page: ft.Page):
    JullBrainApp(page)

if __name__ == "__main__":
    ft.app(target=main)
