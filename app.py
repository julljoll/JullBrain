import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.colored_header import colored_header
from streamlit_card import card
from streamlit_lottie import st_lottie
from annotated_text import annotated_text
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_ace import st_ace

import os
import sys
import psutil
import time
import yaml
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime

# Importar funciones de validación local
try:
    from validator import validate_md_file, ValidationReport
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False

# Configuración de página
st.set_page_config(
    page_title="JullBrain IA - Orquestador Juridico",
    page_icon="img/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores JullBrain: Estilos visuales complementarios
CSS_THEME = """
<style>
    /* Bordes y acentos visuales complementarios */
    [data-testid="stSidebar"] {
        border-right: 2px solid #FECF06;
    }
    
    /* Tipografía y colores de encabezados */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Botones premium */
    .stButton>button {
        background-color: #FECF06 !important;
        color: #1a1400 !important;
        font-weight: bold !important;
        border: 2px solid #00FF41 !important;
        border-radius: 4px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00FF41 !important;
        color: #1a1400 !important;
        box-shadow: 0 0 10px #00FF41;
    }
    
    /* Cajas y terminales */
    code, pre {
        background-color: #1a1400 !important;
        color: #00FF41 !important;
        border: 1px solid #FECF06 !important;
    }

    /* Estilización de Bloques de Arquitectura */
    .arch-card {
        background-color: #3b2e00;
        border: 2px solid #FECF06;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        text-align: center;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.4);
    }
    .arch-card-input {
        border-color: #ff4b4b;
    }
    .arch-card-process {
        border-color: #FECF06;
    }
    .arch-card-output {
        border-color: #00FF41;
    }
    .arch-title {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 10px;
        color: #FECF06;
        font-family: 'Courier New', Courier, monospace;
    }
    .arch-body {
        font-size: 13px;
        color: #00FF41;
    }
</style>
"""
st.markdown(CSS_THEME, unsafe_allow_html=True)

# Rutas globales
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "normativas_pdf"
OUTPUT_DIR = BASE_DIR / "normativas_rag"
CHUNKS_DIR = BASE_DIR / "normativas_chunks"
CACHE_DIR = BASE_DIR / ".conversion_cache"
MANIFEST_PATH = CACHE_DIR / "manifest.json"

# Asegurar directorios
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CHUNKS_DIR.mkdir(exist_ok=True)

# ─── NAVEGACIÓN LATERAL ───
with st.sidebar:
    st.image("img/logo.svg", width=120)
    st.markdown("### **JULLBRAIN RAG**")
    st.markdown("---")
    
    menu_selected = option_menu(
        menu_title="Navegacion",
        options=["Pipeline de Arquitectura", "Orquestar Conversiones", "Integridad y Reportes", "Editor de Leyes RAG", "Ajustes del Pipeline"],
        icons=["diagram-3", "play-circle", "shield-check", "pencil-square", "gear"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"background-color": "#3b2e00"},
            "icon": {"color": "#FECF06", "font-size": "18px"},
            "nav-link": {"color": "#00FF41", "font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#524000"},
            "nav-link-selected": {"background-color": "#524000", "color": "#FECF06"},
        }
    )
    st.markdown("---")
    st.markdown("**Desarrollado Por:**  \nJull Ortiz")
    st.markdown("**Rol:**  \nArquitecto de Datos con y para la IA Juridica")
    st.markdown("**Licencia:** Apache 2.0")

# Escaneo común de archivos
pdfs_files = list(INPUT_DIR.rglob("*.pdf")) + list(INPUT_DIR.rglob("*.docx")) + list(INPUT_DIR.rglob("*.doc"))
md_files = list(OUTPUT_DIR.rglob("*.md"))
chunk_jsons = list(CHUNKS_DIR.rglob("hierarchical_chunks.json"))

# ─── MÓDULO 1: PIPELINE DE ARQUITECTURA (Siguiendo jullbrain_architecture.svg) ───
if menu_selected == "Pipeline de Arquitectura":
    colored_header(label="🏛️ JullBrain RAG-Pipeline - Arquitectura de Datos", description="Estructura e interaccion de capas del pipeline basadas en jullbrain_architecture.svg", color_name="yellow-70")
    
    # KPIs Rápidos
    total_articles = 0
    for md_path in md_files:
        try:
            content = md_path.read_text(encoding="utf-8")
            if content.startswith("---"):
                end_fm = content.find("\n---\n", 4)
                if end_fm > 0:
                    fm_data = yaml.safe_load(content[3:end_fm])
                    if fm_data and "articulos_detectados" in fm_data:
                        total_articles += int(fm_data["articulos_detectados"])
        except Exception:
            pass
            
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Documentos Origen (PDF/Word)", value=len(pdfs_files))
    col2.metric(label="Documentos Estructurados (RAG)", value=len(md_files))
    col3.metric(label="Articulos Juridicos Identificados", value=total_articles)
    col4.metric(label="Archivos de Chunks (RAGFlow)", value=len(chunk_jsons))
    
    st.markdown("---")
    
    # Distribución en 3 Columnas siguiendo jullbrain_architecture.svg
    st.write("### 🗺️ Visualizacion del Pipeline de Trabajo (Fases)")
    
    arch_col1, arch_col2, arch_col3 = st.columns(3)
    
    with arch_col1:
        st.markdown(f"""
        <div class="arch-card arch-card-input">
            <div class="arch-title">📥 1. FUENTES DE INGESTAS (Inputs)</div>
            <div class="arch-body">
                <b>Carpeta Origen:</b> normativas_pdf/<br><br>
                Archivos en cola para IA:<br>
                • PDFs de Leyes Venezolanas<br>
                • Actas e Imagenes de Evidencia<br>
                • Documentos Word (.doc, .docx)<br><br>
                <b>Total Archivos Detectados:</b> {len(pdfs_files)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with arch_col2:
        # Calcular archivos de cache
        cache_count = 0
        if MANIFEST_PATH.exists():
            try:
                manifest_data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
                cache_count = len(manifest_data)
            except Exception:
                pass
                
        st.markdown(f"""
        <div class="arch-card arch-card-process">
            <div class="arch-title">⚙️ 2. ENTORNO DE PROCESAMIENTO (docling_env)</div>
            <div class="arch-body">
                <b>Motor de Conversion:</b> IBM Docling<br>
                <b>Optimizacion:</b> Cache SHA-256 (manifest.json)<br><br>
                <b>Pipeline de Orquestacion:</b><br>
                • legalizer.py (Estructura articulos)<br>
                • metadata_extractor.py (Frontmatter YAML)<br>
                • validator.py (Integridad y control de saltos)<br><br>
                <b>Archivos en Cache:</b> {cache_count}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with arch_col3:
        st.markdown(f"""
        <div class="arch-card arch-card-output">
            <div class="arch-title">📤 3. CORPUS ESTRUCTURADO (Outputs)</div>
            <div class="arch-body">
                <b>Directorio RAG:</b> normativas_rag/<br>
                <b>Directorio Chunks:</b> normativas_chunks/<br><br>
                Entregables listos para RAGFlow:<br>
                • Markdown con YAML frontmatter e Indices<br>
                • Chunks jerarquicos atómicos (JSON)<br><br>
                <b>Leyes convertidas:</b> {len(md_files)}<br>
                <b>Chunks atómicos:</b> {len(chunk_jsons)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Recursos de hardware
    st.subheader("💻 Monitoreo de Recursos del Servidor")
    h_col1, h_col2, h_col3 = st.columns(3)
    cpu_use = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('.')
    
    with h_col1:
        st.progress(cpu_use / 100.0)
        st.markdown(f"**Uso de CPU:** {cpu_use}%")
    with h_col2:
        st.progress(ram.percent / 100.0)
        st.markdown(f"**Uso de RAM:** {ram.percent}% ({ram.available / 1024**3:.1f} GB Libres de {ram.total / 1024**3:.1f} GB)")
    with h_col3:
        st.progress(disk.percent / 100.0)
        st.markdown(f"**Almacenamiento Libre:** {disk.free / 1024**3:.1f} GB ({disk.percent}% Utilizado)")

# ─── MÓDULO 2: ORQUESTAR CONVERSIONES (Ejecuta Docling y Scripts de Ingesta/Caché) ───
elif menu_selected == "Orquestar Conversiones":
    colored_header(label="🚀 Ingesta e Indexacion (Fase 2 de Arquitectura)", description="Ejecuta la conversion de archivos origen en subprocesos usando la cache SHA-256", color_name="yellow-70")
    
    table_data = []
    for f in pdfs_files:
        try:
            rel_p = f.relative_to(INPUT_DIR)
        except ValueError:
            rel_p = Path(f.name)
            
        out_md = OUTPUT_DIR / rel_p.with_suffix(".md")
        converted = out_md.exists()
        
        table_data.append({
            "Archivo": f.name,
            "Ruta Relativa": str(rel_p.parent),
            "Extension": f.suffix.upper(),
            "Tamano (KB)": round(f.stat().st_size / 1024, 1),
            "Estado": "Ya Convertido (OK)" if converted else "Pendiente (..)"
        })
        
    st.write("### Archivos Detectados en Carpeta de Entrada `normativas_pdf/`")
    if table_data:
        import pandas as pd
        df_files = pd.DataFrame(table_data)
        
        grid_options = GridOptionsBuilder.from_dataframe(df_files)
        grid_options.configure_selection(selection_mode="multiple", use_checkbox=True)
        grid_options.configure_pagination(paginationAutoPageSize=True)
        
        grid_response = AgGrid(
            df_files,
            gridOptions=grid_options.build(),
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            theme="alpine"
        )
    else:
        st.info("No se encontraron archivos en la carpeta normativas_pdf")
        
    st.markdown("---")
    
    # Control de ejecución
    c_col1, c_col2, c_col3 = st.columns(3)
    
    run_normal = c_col1.button("▶️ Iniciar Conversion (Cache)")
    run_force = c_col2.button("🔄 Reprocesar Todo (Forzar)")
    run_post = c_col3.button("📝 Ejecutar Post-Procesado RAG")
    
    if run_normal or run_force or run_post:
        if run_post:
            st.info("Ejecutando post-procesado legal en todos los archivos...")
            cmd = [sys.executable, str(BASE_DIR / "convert_normativas.py"), "--post-process-only"]
            
            st.write("### 📺 Consola del Pipeline en Vivo")
            console_area = st.empty()
            
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    bufsize=1
                )
                
                log_lines = []
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        log_lines.append(line.strip())
                        console_area.code("\n".join(log_lines[-25:]))
                        
                rc = process.poll()
                if rc == 0:
                    st.success("🎉 Post-procesado finalizado con éxito.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error en la ejecucion. Codigo de salida: {rc}")
            except Exception as e:
                st.error(f"Error iniciando el subproceso: {e}")
        else:
            # Conversión/Transformación pesada (una por una con barra de progreso)
            selected_filenames = []
            if grid_response and 'selected_rows' in grid_response and grid_response['selected_rows'] is not None:
                sel_rows = grid_response['selected_rows']
                import pandas as pd
                if isinstance(sel_rows, pd.DataFrame):
                    if not sel_rows.empty and 'Archivo' in sel_rows.columns:
                        selected_filenames = sel_rows['Archivo'].tolist()
                elif isinstance(sel_rows, list):
                    selected_filenames = [r['Archivo'] for r in sel_rows if isinstance(r, dict) and 'Archivo' in r]
                elif isinstance(sel_rows, dict) and 'rows' in sel_rows:
                    selected_filenames = [r['Archivo'] for r in sel_rows['rows'] if isinstance(r, dict) and 'Archivo' in r]

            files_to_process = []
            if run_force:
                st.warning("Eliminando cache y rehaciendo conversion desde cero...")
                if CACHE_DIR.exists():
                    import shutil
                    shutil.rmtree(CACHE_DIR, ignore_errors=True)
                for md_f in OUTPUT_DIR.rglob("*.md"):
                    try:
                        md_f.unlink()
                    except Exception:
                        pass
                files_to_process = pdfs_files
            else:
                if selected_filenames:
                    files_to_process = [f for f in pdfs_files if f.name in selected_filenames]
                else:
                    # Iniciar conversión de pendientes
                    for f in pdfs_files:
                        try:
                            rel_p = f.relative_to(INPUT_DIR)
                        except ValueError:
                            rel_p = Path(f.name)
                        out_md = OUTPUT_DIR / rel_p.with_suffix(".md")
                        if not out_md.exists():
                            files_to_process.append(f)

            if not files_to_process:
                st.info("No hay archivos pendientes para procesar.")
            else:
                st.write(f"### ⚙️ Procesando {len(files_to_process)} normativas...")
                progress_bar = st.progress(0.0)
                status_text = st.empty()
                console_area = st.empty()
                
                success_count = 0
                fail_count = 0
                total_files = len(files_to_process)
                
                for idx, f_path in enumerate(files_to_process):
                    progress_val = idx / total_files
                    progress_bar.progress(progress_val)
                    status_text.markdown(f"🔄 **Archivo {idx + 1} de {total_files}:** `{f_path.name}` en procesamiento...")
                    
                    cmd = [sys.executable, str(BASE_DIR / "convert_normativas.py"), "--file-path", str(f_path)]
                    
                    log_lines = [f"--- Iniciando procesamiento de: {f_path.name} ---"]
                    console_area.code("\n".join(log_lines))
                    
                    try:
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            encoding="utf-8",
                            bufsize=1
                        )
                        
                        while True:
                            line = process.stdout.readline()
                            if not line and process.poll() is not None:
                                break
                            if line:
                                log_lines.append(line.strip())
                                console_area.code("\n".join(log_lines[-25:]))
                                
                        rc = process.poll()
                        if rc == 0:
                            success_count += 1
                            log_lines.append(f"--- [OK] Finalizado exitosamente: {f_path.name} ---")
                        else:
                            fail_count += 1
                            log_lines.append(f"--- [ERROR] Falló procesamiento (código {rc}): {f_path.name} ---")
                        console_area.code("\n".join(log_lines[-25:]))
                    except Exception as e:
                        fail_count += 1
                        st.error(f"Error procesando {f_path.name}: {e}")
                
                progress_bar.progress(1.0)
                status_text.markdown(f"✅ **Procesamiento completado:** {success_count} exitosos, {fail_count} fallidos.")
                
                if fail_count == 0:
                    st.success("🎉 Todas las normativas se transformaron con éxito.")
                else:
                    st.warning(f"⚠️ Proceso finalizado con {fail_count} errores.")
                
                time.sleep(2)
                st.rerun()

# ─── MÓDULO 3: INTEGRIDAD Y REPORTES (Validador de Integridad Legal) ───
elif menu_selected == "Integridad y Reportes":
    colored_header(label="🛡️ Integridad Legal y Auditoria Forense", description="Filtros de trazabilidad y deteccion de inconsistencias de folios usando validator.py", color_name="yellow-70")
    
    if not md_files:
        st.info("No hay archivos estructurados en RAG para auditar.")
    elif not VALIDATOR_AVAILABLE:
        st.error("Modulo validator.py no disponible.")
    else:
        reports = []
        for f_path in md_files:
            rep = validate_md_file(str(f_path))
            reports.append(rep)
            
        # Tabla resumen
        res_data = []
        for r in reports:
            res_data.append({
                "Archivo": r.filename,
                "Articulos": r.articles_found,
                "Score de Calidad": f"{r.quality_score:.1%}",
                "Frontmatter": "OK" if r.has_frontmatter else "Falta",
                "Estado": r.overall_status
            })
            
        import pandas as pd
        df_res = pd.DataFrame(res_data)
        st.dataframe(df_res, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔍 Detalle de Leyes Auditadas")
        
        selected_file = st.selectbox("Selecciona un documento para ver reporte completo:", [r.filename for r in reports])
        
        if selected_file:
            report = next(r for r in reports if r.filename == selected_file)
            
            st.markdown(f"#### **Ley:** {report.filename}")
            c_score = report.quality_score
            st.metric(label="Score de Calidad General", value=f"{c_score:.1%}")
            
            # st-annotated-text para fallas
            if report.sequence_gaps:
                st.warning("⚠️ Se detectaron saltos de secuencia (Articulos faltantes):")
                gap_elements = []
                for gap in report.sequence_gaps:
                    gap_elements.append(f"Faltan articulos: ")
                    gap_elements.append((str(gap), "SALTOS", "#ff4b4b"))
                    gap_elements.append(" | ")
                annotated_text(*gap_elements[:-1])
            else:
                st.success("✅ Secuencia cronologica de articulos correcta.")
                
            if report.duplicates:
                st.warning("⚠️ Articulos Duplicados en el archivo:")
                dup_elements = []
                for d in report.duplicates:
                    dup_elements.append(f"Duplicado: ")
                    dup_elements.append((f"Art. {d}", "DUPLICADO", "#ffaa00"))
                    dup_elements.append(" | ")
                annotated_text(*dup_elements[:-1])
                
            if report.short_articles:
                st.info(f"ℹ️ Articulos extremadamente cortos (< 50 caracteres): {report.short_articles}")

# ─── MÓDULO 4: EDITOR DE LEYES RAG (Ace Editor interactivo) ───
elif menu_selected == "Editor de Leyes RAG":
    colored_header(label="📝 Visor y Editor de Conocimientos RAG (Outputs)", description="Corrige fallas del OCR o ajusta metadatos del YAML frontmatter directamente", color_name="yellow-70")
    
    if not md_files:
        st.info("No hay archivos estructurados en RAG para editar.")
    else:
        file_options = {f.name: f for f in md_files}
        selected_name = st.selectbox("Selecciona el archivo estructurado para editar:", list(file_options.keys()))
        
        if selected_name:
            file_path = file_options[selected_name]
            original_content = file_path.read_text(encoding="utf-8", errors="replace")
            
            st.markdown(f"📄 **Ruta Fisica:** `{file_path}`")
            
            # Editor de Streamlit Ace
            edited_content = st_ace(
                value=original_content,
                language="markdown",
                theme="monokai",
                keybinding="vscode",
                height=450,
                auto_update=False
            )
            
            if edited_content != original_content:
                if st.button("💾 Guardar Cambios"):
                    try:
                        file_path.write_text(edited_content, encoding="utf-8")
                        st.success("✅ Archivo guardado correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar el archivo: {e}")

# ─── MÓDULO 5: AJUSTES DEL PIPELINE ───
elif menu_selected == "Ajustes del Pipeline":
    colored_header(label="⚙️ Parametros y Ajustes del Pipeline", description="Ajustes de variables de entorno y procesamiento de IBM Docling", color_name="yellow-70")
    
    st.markdown("### Parametros de Procesamiento")
    ocr_active = st.checkbox("Activar OCR (Recomendado para escaneos de Gaceta)", value=True)
    chunks_active = st.checkbox("Generar Chunks Jerarquicos JSON para RAGFlow", value=True)
    
    st.markdown("---")
    st.markdown("### Configuracion de Licencia y Encabezados")
    st.info("El encabezado de los archivos Markdown se sincroniza automaticamente con el banner de la consola de orquestador_JullBrain.bat. Puedes editar la variable `HEADER_TEMPLATE` en `convert_normativas.py` para modificaciones permanentes.")
