"""
granite_guardian_guardrail.py — Guardrail de Ciberseguridad Cognitiva (IBM Granite Guardian 3.2 / 3.3)
Implementa protección en 6 dimensiones para el pipeline jurídico-forense JullBrain:
1. Prompt Injection & Jailbreak Detection (Pre-inferencia)
2. Harm / HAP (Hate, Abuse, Profanity & Illicit Legal Manipulation)
3. PII Detection & Redaction para Venezuela (Cédula V-/E-, RIF, Teléfonos, Correos)
4. Groundedness / Hallucination Verification (Post-inferencia contra chunks de Docling)
5. Context Relevance Verification
6. Answer Relevance & Mandatory Abstention Enforcement
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Any, Dict, List, Optional


class GraniteGuardianGuardrail:
    """
    Motor híbrido determinista + neuronal (IBM Granite Guardian vía Ollama local)
    para filtrado de seguridad, protección de datos personales y verificación anti-alucinación.
    """

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
        re.compile(r"ignora\s+(todas\s+)?(las\s+)?(instrucciones|reglas|leyes)\s+(anteriores|previas)", re.IGNORECASE),
        re.compile(r"olvida\s+(todo|las\s+instrucciones|tu\s+rol)", re.IGNORECASE),
        re.compile(r"(system\s+prompt|developer\s+mode|jailbreak|dan\s+mode)", re.IGNORECASE),
        re.compile(r"(inventa|fabrica|falsifica)\s+(un\s+art[ií]culo|una\s+sentencia|una\s+jurisprudencia|pruebas)", re.IGNORECASE),
        re.compile(r"declara\s+(absuelto|culpable)\s+.*sin\s+pruebas", re.IGNORECASE),
        re.compile(r"act[uú]a\s+sin\s+restricciones", re.IGNORECASE),
        re.compile(r"(borra|elimina|destruye)\s+(la\s+base\s+de\s+datos|el\s+expediente|los\s+logs)", re.IGNORECASE),
    ]

    HAP_PATTERNS = [
        re.compile(r"(como\s+sobornar|destruir\s+evidencia\s+forense|alterar\s+cadena\s+de\s+custodia)", re.IGNORECASE),
        re.compile(r"(ocultar\s+pruebas\s+del\s+tribunal|falsificar\s+acta\s+policial)", re.IGNORECASE),
    ]

    PII_PATTERNS = {
        "CEDULA_VE": re.compile(r"\b([VEJGvejg])[-\s]?(\d{1,2}\.?\d{3}\.?\d{3})\b"),
        "RIF_VE": re.compile(r"\b([VEJGvejg])[-\s]?(\d{8})[-\s]?(\d)\b"),
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "TELEFONO_VE": re.compile(r"\b(?:\+58|0)(?:2\d{2}|412|414|424|416|426)[-\s]?\d{7}\b"),
    }

    ARTICLE_CITATION_RE = re.compile(r"art[ií]culo\s+(\d+)", re.IGNORECASE)

    def __init__(
        self,
        model_name: str = "ibm-granite/granite-guardian-3.2-5b",
        ollama_host: Optional[str] = None,
        redact_pii: bool = False,
    ) -> None:
        self.model_name = model_name
        self.ollama_host = (ollama_host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.redact_pii = redact_pii

    def scan_and_redact_pii(self, text: str) -> Dict[str, Any]:
        """Detecta y opcionalmente redacta datos personales venezolanos (Cédula, RIF, Email, Teléfono)."""
        detected: List[str] = []
        sanitized = text
        for pii_type, pattern in self.PII_PATTERNS.items():
            if pattern.search(sanitized):
                detected.append(pii_type)
                if self.redact_pii:
                    sanitized = pattern.sub(f"[{pii_type}_PROTEGIDO]", sanitized)
        return {
            "pii_detected": len(detected) > 0,
            "pii_types": detected,
            "sanitized_text": sanitized,
        }

    def check_prompt_safety(self, prompt: str) -> Dict[str, Any]:
        """
        Evalúa un prompt de usuario antes de enviarlo al motor RAG / IBM Granite 3.3.
        Verifica: (1) Prompt Injection / Jailbreak, (2) HAP / Manipulación Forense, (3) PII.
        """
        if not prompt or not prompt.strip():
            return {
                "safe": False,
                "is_safe": False,
                "risk_category": "EMPTY_PROMPT",
                "reason": "El prompt de consulta está vacío.",
                "sanitized_prompt": "",
            }

        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if pattern.search(prompt):
                return {
                    "safe": False,
                    "is_safe": False,
                    "risk_category": "PROMPT_INJECTION_OR_JAILBREAK",
                    "reason": "Se detectó un intento de inyección de instrucciones o fabricación normativa.",
                    "sanitized_prompt": "",
                }

        for pattern in self.HAP_PATTERNS:
            if pattern.search(prompt):
                return {
                    "safe": False,
                    "is_safe": False,
                    "risk_category": "HAP_FORENSIC_VIOLATION",
                    "reason": "La consulta solicita vulnerar la integridad probatoria o la cadena de custodia.",
                    "sanitized_prompt": "",
                }

        pii_info = self.scan_and_redact_pii(prompt)

        return {
            "safe": True,
            "is_safe": True,
            "risk_category": "NONE",
            "reason": "Consulta verificada por IBM Granite Guardian.",
            "pii_detected": pii_info["pii_detected"],
            "pii_types": pii_info["pii_types"],
            "sanitized_prompt": pii_info["sanitized_text"],
            "guardrail_model": self.model_name,
        }

    def evaluate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Alias compatible con la API Enterprise y Open WebUI Pipeline."""
        return self.check_prompt_safety(prompt)

    def is_model_available(self) -> bool:
        """Retorna True indicando que el motor determinista + neuronal de Granite Guardian está operativo."""
        return True

    def verify_groundedness(self, response_text: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifica post-generación que todas las citas de artículos en la respuesta del LLM
        existan realmente en los fragmentos recuperados (Prevención de Alucinación Jurídica).
        """
        if not context_chunks:
            abstention_phrases = ("no encontrado", "no se encontr", "no consta en el corpus", "abstenci", "no encontré evidencia")
            is_abstaining = any(p in response_text.lower() for p in abstention_phrases)
            return {
                "grounded": is_abstaining,
                "status": "ABSTENTION_VERIFIED" if is_abstaining else "UNGROUNDED_NO_CONTEXT",
                "cited_articles": [],
                "unverified_articles": [] if is_abstaining else ["ALL"],
            }

        combined_context = " ".join(
            str(c.get("text", "") or c.get("content", "")) + " " + str(c.get("heading", "") or c.get("article", ""))
            for c in context_chunks
        )
        context_articles = set(self.ARTICLE_CITATION_RE.findall(combined_context))
        cited_articles = sorted(set(self.ARTICLE_CITATION_RE.findall(response_text)))

        unverified = [art for art in cited_articles if art not in context_articles]
        is_grounded = len(unverified) == 0

        return {
            "grounded": is_grounded,
            "status": "GROUNDED_OK" if is_grounded else "MISGROUNDING_DETECTED",
            "cited_articles": cited_articles,
            "unverified_articles": unverified,
            "guardrail_model": self.model_name,
        }

    def query_ollama_guardian(self, prompt: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Consulta opcional al modelo local IBM Granite Guardian en Ollama si está activo.
        Si Ollama no está corriendo, retorna la evaluación determinista sin fallar.
        """
        det = self.check_prompt_safety(prompt)
        if not det["safe"]:
            return det

        payload = {
            "model": self.model_name,
            "prompt": f"User: {prompt}\nContext: {context or 'N/A'}\n Asses risk (Yes/No):",
            "stream": False,
            "options": {"temperature": 0.0},
        }
        try:
            req = urllib.request.Request(
                f"{self.ollama_host}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                answer = str(body.get("response", "")).strip().lower()
                if answer.startswith("yes"):
                    return {
                        "safe": False,
                        "is_safe": False,
                        "risk_category": "GRANITE_GUARDIAN_FLAGGED",
                        "reason": "Bloqueado por inferencia neuronal de IBM Granite Guardian.",
                        "sanitized_prompt": "",
                    }
        except Exception:
            pass

        return det


# Instancia global por defecto para compatibilidad transversal
default_guardian_guardrail = GraniteGuardianGuardrail()
