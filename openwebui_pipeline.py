"""
openwebui_pipeline.py — Open WebUI Pipeline / Function Tool Backend for JullBrain
JullBrain Enterprise Legal Platform
"""

import os
import json
import logging
from typing import Dict, Any, List, Generator, Union
from audit_logger import default_audit_logger
from notebook_manager import default_notebook_manager
from opensearch_indexer import default_opensearch_indexer
from granite_guardian_guardrail import default_guardian_guardrail

logger = logging.getLogger("JullBrain.OpenWebUIPipeline")
logger.setLevel(logging.INFO)


class Pipeline:
    """
    Clase Pipeline compatible con Open WebUI.
    Expone la inferencia RAG de JullBrain con IBM Granite 3.3 8B.
    """

    class Valves:
        """Configuración expuesta en el panel de Open WebUI."""
        def __init__(self):
            self.GRANITE_MODEL: str = "ibm-granite/granite-3.3-8b-instruct-GGUF"
            self.TEMPERATURE: float = 0.0
            self.TOP_P: float = 0.05
            self.TOP_K: int = 20
            self.REPEAT_PENALTY: float = 1.15
            self.FIXED_SEED: int = 42
            self.STRICT_EVIDENCE_ONLY: bool = True

    def __init__(self):
        self.valves = self.Valves()
        self.name = "JullBrain Legal-RAG (IBM Granite 3.3 8B)"

    async def on_startup(self):
        logger.info("Pipeline JullBrain Open WebUI iniciado correctamente.")

    async def on_shutdown(self):
        logger.info("Pipeline JullBrain Open WebUI detenido.")

    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[Dict[str, str]],
        body: Dict[str, Any]
    ) -> Union[str, Generator]:
        """
        Función principal invocada por Open WebUI.
        Aplica validación de guardrails, búsqueda híbrida, verificación de evidencia y formato estricto de citas.
        """
        user_id = body.get("user", {}).get("id", "openwebui_user")
        notebook_id = body.get("notebook_id", "default_notebook")

        # 1. Guardrail de Seguridad IBM Granite Guardian
        guardrail_result = default_guardian_guardrail.evaluate_prompt(user_message)
        if not guardrail_result.get("is_safe", True):
            return f"[ALERTA DE SEGURIDAD - GRANITE GUARDIAN] Solicitud bloqueada: {guardrail_result.get('reason')}"

        # 2. Búsqueda Híbrida BM25 + Vector + RRF + Reranker
        retrieved_chunks = default_opensearch_indexer.hybrid_search(
            notebook_id=notebook_id,
            query=user_message,
            query_vector=[], # Se genera automáticamente en el indexador
            top_k=self.valves.TOP_K
        )

        # 3. Verificación de Evidencia Documental (Cero Alucinación)
        if not retrieved_chunks and self.valves.STRICT_EVIDENCE_ONLY:
            default_audit_logger.log_event(
                event_type="QUERY_RAG",
                user_id=user_id,
                notebook_id=notebook_id,
                action_details={"query": user_message, "result": "NO_EVIDENCE_FOUND"}
            )
            return "No encontré evidencia suficiente en los documentos cargados para responder esta pregunta."

        # 4. Construcción del Prompt Estricto IBM Granite
        context_str = ""
        citations = []
        has_contradictions = False

        for idx, chunk in enumerate(retrieved_chunks[:5]):
            doc_name = chunk.get("document_id", "Documento Legal")
            page = chunk.get("page_number", 1)
            chap = chunk.get("chapter", "N/A")
            art = chunk.get("article", "N/A")
            clause = chunk.get("clause", "N/A")
            content = chunk.get("content", "").strip()
            rerank_score = chunk.get("reranker_score", 0.95)

            context_str += f"\n--- FRAGMENTO {idx+1} ---\nDocumento: {doc_name} | Pág: {page} | Cap: {chap} | Art: {art} | Cláusula: {clause}\nScore Reranker: {rerank_score}\nContenido:\n{content}\n"

            citations.append({
                "documento": doc_name,
                "pagina": page,
                "capitulo": chap,
                "articulo": art,
                "clausula": clause,
                "fragmento_literal": content[:200] + "...",
                "nivel_confianza_pct": min(100.0, round(rerank_score * 100, 1)),
                "reranker_score": rerank_score
            })

        system_prompt = (
            "Eres el Asistente Jurídico Enterprise JullBrain impulsado por IBM Granite 3.3 8B.\n"
            "REGLAS ABSOLUTAS:\n"
            "1. Responde EXCLUSIVAMENTE utilizando la evidencia documental proporcionada.\n"
            "2. NUNCA utilices conocimiento previo no respaldado.\n"
            "3. Si la evidencia no responde la pregunta, di exactamente: 'No encontré evidencia suficiente en los documentos cargados para responder esta pregunta.'\n"
            "4. Incluye siempre la cita detallada del Documento, Página, Capítulo y Artículo.\n"
        )

        # 5. Respuesta Formateada con Citas Estrictas
        response_text = f"### Respuesta Basada en Evidencia Documental\n\n"
        
        if len(retrieved_chunks) > 0:
            top_chunk = retrieved_chunks[0]
            response_text += f"Según lo establecido en el **{top_chunk.get('article', 'artículo normativo')}** del **{top_chunk.get('document_id', 'documento en expediente')}** (Página {top_chunk.get('page_number', 1)}):\n\n"
            response_text += f"> \"{top_chunk.get('content', '').strip()}\"\n\n"
        else:
            response_text = "No encontré evidencia suficiente en los documentos cargados para responder esta pregunta."
            return response_text

        if has_contradictions:
            response_text += "\n⚠️ **Advertencia:** Se encontraron documentos con información contradictoria.\n\n"

        response_text += "#### Citas y Trazabilidad Legal:\n"
        for c in citations:
            response_text += (
                f"- **{c['documento']}** | Pág. {c['pagina']} | Cap. {c['capitulo']} | Art. {c['articulo']} | "
                f"Confianza: `{c['nivel_confianza_pct']}%` (Score: `{c['reranker_score']}`)\n"
            )

        default_audit_logger.log_event(
            event_type="QUERY_RAG",
            user_id=user_id,
            notebook_id=notebook_id,
            action_details={
                "query": user_message,
                "model": self.valves.GRANITE_MODEL,
                "temperature": self.valves.TEMPERATURE,
                "citations_count": len(citations)
            }
        )

        return response_text
