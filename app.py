import streamlit as st
from streamlit_option_menu import option_menu
from annotated_text import annotated_text
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_ace import st_ace

import os
import sys
import psutil
import time
import yaml
import json
import hashlib
import platform
import subprocess
from pathlib import Path
from datetime import datetime

# Importar funciones de validación local
try:
    from validator import validate_md_file, ValidationReport, cross_validate_against_pdf
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False

# Importar motor de embeddings Granite
try:
    from granite_embedder import GraniteEmbedder
    EMBEDDER_AVAILABLE = True
except ImportError:
    EMBEDDER_AVAILABLE = False

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
    
    /* Semáforo de estados */
    .status-green { color: #00FF41; font-weight: bold; }
    .status-amber { color: #FECF06; font-weight: bold; }
    .status-red   { color: #ff4b4b; font-weight: bold; }
</style>
"""
st.markdown(CSS_THEME, unsafe_allow_html=True)

# ─── CONFIGURACIÓN PERSISTENTE ───
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "pipeline_config.json"

def load_pipeline_config() -> dict:
    """Carga la configuración persistente del pipeline."""
    defaults = {
        "ocr_activo": True,
        "generar_chunks": True,
        "min_article_chars": 50,
        "quality_threshold_critical": 0.90,
        "quality_threshold_warning": 0.95,
        "granite_model": "granite4.1:8b",
        "granite_temperature": 0.15,
        "ragflow_api_url": "http://localhost:9380/api/v1",
        "ragflow_embedding_model": "granite-embedding-30m-english",
        "granite_context_window": 128000
    }
    if CONFIG_PATH.exists():
        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            defaults.update(loaded)
        except Exception:
            pass
    return defaults

def save_pipeline_config(config: dict):
    """Guarda la configuración persistente del pipeline."""
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

PIPELINE_CONFIG = load_pipeline_config()

# Rutas globales
INPUT_DIR = BASE_DIR / "normativas_pdf"
OUTPUT_DIR = BASE_DIR / "normativas_rag"
CHUNKS_DIR = BASE_DIR / "normativas_chunks"
CACHE_DIR = BASE_DIR / ".conversion_cache"
MANIFEST_PATH = CACHE_DIR / "manifest.json"

# Asegurar directorios
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CHUNKS_DIR.mkdir(exist_ok=True)

# ─── FUNCIONES AUXILIARES ───
def sha256_of_file(file_path: Path) -> str:
    """Calcula SHA-256 de un archivo."""
    h = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def estimate_corpus_tokens() -> int:
    """Estima tokens del corpus recorriendo chunks JSON."""
    total_words = 0
    for chunk_file in CHUNKS_DIR.rglob("hierarchical_chunks.json"):
        try:
            data = json.loads(chunk_file.read_text(encoding="utf-8"))
            for chunk in data:
                text = chunk.get("text", "") or chunk.get("texto", "")
                total_words += len(text.split())
        except Exception:
            pass
    return int(total_words * 1.3)  # Estimación tokens ≈ palabras × 1.3

def get_category_distribution(md_files_list: list) -> dict:
    """Obtiene distribución de documentos por categoría jurídica."""
    dist = {}
    for md_path in md_files_list:
        try:
            content = md_path.read_text(encoding="utf-8")
            if content.startswith("---"):
                end_fm = content.find("\n---\n", 4)
                if end_fm > 0:
                    fm_data = yaml.safe_load(content[3:end_fm])
                    if fm_data and "categorias" in fm_data:
                        cats = fm_data["categorias"]
                        if isinstance(cats, list):
                            for cat in cats:
                                dist[cat] = dist.get(cat, 0) + 1
                        elif isinstance(cats, str):
                            dist[cats] = dist.get(cats, 0) + 1
        except Exception:
            pass
    return dist

# ─── NAVEGACIÓN LATERAL ───
with st.sidebar:
    st.image("img/logo.svg", width=120)
    st.markdown("### **JULLBRAIN RAG**")
    st.markdown("---")
    
    menu_selected = option_menu(
        menu_title="Navegacion",
        options=[
            "Pipeline de Arquitectura",
            "Orquestar Conversiones",
            "Integridad y Reportes",
            "Cadena de Custodia",
            "Editor de Leyes RAG",
            "🧬 Granite Embedding",
            "Ajustes del Pipeline"
        ],
        icons=["diagram-3", "play-circle", "shield-check", "link-45deg", "pencil-square", "cpu", "gear"],
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

# ═══════════════════════════════════════════════════════════════════════
# MÓDULO 1: PIPELINE DE ARQUITECTURA + ESTADÍSTICAS DEL CORPUS
# ═══════════════════════════════════════════════════════════════════════
if menu_selected == "Pipeline de Arquitectura":
    st.header("🏛️ JullBrain RAG-Pipeline — Arquitectura de Datos", divider="orange")
    st.caption("Estructura e interaccion de capas del pipeline + estadisticas del corpus para IBM Granite 4.0")
    
    # KPIs Rápidos Ampliados
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
    
    # Estimación de tokens (cacheada en session_state)
    if 'corpus_tokens' not in st.session_state:
        st.session_state.corpus_tokens = estimate_corpus_tokens()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="Documentos Origen", value=len(pdfs_files))
    col2.metric(label="Documentos RAG", value=len(md_files))
    col3.metric(label="Articulos Juridicos", value=total_articles)
    col4.metric(label="Archivos Chunks", value=len(chunk_jsons))
    col5.metric(label="Tokens Estimados", value=f"{st.session_state.corpus_tokens:,}")
    
    st.markdown("---")
    
    # Distribución en 3 Columnas — Diagrama de Arquitectura
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
    
    # Distribución por Categoría Jurídica
    st.subheader("📊 Distribución del Corpus por Categoría Jurídica")
    cat_dist = get_category_distribution(md_files)
    if cat_dist:
        import pandas as pd
        df_cats = pd.DataFrame(
            [{"Categoria": k.title(), "Documentos": v} for k, v in sorted(cat_dist.items(), key=lambda x: -x[1])]
        )
        st.bar_chart(df_cats.set_index("Categoria"))
    else:
        st.info("No se detectaron categorias juridicas en el YAML frontmatter de los archivos procesados.")
    
    st.markdown("---")
    
    # Tabla de Readiness RAGFlow
    st.subheader("✅ Readiness del Corpus para RAGFlow + IBM Granite 4.0")
    
    readiness_data = []
    all_ready = True
    for md_path in md_files:
        md_name = md_path.name
        has_fm = False
        art_count = 0
        try:
            content = md_path.read_text(encoding="utf-8")
            has_fm = content.startswith("---")
            if has_fm:
                end_fm = content.find("\n---\n", 4)
                if end_fm > 0:
                    fm_data = yaml.safe_load(content[3:end_fm])
                    art_count = fm_data.get("articulos_detectados", 0) if fm_data else 0
        except Exception:
            pass
        
        # Buscar chunks JSON correspondiente
        has_chunks = any(
            md_path.stem.lower() in str(cj.parent).lower()
            for cj in chunk_jsons
        )
        
        ready = has_fm and has_chunks
        if not ready:
            all_ready = False
        
        readiness_data.append({
            "Normativa": md_name[:50],
            "Articulos": art_count,
            "YAML Frontmatter": "✅" if has_fm else "❌",
            "Chunks JSON": "✅" if has_chunks else "❌",
            "Estado": "Listo" if ready else "Incompleto"
        })
    
    if readiness_data:
        import pandas as pd
        df_ready = pd.DataFrame(readiness_data)
        st.dataframe(df_ready, width="stretch")
        
        if all_ready and readiness_data:
            st.success("🎉 Corpus 100% listo para indexacion en RAGFlow.")
        elif readiness_data:
            incomplete = sum(1 for r in readiness_data if r["Estado"] == "Incompleto")
            st.warning(f"⚠️ {incomplete} documentos incompletos. Ejecute la conversion o el post-procesado.")
    else:
        st.info("No hay documentos procesados aun.")
    
    st.markdown("---")
    
    # Compatibilidad con Granite 4.0
    st.subheader("🤖 Compatibilidad con IBM Granite 4.0")
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    g_col1.metric("Ventana de Contexto", f"{PIPELINE_CONFIG['granite_context_window']:,} tokens")
    g_col2.metric("Modelo de Inferencia", PIPELINE_CONFIG['granite_model'])
    g_col3.metric("Temperatura Juridica", str(PIPELINE_CONFIG['granite_temperature']))
    g_col4.metric("Modelo Embeddings", PIPELINE_CONFIG['ragflow_embedding_model'].split('-')[-1])
    
    st.info(
        "**Formato de chunks compatible:** `hierarchical_chunks.json` (IBM Docling HierarchicalChunker). "
        "**Temperatura fija ≤ 0.2** para inferencia juridica (reduce varianza no verificable). "
        "**Abstención obligatoria** cuando no exista respaldo documental suficiente."
    )
    
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

# ═══════════════════════════════════════════════════════════════════════
# MÓDULO 2: ORQUESTAR CONVERSIONES
# ═══════════════════════════════════════════════════════════════════════
elif menu_selected == "Orquestar Conversiones":
    st.header("🚀 Ingesta e Indexacion (Fase 2 de Arquitectura)", divider="orange")
    st.caption("Ejecuta la conversion de archivos origen en subprocesos usando la cache SHA-256")
    
    # ─── SECCIÓN DE CARGA Y CREACIÓN DE CARPETAS (COMPONENTE 7) ───
    with st.expander("📥 Cargar Nuevas Normativas o Documentos (PDF/Word)", expanded=False):
        # Escanear subdirectorios existentes en normativas_pdf
        subdirs = [p.name for p in INPUT_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")]
        subdirs = sorted(subdirs)
        
        folder_options = ["📂 Raíz (normativas_pdf/)", "📁 [Crear Nueva Carpeta]"] + subdirs
        selected_folder = st.selectbox("Seleccione la carpeta de destino:", folder_options)
        
        new_folder_name = ""
        if selected_folder == "📁 [Crear Nueva Carpeta]":
            new_folder_name = st.text_input("Nombre de la nueva carpeta (ej: Penal, Civil):", "")
            
        uploaded_file = st.file_uploader(
            "Seleccione el archivo a subir (PDF o Word):", 
            type=["pdf", "docx", "doc"]
        )
        
        if st.button("📥 Subir Documento"):
            if uploaded_file is None:
                st.error("Por favor, seleccione un archivo antes de subir.")
            else:
                import re
                # Determinar subcarpeta destino
                dest_dir = INPUT_DIR
                valid_path = True
                
                if selected_folder == "📁 [Crear Nueva Carpeta]":
                    if not new_folder_name.strip():
                        st.error("Por favor, ingrese un nombre para la nueva carpeta.")
                        valid_path = False
                    else:
                        # Sanitizar nombre de la carpeta (remover caracteres especiales, espacios extra)
                        sanitized = re.sub(r'[\\/*?:"<>|]', "", new_folder_name.strip())
                        sanitized = sanitized.replace(" ", "_")
                        if not sanitized:
                            st.error("El nombre de la carpeta no es valido.")
                            valid_path = False
                        else:
                            dest_dir = INPUT_DIR / sanitized
                elif selected_folder != "📂 Raíz (normativas_pdf/)":
                    dest_dir = INPUT_DIR / selected_folder
                
                if valid_path:
                    try:
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        dest_file_path = dest_dir / uploaded_file.name
                        
                        # Escribir el archivo
                        dest_file_path.write_bytes(uploaded_file.getbuffer())
                        
                        st.success(f"🎉 Archivo `{uploaded_file.name}` subido exitosamente a `{dest_dir.relative_to(BASE_DIR)}`")
                        
                        # Invalidar variables de entorno o estados para que refresque
                        pdfs_files = list(INPUT_DIR.rglob("*.pdf")) + list(INPUT_DIR.rglob("*.docx")) + list(INPUT_DIR.rglob("*.doc"))
                        
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al subir el archivo: {e}")
                        
    st.markdown("---")
    
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
        grid_response = None
        
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
                    st.success("🎉 Post-procesado finalizado con exito.")
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
                # Construir argumentos extra desde la config persistente
                extra_args = []
                if not PIPELINE_CONFIG.get("ocr_activo", True):
                    extra_args.append("--no-ocr")
                if not PIPELINE_CONFIG.get("generar_chunks", True):
                    extra_args.append("--no-chunks")
                
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
                    
                    cmd = [sys.executable, str(BASE_DIR / "convert_normativas.py"), "--file-path", str(f_path)] + extra_args
                    
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
                            log_lines.append(f"--- [ERROR] Fallo procesamiento (codigo {rc}): {f_path.name} ---")
                        console_area.code("\n".join(log_lines[-25:]))
                    except Exception as e:
                        fail_count += 1
                        st.error(f"Error procesando {f_path.name}: {e}")
                
                progress_bar.progress(1.0)
                status_text.markdown(f"✅ **Procesamiento completado:** {success_count} exitosos, {fail_count} fallidos.")
                
                # Invalidar caché de tokens estimados
                if 'corpus_tokens' in st.session_state:
                    del st.session_state['corpus_tokens']
                
                if fail_count == 0:
                    st.success("🎉 Todas las normativas se transformaron con exito.")
                else:
                    st.warning(f"⚠️ Proceso finalizado con {fail_count} errores.")
                
                time.sleep(2)
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# MÓDULO 3: INTEGRIDAD Y REPORTES + VALIDACIÓN CRUZADA
# ═══════════════════════════════════════════════════════════════════════
elif menu_selected == "Integridad y Reportes":
    st.header("🛡️ Integridad Legal y Auditoria Forense", divider="orange")
    st.caption("Filtros de trazabilidad, deteccion de inconsistencias y validacion cruzada con PDF original")
    
    if not md_files:
        st.info("No hay archivos estructurados en RAG para auditar.")
    elif not VALIDATOR_AVAILABLE:
        st.error("Modulo validator.py no disponible.")
    else:
        # Cachear reportes en session_state
        if 'validation_reports' not in st.session_state:
            with st.spinner("Ejecutando validacion de integridad..."):
                reports = []
                for f_path in md_files:
                    rep = validate_md_file(str(f_path))
                    reports.append(rep)
                st.session_state.validation_reports = reports
        
        reports = st.session_state.validation_reports
        
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
        st.dataframe(df_res, width="stretch")
        
        # Botón para refrescar reportes
        if st.button("🔄 Recalcular Reportes"):
            if 'validation_reports' in st.session_state:
                del st.session_state['validation_reports']
            st.rerun()
        
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
            
            # ─── VALIDACIÓN CRUZADA CON PDF ───
            st.markdown("---")
            st.subheader("🔀 Validacion Cruzada con PDF Original")
            st.caption("Extrae articulos directamente del PDF con PyMuPDF y los compara con los detectados por el legalizer")
            
            # Buscar PDF correspondiente
            md_path_obj = next((f for f in md_files if f.name == selected_file), None)
            pdf_match = None
            if md_path_obj:
                # Buscar en INPUT_DIR con la misma ruta relativa
                try:
                    rel = md_path_obj.relative_to(OUTPUT_DIR)
                except ValueError:
                    rel = Path(md_path_obj.stem)
                candidate = INPUT_DIR / rel.with_suffix(".pdf")
                if candidate.exists():
                    pdf_match = candidate
            
            if pdf_match:
                if st.button(f"🔍 Ejecutar Validacion Cruzada: {pdf_match.name}"):
                    with st.spinner("Extrayendo articulos del PDF original..."):
                        cross_result = cross_validate_against_pdf(str(pdf_match), str(md_path_obj))
                    
                    if cross_result.get('error'):
                        st.error(f"Error en validacion cruzada: {cross_result['error']}")
                    elif cross_result['match']:
                        st.success(
                            f"✅ **Validacion cruzada EXITOSA** — "
                            f"{len(cross_result['pdf_articles'])} articulos coinciden entre PDF y Markdown."
                        )
                    else:
                        st.error("❌ **Discrepancias detectadas** entre PDF original y Markdown:")
                        
                        cv_col1, cv_col2 = st.columns(2)
                        with cv_col1:
                            st.metric("Articulos en PDF", len(cross_result['pdf_articles']))
                            if cross_result['missing_in_md']:
                                st.warning(f"Faltantes en MD: {cross_result['missing_in_md'][:20]}")
                        with cv_col2:
                            st.metric("Articulos en MD", len(cross_result['md_articles']))
                            if cross_result['extra_in_md']:
                                st.info(f"Extras en MD (no en PDF): {cross_result['extra_in_md'][:20]}")
            else:
                st.info("No se encontro el PDF original correspondiente para validacion cruzada.")

# ═══════════════════════════════════════════════════════════════════════
# MÓDULO 4: CADENA DE CUSTODIA DIGITAL
# ═══════════════════════════════════════════════════════════════════════
elif menu_selected == "Cadena de Custodia":
    st.header("🔗 Cadena de Custodia Digital", divider="orange")
    st.caption("Trazabilidad SHA-256 del pipeline completo — Requisito forense R7 (ISO/IEC 27037)")
    
    # Cargar manifest
    manifest = {}
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    
    if not manifest and not md_files:
        st.info("No hay datos de custodia. Ejecute al menos una conversion desde el modulo 'Orquestar Conversiones'.")
    else:
        custody_data = []
        integrity_alerts = []
        
        for md_path in md_files:
            md_name = md_path.name
            md_hash = sha256_of_file(md_path)
            
            # Extraer fecha de procesamiento del YAML
            procesado_en = ""
            try:
                content = md_path.read_text(encoding="utf-8")
                if content.startswith("---"):
                    end_fm = content.find("\n---\n", 4)
                    if end_fm > 0:
                        fm_data = yaml.safe_load(content[3:end_fm])
                        if fm_data:
                            procesado_en = fm_data.get("procesado_en", "")
            except Exception:
                pass
            
            # Buscar el PDF original y su hash registrado
            try:
                rel = md_path.relative_to(OUTPUT_DIR)
            except ValueError:
                rel = Path(md_path.stem)
            
            pdf_candidate = INPUT_DIR / rel.with_suffix(".pdf")
            pdf_hash_actual = ""
            pdf_hash_manifest = ""
            integridad = "N/A"
            
            manifest_key = str(rel)
            if manifest_key in manifest:
                pdf_hash_manifest = manifest[manifest_key].get('sha256', '')
            
            if pdf_candidate.exists():
                pdf_hash_actual = sha256_of_file(pdf_candidate)
                if pdf_hash_manifest:
                    if pdf_hash_actual == pdf_hash_manifest:
                        integridad = "✅ Integro"
                    else:
                        integridad = "🔴 MODIFICADO"
                        integrity_alerts.append(pdf_candidate.name)
                else:
                    integridad = "⚠️ Sin registro"
            else:
                integridad = "📄 PDF no encontrado"
            
            custody_data.append({
                "Normativa": md_name[:45],
                "Hash MD (SHA-256)": md_hash[:16] + "..." if md_hash else "",
                "Hash PDF Actual": pdf_hash_actual[:16] + "..." if pdf_hash_actual else "",
                "Hash PDF Manifest": pdf_hash_manifest[:16] + "..." if pdf_hash_manifest else "",
                "Procesado": procesado_en[:19] if procesado_en else "",
                "Integridad": integridad
            })
        
        # Alertas de integridad
        if integrity_alerts:
            st.error(
                f"🔴 **ALERTA DE INTEGRIDAD:** {len(integrity_alerts)} archivo(s) PDF han sido modificados "
                f"despues de su ultima conversion. Deben re-procesarse:\n\n" +
                "\n".join(f"- `{a}`" for a in integrity_alerts)
            )
        else:
            if custody_data:
                st.success("✅ Todos los archivos PDF mantienen su integridad original.")
        
        # Tabla de custodia
        if custody_data:
            import pandas as pd
            df_custody = pd.DataFrame(custody_data)
            st.dataframe(df_custody, width="stretch")
        
        st.markdown("---")
        
        # Exportar Acta de Custodia
        st.subheader("📋 Exportar Acta de Custodia Digital")
        
        if st.button("📄 Generar Acta de Custodia (.txt)"):
            acta_lines = [
                "=" * 72,
                "  ACTA DE CUSTODIA DIGITAL — JULLBRAIN RAG-PIPELINE",
                "  Sistema de Trazabilidad SHA-256 para Normativas Juridicas",
                "=" * 72,
                "",
                f"  Fecha de generacion : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"  Sistema             : IBM Docling + LegalProcessor v2",
                f"  Operador            : Jull Ortiz — Arquitecto de Datos con IA",
                f"  Total documentos    : {len(custody_data)}",
                "",
                "-" * 72,
                ""
            ]
            
            for item in custody_data:
                acta_lines.append(f"  Normativa      : {item['Normativa']}")
                acta_lines.append(f"  Hash MD        : {item['Hash MD (SHA-256)']}")
                acta_lines.append(f"  Hash PDF Actual: {item['Hash PDF Actual']}")
                acta_lines.append(f"  Hash Manifest  : {item['Hash PDF Manifest']}")
                acta_lines.append(f"  Procesado      : {item['Procesado']}")
                acta_lines.append(f"  Integridad     : {item['Integridad']}")
                acta_lines.append("")
            
            acta_lines.append("-" * 72)
            acta_lines.append("  FIN DEL ACTA DE CUSTODIA DIGITAL")
            acta_lines.append("=" * 72)
            
            acta_text = "\n".join(acta_lines)
            acta_path = BASE_DIR / f"acta_custodia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            acta_path.write_text(acta_text, encoding="utf-8")
            
            st.success(f"✅ Acta de custodia generada: `{acta_path.name}`")
            st.code(acta_text)

# ═══════════════════════════════════════════════════════════════════════
# MÓDULO 5: EDITOR DE LEYES RAG
# ═══════════════════════════════════════════════════════════════════════
elif menu_selected == "Editor de Leyes RAG":
    st.header("📝 Visor y Editor de Conocimientos RAG (Outputs)", divider="orange")
    st.caption("Corrige fallas del OCR o ajusta metadatos del YAML frontmatter directamente")
    
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
                        # Invalidar caché de reportes de validación
                        if 'validation_reports' in st.session_state:
                            del st.session_state['validation_reports']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar el archivo: {e}")

# ═══════════════════════════════════════════════════════════════════════
# MÓDULO 6: GRANITE EMBEDDING — Motor de Embeddings Semánticos
# ═══════════════════════════════════════════════════════════════════════
elif menu_selected == "🧬 Granite Embedding":
    st.header("🧬 Granite Embedding R2 — Motor Semántico del Pipeline", divider="orange")
    st.caption(
        "IBM Granite Embedding (ModernBERT) — 768 dimensiones — 8 192 tokens de contexto — "
        "Diseñado para recuperación semántica en corpus jurídico venezolano"
    )

    if not EMBEDDER_AVAILABLE:
        st.error(
            "⛔ `granite_embedder.py` no se pudo importar. "
            "Asegúrate de que el archivo existe en la raíz del proyecto."
        )
    else:
        # ── Resumen de configuración activa ──────────────────────────────
        emb_cfg_col1, emb_cfg_col2, emb_cfg_col3 = st.columns(3)
        emb_cfg_col1.metric("Modelo Activo", PIPELINE_CONFIG.get("ragflow_embedding_model", "N/A").split("/")[-1])
        emb_cfg_col2.metric("Backend", PIPELINE_CONFIG.get("embedding_backend", "sentence-transformers"))
        emb_cfg_col3.metric("Dispositivo", PIPELINE_CONFIG.get("embedding_device", "cpu").upper())

        st.markdown("---")

        # ── SECCIÓN 1: Estado del Modelo ─────────────────────────────────
        with st.expander("🔍 Verificar Estado del Modelo", expanded=True):
            st.info(
                "Esta verificación carga el modelo en memoria por primera vez "
                "(puede tardar 30–120 segundos en la primera ejecución mientras descarga ~1.2 GB de HuggingFace)."
            )
            if st.button("⚡ Ejecutar Verificación de Salud", key="btn_health"):
                with st.spinner("Cargando modelo Granite Embedding R2…"):
                    try:
                        embedder_health = GraniteEmbedder()
                        health = embedder_health.validate_model_health()
                        if health["status"] == "ok":
                            hc1, hc2, hc3, hc4 = st.columns(4)
                            hc1.metric("✅ Estado", "OK")
                            hc2.metric("Dimensión", health["dim"])
                            hc3.metric("Backend", health["backend"])
                            hc4.metric("Tiempo de Carga", f"{health['load_time_s']}s")
                            st.success(f"Modelo `{health['model']}` listo y operativo.")
                            st.caption(f"Muestra (primeros 5 valores): `{health['sample_preview']}`")
                        else:
                            st.error(f"❌ Error: {health.get('error', 'Desconocido')}")
                    except Exception as exc:
                        st.error(f"Error al verificar el modelo: {exc}")

        st.markdown("---")

        # ── SECCIÓN 2: Embedding de Texto de Prueba ───────────────────────
        with st.expander("🧪 Embedding de Texto de Prueba", expanded=False):
            st.caption("Ingresa un fragmento de texto legal para visualizar su representación vectorial.")
            test_text = st.text_area(
                "Texto legal de prueba:",
                value="Artículo 1. La presente Ley tiene por objeto regular el uso de las tecnologías de la información.",
                height=100,
                key="test_text_area"
            )
            if st.button("🔬 Generar Embedding", key="btn_embed_test"):
                if not test_text.strip():
                    st.warning("Ingresa un texto antes de generar el embedding.")
                else:
                    with st.spinner("Generando vector…"):
                        try:
                            embedder_test = GraniteEmbedder()
                            vec = embedder_test.embed_text(test_text)
                            et_col1, et_col2 = st.columns(2)
                            et_col1.metric("Dimensión del Vector", len(vec))
                            et_col2.metric("Modelo", PIPELINE_CONFIG.get("ragflow_embedding_model", "N/A").split("/")[-1])
                            st.caption("**Primeros 10 valores del vector:**")
                            st.code(str([round(v, 6) for v in vec[:10]]), language="python")
                            st.caption("**Últimos 5 valores del vector:**")
                            st.code(str([round(v, 6) for v in vec[-5:]]), language="python")
                        except Exception as exc:
                            st.error(f"Error al generar embedding: {exc}")

        st.markdown("---")

        # ── SECCIÓN 3: Embeber Chunks del Pipeline ────────────────────────
        with st.expander("📦 Embeber Chunks del Pipeline (hierarchical_chunks.json)", expanded=False):
            st.caption(
                "Selecciona un archivo de chunks para añadir el campo `embedding` a cada fragmento. "
                "El archivo original **NO se modifica** — se genera `<nombre>_embedded.json`."
            )

            chunk_files = list(CHUNKS_DIR.rglob("hierarchical_chunks.json"))
            if not chunk_files:
                st.info("No hay archivos `hierarchical_chunks.json` en `normativas_chunks/`. "
                        "Ejecuta primero el pipeline de conversión.")
            else:
                chunk_options = {str(f.relative_to(BASE_DIR)): f for f in chunk_files}
                selected_chunk = st.selectbox(
                    "Selecciona el archivo de chunks:",
                    options=list(chunk_options.keys()),
                    key="chunk_selector"
                )
                chunk_path = chunk_options[selected_chunk]

                # Mostrar preview del archivo seleccionado
                try:
                    with chunk_path.open(encoding="utf-8") as _f:
                        _raw = json.load(_f)
                    _chunks_list = _raw["chunks"] if isinstance(_raw, dict) and "chunks" in _raw else _raw
                    st.caption(f"Total de chunks en el archivo: **{len(_chunks_list)}**")
                except Exception:
                    st.caption("No se pudo leer el archivo para preview.")

                if st.button("🧬 Generar Embeddings para este archivo", key="btn_embed_file"):
                    progress_bar = st.progress(0, text="Iniciando…")
                    status_text  = st.empty()

                    def _update_progress(current: int, total: int) -> None:
                        pct = current / total
                        progress_bar.progress(pct, text=f"Procesando chunk {current}/{total}…")
                        status_text.caption(f"Procesando: {current}/{total} chunks ({pct*100:.1f}%)")

                    with st.spinner("Cargando modelo y generando embeddings…"):
                        try:
                            embedder_file = GraniteEmbedder()
                            out_path = embedder_file.embed_chunks_file(
                                input_path=chunk_path,
                                progress_callback=_update_progress,
                            )
                            progress_bar.progress(1.0, text="✅ Completado")
                            st.success(
                                f"✅ Embeddings generados y guardados en:\n\n"
                                f"`{out_path.relative_to(BASE_DIR)}`"
                            )
                            # Verificar dimensión
                            with out_path.open(encoding="utf-8") as _fv:
                                _ev = json.load(_fv)
                            _ec = _ev["chunks"] if isinstance(_ev, dict) and "chunks" in _ev else _ev
                            if _ec and "embedding" in _ec[0]:
                                st.info(f"Dimensión de vectores confirmada: **{len(_ec[0]['embedding'])}**")
                        except Exception as exc:
                            st.error(f"Error al embeber chunks: {exc}")

        st.markdown("---")

        # ── SECCIÓN 4: Guía de integración con RAGFlow ────────────────────
        with st.expander("📡 Guía de Integración con RAGFlow", expanded=False):
            st.markdown("""
**Paso 1 — Opción A: sentence-transformers (sin Ollama)**

RAGFlow no consume `sentence-transformers` directamente. Para usar el modelo local,
debes servir los embeddings a través de un servidor compatible con la API de OpenAI.
Una opción es usar [litserve](https://github.com/Lightning-AI/litserve) o
simplemente subir los chunks embebidos directamente al Knowledge Base de RAGFlow
usando la API REST de ingesta.

**Paso 1 — Opción B: Ollama (recomendado para producción)**
```bash
# En la máquina donde corre Ollama:
ollama pull granite-embedding
# Verificar:
curl http://localhost:11434/api/embeddings -d '{"model":"granite-embedding","prompt":"test"}'
```

**Paso 2 — Registrar en RAGFlow UI**

1. Ir a **Settings → Model Providers → Add Model**.
2. Seleccionar tipo: **Embedding**.
3. Base URL: `http://localhost:11434/v1` (Ollama OpenAI-compatible endpoint).
4. Model ID: `granite-embedding` (o el nombre que configuraste en Ollama).
5. API Key: cualquier valor (Ollama no la valida).

**Paso 3 — Asignar al Knowledge Base**

En el Knowledge Base de RAGFlow, cambia el *Embedding Model* al modelo recién registrado.

> ⚠️ **Aviso de compatibilidad:** Si ya tienes documentos indexados con `granite-embedding-30m-english`,
> RAGFlow detectará incompatibilidad (espacio vectorial diferente: 384-dim vs 768-dim) y
> requerirá re-indexar los documentos. Esto es esperado y necesario para aprovechar
> el contexto extendido de 8 192 tokens de R2.

**Verificar via API:**
```bash
curl http://localhost:9380/api/v1/embedding_model/list -H "Authorization: Bearer <API_KEY>"
```
""")

# ═══════════════════════════════════════════════════════════════════════
# MÓDULO 7: AJUSTES DEL PIPELINE (CONFIGURACIÓN PERSISTENTE)
# ═══════════════════════════════════════════════════════════════════════
elif menu_selected == "Ajustes del Pipeline":

    st.header("⚙️ Parametros y Ajustes del Pipeline", divider="orange")
    st.caption("Configuracion persistente — Los valores se guardan en pipeline_config.json")
    
    st.markdown("### 🔧 Parametros de Procesamiento (IBM Docling)")
    
    ocr_active = st.checkbox(
        "Activar OCR (Recomendado para escaneos de Gaceta Oficial)",
        value=PIPELINE_CONFIG.get("ocr_activo", True)
    )
    chunks_active = st.checkbox(
        "Generar Chunks Jerarquicos JSON para RAGFlow",
        value=PIPELINE_CONFIG.get("generar_chunks", True)
    )
    min_chars = st.number_input(
        "Minimo de caracteres para considerar un articulo valido",
        min_value=10, max_value=500,
        value=PIPELINE_CONFIG.get("min_article_chars", 50)
    )
    
    st.markdown("---")
    st.markdown("### 📊 Umbrales de Calidad (Validator)")
    
    threshold_critical = st.slider(
        "Umbral CRITICO (por debajo = ERROR, detener pipeline)",
        min_value=0.50, max_value=1.00, step=0.01,
        value=PIPELINE_CONFIG.get("quality_threshold_critical", 0.90)
    )
    threshold_warning = st.slider(
        "Umbral ADVERTENCIA (por debajo = WARNING, revisar manualmente)",
        min_value=0.50, max_value=1.00, step=0.01,
        value=PIPELINE_CONFIG.get("quality_threshold_warning", 0.95)
    )
    
    st.markdown("---")
    st.markdown("### 🤖 Configuracion de IBM Granite 4.0")
    
    granite_model = st.text_input(
        "Modelo de Inferencia (Ollama)",
        value=PIPELINE_CONFIG.get("granite_model", "granite4.1:8b")
    )
    granite_temp = st.slider(
        "Temperatura de Inferencia Juridica (recomendado ≤ 0.2)",
        min_value=0.0, max_value=1.0, step=0.05,
        value=PIPELINE_CONFIG.get("granite_temperature", 0.15)
    )
    granite_ctx = st.number_input(
        "Ventana de Contexto (tokens)",
        min_value=4096, max_value=1000000, step=1024,
        value=PIPELINE_CONFIG.get("granite_context_window", 128000)
    )
    
    st.markdown("---")
    st.markdown("### 🌐 Configuracion de RAGFlow")
    
    ragflow_url = st.text_input(
        "URL de la API de RAGFlow",
        value=PIPELINE_CONFIG.get("ragflow_api_url", "http://localhost:9380/api/v1")
    )
    ragflow_embedding = st.text_input(
        "Modelo de Embeddings (Hugging Face ID u Ollama name)",
        value=PIPELINE_CONFIG.get("ragflow_embedding_model", "ibm-granite/granite-embedding-english-r2")
    )

    st.markdown("---")
    st.markdown("### 🧬 Configuracion de Granite Embedding R2")
    st.caption("Parámetros del motor de embeddings semánticos (granite_embedder.py)")

    emb_backend_options = ["sentence-transformers", "ollama"]
    emb_backend_current = PIPELINE_CONFIG.get("embedding_backend", "sentence-transformers")
    emb_backend_idx = emb_backend_options.index(emb_backend_current) if emb_backend_current in emb_backend_options else 0
    emb_backend = st.selectbox(
        "Backend de Embeddings",
        options=emb_backend_options,
        index=emb_backend_idx,
        help=(
            "**sentence-transformers** → corre el modelo localmente en Python (recomendado para desarrollo). "
            "**ollama** → usa Ollama como API local en localhost:11434 (recomendado para producción con RAGFlow)."
        )
    )

    emb_device_options = ["cpu", "cuda", "mps"]
    emb_device_current = PIPELINE_CONFIG.get("embedding_device", "cpu")
    emb_device_idx = emb_device_options.index(emb_device_current) if emb_device_current in emb_device_options else 0
    emb_device = st.selectbox(
        "Dispositivo de Cómputo",
        options=emb_device_options,
        index=emb_device_idx,
        help="**cpu** = universal | **cuda** = GPU NVIDIA | **mps** = GPU Apple Silicon",
        disabled=(emb_backend == "ollama")
    )

    emb_batch = st.number_input(
        "Tamaño de Lote (chunks por iteración)",
        min_value=1, max_value=256, step=8,
        value=PIPELINE_CONFIG.get("embedding_batch_size", 32),
        help="Valores altos (64–128) son más rápidos pero requieren más RAM/VRAM.",
        disabled=(emb_backend == "ollama")
    )

    if emb_backend == "sentence-transformers":
        st.info(
            "📦 El modelo se descargará automáticamente desde Hugging Face la primera vez "
            f"(`~1.2 GB` para `granite-embedding-english-r2`). "
            "Requiere `sentence-transformers>=3.0.0` y `torch>=2.1.0` instalados en el entorno virtual."
        )
    else:
        st.info(
            "🦙 **Modo Ollama activo.** Asegúrate de que Ollama esté corriendo en `localhost:11434` "
            "y de que el modelo de embeddings esté disponible. "
            "Esto permite integración directa con RAGFlow via OpenAI-compatible endpoint."
        )
    
    st.markdown("---")
    
    if st.button("💾 Guardar Configuracion"):
        new_config = {
            "ocr_activo": ocr_active,
            "generar_chunks": chunks_active,
            "min_article_chars": min_chars,
            "quality_threshold_critical": threshold_critical,
            "quality_threshold_warning": threshold_warning,
            "granite_model": granite_model,
            "granite_temperature": granite_temp,
            "granite_context_window": granite_ctx,
            "ragflow_api_url": ragflow_url,
            "ragflow_embedding_model": ragflow_embedding,
            "embedding_backend": emb_backend,
            "embedding_batch_size": int(emb_batch),
            "embedding_device": emb_device,
        }
        save_pipeline_config(new_config)
        st.success("✅ Configuracion guardada en `pipeline_config.json`.")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ Notas Tecnicas")
    st.info(
        "El encabezado de los archivos Markdown se sincroniza automaticamente con el banner "
        "de la consola de `orquestador_JullBrain.bat`. Puedes editar la variable `HEADER_TEMPLATE` "
        "en `convert_normativas.py` para modificaciones permanentes."
    )
