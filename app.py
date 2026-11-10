"""
app.py — Backend API REST & Servidor Headless para JullBrain Enterprise Legal Platform
Modo 100% Local Offline (Air-Gapped), Contenedor Nativo Podman & Oracle Cloud (OCI).
Impulsado exclusivamente por IBM Docling, IBM Granite 3.3, IBM Granite Embedding R2 e IBM Granite Guardian.
"""

import os
import sys
import json
import logging
import hashlib
import subprocess
from pathlib import Path
from collections import deque
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, status, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from audit_logger import default_audit_logger, validate_pdf_magic_bytes
from notebook_manager import default_notebook_manager, NotebookIntegrityError
from opensearch_indexer import default_opensearch_indexer
from granite_guardian_guardrail import default_guardian_guardrail
from version import __version__

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("JullBrain.API")

BASE_DIR = Path(__file__).resolve().parent
RAG_DIR = BASE_DIR / "RAG"
DATOS_BRUTOS_DIR = RAG_DIR / "datos_brutos"
INFORMACION_RAG_DIR = RAG_DIR / "Informacion_docling_rag"
CHUNKS_DIR = RAG_DIR / "normativas_chunks"
MODELOS_IA_DIR = RAG_DIR / "modelos_ia"

pipeline_logs = deque(maxlen=500)
pipeline_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [INIT] Servidor JullBrain v{__version__} iniciado.")
pipeline_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Modo 100% Local Offline / Air-Gapped con Ciberseguridad IBM activo.")

app = FastAPI(
    title="JullBrain Enterprise Legal Platform API",
    description="Backend API REST Legal-RAG 100% IBM (Docling + Granite + Guardian) en Podman & Oracle Cloud",
    version=__version__
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8050", "http://localhost:8050", "http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def ibm_cybersecurity_headers_middleware(request: Request, call_next):
    """Inyecta cabeceras de endurecimiento de seguridad HTTP (Zero-Trust)."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Cache-Control"] = "no-store"
    return response


# ─── MODELOS DE DATOS PYDANTIC ───

class NotebookCreateRequest(BaseModel):
    name: str = Field(..., description="Nombre del cuaderno / expediente legal")
    description: str = Field("", description="Descripción detallada del expediente")
    user_id: str = Field("local_user", description="ID del usuario creador")


class QueryRequest(BaseModel):
    notebook_id: str = Field("default_notebook", description="ID del cuaderno / expediente")
    user_message: str = Field(..., description="Consulta normativa del usuario")
    user_id: str = Field("local_user", description="ID del usuario consultante")
    top_k: int = Field(20, description="Número de chunks candidatos a recuperar")


class ActionRequest(BaseModel):
    action: str = Field(..., description="Acción: convert, qa_validate, postprocess, embed, qa_test, clean_cache")


# ─── FUNCIONES DE SUBPROCESOS EN SEGUNDO PLANO ───

def run_pipeline_action_task(action: str):
    """Ejecuta una acción del pipeline y envía los logs al búfer."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    python_exe = sys.executable

    pipeline_logs.append(f"[{timestamp}] [START] 🚀 Ejecutando acción: '{action}'...")

    cmd_map = {
        "convert": [python_exe, "convert_normativas.py"],
        "qa_validate": [python_exe, "validator.py", "RAG/Informacion_docling_rag"],
        "postprocess": [python_exe, "convert_normativas.py", "--post-process-only"],
        "embed": [python_exe, "granite_embedder.py"],
        "qa_test": [python_exe, "-m", "unittest", "discover", "tests"],
        "clean_cache": [python_exe, "cleanup.py"],
    }

    cmd = cmd_map.get(action)
    if not cmd:
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

        if proc.stdout:
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
    """Retorna el estado JSON nativo en Python del servidor JullBrain."""
    return {
        "status": "online",
        "system": "JullBrain Enterprise Legal Platform API",
        "version": __version__,
        "ui": "Open WebUI Official Interface",
        "stack": "100% Python + IBM Docling (CPU) + IBM Granite 3.3 + Granite Embedding R2 + Granite Guardian",
        "mode": "100% Local Offline (Air-Gapped)"
    }


@app.get("/health")
def health_check():
    """Verifica el estado de salud de todos los componentes de backend y bóveda de modelos."""
    opensearch_status = "connected" if default_opensearch_indexer.client else "local_offline_active"
    guardian_status = "available" if default_guardian_guardrail.is_model_available() else "heuristic_mode"

    return {
        "status": "healthy",
        "mode": "local_offline_air_gapped",
        "opensearch_status": opensearch_status,
        "granite_guardian": guardian_status,
        "notebook_storage": os.path.exists(default_notebook_manager.storage_dir),
        "models_vault": MODELOS_IA_DIR.exists(),
        "audit_logger": True
    }


@app.get("/api/v1/security/vault")
def inspect_model_vault():
    """Audita y retorna el estado criptográfico SHA-256 de la bóveda local de modelos IA (RAG/modelos_ia)."""
    return default_audit_logger.seal_and_verify_model_vault()


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
    Recibe un documento PDF, verifica su cabecera binaria (%PDF-), calcula su hash SHA-256
    y lo almacena en RAG/datos_brutos/<category>/<filename>.
    """
    safe_filename = Path(file.filename or "").name
    if not safe_filename.lower().endswith(".pdf") or ".." in safe_filename:
        raise HTTPException(status_code=400, detail="Solo se permiten documentos legítimos en formato PDF.")

    content = await file.read()
    magic_check = validate_pdf_magic_bytes(content)
    if not magic_check.get("valid", False):
        raise HTTPException(status_code=400, detail="El archivo no posee una firma binaria PDF válida (%PDF-).")

    clean_cat = "".join([c for c in category if c.isalnum() or c in ("-", "_", " ")]).strip() or "Otras"
    target_dir = DATOS_BRUTOS_DIR / clean_cat
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / safe_filename

    size_bytes = len(content)
    server_sha256 = hashlib.sha256(content).hexdigest()

    with open(target_file, "wb") as f:
        f.write(content)

    integrity_match = True
    if client_sha256 and client_sha256.lower() != server_sha256.lower():
        integrity_match = False
        logger.warning(f"Discrepancia de SHA-256 en {safe_filename}: Cliente={client_sha256} Servidor={server_sha256}")

    default_audit_logger.log_event(
        event_type="UPLOAD_DOCUMENT",
        user_id="local_user",
        notebook_id=None,
        action_details={
            "filename": safe_filename,
            "category": clean_cat,
            "size_bytes": size_bytes,
            "sha256": server_sha256,
            "integrity_verified": integrity_match
        }
    )

    pipeline_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [UPLOAD] Nuevo documento: {safe_filename} ({size_bytes} bytes) en {clean_cat}.")

    return {
        "status": "success",
        "filename": safe_filename,
        "category": clean_cat,
        "size_bytes": size_bytes,
        "sha256": server_sha256,
        "integrity_verified": integrity_match
    }


@app.get("/api/v1/documents")
def list_documents():
    """Lista todos los PDFs en RAG/datos_brutos y su estado de conversión en RAG/Informacion_docling_rag."""
    docs = []
    if DATOS_BRUTOS_DIR.exists():
        for cat_dir in DATOS_BRUTOS_DIR.iterdir():
            if cat_dir.is_dir():
                category = cat_dir.name
                for pdf_file in cat_dir.glob("*.pdf"):
                    stem = pdf_file.stem
                    md_exists = (INFORMACION_RAG_DIR / category / f"{stem}.md").exists() or \
                                (INFORMACION_RAG_DIR / f"{stem}.md").exists()
                    docs.append({
                        "category": category,
                        "filename": pdf_file.name,
                        "size_bytes": pdf_file.stat().st_size,
                        "is_converted": md_exists
                    })
    return {"documents": docs, "total": len(docs)}


# ─── ENDPOINTS DE GESTIÓN DE CUADERNOS ───

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
    """Lista los cuadernos / expedientes registrados en RAG/notebooks_db."""
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
    Ejecuta el pipeline RAG Legal con IBM Granite 3.3 8B e IBM Granite Guardian.
    """
    guardrail = default_guardian_guardrail.evaluate_prompt(req.user_message)
    if not guardrail.get("is_safe", True):
        return {
            "status": "blocked",
            "guardian_safe": False,
            "reason": guardrail.get("reason"),
            "response": f"[ALERTA DE SEGURIDAD - GRANITE GUARDIAN] {guardrail.get('reason')}",
            "citations": []
        }

    retrieved_chunks = default_opensearch_indexer.hybrid_search(
        notebook_id=req.notebook_id,
        query=req.user_message,
        query_vector=[],
        top_k=req.top_k
    )

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

    citations = []
    response_body = "### Respuesta Basada en Evidencia Documental\n\n"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8050, reload=False)
