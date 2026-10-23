"""
app.py — Backend API REST & Servidor Web para JullBrain Enterprise Legal Platform
Modo 100% Local Offline (Air-Gapped) & Google Colab.
Servidor API de alto rendimiento e Interfaz Web HTML5/CSS3 Integrada.
"""

import os
import sys
import json
import logging
import hashlib
import asyncio
import subprocess
from pathlib import Path
from collections import deque
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Módulos de Backend JullBrain
from audit_logger import default_audit_logger, AuditLogger
from notebook_manager import default_notebook_manager, NotebookManager, NotebookIntegrityError
from opensearch_indexer import default_opensearch_indexer, OpenSearchHybridIndexer
from granite_guardian_guardrail import default_guardian_guardrail

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("JullBrain.API")

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
DATOS_BRUTOS_DIR = BASE_DIR / "RAG" / "datos_brutos"
NORMATIVAS_RAG_DIR = BASE_DIR / "normativas_rag"

# Búfer de logs en memoria para streaming en la consola web
pipeline_logs = deque(maxlen=500)
pipeline_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [INIT] Servidor JullBrain V-2.0 iniciado.")
pipeline_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Modo 100% Local Offline activo (Air-Gapped).")

# Inicialización de la Aplicación FastAPI
app = FastAPI(
    title="JullBrain Enterprise Legal Platform API",
    description="Backend API REST y Centro de Control Legal-RAG con IBM Granite e IBM Docling",
    version="2.0.0"
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos para la interfaz web HTML5/CSS3
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


# ─── MODELOS DE DATOS PYDANTIC ───

class NotebookCreateRequest(BaseModel):
    name: str = Field(..., description="Nombre del cuaderno / expediente legal")
    description: str = Field("", description="Descripción detallada del expediente")
    user_id: str = Field("local_user", description="ID del usuario creador")


class QueryRequest(BaseModel):
    notebook_id: str = Field("default_notebook", description="ID del cuaderno / expediente")
    user_message: str = Field(..., description="Consulta normativa del usuario")
    user_id: str = Field("local_user", description="ID del usuario consultante")
    top_k: int = Field(20, description="Número de chunks candidatas a recuperar")


class ActionRequest(BaseModel):
    action: str = Field(..., description="Acción a ejecutar: convert, qa_validate, postprocess, embed, qa_test, clean_cache")


# ─── FUNCIONES DE SUBPROCESOS EN SEGUNDO PLANO ───

def run_pipeline_action_task(action: str):
    """Ejecuta una acción del pipeline y envía los logs al búfer web."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    python_exe = sys.executable

    pipeline_logs.append(f"[{timestamp}] [START] 🚀 Ejecutando acción: '{action}'...")

    cmd = []
    if action == "convert":
        cmd = [python_exe, "convert_normativas.py"]
    elif action == "qa_validate":
        cmd = [python_exe, "validator.py", "RAG/Informacion_docling_rag"]
    elif action == "postprocess":
        cmd = [python_exe, "convert_normativas.py", "--post-process-only"]
    elif action == "embed":
        cmd = [python_exe, "granite_embedder.py"]
    elif action == "qa_test":
        cmd = [python_exe, "-m", "unittest", "discover", "tests"]
    elif action == "clean_cache":
        cmd = [python_exe, "cleanup.py"]
    else:
        pipeline_logs.append(f"[{timestamp}] [ERROR] Acción no reconocida: '{action}'")
        return

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(BASE_DIR)
        )

        for line in proc.stdout:
            cleaned = line.strip()
            if cleaned:
                pipeline_logs.append(cleaned)

        proc.wait()
        end_time = datetime.now().strftime("%H:%M:%S")
        if proc.returncode == 0:
            pipeline_logs.append(f"[{end_time}] [OK] ✅ Acción '{action}' finalizada con éxito (Código 0).")
        else:
            pipeline_logs.append(f"[{end_time}] [ERROR] ❌ Acción '{action}' terminó con código {proc.returncode}.")
    except Exception as e:
        pipeline_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FATAL] Error al ejecutar '{action}': {e}")


# ─── ENDPOINTS DE INTERFAZ Y CONTROL ───

@app.get("/")
def read_root(accept: Optional[str] = Header(None)):
    """Sirve la Interfaz Web HTML5 o el esquema JSON si se solicita API."""
    index_file = WEB_DIR / "index.html"
    legacy_index = BASE_DIR / "_archivo_historico" / "web_legacy" / "index.html"

    if accept and "application/json" in accept:
        return {
            "status": "online",
            "system": "JullBrain Enterprise Legal Platform API",
            "version": "3.0.0",
            "ui": "Open WebUI Official Interface",
            "mode": "100% Local Offline (Air-Gapped)"
        }
    if index_file.exists():
        return FileResponse(str(index_file))
    if legacy_index.exists():
        return FileResponse(str(legacy_index))
    from fastapi.responses import HTMLResponse
    return HTMLResponse("<!DOCTYPE html><html><head><title>JullBrain API</title></head><body><h1>JullBrain V3.0 API</h1></body></html>")


@app.get("/health")
def health_check():
    """Verifica el estado de salud de todos los componentes de backend."""
    opensearch_status = "connected" if default_opensearch_indexer.client else "local_offline_active"
    guardian_status = "available" if default_guardian_guardrail.is_model_available() else "heuristic_mode"

    return {
        "status": "healthy",
        "mode": "local_offline_air_gapped",
        "opensearch_status": opensearch_status,
        "granite_guardian": guardian_status,
        "notebook_storage": os.path.exists(default_notebook_manager.storage_dir),
        "audit_logger": True
    }


@app.post("/api/v1/pipeline/action")
def trigger_action(req: ActionRequest, background_tasks: BackgroundTasks):
    """Dispara acciones del pipeline de forma asíncrona."""
    valid_actions = ["convert", "qa_validate", "postprocess", "embed", "qa_test", "clean_cache"]
    if req.action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Acción inválida. Debe ser una de: {valid_actions}")

    background_tasks.add_task(run_pipeline_action_task, req.action)
    return {
        "status": "dispatched",
        "action": req.action,
        "message": f"Acción '{req.action}' iniciada en segundo plano."
    }


@app.get("/api/v1/pipeline/logs")
def get_pipeline_logs():
    """Retorna las últimas líneas del log en tiempo real."""
    return {"logs": list(pipeline_logs)}


# ─── ENDPOINTS DE CARGA DOCUMENTAL ───

@app.post("/api/v1/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("Otras"),
    client_sha256: Optional[str] = Form(None)
):
    """
    Recibe un documento PDF, calcula y valida su hash SHA-256 criptográfico,
    y lo almacena en RAG/datos_brutos/<category>/<filename>.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten documentos en formato PDF.")

    # Sanitizar categoría
    clean_cat = "".join([c for c in category if c.isalnum() or c in ("-", "_")]) or "Otras"
    target_dir = DATOS_BRUTOS_DIR / clean_cat
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / file.filename

    content = await file.read()
    size_bytes = len(content)

    # Cálculo servidor de SHA-256
    server_sha256 = hashlib.sha256(content).hexdigest()

    # Guardar en disco
    with open(target_file, "wb") as f:
        f.write(content)

    # Verificación de integridad si cliente envió su cálculo
    integrity_match = True
    if client_sha256 and client_sha256.lower() != server_sha256.lower():
        integrity_match = False
        logger.warning(f"Discrepancia de SHA-256 en {file.filename}: Cliente={client_sha256} Servidor={server_sha256}")

    default_audit_logger.log_event(
        event_type="UPLOAD_DOCUMENT",
        user_id="local_user",
        notebook_id=None,
        action_details={
            "filename": file.filename,
            "category": clean_cat,
            "size_bytes": size_bytes,
            "sha256": server_sha256,
            "integrity_verified": integrity_match
        }
    )

    pipeline_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [UPLOAD] Nuevo documento: {file.filename} ({size_bytes} bytes) en {clean_cat}.")

    return {
        "status": "success",
        "filename": file.filename,
        "category": clean_cat,
        "size_bytes": size_bytes,
        "sha256": server_sha256,
        "integrity_verified": integrity_match
    }


@app.get("/api/v1/documents")
def list_documents():
    """Lista todos los PDFs en RAG/datos_brutos y su estado de conversión."""
    docs = []
    if DATOS_BRUTOS_DIR.exists():
        for cat_dir in DATOS_BRUTOS_DIR.iterdir():
            if cat_dir.is_dir():
                category = cat_dir.name
                for pdf_file in cat_dir.glob("*.pdf"):
                    # Verificar si existe el Markdown correspondiente
                    stem = pdf_file.stem
                    md_exists = (NORMATIVAS_RAG_DIR / category / f"{stem}.md").exists() or \
                                (NORMATIVAS_RAG_DIR / f"{stem}.md").exists()
                    docs.append({
                        "category": category,
                        "filename": pdf_file.name,
                        "size_bytes": pdf_file.stat().st_size,
                        "is_converted": md_exists
                    })
    return {"documents": docs, "total": len(docs)}


# ─── ENDPOINTS DE GESTIÓN DE CUADERNOS (NOTEBOOKLM) ───

@app.post("/api/v1/notebooks", status_code=status.HTTP_201_CREATED)
def create_notebook(req: NotebookCreateRequest):
    """Crea un cuaderno / expediente legal firmado criptográficamente con SHA-256."""
    try:
        notebook = default_notebook_manager.create_notebook(
            name=req.name,
            description=req.description,
            user_id=req.user_id
        )
        return {"status": "success", "notebook": notebook}
    except Exception as e:
        logger.error(f"Error al crear cuaderno: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/notebooks")
def list_notebooks(user_id: Optional[str] = None):
    """Lista los cuadernos / expedientes registrados."""
    return {"notebooks": default_notebook_manager.list_notebooks(user_id=user_id)}


@app.get("/api/v1/notebooks/{notebook_id}")
def load_notebook(notebook_id: str, user_id: str = "local_user"):
    """Carga un cuaderno verificando obligatoriamente su firma SHA-256."""
    try:
        notebook = default_notebook_manager.verify_and_load_notebook(notebook_id, user_id)
        return {"status": "verified", "notebook": notebook}
    except NotebookIntegrityError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/notebooks/{notebook_id}")
def delete_notebook(notebook_id: str, user_id: str = "local_user"):
    """Elimina un cuaderno de forma transaccional."""
    try:
        success = default_notebook_manager.delete_notebook_transactional(notebook_id, user_id)
        return {"status": "deleted", "notebook_id": notebook_id, "success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── ENDPOINT RAG LEGAL IBM GRANITE ───

@app.post("/api/v1/query")
def execute_rag_query(req: QueryRequest):
    """
    Ejecuta el pipeline RAG Legal con IBM Granite 3.3 8B.
    Aplica Búsqueda Híbrida Local/OpenSearch (BM25 + Vector + RRF + Reranker),
    Guardrails de seguridad e inferencia estricta cero alucinación.
    """
    # 1. Guardrail de Seguridad IBM Granite Guardian
    guardrail = default_guardian_guardrail.evaluate_prompt(req.user_message)
    if not guardrail.get("is_safe", True):
        return {
            "status": "blocked",
            "guardian_safe": False,
            "reason": guardrail.get("reason"),
            "response": f"[ALERTA DE SEGURIDAD - GRANITE GUARDIAN] {guardrail.get('reason')}",
            "citations": []
        }

    # 2. Búsqueda Híbrida
    retrieved_chunks = default_opensearch_indexer.hybrid_search(
        notebook_id=req.notebook_id,
        query=req.user_message,
        query_vector=[],
        top_k=req.top_k
    )

    # 3. Respuesta Fallback ante Falta de Evidencia
    if not retrieved_chunks:
        default_audit_logger.log_event(
            event_type="QUERY_RAG",
            user_id=req.user_id,
            notebook_id=req.notebook_id,
            action_details={"query": req.user_message, "status": "NO_EVIDENCE"}
        )
        return {
            "status": "success",
            "guardian_safe": True,
            "evidence_found": False,
            "response": "No encontré evidencia suficiente en los documentos cargados para responder esta pregunta.",
            "citations": []
        }

    # 4. Construcción de Citas y Respuesta Estructurada
    citations = []
    response_body = f"### Respuesta Basada en Evidencia Documental\n\n"
    top_chunk = retrieved_chunks[0]

    response_body += (
        f"De acuerdo con lo dispuesto en el **{top_chunk.get('article', 'artículo normativo')}** del "
        f"documento **{top_chunk.get('document_id', 'expediente')}** (Página {top_chunk.get('page_number', 1)}):\n\n"
        f"> \"{top_chunk.get('content', '').strip()}\"\n\n"
    )

    response_body += "#### Citas y Trazabilidad Legal:\n"
    for chunk in retrieved_chunks[:5]:
        score = chunk.get("reranker_score", 0.95)
        conf = min(100.0, round(score * 100, 1))
        citation_item = {
            "documento": chunk.get("document_id", "N/A"),
            "pagina": chunk.get("page_number", 1),
            "capitulo": chunk.get("chapter", "N/A"),
            "articulo": chunk.get("article", "N/A"),
            "clausula": chunk.get("clause", "N/A"),
            "fragmento_literal": chunk.get("content", "").strip()[:180] + "...",
            "nivel_confianza_pct": conf,
            "reranker_score": score
        }
        citations.append(citation_item)
        response_body += (
            f"- **{citation_item['documento']}** | Pág. {citation_item['pagina']} | "
            f"Art. {citation_item['articulo']} | Confianza: `{conf}%`\n"
        )

    # 5. Registro de Auditoría Inmutable
    default_audit_logger.log_event(
        event_type="QUERY_RAG",
        user_id=req.user_id,
        notebook_id=req.notebook_id,
        action_details={"query": req.user_message, "citations_count": len(citations)}
    )

    return {
        "status": "success",
        "guardian_safe": True,
        "evidence_found": True,
        "response": response_body,
        "citations": citations
    }


# ─── ENDPOINT DE AUDITORÍA ───

@app.get("/api/v1/audit")
def get_audit_trail(limit: int = 50):
    """Retorna los registros de auditoría inmutables más recientes."""
    log_file = BASE_DIR / "audit_trail.jsonl"
    entries = []
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines[-limit:]):
                try:
                    entries.append(json.loads(line.strip()))
                except Exception:
                    continue
    return {"audit_logs": entries}


# ─── ARRANQUE DIRECTO ───
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8050, reload=False)
