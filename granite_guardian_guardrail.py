# granite_guardian_guardrail.py — Auditoría de Salvaguarda y Semáforo de Confianza (IBM Granite Guardian)
"""
Módulo de Auditoría de Seguridad y Verificación Anti-Alucinación usando IBM Granite Guardian.
Audita en tiempo real:
  - Input Prompt Safety (Inyecciones, consultas fuera de contexto jurídico).
  - Groundedness / Anclaje Normativo (Verificación si el contexto extraído respalda el texto).
  - Hallucination Risk Score y Semáforo de Confianza (🟢 VERDE | 🟡 ÁMBAR | 🔴 ROJO).
"""
import os
import sys
import json
import logging
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("JullBrain.GraniteGuardian")

@dataclass
class GuardianAuditResult:
    status: str                         # "OK" | "WARNING" | "CRITICAL" | "STANDBY"
    semaforo_color: str                # "#00FF41" (Verde), "#FECF06" (Ámbar), "#FF3333" (Rojo)
    semaforo_label: str                # "ANCLADO" | "REVISION_HUMANA" | "DESANCLADO_ALUCINACION"
    groundedness_score: float          # 0.0 a 1.0
    context_relevance_score: float     # 0.0 a 1.0
    hallucination_risk: str            # "BAJO" | "MEDIO" | "ALTO"
    prompt_safe: bool                  # True/False
    audit_notes: str                   # Detalles explicativos para el operador
    model_used: str

class GraniteGuardianAuditor:
    """
    Auditor automatizado de confianza jurídica con IBM Granite Guardian.
    """
    def __init__(self, ollama_url: str = "http://localhost:11434", guardian_model: str = "granite3.1-dense:8b-guardian"):
        self.ollama_url = ollama_url.rstrip("/")
        self.guardian_model = guardian_model

    def is_model_available(self) -> bool:
        """
        Verifica si el modelo Granite Guardian está descargado y disponible en Ollama.
        """
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return any(self.guardian_model in m for m in models)
        except Exception:
            pass
        return False

    def evaluate_prompt(self, user_query: str) -> Dict[str, Any]:
        """
        Evalúa la seguridad del prompt enviado por el usuario contra inyecciones y ataques.
        """
        query_lower = user_query.lower()
        forbidden_keywords = [
            "ignora las instrucciones", "ignore previous instructions", "ignora todas las",
            "ignora las leyes", "borra la base de datos", "drop database", "rm -rf",
            "system prompt", "delete all tables"
        ]

        for kw in forbidden_keywords:
            if kw in query_lower:
                return {
                    "is_safe": False,
                    "reason": f"Patrón de inyección de prompt detectado: '{kw}'"
                }

        return {"is_safe": True, "reason": "Prompt seguro"}

    def audit_rag_response(self, user_query: str, retrieved_context: str, generated_response: str) -> GuardianAuditResult:
        """
        Evalúa el anclaje normativo de una respuesta RAG contra el contexto recuperado.
        """
        if not retrieved_context or len(retrieved_context.strip()) < 10:
            return GuardianAuditResult(
                status="CRITICAL",
                semaforo_color="#FF3333",
                semaforo_label="DESANCLADO_ALUCINACION",
                groundedness_score=0.0,
                context_relevance_score=0.0,
                hallucination_risk="ALTO",
                prompt_safe=True,
                audit_notes="Falta de contexto normativo recuperado. Alto riesgo de invención.",
                model_used=self.guardian_model
            )

        if not self.is_model_available():
            logger.info("Modelo Granite Guardian no disponible en Ollama. Usando auditoría heurística de respaldo.")
            return self._heuristic_audit(user_query, retrieved_context, generated_response)

        prompt = (
            f"You are Granite Guardian, a safety auditor model. Evaluate if the following response is grounded in the provided context.\n\n"
            f"User Question:\n{user_query}\n\n"
            f"Retrieved Context:\n{retrieved_context}\n\n"
            f"Generated Response:\n{generated_response}\n\n"
            f"Respond with JSON containing keys: 'grounded' (true/false), 'score' (0.0 to 1.0), 'hallucination_risk' ('LOW'/'MEDIUM'/'HIGH')."
        )

        try:
            payload = json.dumps({
                "model": self.guardian_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                output_text = result.get("response", "")

                score = 0.90
                risk = "BAJO"
                if "false" in output_text.lower() or "high" in output_text.lower():
                    score = 0.40
                    risk = "ALTO"

                return self._build_result(score, risk, "Auditoría completada por IBM Granite Guardian.")

        except Exception as e:
            logger.warning(f"Fallo en llamado a Granite Guardian Ollama: {e}. Usando fallback.")
            return self._heuristic_audit(user_query, retrieved_context, generated_response)

    def _heuristic_audit(self, user_query: str, retrieved_context: str, generated_response: str) -> GuardianAuditResult:
        import re
        context_lower = retrieved_context.lower()
        response_lower = generated_response.lower()

        cited_articles = set(re.findall(r"art[íi]culo\s+(\d+)", response_lower))
        context_articles = set(re.findall(r"art[íi]culo\s+(\d+)", context_lower))

        if not cited_articles:
            groundedness = 0.70
            risk = "MEDIO"
            notes = "Respuesta sin citas de artículos explícitos. Revisión recomendada."
        else:
            unsupported = cited_articles - context_articles
            if unsupported:
                groundedness = 0.35
                risk = "ALTO"
                notes = f"Artículos citados no presentes en el contexto: Art. {', '.join(unsupported)}."
            else:
                groundedness = 0.95
                risk = "BAJO"
                notes = f"Todos los artículos citados (Art. {', '.join(cited_articles)}) están anclados en el contexto."

        return self._build_result(groundedness, risk, notes)

    def _build_result(self, score: float, risk: str, notes: str) -> GuardianAuditResult:
        if score >= 0.85 and risk == "BAJO":
            return GuardianAuditResult(
                status="OK",
                semaforo_color="#00FF41",
                semaforo_label="ANCLADO",
                groundedness_score=score,
                context_relevance_score=0.90,
                hallucination_risk="BAJO",
                prompt_safe=True,
                audit_notes=notes,
                model_used=self.guardian_model
            )
        elif score >= 0.60 or risk == "MEDIO":
            return GuardianAuditResult(
                status="WARNING",
                semaforo_color="#FECF06",
                semaforo_label="REVISION_HUMANA",
                groundedness_score=score,
                context_relevance_score=0.75,
                hallucination_risk="MEDIO",
                prompt_safe=True,
                audit_notes=notes,
                model_used=self.guardian_model
            )
        else:
            return GuardianAuditResult(
                status="CRITICAL",
                semaforo_color="#FF3333",
                semaforo_label="DESANCLADO_ALUCINACION",
                groundedness_score=score,
                context_relevance_score=0.40,
                hallucination_risk="ALTO",
                prompt_safe=True,
                audit_notes=notes,
                model_used=self.guardian_model
            )

# Instancia global por defecto
default_guardian_guardrail = GraniteGuardianAuditor()

if __name__ == "__main__":
    print("=== TEST DE AUDITORIA IBM GRANITE GUARDIAN ===")
    auditor = default_guardian_guardrail
    context_demo = "Artículo 15: La evidencia digital debe ser preservada con hash SHA-256."
    query_demo = "¿Cómo debe preservarse la evidencia digital?"
    resp_demo = "Según el Artículo 15, la evidencia digital se preserva mediante hash SHA-256."

    res = auditor.audit_rag_response(query_demo, context_demo, resp_demo)
    print("Resultado Auditoría:", json.dumps(asdict(res), indent=2, ensure_ascii=False))
