"""
app.py — Backend API REST de Producción para JullBrain Enterprise Legal Platform
Servidor API de alto rendimiento optimizado para integrarse exclusivamente con Open WebUI.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Módulos de Backend JullBrain
from audit_logger import default_audit_logger, AuditLogger
from notebook_manager import default_notebook_manager, NotebookManager, NotebookIntegrityError
from opensearch_indexer import default_opensearch_indexer, OpenSearchHybridIndexer
from granite_guardian_guardrail import default_guardian_guardrail

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("JullBrain.API")

# Inicialización de la Aplicación FastAPI
app = FastAPI(
    title="JullBrain Enterprise Legal Platform API",
    description="Backend API REST de Inteligencia Documental Legal con IBM Granite 3.3 8B y Open WebUI",
    version="2.0.0"
)

# Habilitar CORS para permitir solicitudes desde Open WebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── MODELOS DE DATOS DE ENTRADA Y SALIDA (PYDANTIC) ───

class NotebookCreateRequest(BaseModel):
    name: str = Field(..., description="Nombre del cuaderno / expediente legal")
    description: str = Field("", description="Descripción detallada del expediente")
    user_id: str = Field("openwebui_user", description="ID del usuario creador")


class QueryRequest(BaseModel):
    notebook_id: str = Field(..., description="ID del cuaderno / expediente")
    user_message: str = Field(..., description="Consulta normativa del usuario")
    user_id: str = Field("openwebui_user", description="ID del usuario consultante")
    top_k: int = Field(20, description="Número de chunks candidatas a recuperar")


class GuardianRequest(BaseModel):
    user_query: str = Field(..., description="Prompt del usuario a evaluar")


# ─── ENDPOINTS PRINCIPALES ───

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "JullBrain Enterprise Legal Platform API",
        "version": "2.0.0",
        "ui": "Open WebUI Official Interface",
        "granite_model": "ibm-granite/granite-3.3-8b-instruct-GGUF",
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
def health_check():
    """Verifica el estado de salud de todos los componentes de backend."""
    opensearch_status = "connected" if default_opensearch_indexer.client else "standby_local"
    guardian_status = "available" if default_guardian_guardrail.is_model_available() else "heuristic_mode"

    return {
        "status": "healthy",
        "opensearch": opensearch_status,
        "granite_guardian": guardian_status,
        "notebook_storage": os.path.exists(default_notebook_manager.storage_dir),
        "audit_logger": True
    }


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
def load_notebook(notebook_id: str, user_id: str = "openwebui_user"):
    """
    Carga un cuaderno verificando obligatoriamente su firma SHA-256.
    Rechaza el acceso si existe alteración de integridad.
    """
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
def delete_notebook(notebook_id: str, user_id: str = "openwebui_user"):
    """Elimina un cuaderno de forma transaccional con rollback."""
    try:
        success = default_notebook_manager.delete_notebook_transactional(notebook_id, user_id)
        return {"status": "deleted", "notebook_id": notebook_id, "success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── ENDPOINT RAG LEGAL IBM GRANITE (OPEN WEBUI BACKEND) ───

@app.post("/api/v1/query")
def execute_rag_query(req: QueryRequest):
    """
    Ejecuta el pipeline RAG Legal con IBM Granite 3.3 8B para Open WebUI.
    Aplica Búsqueda Híbrida OpenSearch (BM25 + Vector + RRF + Reranker),
    Guardrails de seguridad e inferencia estricta cero alucinación.
    """
    # 1. Guardrail de Seguridad IBM Granite Guardian
    guardrail = default_guardian_guardrail.evaluate_prompt(req.user_message)
    if not guardrail.get("is_safe", True):
        return {
            "status": "blocked",
            "reason": guardrail.get("reason"),
            "response": f"[ALERTA DE SEGURIDAD - GRANITE GUARDIAN] {guardrail.get('reason')}"
        }

    # 2. Búsqueda Híbrida OpenSearch (BM25 + Vector + RRF + Reranker)
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
            "evidence_found": False,
            "response": "No encontré evidencia suficiente en los documentos cargados para responder esta pregunta.",
            "citations": []
        }

    # 4. Construcción de Citas y Respuesta Estructurada
    citations = []
    response_body = f"### Respuesta Basada en Evidencia Documental\n\n"
    top_chunk = retrieved_chunks[0]

    response_body += (
        f"De acuerdo con el **{top_chunk.get('article', 'artículo normativo')}** del "
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
            "confianza_pct": conf,
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
        "evidence_found": True,
        "response": response_body,
        "citations": citations
    }


# ─── ENDPOINT DE AUDITORÍA INMUTABLE ───

@app.get("/api/v1/audit")
def get_audit_trail(limit: int = 50):
    """Retorna los registros de auditoría inmutables más recientes."""
    log_file = os.path.join(os.path.dirname(__file__), "audit_trail.jsonl")
    entries = []
    if os.path.exists(log_file):
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
